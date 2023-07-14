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

import os
import argparse
import gzip
from datetime import datetime
import requests
import yaml


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


def write_to_disk(path, date_str, feed_name, content):
    """
    Write content to disk as a gzipped file.
    """
    output_file = os.path.join(path, f"{date_str}_{feed_name}.txt.gz")
    try:
        with gzip.open(output_file, 'wb') as file:
            file.write(content)
    except (OSError, TypeError) as err:
        print(f"Failed to write to {output_file} due to {str(err)}")

def main():
    """
    Main function of the script.

    This function does the following:
        1. Parses command-line arguments.
        2. Loads feeds from the YAML file.
        3. Creates necessary directories.
        4. Downloads content for each feed.
        5. Writes content to disk if download is successful.
    """
    args = parse_args()

    # Path to your YAML file
    yaml_file = args.feed

    # Root directory for output
    root_dir = args.workdir

    # Load feeds from the YAML file
    feeds = load_feeds(yaml_file)

    # For each feed in the YAML file
    for feed in feeds:
        # Create a subdirectory with the current date
        date_str = datetime.now().strftime("%Y/%m/%d")
        output_dir = os.path.join(root_dir, date_str)
        create_directory(output_dir)

        # Download the file from feed's url
        content = download_feed(feed['url'])

        # If the download was successful, write the file to disk
        if content is not None:
            write_to_disk(output_dir, date_str.replace("/", "_"), feed['name'], content)


if __name__ == "__main__":
    main()
