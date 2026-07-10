import logging
import pandas as pd
import pyarrow

from config.s3_utils import get_s3_client_and_storage_options

def extract_csv_file_from_aws_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """Read a CSV file from AWS S3 into a DataFrame."""

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"Successfully loaded s3 path: {s3_path}")

    try:
        df = pd.read_csv(s3_path, storage_options=storage_options)
    except Exception as e:
        logging.error(f"Failed to extract CSV from S3: {s3_path}")
        raise
    logging.info(f"Succcessfully extracted CSV from S3: {s3_path}")

    return df

def extract_parquet_file_from_aws_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """Read a Parquet file from AWS S3 into a DataFrame."""

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"Successfully loaded s3 path: {s3_path}")

    try:
        df = pd.read_parquet(s3_path, storage_options=storage_options)
    except Exception as e:
        logging.error(f"Failed to extract PARQUET from S3: {s3_path}")
        raise
    logging.info(f"Succcessfully extracted PARQUET from S3: {s3_path}")

    return df


def extract_json_file_from_aws_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """Read a JSON file from AWS S3 into a DataFrame."""

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"Successfully loaded s3 path: {s3_path}")

    try:
        df = pd.read_json(s3_path, storage_options=storage_options)
    except Exception as e:
        logging.error(f"Failed to extract JSON from S3: {s3_path}")
        raise
    logging.info(f"Succcessfully extracted JSON from S3: {s3_path}")

    return df

# Try to unify the above 3 functions in one

