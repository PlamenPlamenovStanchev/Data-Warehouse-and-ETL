import pandas as pd
import sys
from pathlib import Path

from include.validation.anomalies_schema import validate_anomalies_schema

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "include" / "config.yaml"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from airflow.decorators import task_group
from airflow.sdk import task, dag
from airflow.utils import yaml
from pendulum import datetime

from include.etl_proccess.extract_data import extract_data_from_s3
from include.etl_proccess.transform_data import (
    clean_sales_data,
    clean_customers_data,
    clean_products_data,
    compute_monthly_aggregates,
    detect_sales_anomalies,
    forecast_sales,
    merge_dataframes as merge_cleaned_dataframes,
    segment_customers,
)

from include.etl_proccess.load_data import load_data_to_snowflake


with CONFIG_PATH.open("r") as file:
    config = yaml.safe_load(file)


@dag(
    start_date=datetime(2026, 7, 1, 16),
    schedule="@daily",
    catchup=False,
    tags=["ETL", "S3", "Data Pipeline"],
)

def etl_pipeline_dag():
    @task()
    def extract_data_task(bucket: str, folder: str, aws_conn_id: str) -> dict:
        """
        Task to extract data from S3 bucket.

        Args:
            bucket (str): The name of the S3 bucket.
            folder (str): The folder path within the S3 bucket.
            aws_conn_id (str): The AWS connection ID for authentication.    
        """

        return extract_data_from_s3(bucket=bucket, folder=folder, aws_conn_id=aws_conn_id)
    
    @task()
    def get_sales_file(files: dict) -> str:
        """
        Task to retrieve the sales CSV file from the extracted files.

        Args:
            files (dict): A dictionary containing DataFrames for each CSV file.
        """
        for key, df in files.items():
            if "sales" in key:
                return df.to_json(orient="split")
        raise ValueError("Sales file not found")
    

    @task()
    def get_customers_file(files: dict) -> str:
        """
        Task to retrieve the customers CSV file from the extracted files.

        Args:
            files (dict): A dictionary containing DataFrames for each CSV file.
        """
        for key, df in files.items():
            if "customer" in key:
                return df.to_json(orient="split")
        raise ValueError("Customers file not found")
    
    @task()
    def get_products_file(files: dict) -> str:  
        """
        Task to retrieve the products CSV file from the extracted files.

        Args:
            files (dict): A dictionary containing DataFrames for each CSV file.
        """
        for key, df in files.items():
            if "product" in key:
                return df.to_json(orient="split")
        raise ValueError("Products file not found")
    

    @task()
    def transform_sales_data(sales_file: str) -> str:
        """
        Task to transform the sales data.

        Args:
            sales_json (str): The sales DataFrame in JSON format.
        """
        

        sales_df = pd.read_json(sales_file, orient="split")
        sales_df = clean_sales_data(sales_df)
        return sales_df.to_json(orient="split", date_format="iso")

    @task()
    def transform_customers_data(customers_file: str) -> str:
        """
        Task to transform the customers data.

        Args:
            customers_json (str): The customers DataFrame in JSON format.
        """
        

        customers_df = pd.read_json(customers_file, orient="split")
        customers_df = clean_customers_data(customers_df)
        return customers_df.to_json(orient="split", date_format="iso")

    @task()
    def transform_products_data(products_file: str) -> str:
        """
        Task to transform the products data.

        Args:
            products_json (str): The products DataFrame in JSON format.
        """
        

        products_df = pd.read_json(products_file, orient="split")
        products_df = clean_products_data(products_df)
        return products_df.to_json(orient="split")


    @task()
    def merge_dataframes_task(transformed_sales: str, transformed_customers: str, transformed_products: str) -> str:
        """
        Task to merge the sales, customers, and products DataFrames.

        Args:
            sales_json (str): The sales DataFrame in JSON format.
            customers_json (str): The customers DataFrame in JSON format.
            products_json (str): The products DataFrame in JSON format.
        """
        

        sales_df = pd.read_json(transformed_sales, orient="split")
        customers_df = pd.read_json(transformed_customers, orient="split")
        products_df = pd.read_json(transformed_products, orient="split")

        merged_df = merge_cleaned_dataframes(sales_df, customers_df, products_df)

        return merged_df.to_json(orient="split", date_format="iso")
    
    @task()
    def aggregate_data_task(merged_data: str) -> str:
        """
        Task to aggregate the merged data.

        Args:
            merged_data (str): The merged DataFrame in JSON format.
        """
        
        merged_df = pd.read_json(merged_data, orient="split")
        aggregated_df = compute_monthly_aggregates(merged_df)

        return aggregated_df.to_json(orient="split", date_format="iso")


    @task()
    def segmented_customer_task(sales_df: str, customers_df: str) -> str:
        """
        Task to segment customers based on their total spending.

        Args:
            sales_df (str): The sales DataFrame in JSON format.
            customers_df (str): The customers DataFrame in JSON format.
        """
        
        sales_df = pd.read_json(sales_df, orient="split")
        customers_df = pd.read_json(customers_df, orient="split")
        segmented_df = segment_customers(sales_df, customers_df)
        return segmented_df.to_json(orient="split", date_format="iso")
    
    @task()
    def anomalies_sales_task(sales_df: str) -> str:
        """
        Task to detect anomalies in the sales data.

        Args:
            sales_df (str): The sales DataFrame in JSON format.
        """
        
        sales_df = pd.read_json(sales_df, orient="split")
        sales_df = detect_sales_anomalies(sales_df)
        return sales_df.to_json(orient="split", date_format="iso")
    
    @task()
    def forecast_sales_task(sales_df : str) -> str:
        """
        Task to forecast future sales based on the aggregated data.

        Args:
            aggregated_data (str): The aggregated DataFrame in JSON format.
        """
        
        sales_df = pd.read_json(sales_df, orient="split")
        sales_df = forecast_sales(sales_df)
        return sales_df.to_json(orient="split", date_format="iso")
        

    @task()
    def load_data_to_snowflake_task(
        final_json: str,
        database: str,
        schema: str,
        table_name: str,
        snowflake_conn_id: str,
    ) -> None:
        """
        Task to load the aggregated data into a Snowflake table.

        Args:
            final_json (str): The final DataFrame in JSON format.
            database (str): The target Snowflake database.
            schema (str): The target Snowflake schema.
            table_name (str): The target Snowflake table name.
        """
        
        final_df = pd.read_json(final_json, orient="split")
        load_data_to_snowflake(final_df, database, schema, table_name, snowflake_conn_id)

    @task_group(group_id="extraction")
    def extraction_group() -> tuple[str, str, str]:
        files = extract_data_task(
            bucket=config["s3"]["bucket"],
            folder=config["s3"]["folder"],
            aws_conn_id=config["aws_conn_id"]
        )
        sales_file = get_sales_file(files)
        customers_file = get_customers_file(files)
        products_file = get_products_file(files)

        return sales_file, customers_file, products_file

    @task_group(group_id="transformation")
    def transformation_group(sales_file: str, customers_file: str, products_file: str) -> tuple[str, str, str, str]:
        transformed_sales = transform_sales_data(sales_file=sales_file)
        transformed_customers = transform_customers_data(customers_file=customers_file)
        transformed_products = transform_products_data(products_file=products_file)

        merged_data = merge_dataframes_task(
            transformed_sales=transformed_sales,
            transformed_customers=transformed_customers,
            transformed_products=transformed_products,
        )

        return transformed_sales, transformed_customers, transformed_products, merged_data

    @task_group(group_id="analytics")
    def analytics_group(transformed_sales: str, transformed_customers: str, merged_data: str) -> tuple[str, str, str, str]:
        aggregated_data = aggregate_data_task(merged_data=merged_data)
        segmented_customers = segmented_customer_task(transformed_sales, transformed_customers)
        sales_anomalies = anomalies_sales_task(transformed_sales)
        forecasted_sales = forecast_sales_task(transformed_sales)

        return aggregated_data, segmented_customers, sales_anomalies, forecasted_sales

    @task_group(group_id="load")
    def load_group(
        transformed_sales: str,
        transformed_customers: str,
        transformed_products: str,
        aggregated_data: str,
        segmented_customers: str,
        sales_anomalies: str,
        forecasted_sales: str,
    ) -> None:
        load_data_to_snowflake_task(
            transformed_sales,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["sales"]["schema"],
            config["snowflake"]["targets"]["sales"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            transformed_customers,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["customers"]["schema"],
            config["snowflake"]["targets"]["customers"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            transformed_products, 
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["products"]["schema"],   
            config["snowflake"]["targets"]["products"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            aggregated_data,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["monthly_sales"]["schema"],
            config["snowflake"]["targets"]["monthly_sales"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            segmented_customers,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["customer_segments"]["schema"],
            config["snowflake"]["targets"]["customer_segments"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            sales_anomalies,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["detect_sales_anomalies"]["schema"],
            config["snowflake"]["targets"]["detect_sales_anomalies"]["table"],
            config["snowflake"]["conn_id"],
        )

        load_data_to_snowflake_task(
            forecasted_sales,
            config["snowflake"]["database"],
            config["snowflake"]["targets"]["forecasted_sales"]["schema"],
            config["snowflake"]["targets"]["forecasted_sales"]["table"],
            config["snowflake"]["conn_id"],
        )

    sales_file, customers_file, products_file = extraction_group()
    transformed_sales, transformed_customers, transformed_products, merged_data = transformation_group(
        sales_file=sales_file,
        customers_file=customers_file,
        products_file=products_file,
    )
    aggregated_data, segmented_customers, sales_anomalies, forecasted_sales = analytics_group(
        transformed_sales=transformed_sales,
        transformed_customers=transformed_customers,
        merged_data=merged_data,
    )
    load_group(
        transformed_sales=transformed_sales,
        transformed_customers=transformed_customers,
        transformed_products=transformed_products,
        aggregated_data=aggregated_data,
        segmented_customers=segmented_customers,
        sales_anomalies=sales_anomalies,
        forecasted_sales=forecasted_sales,
    )


etl_pipeline_dag()
