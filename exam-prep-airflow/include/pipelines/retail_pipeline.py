import pandas as pd
from airflow.sdk import task, task_group
from airflow.exceptions import AirflowException
from airflow.utils import yaml
from setuptools.tests.config.downloads import output_file

from include.etl.extract_data import extract_data_from_s3
from include.etl.load_to_s3 import load_df_to_s3_csv
from include.etl.transformation import transform_sales_data, transform_product_data, enrich_merged_data, \
    hourly_sales_trend, revenue_concentration, seasonal_sales_pattern
from include.s3_utils import get_storage_options


with open ("include/config.yaml") as config_file:
    config = yaml.safe_load(config_file)


s3_hook, storage_options = get_storage_options(aws_conn_id=config["aws_conn_id"])

@task_group(group_id="extract_group")
def extract_group():
    @task()
    def extract_csv_files(bucket: str, folder: str, aws_conn_id: str) -> list[str]:
        """
        Extract CSV files from S3 bucket and folder.

        :param bucket: The name of the S3 bucket.
        :param folder: The folder path within the S3 bucket.
        :param aws_conn_id: The Airflow connection ID for AWS.
        :return: A list of paths to the extracted CSV files.
        """
        return extract_data_from_s3(bucket=bucket, folder=folder, aws_conn_id=aws_conn_id, file_type="csv")

    @task()
    def extract_json_files(bucket: str, folder: str, aws_conn_id: str) -> list[str]:
        """
        Extract JSON files from S3 bucket and folder.

        :param bucket: The name of the S3 bucket.
        :param folder: The folder path within the S3 bucket.
        :param aws_conn_id: The Airflow connection ID for AWS.
        :return: A list of paths to the extracted JSON files.
        """
        return extract_data_from_s3(bucket=bucket, folder=folder, aws_conn_id=aws_conn_id, file_type="json")

    @task()
    def get_sales_path(paths: list)->list:
        for path in  paths:
            if "sales" in path.lower():
                return path
        raise AirflowException("No sales file found in the extracted paths.")

    @task()
    def get_product_path(paths: list)->list:
        for path in  paths:
            if "product" in path.lower():
                return path
        raise AirflowException("No product file found in the extracted paths.")

    csv_path = extract_csv_files(config["s3"]["bucket"], config["s3"]["folder"], config["aws_conn_id"])
    json_path = extract_json_files(config["s3"]["bucket"], config["s3"]["folder"], config["aws_conn_id"])
    sales_path = get_sales_path(csv_path)
    product_path = get_product_path(json_path)

    return {
        "sales_path": sales_path,
        "product_path": product_path
    }

