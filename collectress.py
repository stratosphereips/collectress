"""
This script is used to programmatically download feeds from a YAML file.

The YAML file should contain a list of feeds, each with a name and a URL.
The script creates a directory structure for each feed, and stores the
downloaded content in directories named by the current date.

The script requires two command-line arguments:
    -f or --feedfile: The path to the YAML file containing the feeds.
    -w or --workdir: The path to the root directory for output.

Example usage:
    python script.py -f data_feeds.yaml -w path/to/directory
"""

import tempfile
import time
import os
import argparse
import gzip
from datetime import datetime
import logging
import requests
import yaml
from tqdm import tqdm
from pythonjsonlogger import jsonlogger
from lib.etag_cache import load_etag_cache
from lib.etag_cache import add_to_etag_cache
from lib.etag_cache import remove_from_etag_cache
from lib.etag_cache import copy_file_from_cache
from lib.etag_cache import save_etag_cache
from lib.etag_cache import remove_old_etags

# Create a logger
logger = logging.getLogger()

# Create a handler that writes log records to a file
handler = logging.FileHandler('log.json')

# Create a formatter that outputs log records in JSON
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Set the severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger.setLevel(logging.INFO)

def parse_args():
    """
    Parse command-line arguments.

    The function expects two command-line arguments:
    -e or --etagcache: The path to the YAML file containing the feeds.
    -f or --feed: The path to the YAML file containing the feeds.
    -w or --workdir: The path to the root directory for output.

    Returns:
        args: A Namespace object built from the attributes parsed out of the command line.
              It contains two attributes:
                  args.feedfile: The path to the YAML file containing the feeds.
                  args.workdir: The path to the root directory for output.
    """


    parser = argparse.ArgumentParser(description='Programatically download feeds from YAML file.')
    parser.add_argument('-e', '--ecache', required=True, help='eTag cache for optimizing downloads')
    parser.add_argument('-f', '--feed', required=True, help='YAML file containing the feeds')
    parser.add_argument('-w', '--workdir', required=True, help='The root of the output directory')
    return parser.parse_args()


def load_feeds(yaml_file):
    """
    Load feeds from a YAML file.

    The function reads a YAML file and returns a list of feeds,
    where each feed is a dictionary with 'name' and 'url' keys.

    Args:
        yaml_file (str): The path to the YAML file containing the feeds.

    Returns:
        list: A list of dictionaries. Each dictionary represents a feed with 'name' and 'url' keys.

    Raises:
        Exception: An exception is raised if there's an error reading the file or parsing the YAML.
    """
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data['feeds']
    except (OSError, yaml.YAMLError) as err:
        print(f"Failed to load feeds from {yaml_file} due to {str(err)}")
        return []

