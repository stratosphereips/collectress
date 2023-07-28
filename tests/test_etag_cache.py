# pylint: disable=missing-docstring
import json
import sys
import tempfile
from datetime import datetime
from datetime import timedelta
from os import path
from unittest.mock import ANY
from unittest.mock import patch
from unittest.mock import mock_open
sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from lib.etag_cache import load_etag_cache
from lib.etag_cache import add_to_etag_cache
from lib.etag_cache import remove_from_etag_cache
from lib.etag_cache import copy_file_from_cache
from lib.etag_cache import save_etag_cache
from lib.etag_cache import remove_old_etags


class TestEtagCache:
    def test_load_etag_cache(self):
        # Prepare a dictionary with ETag cache data
        etag_data = {
            "https://example.com/feed1.xml": {
                "etag": "\"33a64df551425fcc55e4d42a148795d9f25f89d4\"",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": "2023-07-21T14:30:16.123456"
            },
            "https://example.com/feed2.xml": {
                "etag": "\"58e6b3a414a1e090dfc6029add0f3555ccba172f\"",
                "feed_name": "Feed 2",
                "feed_organization": "Organization 2",
                "download_date": "2023-07-21T14:35:42.654321"
            }
        }

        # Create a temporary file and write the ETag cache data into it
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpfile:
            json.dump(etag_data, tmpfile)

        # Load the ETag cache using the function under test
        loaded_etag_data = load_etag_cache(tmpfile.name)

        # Assert that the loaded data matches the original data
        assert loaded_etag_data == etag_data

    def test_remove_from_etag_cache(self):
        # Create a sample etag_cache dictionary
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "etag1",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": "2023-07-21T14:30:16.123456"
            },
            "https://dummyurl.com/feed2.xml": {
                "etag": "etag2",
                "feed_name": "Feed 2",
                "feed_organization": "Organization 2",
                "download_date": "2023-07-21T14:35:42.654321"
            }
        }

        # Call the function to remove an etag from the cache
        remove_from_etag_cache("https://dummyurl.com/feed1.xml", etag_cache)

        # Assert that the etag has been removed from the cache
        assert "https://dummyurl.com/feed1.xml" not in etag_cache

    def test_remove_nonexistent_from_etag_cache(self):
        # Create a sample etag_cache dictionary
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "etag1",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": "2023-07-21T14:30:16.123456"
            },
            "https://dummyurl.com/feed2.xml": {
                "etag": "etag2",
                "feed_name": "Feed 2",
                "feed_organization": "Organization 2",
                "download_date": "2023-07-21T14:35:42.654321"
            }
        }

        # Call the function to remove an etag that does not exist in the cache
        remove_from_etag_cache("https://nonexistenturl.com/feed3.xml", etag_cache)

        # Assert that the cache has not been modified
        assert len(etag_cache) == 2

    def test_add_to_etag_cache(self):
        # Create a sample etag_cache dictionary
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "etag1",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": "2023-07-21T14:30:16.123456"
            }
        }

        # Call the function to add an etag to the cache
        add_to_etag_cache(etag_cache,
                          "etag2",
                          "https://dummyurl.com/feed2.xml",
                          "Feed 2",
                          "Organization 2")

        # Assert that the etag has been added to the cache
        assert "https://dummyurl.com/feed2.xml" in etag_cache
        assert etag_cache["https://dummyurl.com/feed2.xml"] == {
            "etag": "etag2",
            "feed_name": "Feed 2",
            "feed_organization": "Organization 2",
            "download_date": ANY  # We can't know the exact datetime
        }


    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_etag_cache(self, mock_json_dump, mock_file):
        # Create a sample etag_cache dictionary
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "etag1",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": "2023-07-21T14:30:16.123456"
            }
        }

        # Call the function to save the etag cache
        save_etag_cache("etag_cache.json", etag_cache)

        # Assert that the function correctly called the built-in open function
        mock_file.assert_called_once_with("etag_cache.json", 'w', encoding='utf-8')

        # Assert that the function correctly called json.dump with the correct arguments
        mock_json_dump.assert_called_once_with(etag_cache, mock_file())


    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.isfile')
    @patch('shutil.copy2')
    def test_copy_file_from_cache(self, mock_copy, mock_isfile, mock_file):
        # Setup: create a mock feed and root_dir
        feed = {'org': 'test_org', 'name': 'test_name'}
        root_dir = '/path/to/root_dir'

        # Case 1: yesterday's file exists, today's file does not
        mock_isfile.side_effect = [False, True]  # Reversed the order
        assert copy_file_from_cache(root_dir, feed) is True
        mock_copy.assert_called_once()

        # Reset mock for the next test case
        mock_copy.reset_mock()

        # Case 2: yesterday's file does not exist
        mock_isfile.side_effect = [False, False]  # No file exists
        assert copy_file_from_cache(root_dir, feed) is False
        mock_copy.assert_not_called()

        # Case 3: yesterday's file exists, today's file also exists
        mock_isfile.side_effect = [True, True]  # Both files exist
        assert copy_file_from_cache(root_dir, feed) is True
        mock_copy.assert_not_called()

        # Case 4: IOError when attempting to copy file
        mock_isfile.side_effect = [False, True]  # yesterday's file exists, today's file does not
        mock_copy.side_effect = IOError()
        assert copy_file_from_cache(root_dir, feed) is False


    @patch('json.dump')
    def test_remove_old_etags(self, mock_json_dump):
        # Case 1: ETag cache is empty
        etag_cache = {}
        remove_old_etags(etag_cache, "etag_cache.json")
        mock_json_dump.assert_called_once_with(etag_cache, ANY)

        # Reset mock for the next test case
        mock_json_dump.reset_mock()

        # Case 2: ETag cache contains some ETags that are less than 24 hours old
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "\"etag1\"",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": (datetime.now() - timedelta(hours=23)).isoformat()
            }
        }
        remove_old_etags(etag_cache, "etag_cache.json")
        mock_json_dump.assert_called_once_with(etag_cache, ANY)

        # Reset mock for the next test case
        mock_json_dump.reset_mock()

        # Case 3: ETag cache contains some ETags that are more than 24 hours old
        etag_cache = {
            "https://dummyurl.com/feed1.xml": {
                "etag": "\"etag1\"",
                "feed_name": "Feed 1",
                "feed_organization": "Organization 1",
                "download_date": (datetime.now() - timedelta(hours=25)).isoformat()
            }
        }
        expected_etag_cache = {}  # After removing the old ETag, the cache should be empty
        remove_old_etags(etag_cache, "etag_cache.json")
        mock_json_dump.assert_called_once_with(expected_etag_cache, ANY)
