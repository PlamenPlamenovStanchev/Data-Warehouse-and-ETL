import pandas as pd

from include.s3_utils import get_storage_options


def load_df_to_s3_csv(df: pd.DataFrame, s3_path: str, aws_conn_id: str) -> None:
    """
    Load a DataFrame to S3 as a CSV file.

    :param df: The DataFrame to load.
    :param bucket: The name of the S3 bucket.
    :param key: The S3 key (path) where the CSV will be stored.
    :param aws_conn_id: The Airflow connection ID for AWS.
    """
    s3_hook, storage_options = get_storage_options(aws_conn_id=aws_conn_id)
    try:
        df.to_csv(s3_path, index=False, storage_options=storage_options)
    except Exception as e:
        print(f"Failed to load DataFrame to S3 at {s3_path}: {e}")
        raise
    print(f"Successfully loaded DataFrame to S3 at {s3_path}")

