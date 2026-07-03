import pandas as pd 
import psycopg2
from sqlalchemy import create_engine, exists

from config.config import PORT, USER, PASSWORD, HOST, DATABASE

def create_database_if_not_exists():
    """
    Create the database if it does not exist.
    """
    try:
        # Connect to the default database (usually 'postgres')
        conn = psycopg2.connect(
            dbname='postgres',
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the target database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DATABASE}'")
        if cursor.fetchone() is None:  # Database does not exist
            # Create the database if it does not exist
            cursor.execute(f"CREATE DATABASE {DATABASE}")
            print(f"Database '{DATABASE}' created successfully.")
        else:
            print(f"Database '{DATABASE}' already exists.") 

    finally:
        cursor.close()
        conn.close()

def load_to_postgres(df: pd.DataFrame, table_name: str, if_exists: str = 'append'):
    """
    Load a DataFrame to a PostgreSQL table.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        table_name (str): The name of the target table in PostgreSQL.
        if_exists (str): What to do if the table already exists. Options are 'fail', 'replace', or 'append'.
    """
    try:
        
        # Create a connection string
        connection_string = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
        # Create an SQLAlchemy engine
        engine = create_engine(connection_string)

        # Load the DataFrame to PostgreSQL
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        print(f"Data loaded to table '{table_name}' successfully.")
    except Exception as e:
        print(f"Error occurred while loading data to PostgreSQL: {e}")
        raise


def load_transformed_data_to_postgres(transformed_df: pd.DataFrame, table_name: str):
    """
    Load the transformed DataFrame to PostgreSQL.

    Args:
        transformed_df (pd.DataFrame): The transformed DataFrame to load.
        table_name (str): The name of the target table in PostgreSQL.
    """
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        order_id INT PRIMARY KEY,  
        customer_id INT,
        total_revenue NUMERIC (10, 2),
        profit_margin NUMERIC (5, 2),
        shipping_days INT
    );
    """
    insert_sql = f"""
    INSERT INTO {table_name} (order_id, customer_id, total_revenue, profit_margin, shipping_days)
    VALUES %s
    ON CONFLICT (order_id) DO UPDATE
    SET 
        total_revenue = EXCLUDED.total_revenue,
        profit_margin = EXCLUDED.profit_margin,
        shipping_days = EXCLUDED.shipping_days;
    """

    db_params = {
        "dbname": DATABASE,
        "user": USER,
        "password": PASSWORD,
        "host": HOST,
        "port": PORT
    }
    try:
        columns_to_load = [
            "order_id",
            "customer_id",
            "total_revenue",
            "profit_margin",
            "shipping_days"
        ]

        missing_columns = [column for column in columns_to_load if column not in transformed_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in the DataFrame: {missing_columns}")
        
        values = list(transformed_df[columns_to_load].itertuples(index=False, name=None))
        if not values:
            raise ValueError("The DataFrame is empty. No data to load.")
        
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                psycopg2.extras.execute_values(cursor, insert_sql, values)
                conn.commit()
                print(f"Data loaded to table '{table_name}' successfully.")
    except Exception as e:
        print(f"Error occurred while loading data to PostgreSQL: {e}")
        raise