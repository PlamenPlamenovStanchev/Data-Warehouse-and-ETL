import pandas as pd
import fsspec
import s3fs

from botocore.exceptions import BotoCoreError
from config.s3_utils import s3_client_and_storage_options

def extract_from_s3(bucket_name: str, folder_name: str)-> list:
    """
    Extract data from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        folder_name (str): The name of the folder in the S3 bucket.
    """

    s3_client, storage_options = s3_client_and_storage_options()
    mapping = {"sales": None, "customer": None, "product": None, "shipping": None}

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        contents = response.get("Contents", [])
        if not contents:
            raise FileNotFoundError(f"No files found in the specified S3 bucket '{bucket_name}' and folder '{folder_name}'.") 
    except BotoCoreError as e:
        print(f"S3 access error for {bucket_name}/{folder_name}: {e}") 
        raise

    for obj in contents:
        key = obj["Key"]

        if not key.lower().endswith(".csv"):
            continue  # Skip non-CSV files

        s3_path = f"s3://{bucket_name}/{key}"

        try:
            df = pd.read_csv(s3_path, storage_options=storage_options)
        except Exception as e:
            print(f"Skipping file {s3_path} due to read error: {e}")
            continue

        for name in mapping.keys():
            if name in key.lower():
                mapping[name] = df
                break

    return [mapping["sales"], mapping["customer"], mapping["product"], mapping["shipping"]]  

