import logging 
import pandas as pd

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

def load_data_to_local_csv_file(data: pd.DataFrame, filename: str) -> None:
    """
    Load data to a local CSV file.

    Args:
        data (pd.DataFrame): The data to be saved.
        filename (str): The name of the output CSV file.

    Returns:
        None
    """
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file_path = OUTPUT_DIR / filename
        data.to_csv(output_file_path, index=False)
        logging.info(f"Data successfully loaded to {output_file_path}")
    except Exception as e:
        logging.error(f"Error loading data to local CSV file: {e}")
        raise



def load_data_to_local_json_file(data: pd.DataFrame, filename: str) -> None:
    """
    Load data to a local JSON file.

    Args:
        data (pd.DataFrame): The data to be saved.
        filename (str): The name of the output JSON file.

    Returns:
        None
    """
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file_path = OUTPUT_DIR / filename
        data.to_json(output_file_path, orient='records', lines=True)
        logging.info(f"Data successfully loaded to {output_file_path}")
    except Exception as e:
        logging.error(f"Error loading data to local JSON file: {e}")
        raise