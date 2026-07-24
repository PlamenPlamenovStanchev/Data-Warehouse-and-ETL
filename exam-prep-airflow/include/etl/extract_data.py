import pandas as pd
from airflow.exceptions import AirflowException
from include import s3_utils


def extract_data_from_s3(bucket: str, folder: str, aws_conn_id: str, file_type: str = "csv") ->list[str]:
    """
    Extract data from S3 bucket and folder.

    :param bucket: The name of the S3 bucket.
    :param folder: The folder path within the S3 bucket.
    :param aws_conn_id: The Airflow connection ID for AWS.
    :return: A pandas DataFrame containing the extracted data.
    """
    print(f"Listening for {file_type} in S3 bucket '{bucket}' with prefix '{folder}'...")
    s3_hook, storage_options = s3_utils.get_storage_options(aws_conn_id=aws_conn_id)

    # List all files in the specified S3 folder
    files = s3_hook.list_keys(bucket_name=bucket, prefix=folder)

    if not files:
        raise AirflowException(f"No files found in S3 bucket '{bucket}' with prefix '{folder}'.")

    # Read all CSV files into a single DataFrame
    matches_path =[f"s3://{bucket}/{file}" for file in files if file.lower().endswith(f".{file_type}")]

    if not matches_path:
        raise AirflowException(f"No CSV files found in S3 bucket '{bucket}' with prefix '{folder}'.")

    return matches_path