# Collectress

[![Python package](https://github.com/stratosphereips/collectress/actions/workflows/python-checks.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/python-checks.yml)
[![Validate-YAML](https://github.com/stratosphereips/collectress/actions/workflows/validate-yml.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/validate-yml.yml)
[![Docker GHCR](https://github.com/stratosphereips/collectress/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/docker-publish.yml)

Collectress is a Python tool designed for downloading web data feeds periodically and consistently. The data to download is specified in a YAML feed file. The data is downloaded and stored in a directory structure for each feed and in directories named by the current date.

## Features

- Downloads content from multiple feeds specified in a YAML file
- Creates a directory for each feed
- Organizes downloaded content in a date-structured directory format (YYYY/MM/DD)
- Skips any URLs that return a status code other than 200
- Handles errors gracefully, allowing the tool to continue even if a single operation fails
- Command-line arguments for specifying the YAML file and the root output directory
- Checks if the file to be downloaded already exists on disk, and if so, compares the size to decide whether to replace it
- Logs a JSON-formatted activity summary per script run
- Includes timestamp and count of total feeds processed
- Logs successful and failed feed download counts
- Records total data downloaded in bytes
- Tracks and logs failed download feeds
- Calculates and logs success and error rates
- Records total script execution time
- Implements eTag cache to optimise network donwloads

## Usage

Collectress can be run from the command line as follows (a `log.json` will be created upon execution):

```bash
python collectress.py -f data_feeds.yaml -w data_feeds/ -e etag_cache.json
```

Parameters:
```bash
  -h, --help            show this help message and exit
  -e ECACHE, --ecache ECACHE
                        eTag cache for optimizing downloads
  -f FEED, --feed FEED  YAML file containing the feeds
  -w WORKDIR, --workdir WORKDIR
                        The root of the output directory
```

## Usage Docker

Collectress can be used through its Docker image:

```bash
docker run --rm -e TZ=$(readlink /etc/localtime | sed -e 's,/usr/share/zoneinfo/,,' ) -v ${PWD}/data_feeds.yml:/collectress/data_feeds.yml -v ${PWD}/log.json:/collectress/log.json -v ${PWD}/etag_cache.json:/collectress/etag_cache.json -v ${PWD}/data_output:/data ghcr.io/stratosphereips/collectress:main python collectress.py -f data_feeds.yml -e etag_cache.json -w /data
```

# About

This tool was developed at the Stratosphere Laboratory at the Czech Technical University in Prague. 
