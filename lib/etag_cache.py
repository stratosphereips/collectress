"""
Utility functions for the Collectress tool.

This module contains functions for managing the ETag cache used by the Collectress tool,
which is responsible for downloading data feeds.

Functions:
    load_etag_cache: Load the ETag cache from a JSON file at the specified path.
    save_etag_cache: Save the ETag cache to a JSON file at the specified path.
    add_to_etag_cache: Add an ETag and associated feed information to the ETag cache.
Each function is documented individually below.
"""

import json
import os
import shutil
from datetime import datetime
from datetime import timedelta

def add_to_etag_cache(etag_cache, etag, feed_url, feed_name, feed_organization):
    """
    Adds an ETag and associated feed information to the ETag cache.

    Args:
        etag_cache (dict): The ETag cache.
        etag (str): The ETag.
        feed_url (str): The URL of the feed.
        feed_name (str): The name of the feed.
        feed_organization (str): The organization that provides the feed.

    Returns:
        None. The ETag cache is updated in-place.
    """
    download_date = datetime.now().isoformat()

    etag_cache[feed_url] = {
        "etag": etag,
        "feed_name": feed_name,
        "feed_organization": feed_organization,
        "download_date": download_date
    }


def remove_from_etag_cache(feed_url, etag_cache):
    """
    Removes an ETag and associated feed information from the ETag cache.

    Args:
        feed_url (str): The URL of the feed.
        etag_cache (dict): The ETag cache.

    Returns:
        None. The ETag cache is updated in-place.
    """
    if feed_url in etag_cache:
        del etag_cache[feed_url]


def load_etag_cache(etag_cache_file):
    """
    Load the ETag cache from a file.

    Args:
        etag_cache_file (str): The path to the ETag cache file.

    Returns:
        dict: The ETag cache. If an error occurs while reading the file,
              or if the file does not exist, return an empty dictionary.
    """
    try:
        with open(etag_cache_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_etag_cache(etag_cache_file, etag_cache):
    """
    Save the ETag cache to a file.

    Args:
        etag_cache_file (str): The path to the ETag cache file.
        etag_cache (dict): The ETag cache to be saved.

    Raises:
        IOError: An error occurred while writing the ETag cache to the file.
    """
    try:
        with open(etag_cache_file, 'w', encoding='utf-8') as file:
            json.dump(etag_cache, file)
    except IOError as err:
        print(f"An error occurred writing the ETag cache to the file {etag_cache_file}: {err}")

def copy_file_from_cache(root_dir, feed):
    """
    If there was a cache hit, this function Copies the file from
    yesterday's directory to today's directory.

    Args:
        root_dir (str): The root directory where files are stored.
        output_dir (str): The output directory for today.
        feed (dict): The feed information.

    Returns:
        bool: True if the file was successfully copied, False otherwise.
    """
    yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    today_date_str = (datetime.now()).strftime("%Y/%m/%d")

    yesterday_file_path = os.path.join(root_dir,
            yesterday_date_str,
            f"{yesterday_date_str.replace('/', '_')}_{feed['org']}_{feed['name']}.txt.gz")

    today_file_path = os.path.join(root_dir,
            today_date_str,
            f"{today_date_str.replace('/', '_')}_{feed['org']}_{feed['name']}.txt.gz")

    # Case 1: check if today's file exists
    #         - Content was not modified and file exists = true = no action
    if os.path.isfile(today_file_path):
        return True

    # Case 2: today file does not exist, check if yesterday's file exists
    #         - If yesterday file does not exist = false = no action
    if not os.path.isfile(yesterday_file_path):
        return False

    # Case 3: today file is not there, yesterday file is there
    #         - Copy the file from yesterday and today = True
    try:
        shutil.copy2(yesterday_file_path, today_file_path)
        return True
    except IOError:
        return False


def remove_old_etags(etag_cache, cache_file_path):
    """
    Removes ETags that are older than 24 hours from the ETag cache.

    Args:
        etag_cache (dict): The ETag cache.
        cache_file_path (str): The path to the ETag cache file.

    Returns:
        None. The ETag cache is updated in-place.
    """
    # Get the current date and time
    now = datetime.now()

    # Initialize a list to store the feed URLs of old ETags
    old_etags = []

    # Iterate over the ETag cache
    for feed_url, etag_info in etag_cache.items():
        # Parse the download date of the ETag as a datetime object
        download_date = datetime.fromisoformat(etag_info['download_date'])

        # If the ETag is older than 24 hours, add its feed URL to the list of old ETags
        if now - download_date > timedelta(hours=24):
            old_etags.append(feed_url)

    # Remove the old ETags from the cache
    for feed_url in old_etags:
        etag_cache.pop(feed_url)

    # Save the updated ETag cache
    with open(cache_file_path, 'w', encoding='utf-8') as file:
        json.dump(etag_cache, file)
