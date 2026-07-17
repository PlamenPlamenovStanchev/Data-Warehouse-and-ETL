import pandas as pd

from ..s3_utils import get_storage_options
from ..logger import setup_logger

logging = setup_logger(__name__)


def extract_data_from_s3(bucket: str, folder: str, aws_conn_id: str) -> dict:
    """
    Extracts data from S3 bucket and returns a dictionary of DataFrames.

    Args:
        bucket (str): The name of the S3 bucket.
        folder (str): The folder path within the S3 bucket.
        aws_conn_id (str): The AWS connection ID for authentication.

    Returns:
        dict: A dictionary containing DataFrames for each CSV file in the specified folder.
    """
    s3_hook, storage_options = get_storage_options(aws_conn_id)
    keys = s3_hook.list_keys(bucket_name=bucket, prefix=folder)

    if not keys:
        raise ValueError(f"No files found in S3 bucket '{bucket}' with prefix '{folder}'.")
    
    dfs = {}

    for key in keys:
        if not key.lower().endswith(".csv"):
            logging.info(f"Skipping non-CSV file: {key}")
            continue

        s3_path = f"s3://{bucket}/{key}"
        logging.info(f"Extracting data from S3 path: {s3_path}")

        try:
            df = pd.read_csv(s3_path, storage_options=storage_options)
            logging.info(f"Successfully extracted data from {s3_path}")

            if df.empty:
                logging.warning(f"The DataFrame extracted from {s3_path} is empty.")
                continue
        except Exception as e:
            logging.error(f"Error extracting data from {s3_path}: {e}")
            raise

        dfs[key] = df  
        
    return dfs