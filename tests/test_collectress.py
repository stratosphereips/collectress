import argparse
import sys
import os
import shutil
from os import path
from unittest.mock import patch
import gzip
sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from collectress import create_directory
from collectress import write_to_disk
from collectress import load_feeds
from collectress import should_replace
from collectress import download_feed
from collectress import parse_args

class TestDirectoryAndFileHandling:
    def test_create_directory(self):
        # Call the function with a test path
        create_directory('test_dir')

        # Assert that the directory now exists
        assert os.path.isdir('test_dir')

        # Clean up after the test by removing the directory
        shutil.rmtree('test_dir')

    def test_write_to_disk(self):
        # Create a temporary directory for the test
        os.makedirs('temp_dir', exist_ok=True)

        # Call the function with test data
        write_to_disk('temp_dir', 'test_date', 'test_org', 'test_feed', b'test_content')

        # Assert that the file now exists
        assert os.path.isfile('temp_dir/test_date_test_org_test_feed.txt.gz')

        # Clean up after the test by removing the directory
        shutil.rmtree('temp_dir')

    def test_should_replace(self,tmp_path):
        # Create a file with some content
        existing_file = tmp_path / "existing_file.txt.gz"
        new_content = b"New content"

        # Since there's no existing file, should_replace should return True
        assert should_replace(existing_file, new_content)

        # Let's create an existing file
        with gzip.open(existing_file, "wb") as f:
            f.write(b"Existing content")

        # The new content is smaller, so should_replace should return False
        new_content = b"New"
        assert not should_replace(existing_file, new_content)

        # The new content is larger, so should_replace should return True
        new_content = b"New content that is definitely longer than the existing content"
        assert should_replace(existing_file, new_content)

class TestInputs:
    def test_load_feeds_valid(self):
        # Given
        # Assuming the file 'valid_feeds.yaml' contains valid feeds data.
        yaml_file = 'valid_feeds.yaml'

        # When
        feeds = load_feeds(yaml_file)

        # Then
        assert isinstance(feeds, list)
        for feed in feeds:
            assert 'name' in feed
            assert 'url' in feed

    def test_load_feeds_invalid(self):
        # Given
        # Assuming the file 'invalid_feeds.yaml' contains invalid or no feeds data.
        yaml_file = 'invalid_feeds.yaml'

        # When
        feeds = load_feeds(yaml_file)

        # Then
        assert feeds == []

    def test_load_feeds_nonexistent(self):
        # Given
        # Assuming the file does not exist.
        yaml_file = 'nonexistent.yaml'

        # When
        feeds = load_feeds(yaml_file)

        # Then
        assert feeds == []

class TestDownloadFunctions:
    def test_download_feed_200(self):
        with patch('requests.get') as mock_get:
            # Mock the response from requests.get
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b"Testing 200 OK"

            # Call the function with a dummy URL
            content = download_feed("https://dummyurl.com")

            # Assert that the function correctly returned the mocked content
            assert content == b"Testing 200 OK"

    def test_download_feed_404(self):
        with patch('requests.get') as mock_get:
            # Mock the response from requests.get
            mock_get.return_value.status_code = 404

            # Call the function with a dummy URL
            content = download_feed("https://dummyurl.com")

            # Assert that the function correctly handled the 404 error
            assert content is None

class TestCommandArguments:

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(feed='test_feed.yaml', workdir='test_dir'))
    def test_parse_args(self, mock_args):
        args = parse_args()
        assert args.feed == 'test_feed.yaml'
        assert args.workdir == 'test_dir'
