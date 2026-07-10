import os
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

#AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FOLDER_NAME = os.getenv("FOLDER_NAME")
FULL_CSV_PATH = os.getenv("FULL_CSV_PATH")
FULL_JSON_PATH = os.getenv("FULL_JSON_PATH")
FULL_PARQUET_PATH = os.getenv("FULL_PARQUET_PATH")


#PostgreSQL Configuration
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")