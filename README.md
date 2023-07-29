<img width="1020" alt="image" src="https://github.com/stratosphereips/collectress/assets/2458879/0871f21b-16c5-4101-9c3f-349864237bb4">

[![Python package](https://github.com/stratosphereips/collectress/actions/workflows/python-checks.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/python-checks.yml)
[![Validate-YAML](https://github.com/stratosphereips/collectress/actions/workflows/validate-yml.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/validate-yml.yml)
[![CodeQL](https://github.com/stratosphereips/collectress/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/github-code-scanning/codeql)
[![Docker GHCR](https://github.com/stratosphereips/collectress/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/docker-publish.yml)
[![Docker Hub CI](https://github.com/stratosphereips/collectress/actions/workflows/docker-hub.yml/badge.svg)](https://github.com/stratosphereips/collectress/actions/workflows/docker-hub.yml)


Collectress is a Python tool designed for downloading web data feeds periodically and consistently. The data to download is specified in a YAML feed file. The data is downloaded and stored in a directory structure for each feed and in directories named by the current date.

## Features

- Downloads content from multiple feeds specified in a YAML file
- Creates a directory for each feed
- Content stored in a date-structured directory format (YYYY/MM/DD)
- Handles errors gracefully, allowing the tool to continue even if a single operation fails
- Command-line arguments for input, output, and cache.
- Download optimisation through eTag cache.
- Logs a JSON-formatted comprehensive activity summary per script run

## Usage

Collectress can be run from the command line as follows (a `log.json` will be created upon execution):

```bash
python collectress.py -f data_feeds.yml -w data_feeds/ -e etag_cache.json
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
docker run --rm \
           -e TZ=$(readlink /etc/localtime | sed -e 's,/usr/share/zoneinfo/,,' ) \
           -v ${PWD}/data_feeds.yml:/collectress/data_feeds.yml \
           -v ${PWD}/log.json:/collectress/log.json \
           -v ${PWD}/etag_cache.json:/collectress/etag_cache.json \
           -v ${PWD}/data_output:/data ghcr.io/stratosphereips/collectress:main \
           python collectress.py -f data_feeds.yml -e etag_cache.json -w /data
```

# About

This tool was developed at the Stratosphere Laboratory at the Czech Technical University in Prague. 
