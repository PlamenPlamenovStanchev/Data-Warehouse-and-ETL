import boto3
from dotenv import load_dotenv
import os

S3 = boto3.client(
    "s3",   
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

BUCKET_NAME = os.getenv("BUCKET_NAME")
FOLDER_NAME = os.getenv("FOLDER_NAME")

FULL_CSV_PATH = os.getenv("FULL_CSV_PATH")
FULL_JSON_PATH = os.getenv("FULL_JSON_PATH")
FULL_PARQUET_PATH = os.getenv("FULL_PARQUET_PATH")

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")