#!/usr/bin/env python3

import logging
import sys

SOURCE_URL = "https://status.yandex.cloud/api/incidents?installation=all&page=1000&lang=ru"

def fetch_incidents(destination_file: str) -> None:
    import requests

    response = requests.get(SOURCE_URL)
    logging.info(f"GET {SOURCE_URL} -> {response.status_code}")
    response.raise_for_status()

    with open(destination_file, "w") as f:
        f.write(response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: fetch.py <output_file>\n")
        sys.exit(1)

    destination_file = sys.argv[1]
    fetch_incidents(destination_file)
