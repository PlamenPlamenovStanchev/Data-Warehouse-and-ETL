import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, DATABASE, FOLDER_NAME
from extract.extract_from_s3 import extract_from_s3
from transform.transform import categorized_products, clean_data, compute_derived_columns, rename_columns, convert_to_datetime, remove_duplicates, merge_dataframes, segment_deliveries    
from load.load_to_postgres import create_database_if_not_exists, load_to_postgres, load_transformed_data_to_postgres

def run_elt_process():
    """
    Run the ELT process by extracting data from S3 and performing transformations and loading.
    """
    # Extract data from S3
    sales_df, customer_df, product_df, shipping_df = extract_from_s3(bucket_name=BUCKET_NAME, folder_name=FOLDER_NAME)

    # Perform transformations and loading (not implemented in this snippet)
    # You can add your transformation and loading logic here
    print(sales_df.columns)
    print(customer_df.columns)
    print(product_df.columns)
    print(shipping_df.columns)
    cleaned_dfs = clean_data([sales_df, customer_df, product_df, shipping_df], old_column="DisKount", new_column="discount") 

    deduped_dfs = remove_duplicates(cleaned_dfs, subset=None, keep='first')  

    merged_columns = [("customer_id", "customer_id"), ("product_id", "product_id"), ("order_id", "order_id")]
    merged_df = merge_dataframes(deduped_dfs, merge_column=merged_columns, how='inner')

    print(merged_df.head())  # Display the first few rows of the merged DataFrame

    merged_df = compute_derived_columns(merged_df)
    merged_df = segment_deliveries(merged_df)
    merged_df = categorized_products(merged_df)

    print(merged_df.head())  # Display the first few rows of the final DataFrame

    create_database_if_not_exists()
    load_to_postgres(df=merged_df, table_name="final_table", if_exists='replace')  # Load the final DataFrame to PostgreSQL
    load_transformed_data_to_postgres(transformed_df=merged_df, table_name="final_transformed_table")  # Load the transformed DataFrame to PostgreSQL

if __name__ == "__main__":
    run_elt_process()
