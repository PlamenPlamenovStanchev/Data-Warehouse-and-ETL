import pandas as pd

from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook   
from ..logger import setup_logger

logging = setup_logger(__name__)    

def load_data_to_snowflake(
    df: pd.DataFrame,
    database: str,
    schema: str,
    table_name: str,
    snowflake_conn_id: str,
) -> None:
    """
    Load a DataFrame into a Snowflake table.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        table_name (str): The name of the target Snowflake table.
        snowflake_conn_id (str): The Airflow connection ID for Snowflake.
    """
    logging.info(f"Loading data into Snowflake table: {table_name}")
    
    if df.empty:
        raise ValueError("The DataFrame is empty. No data to load into Snowflake.")
    
    try:
        snowflake_hook = SnowflakeHook(snowflake_conn_id=snowflake_conn_id)
        engine = snowflake_hook.get_sqlalchemy_engine()

        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists="replace",
            index=False,
            method="multi"
        )
    except Exception as e:
        logging.error(f"Error loading data into Snowflake: {e}")
        raise
