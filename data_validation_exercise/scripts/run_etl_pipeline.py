from extract_data import extract_data_from_local_file
from extract_data.extract_data_from_aws_s3 import extract_csv_file_from_aws_s3, extract_json_file_from_aws_s3, extract_parquet_file_from_aws_s3
from extract_data.extract_from_postgressql_db import extract_sales_from_database
from config.config import BUCKET_NAME, FULL_CSV_PATH, FULL_JSON_PATH, FULL_PARQUET_PATH, DB_DATABASE,DB_HOST,DB_PASSWORD,DB_PORT,DB_USER
from extract_data.extract_data_from_sinoptik_api import extract_weather_data_from_sinoptik
from validations.sales_validations import validate_sales_data
from validations.weather_validations import validate_weather_data
from validations.customers_validations import validate_customers_data
from validations.orders_validations import validate_orders_data
from load_data.load_data_to_local_output_file import load_data_to_local_csv_file, load_data_to_local_json_file
from load_data.load_data_to_aws_s3 import load_df_to_aws_s3_csv, load_df_to_aws_s3_json


if __name__ == "__main__":
    # Example usage of the extract_customers_from_json function
    customers_df = extract_data_from_local_file.extract_customers_from_json("data/customers.json")
    #print(customers_df.head())
    orders_df = extract_data_from_local_file.extract_orders_from_local_file("data/orders.json")
    #print(orders_df.head())
    sales_df_csv = extract_csv_file_from_aws_s3(bucket_name=BUCKET_NAME, file_key=FULL_CSV_PATH)
    #print(sales_df_csv.head())
    sales_df_json = extract_json_file_from_aws_s3(bucket_name=BUCKET_NAME, file_key=FULL_JSON_PATH)
    #print(sales_df_json.head())
    sales_df_parquet = extract_parquet_file_from_aws_s3(bucket_name=BUCKET_NAME, file_key=FULL_PARQUET_PATH)
    #print(sales_df_parquet.head())


    orders_df["order_id"] = orders_df["order_id"].astype(int)
    customers_df["customer_id"] = customers_df["customer_id"].astype(int)

    merged_df = customers_df.merge(orders_df, on="customer_id", how="left")

    sql_query = "SELECT * FROM sales_data"
    db_params = {
        "database": DB_DATABASE,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT
    }

    sales_df_db = extract_sales_from_database(sql_query=sql_query, db_params=db_params)
    #print(sales_df_db.head())

    weather_df = extract_weather_data_from_sinoptik()
    print(weather_df.head())

    validated_customers_df = validate_customers_data(customers_df)
    validated_orders_df = validate_orders_data(orders_df)
    validated_sales_df = validate_sales_data(sales_df_csv)
    validated_weather_df = validate_weather_data(weather_df)


    load_data_to_local_csv_file(validated_customers_df, "validated_customers.csv")
    load_data_to_local_csv_file(validated_orders_df, "validated_orders.csv")
    load_data_to_local_csv_file(validated_sales_df, "validated_sales.csv")
    load_data_to_local_csv_file(validated_weather_df, "validated_weather.csv")

    load_data_to_local_json_file(validated_weather_df, "validated_weather.json")
    load_data_to_local_json_file(validated_customers_df, "validated_customers.json")
    load_data_to_local_json_file(validated_orders_df, "validated_orders.json")
    load_data_to_local_json_file(validated_sales_df, "validated_sales.json")

    load_df_to_aws_s3_csv(validated_customers_df, f"s3://{BUCKET_NAME}/validated_customers.csv")
    load_df_to_aws_s3_csv(validated_orders_df, f"s3://{BUCKET_NAME}/validated_orders.csv")
    load_df_to_aws_s3_csv(validated_sales_df, f"s3://{BUCKET_NAME}/validated_sales.csv")
    load_df_to_aws_s3_json(validated_weather_df, f"s3://{BUCKET_NAME}/validated_weather.json")

    
