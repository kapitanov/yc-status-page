#!/usr/bin/env python3

import sys
import os


from scripts.fetch import fetch_incidents
from scripts.preprocess import preprocess_incidents
from scripts.render import render_incidents

if __name__ == "__main__":
    import logging
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    RAW_DATA_FILE = "data/incidents_raw.json"
    PROCESSED_DATA_FILE = "data/incidents.json"
    OUTPUT_FILE = "web/index.html"
    
    os.makedirs("data", exist_ok=True)
    os.makedirs("web", exist_ok=True)
    
    logging.info(f"Downloading raw incidents data to \"{RAW_DATA_FILE}\"...")
    fetch_incidents(RAW_DATA_FILE)

    logging.info(f"Preprocessing raw incidents data to \"{PROCESSED_DATA_FILE}\"...")
    preprocess_incidents(RAW_DATA_FILE, PROCESSED_DATA_FILE)

    logging.info(f"Rendering incidents data to \"{OUTPUT_FILE}\"...")
    render_incidents(PROCESSED_DATA_FILE, OUTPUT_FILE)

    logging.info("Done")
