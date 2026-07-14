from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import pandas as pd
import io
import yaml


@dag(schedule =None, start_date=datetime(2023, 1, 1), catchup=False, tags=["astro", "s3", "db"])
def etl_pipeline_s3_to_db():
    @task
    def extract_from_s3() -> pd.DataFrame:
        with open("include/config.yaml", "r") as file:
            config = yaml.safe_load(file)

        s3_hook = S3Hook(aws_conn_id=config['aws_conn_id'])
        bucket = config["s3"]['bucket']
        file = config["s3"]['folder']

        key = s3_hook.get_key(file, bucket)

        if not key:
            raise ValueError(f"No files found in bucket {bucket} with prefix {file}")

        content = key.get()['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))

        return df
    
    @task
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        df["sales"] = df["sales"].astype(float)
        aggregated_df = df.groupby("region").agg({"sales": "sum"}).reset_index()
        return aggregated_df

    @task
    def load_to_snowflake(transformed_df: pd.DataFrame):
        with open("include/config.yaml", "r") as file:
            config = yaml.safe_load(file)

        hook = SnowflakeHook(snowflake_conn_id="my_snowflake_conn")
        df = pd.DataFrame(transformed_df)

        for _, row in df.iterrows():
            insert_sql = f"""
            INSERT INTO {config['snowflake']['table']} (region, sales)
            VALUES (%(region)s, %(sales)s)
            """
            hook.run(insert_sql, parameters={"region": row["region"], "sales": row["sales"]})


    raw_data = extract_from_s3()
    transformed_data = transform(raw_data)
    load_to_snowflake(transformed_data)

    
etl_pipeline_s3_to_db()

