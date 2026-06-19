import pandas as pd
import s3fs
from sqlalchemy import create_engine
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "Los Angeles", "Chicago"]
}

#df = pd.DataFrame(data)
#print(df)

#df_sales = pd.read_csv("C:\\Обучения\\DataWarehouse and ETL\\sales.csv")
#print(df_sales)

# Load data from S3 cloud storage (no manual download needed)
df_sales_from_bucket = pd.read_csv("s3://etl-and-data-warehouse/intro-to-data-tools-and-storage/sales.csv", storage_options={"key": aws_access_key_id, "secret": aws_secret_access_key})
print(df_sales_from_bucket)

# Load customer data from S3
df_customers = pd.read_csv("s3://etl-and-data-warehouse/intro-to-data-tools-and-storage/customers.csv", storage_options={"key": aws_access_key_id, "secret": aws_secret_access_key})

# Explore the data at a glance
print("First few rows:")
print(df_sales_from_bucket.head())

print("\nDataFrame shape (rows, columns):")
print(df_sales_from_bucket.shape)

print("\nData types and info:")
print(df_sales_from_bucket.info())

print("\nColumn names:")
print(df_sales_from_bucket.columns.tolist())

# Select a single column to focus on specific data
print("\n--- Single Column Selection ---")
print("First column:")
print(df_sales_from_bucket.iloc[:, 0].head())

# Select multiple columns to focus on relevant data
print("\n--- Multiple Columns Selection ---")
print("First two columns:")
print(df_sales_from_bucket.iloc[:, :2].head())

# See distribution and basic statistics for numeric columns
print("\n--- Descriptive Statistics ---")
print(df_sales_from_bucket.describe())

filtered = df_sales_from_bucket[df_sales_from_bucket['amount'] > 1000]
print("\n--- Filtered Data (Amount > 1000) ---")
print(filtered.head())
print(filtered.sort_values(by='amount', ascending=True).head())
print(filtered.groupby('product_category')['amount'].mean())



# Perform inner join on customer_id (adjust the key if needed)
df_merged = pd.merge(df_sales_from_bucket, df_customers, on='customer_id')
print("\n--- Merged Sales + Customer Data ---")
print("Merged shape:", df_merged.shape)
print("\nFirst few merged records:")
print(df_merged.head())


# Connect to PostgreSQL and write data
engine = create_engine('postgresql+psycopg2://postgres:P^t0n0m1@localhost:5432/sales_db')
df_merged.to_sql('sales_with_customers', con=engine, if_exists='replace', index=False)
print("✓ Data persisted to PostgreSQL")















