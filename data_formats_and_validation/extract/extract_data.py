import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import io
import requests

from config.settings import S3, BUCKET_NAME, FOLDER_NAME, FULL_CSV_PATH, FULL_JSON_PATH, FULL_PARQUET_PATH, USER, PASSWORD, HOST, PORT, DATABASE

def extract_csv(bucket: str, full_path: str) -> pd.DataFrame:
    csv_object = S3.get_object(Bucket=bucket, Key=full_path)
    df = pd.read_csv(csv_object['Body'])
    return df


def extract_json(bucket: str, full_path: str) -> pd.DataFrame:
    json_object = S3.get_object(Bucket=bucket, Key=full_path)
    json_bytes = json_object['Body'].read()
    json_str = json_bytes.decode('utf-8')
    df = pd.read_json(io.StringIO(json_str))
    return df

def extract_parquet(bucket: str, full_path: str) -> pd.DataFrame:
    parquet_object = S3.get_object(Bucket=bucket, Key=full_path)
    parquet_bytes = parquet_object['Body'].read()
    df = pd.read_parquet(io.BytesIO(parquet_bytes))
    return df


def extract_api_data(api_url: str) -> pd.DataFrame:
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data)
        return df
    else:
        raise Exception(f"API request failed with status code {response.status_code}")


def extract_db_data(db_url: str) -> pd.DataFrame:
    engine = create_engine(db_url)
    query = "SELECT * FROM sales_data_from_s3"  # Replace with your actual table name
    db_data = pd.read_sql(query, engine)
    return db_data

