import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import io
import boto3
import dotenv

dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def read_files(bucket_name: str, full_path: str) -> pd.DataFrame:
    obj = s3.get_object(Bucket=bucket_name, Key=full_path)
    raw_data = pd.read_csv(io.BytesIO(obj['Body'].read()))
    return raw_data

def transformation(df_raw_data: pd.DataFrame) -> pd.DataFrame:
    df_raw_data = df_raw_data.copy()
    df_raw_data.columns = df_raw_data.columns.str.lower().str.replace(" ", "_")
    df_raw_data.rename(columns={"diskount": "discount"}, inplace=True)
    df_raw_data["order_date"] = pd.to_datetime(df_raw_data["order_date"], format="%d-%m-%y").fillna(pd.Timestamp("2023-01-01"))
    df_raw_data["amount"] = df_raw_data["amount"].astype(float).fillna(0)
    df_raw_data["discount"] = df_raw_data["discount"].astype(float).fillna(0)
    df_raw_data["total_amount"] = (df_raw_data["amount"] * df_raw_data["quantity"]) * (1 - df_raw_data["discount"] / 100)
    df_raw_data["total_amount"] = df_raw_data["total_amount"].round(2)
    return df_raw_data

def load_to_postgresql(df: pd.DataFrame, table_name: str):
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    database = os.getenv("DATABASE")
    user = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Data loaded successfully into table '{table_name}'.")

def main():
    bucket_name = os.getenv("BUCKET_NAME")
    folder_name = os.getenv("FOLDER_NAME", "")
    file_name = os.getenv("FILE_NAME")
    full_path = f"{folder_name.rstrip('/')}/{file_name}"

    raw_data = read_files(bucket_name, full_path)
    cleaned_data = transformation(raw_data)
    load_to_postgresql(cleaned_data, "sales_data_from_s3")


if __name__ == "__main__":
    main()

