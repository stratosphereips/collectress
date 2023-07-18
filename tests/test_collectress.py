import sys
import os
import shutil
from os import path
sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from collectress import create_directory,write_to_disk,load_feeds


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
        write_to_disk('temp_dir', 'test_date', 'test_feed', b'test_content')

        # Assert that the file now exists
        assert os.path.isfile('temp_dir/test_date_test_feed.txt.gz')

        # Clean up after the test by removing the directory
        shutil.rmtree('temp_dir')

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
