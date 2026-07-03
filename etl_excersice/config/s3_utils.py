import boto3

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def s3_client_and_storage_options():
    """
    Create an S3 client and storage options for accessing S3.

    Returns:
        tuple: A tuple containing the S3 client and storage options.
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    storage_options = {
        "key": AWS_ACCESS_KEY_ID,
        "secret": AWS_SECRET_ACCESS_KEY
    }

    return s3_client, storage_options