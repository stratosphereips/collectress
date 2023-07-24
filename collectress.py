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
from pythonjsonlogger import jsonlogger

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
    -f or --feedfile: The path to the YAML file containing the feeds.
    -w or --workdir: The path to the root directory for output.

    Returns:
        args: A Namespace object built from the attributes parsed out of the command line.
              It contains two attributes:
                  args.feedfile: The path to the YAML file containing the feeds.
                  args.workdir: The path to the root directory for output.
    """


    parser = argparse.ArgumentParser(description='Programatically download feeds from YAML file.')
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


def download_feed(feed_url):
    """
    Download a feed from a given URL.

    This function sends a GET request to the provided URL and returns the response
    content if the status code is 200. If the status code is not 200, or if an error
    occurs during the request, the function will print an error message and return None.

    Args:
        feed_url (str): The URL of the feed to be downloaded.

    Returns:
        bytes: The content of the response if the request is successful; otherwise, None.

    Raises:
        Exception: An exception is raised if there's an error during the request,
                   such as a timeout error or a connection error.
    """
    try:
        response = requests.get(feed_url)
        if response.status_code != 200:
            print(f"Failed to download {feed_url}. Status code: {response.status_code}")
            return None
        return response.content
    except requests.RequestException as err:
        print(f"Failed to download {feed_url} due to {str(err)}")
        return None


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

    # Statistical variables to log
    total_feeds_processed = 0
    total_feeds_success = 0
    total_feeds_failed = 0
    total_data_downloaded = 0
    total_runtime = 0
    successful_feeds = []
    failed_feeds = []
    success_rate = 0
    error_rate = 0

    # For each feed in the YAML file
    for feed in feeds:
        # Increase feeds processed
        total_feeds_processed += 1

        # Create a subdirectory with the current date
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join(root_dir, date_str)
        create_directory(output_dir)

        # Download the file from feed's url
        content = download_feed(feed['url'])

        # If the download was successful, write the file to disk
        if content is not None:
            total_data_downloaded += len(content)
            write_to_disk(output_dir,
                          date_str.replace("/", "_"),
                          feed['org'],
                          feed['name'],
                          content)
            successful_feeds.append(feed['name'])
            total_feeds_success += 1
        else:
            total_feeds_failed += 1
            failed_feeds.append(feed['name'])

    # Calculate success and error rates
    if total_feeds_processed > 0:
        success_rate = (total_feeds_success / total_feeds_processed) * 100
        error_rate = (total_feeds_failed / total_feeds_processed) * 100


    # Record the end time
    end_time = time.time()

    # Calculate the total runtime
    total_runtime = end_time - start_time

    summary = {
        'message': f"{date_str.replace('/', '-')} collectress download summary",
        'timestamp': datetime.now().isoformat(),
        'total_feeds_processed': total_feeds_processed,
        'total_feeds_success': total_feeds_success,
        'total_feeds_failed': total_feeds_failed,
        'successful_feeds': successful_feeds,
        'failed_feeds': failed_feeds,
        'total_data_downloaded_bytes': total_data_downloaded,
        'total_runtime_seconds': total_runtime,
        'success_rate': success_rate,
        'error_rate': error_rate,
    }
    logger.info(summary)

if __name__ == "__main__":
    main()
