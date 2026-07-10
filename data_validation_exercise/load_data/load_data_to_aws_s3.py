import logging
import pandas as pd

from config.s3_utils import get_s3_client_and_storage_options


def load_df_to_aws_s3_csv(data: pd.DataFrame, s3_path: str) -> None:
    """
    Load a DataFrame to AWS S3 as a CSV file.

    Args:
        data (pd.DataFrame): The DataFrame to be saved.
        s3_path (str): The S3 path where the CSV file will be saved.
    Returns:
        None
    """
    try:
        s3_client, storage_options = get_s3_client_and_storage_options()
        data.to_csv(s3_path, index=False, storage_options=storage_options)
        logging.info(f"Data successfully loaded to {s3_path}")
    except Exception as e:
        logging.error(f"Error loading data to AWS S3 CSV file: {e}")
        raise   
      

def load_df_to_aws_s3_json(data: pd.DataFrame, s3_path: str) -> None:
    """
    Load a DataFrame to AWS S3 as a JSON file.

    Args:
        data (pd.DataFrame): The DataFrame to be saved.
        s3_path (str): The S3 path where the JSON file will be saved.
    Returns:
        None
    """
    try:
        s3_client, storage_options = get_s3_client_and_storage_options()
        data.to_json(s3_path, orient='records', lines=True, storage_options=storage_options)
        logging.info(f"Data successfully loaded to {s3_path}")
    except Exception as e:
        logging.error(f"Error loading data to AWS S3 JSON file: {e}")
        raise