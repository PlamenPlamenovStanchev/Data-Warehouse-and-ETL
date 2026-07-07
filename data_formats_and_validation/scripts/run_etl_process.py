import pandas as pd
import pandera as pa
from config.settings import S3, BUCKET_NAME, FOLDER_NAME, FULL_CSV_PATH, FULL_JSON_PATH, FULL_PARQUET_PATH, USER, PASSWORD, HOST, PORT, DATABASE
from data_formats_and_validation.load.load_to_postgres import load_to_postgresql
from data_formats_and_validation.transform.transform import transform_data
from data_formats_and_validation.validations.validations import validate_sales_data
from extract.extract_data import extract_csv, extract_json, extract_parquet
from extract.extract_data import extract_db_data

if __name__ == "__main__":
    # Extract data from S3
    csv_df = extract_csv(bucket=BUCKET_NAME, full_path=FOLDER_NAME + FULL_CSV_PATH)
    json_df = extract_json(bucket=BUCKET_NAME, full_path=FOLDER_NAME + FULL_JSON_PATH)
    #parquet_df = extract_parquet(bucket=BUCKET_NAME, full_path=FOLDER_NAME + FULL_PARQUET_PATH)

    # Print the extracted data
    #print("CSV Data:")
    #print(csv_df.head())
    
    #print("\nJSON Data:")
    #print(json_df.head())
    
    #print("\nParquet Data:")
    #print(parquet_df.head())

    sales_db_data = extract_db_data(db_url=f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    #print("\nSales Database Data:")
    #print(sales_db_data.head())

    transformed_csv_df = transform_data(csv_df)

    try:
        valid_df_csv = validate_sales_data(csv_df)
        print("CSV Data is valid.")
    except pa.errors.SchemaError as e:
        print(f"CSV Data validation failed: {e}")


    load_to_postgresql(valid_df_csv, 'sales_data', DATABASE)

