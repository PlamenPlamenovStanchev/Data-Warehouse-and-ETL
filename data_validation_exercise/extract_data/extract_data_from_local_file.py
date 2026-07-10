import json
import logging
import pandas as pd
from pathlib import Path


def extract_customers_from_json(file_path: str) -> pd.DataFrame:
    """Read customer records from a local JSON file into a DataFrame."""
    logging.info(f"Extracting customers data from JSON file: {file_path}")

    try:
        df = pd.read_json(file_path)
    except Exception as e:
        logging.error(f"Error reading JSON file: {file_path}. Error: {e}")
        raise

    logging.info(f'Successfully extracted {len(df)} records from JSON file: {file_path}')
    return df

def extract_orders_from_local_file(file_path: str | Path) -> pd.DataFrame:
    """Read and flatten order records from a local JSON file."""
    logging.info(f'Reading records from {file_path}')

    try:
        with open(file_path, "r") as file:
            records = json.load(file)
    except Exception as e:
        logging.error(f"Unexpected error reading file {file_path}")
        raise

    try:
        df = pd.json_normalize(records, meta=["order_id", "customer_id"], record_path=["order_details"])
    except Exception as e:
        logging.error(f"Error flattening order JSON file {file_path}")
        raise

    logging.info(f"Loaded {len(df)} records")
    return df
 


        
