import s3fs
import boto3
import fsspec

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def get_s3_client_and_storage_options() -> tuple[boto3.client, dict]:
    """Create an S3 client and pandas-compatible storage options."""
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    storage_options ={
        "key": AWS_ACCESS_KEY_ID,
        "secret": AWS_SECRET_ACCESS_KEY
    }

    return s3, storage_options