def create_directory(path):
    """
    Create a directory at the given path.

    This function creates a new directory at the provided path. If the
    directory already exists, the function will not raise an error.

    Args:
        path (str): The path where the directory should be created.

    Raises:
        Exception: An exception is raised if there's an error creating the directory,
                   such as a permission error or a disk full error.
    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as err:
        print(f"Failed to create directory {path} due to {str(err)}")


def download_feed(feed_url, etag_cache):
    """
    Download a feed from a given URL.

    This function sends a GET request to the provided URL and returns the response
    content, the ETag of the response, and a status code. The status code can be
    one of the following:
    - "success": The feed was downloaded successfully.
    - "not_modified": The feed was not downloaded because the ETag has
                      not changed since the last download.
    - "error": There was an error during the download.

    Args:
        feed_url (str): The URL of the feed to be downloaded.
        etag_cache (dict): A dictionary that maps feed URLs to ETags.

    Returns:
        tuple: A tuple of three items: the content of the response
               (or None if the download was not successful or necessary),
               the ETag of the response (or None if there was an error),
               and a status code.
    """
    headers = {}
    if feed_url in etag_cache:
        headers['If-None-Match'] = etag_cache[feed_url]['etag']

    try:
        response = requests.get(feed_url, headers=headers)

        # If response is 200, file is downloaded and returned
        if response.status_code == 200:
            return response.content, response.headers.get('ETag'), "success"

        # If response is 304, file is not downloaded
        if response.status_code == 304:
            return None, None, "not_modified"

        # Any other case is considered failure and error is returned
        print(f"Failed to download {feed_url}. Status code: {response.status_code}")
        return None, None, "error"
    except requests.RequestException as err:
        print(f"Failed to download {feed_url} due to {str(err)}")
        return None, None, "error"


def should_replace(existing_file, new_content):
    """
    Check if a new file should replace an existing file.

    The new content should replace the existing file if:
    - The new content is larger than the existing file, or
    - The new content has a different hash than the existing file.

    Args:
        existing_file (str): The path to the existing file.
        new_content (bytes): The content to be written.

    Returns:
        bool: True if the new content should replace the existing file, False otherwise.
    """
    # If the existing file doesn't exist, there's nothing to replace
    if not os.path.exists(existing_file):
        return True

    # Write the new content to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".txt.gz", delete=False) as temp_file:
        with gzip.open(temp_file.name, 'wb') as gzip_file:
            gzip_file.write(new_content)
    temp_file_path = temp_file.name

    # Compare the size of the temporary file and the existing file
    if os.path.getsize(temp_file_path) > os.path.getsize(existing_file):
        os.remove(temp_file_path)
        return True

    os.remove(temp_file_path)  # We're done with the temporary file now

    # Otherwise, don't replace the existing file
    return False


def write_to_disk(path, date_str, feed_org, feed_name, content):
    """
    Write content to disk as a gzipped file.
    """
    output_file = os.path.join(path, f"{date_str}_{feed_org}_{feed_name}.txt.gz")

    # If the file already exists and should not be replaced, return
    if os.path.exists(output_file) and not should_replace(output_file, content):
        return

    try:
        with gzip.open(output_file, 'wb') as file:
            file.write(content)
    except (OSError, TypeError) as err:
        print(f"Failed to write to {output_file} due to {str(err)}")


def main(): # pylint: disable=too-many-locals
    """
    Main function of the script.

    This function does the following:
        1. Parses command-line arguments.
        2. Loads feeds from the YAML file.
        3. Creates necessary directories.
        4. Downloads content for each feed.
        5. Writes content to disk if download is successful.
    """
    # Record the start time
    start_time = time.time()

    args = parse_args()

    # Path to your YAML file
    yaml_file = args.feed

    # Root directory for output
    root_dir = args.workdir

    # Load feeds from the YAML file
    feeds = load_feeds(yaml_file)

    # Load etag cache from disk
    etag_cache = load_etag_cache(args.ecache)

    # Check expired eTags
    remove_old_etags(etag_cache, args.ecache)

    # Statistical variables to log
    total_feeds_processed = 0
    total_feeds_not_modified = 0
    total_feeds_success = 0
    total_feeds_failed = 0
    total_data_downloaded = 0
    total_runtime = 0
    successful_feeds = []
    not_modified_feeds = []
    failed_feeds = []
    success_rate = 0
    error_rate = 0

    # For each feed in the YAML file
    for feed in tqdm(feeds):
        # Increase feeds processed
        total_feeds_processed += 1

        # Create a subdirectory with the current date
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join(root_dir, date_str)
        create_directory(output_dir)

        # Download the file from feed's url
        content, etag, status = download_feed(feed['url'], etag_cache)

        # If the download was successful, write the file to disk
        if status == "not_modified":
            # The file has not changed since yesterday
            # Copy file from yesterday to today
            if copy_file_from_cache(root_dir, feed):
                # Record metrics
                not_modified_feeds.append(feed['name'])
                total_feeds_not_modified += 1
            else:
                print("copy_file_from_cache: failed")
                # The file download failed, remove etag from cache
                remove_from_etag_cache(feed['url'], etag_cache)
                # Record metrics
                total_feeds_failed += 1
                failed_feeds.append(feed['name'])
        elif status == "success":
            # Store the ETag in the cache
            add_to_etag_cache(etag_cache, etag, feed['url'], feed['name'], feed['org'])

            # Save the content to disk
            write_to_disk(output_dir,
                          date_str.replace("/", "_"),
                          feed['org'],
                          feed['name'],
                          content)

            # Record metrics
            total_data_downloaded += len(content)
            successful_feeds.append(feed['name'])
            total_feeds_success += 1
        else:
            # The file download failed
            total_feeds_failed += 1
            failed_feeds.append(feed['name'])

    # Calculate success and error rates
    if total_feeds_processed > 0:
        success_rate = ((total_feeds_success+total_feeds_not_modified)/total_feeds_processed) * 100
        error_rate = (total_feeds_failed / total_feeds_processed) * 100


    # Record the end time
    end_time = time.time()

    # Calculate the total runtime
    total_runtime = end_time - start_time

    # Save the ETag cache
    save_etag_cache(args.ecache, etag_cache)

    summary = {
        'message': f"{date_str.replace('/', '-')} collectress download summary",
        'timestamp': datetime.now().isoformat(),
        'total_feeds_processed': total_feeds_processed,
        'total_feeds_not_modified': total_feeds_not_modified,
        'total_feeds_success': total_feeds_success,
        'total_feeds_failed': total_feeds_failed,
        'feeds_not_modified': not_modified_feeds,
        'feeds_successful': successful_feeds,
        'feeds_failed': failed_feeds,
        'total_data_downloaded_bytes': total_data_downloaded,
        'total_runtime_seconds': total_runtime,
        'success_rate': success_rate,
        'error_rate': error_rate,
    }
    logger.info(summary)

if __name__ == "__main__":
    main()
