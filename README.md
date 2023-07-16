# Collectress

Collectress is a Python tool designed for downloading web data feeds periodically and consistently. The data to download is specified in a YAML feed file. The data is downloaded and stored in a directory structure for each feed and in directories named by the current date.

## Features

 - Downloads content from multiple feeds specified in a YAML file
 - Creates a directory for each feed
 - Organizes downloaded content in a date-structured directory format (YYYY/MM/DD)
 - Skips any URLs that return a status code other than 200
 - Handles errors gracefully, allowing the tool to continue even if a single operation fails

## Usage

Collectress can be run from the command line as follows:

```bash
python collectress.py -f data_feeds.yaml -w data_feeds/
```

Parameters:

 - -f, --feedfile (required): Path to the YAML file containing the feeds
 - -w, --workdir (required): Path to the root directory for output

# About

This tool was developed at the Stratosphere Laboratory at the Czech Technical University in Prague. 
