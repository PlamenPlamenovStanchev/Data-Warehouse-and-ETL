from airflow.sdk import dag
from pendulum import datetime

from include.pipelines.retail_pipeline import extract_group, build_retail_pipeline


@dag(
    dag_id="retail_dag",
    start_date=datetime(2026, 7, 23),
    schedule=None,
    catchup=False,
    tags=["retail", "s3", "etl"],
)

def retail_dag():
    """
    DAG for extracting retail data from S3.
    """
    build_retail_pipeline()

retail_dag()