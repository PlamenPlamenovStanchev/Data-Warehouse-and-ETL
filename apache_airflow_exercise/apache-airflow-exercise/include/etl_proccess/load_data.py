import uuid

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


#def load_data_to_snowflake(
#        df: pd.DataFrame,
#        database: str,
#        schema: str,
#        table_name: str,
#) -> dict:
#    """
#    Load a DataFrame into a Snowflake table.

#    Args:
#        df (pd.DataFrame): The DataFrame to load.
#        database (str): The target Snowflake database.
#        schema (str): The target Snowflake schema.
#        table_name (str): The name of the target Snowflake table.
#
#    Returns:
#        dict: A dictionary containing the status and message of the operation.
#    """
    # if df.empty:
    #     raise ValueError("The DataFrame is empty. No data to load into Snowflake.")
    #
    # database = _validate_identifier(database)
    # schema = _validate_identifier(schema)
    # table_name = _validate_identifier(table_name)
    #
    # staging_table = _validate_identifier(f"{table_name}_staging{uuid.uuid4().hex[:8]}")
    # target_fqn = f"{database}.{schema}.{table_name}"
    # staging_fqn = f"{database}.{schema}.{staging_table}"
    #
    # load_df = df.copy()
    #
    # load_df.columns = [_validate_identifier(str(col)) for col in load_df.columns]
    #
    # if load_df.columns.duplicated().any():
    #     raise ValueError("The DataFrame contains duplicate column names after validation.")
    #
    # hook = SnowflakeHook(snowflake_conn_id="my_snowflake_conn", database=database, schema=schema)  # Replace with your actual Snowflake connection ID
    # connection = hook.get_conn()
    # cursor = connection.cursor()
    #
    # try:
    #     cursor.execute(f"SELECT COUNT(*) FROM {database}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s'AND TABLE_TYPE = 'BASE TABLE'" % (schema, table_name))
    #     table_exists = cursor.fetchone()[0] == 1
    #
    #     if target_exists:
    #         cursor.execute(f"CREATE OR REPLACE TABLE {staging_fqn} LIKE {target_fqn}" auto_create_table=False)
    #     else:
    #         auto_create_table = True
    #
    # success, chunk_size, loaded_rows, _ =  write_pandas(
    #     conn = connection,
    #     df = load_df,
    #     table_name = staging_table,
    #     database = database,
    #     schema = schema,
    #     auto_create_table = auto_create_table,
    #     overwrite = False,
    #     quota_identifier = False,
    #     chunk_size = 10_000,
    # )
    #
    # if not success:
    #     raise RuntimeError("Failed to load data into Snowflake staging table.")
    #
    # expected_rows = len(load_df)
    #
    # if loaded_rows != expected_rows:
    #     raise ValueError(f"Loaded rows ({loaded_rows}) do not match expected rows ({expected_rows}).")
    # cursor.execute(f"SELECT COUNT(*) FROM {staging_fqn}")
    #
    # actual_rows = cursor.fetchone()[0]
    #
    # if actual_rows != expected_rows:
    #     raise ValueError(f"Actual rows in staging table ({actual_rows}) do not match expected rows ({expected_rows}).")
    #
    # if target_exists:
    #     cursor.execute(f"ALTER TABLE {target_fqn} SWAP WITH {staging_fqn}")
    #
    #     cursor.execute(f"DROP TABLE {staging_fqn}")
    #
    # else:
    #     cursor.execute(f"ALTER TABLE {staging_fqn} RENAME TO {table_name}")
    #
    #     connection.commit()
    #
    #     result = {
    #         "database": database,
    #         "schema": schema,
    #         "table_name": table_name,
    #         "loaded_rows": expected_rows,
    #         "chunk_size": chunk_size,
    #         "load_type": "full_refresh_swap"
    #     }
    #     logging.info(f"Data loaded successfully into Snowflake table: {target_fqn}. Result: {result}")
    #     return result
    # except Exception as e:
    #     connection.rollback()
    #     logging.error(f"Error loading data into Snowflake: {e}")
    #
    #     try:
    #         cursor.execute(f"DROP TABLE IF EXISTS {staging_fqn}")
    #     except Exception as drop_error:
    #         logging.error(f"Error dropping staging table {staging_fqn}: {drop_error}")
    #         raise
    # finally:
    #     cursor.close()
    #     connection.close()
    pass
    