@task_group(group_id="transform_group")
def transform_group(sales_path: str, product_path: str):
    @task()
    def transform_sales(sales_path: str) :
        """
        Transform the sales data.

        :param sales_path: The path to the sales CSV file.
        :return: A DataFrame containing the transformed sales data.
        """
        df = pd.read_csv(sales_path, storage_options=storage_options)
        df = transform_sales_data(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/transformed_sales.csv"
        load_df_to_s3_csv(df, output_path, config["aws_conn_id"])

        return output_path

    @task()
    def transform_products(product_path: str):
        """
        Transform the sales data.

        :param product_path: The path to the sales CSV file.
        :return: A DataFrame containing the transformed sales data.
        """
        df = pd.read_json(product_path, storage_options=storage_options)
        df = transform_product_data(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/transformed_product.csv"
        load_df_to_s3_csv(df, output_path, config["aws_conn_id"])

        return output_path

    @task()
    def merged_date(cleaned_sales_path: str, cleaned_product_path: str):
        """
        Merge the transformed sales and product data.

        :param cleaned_sales_path: The path to the transformed sales CSV file.
        :param cleaned_product_path: The path to the transformed product CSV file.
        :return: A DataFrame containing the merged data.
        """
        sales_df = pd.read_csv(cleaned_sales_path, storage_options=storage_options)
        product_df = pd.read_csv(cleaned_product_path, storage_options=storage_options)

        merged_df = pd.merge(sales_df, product_df, on="product_id", how="inner")

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/merged_data.csv"
        load_df_to_s3_csv(merged_df, output_path, config["aws_conn_id"])

        return output_path

    def enriched_data(merged_data_path: str):
        """
        Enrich the merged data with additional information.

        :param merged_data_path: The path to the merged data CSV file.
        :return: A DataFrame containing the enriched data.
        """
        merged_df = pd.read_csv(merged_data_path, storage_options=storage_options)

        enriched_df = enrich_merged_data(merged_df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/enriched_data.csv"
        load_df_to_s3_csv(enriched_df, output_path, config["aws_conn_id"])

        return output_path

    clean_sales = transform_sales(sales_path)
    clean_product = transform_products(product_path)
    merged_data = merged_date(clean_sales, clean_product)
    enriched_data(merged_data)

    return {
        "clean_sales": clean_sales,
        "clean_product": clean_product,
        "merged_data": merged_data,
        "enriched_data": enriched_data
    }

@task_group(group_id="analytics_group")
def analytics_group(enriched_path: str):
    @task()
    def run_hourly_sales_trend(enriched_path: str):
        """
        Run the hourly sales trend analysis.

        :param enriched_path: The path to the enriched data CSV file.
        :return: A DataFrame containing the hourly sales trend analysis results.
        """
        enriched_df = pd.read_csv(enriched_path, storage_options=storage_options)
        result = hourly_sales_trend()

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/hourly_sales_trend.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])

        return output_path

    @task()
    def run_product_sales_ranking_with_brand(enriched_df: str):
        """
        Run the product sales ranking analysis with brand information.

        :param enriched_path: The path to the enriched data CSV file.
        :return: A DataFrame containing the product sales ranking analysis results.
        """
        df = pd.read_csv(enriched_df, storage_options=storage_options)

        result = run_product_sales_ranking_with_brand(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/product_sales_ranking_with_brand.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])

        return output_path

    @task()
    def run_revenue_concentration(enriched_df: str):
        """
        Run the revenue concentration analysis.

        :param enriched_path: The path to the enriched data CSV file.
        :return: A DataFrame containing the revenue concentration analysis results.
        """
        df = pd.read_csv(enriched_df, storage_options=storage_options)

        result = revenue_concentration(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/revenue_concentration.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])

        return output_path

    @task()
    def run_seasonal_patterns(enriched_df: str):
        """
        Run the seasonal patterns analysis.

        :param enriched_path: The path to the enriched data CSV file.
        :return: A DataFrame containing the seasonal patterns analysis results.
        """
        df = pd.read_csv(enriched_df, storage_options=storage_options)

        result = seasonal_sales_pattern(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['output_folder']}/seasonal_patterns.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])

        return output_path

    hourly_trend = run_hourly_sales_trend(enriched_path)
    product_ranking = run_product_sales_ranking_with_brand(enriched_path)
    revenue_concentration_result = run_revenue_concentration(enriched_path)
    seasonal_pattern = run_seasonal_patterns(enriched_path)

    return {
        "hourly_trend": hourly_trend,
        "product_ranking": product_ranking,
        "revenue_concentration": revenue_concentration,
        "seasonal_pattern": seasonal_pattern
    }

@task_group(group_id="load_group")
def load_group(hourly_trend_path: str, product_ranking_path: str, revenue_concentration_path: str, seasonal_pattern_path: str):
    @task
    def copy_csv(input_path: str, output_file: str):
        df =pd.read_csv(input_path, storage_options=storage_options)

        bucket = config["s3"]["bucket"]
        folder = config["s3"]["output_folder"]

        output_file_path = f"s3://{bucket}/{folder}/{output_file}"
        load_df_to_s3_csv(df, output_file_path, config["aws_conn_id"])
        return output_file_path

    copy_csv.overrides(task_id="load_hourly_trend")(hourly_trend, output_file="hourly_sales_trend.csv")
    copy_csv.overrides(task_id="load_product_sales_ranking")(product_ranking, output_file="product_sales_ranking_with_brand.csv")
    copy_csv.overrides(task_id="load_seasonal_patterns")(seasonal_pattern, output_file="seasonal_patterns.csv")
    copy_csv.overrides(task_id="load_revenue_concentration")(revenue_concentration, output_file="revenue_concentration.csv")


def build_retail_pipeline():
    """
    Build the retail data pipeline.

    :return: A dictionary containing the paths to the extracted sales and product files.
    """
    extract_output = extract_group()
    sales_path = extract_output["sales_path"]
    product_path = extract_output["product_path"]

    transform_output = transform_group(sales_path, product_path)
    enriched_path = transform_output["enriched_data"]
    analytics_output = analytics_group(enriched_path)
    load_group(
        hourly_trend_path=analytics_output["hourly_trend"],
        product_ranking_path=analytics_output["product_ranking"],
        revenue_concentration_path=analytics_output["revenue_concentration"],
        seasonal_pattern_path=analytics_output["seasonal_pattern"]
    )