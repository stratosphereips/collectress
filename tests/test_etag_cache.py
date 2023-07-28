# pylint: disable=missing-docstring
import json
import sys
import tempfile
from os import path
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
