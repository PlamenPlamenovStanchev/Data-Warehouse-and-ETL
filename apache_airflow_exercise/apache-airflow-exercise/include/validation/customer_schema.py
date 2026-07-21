import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)

pre_customer_schema = pa.DataFrameSchema(
    {
        "customer_id": Column(int, unique=True),
        "name": Column(str),
        "email": Column(str),
        "signup_date": Column(pa.DateTime),
    })

post_customer_schema = pa.DataFrameSchema(
    {
        "customer_id": Column(int, unique=True),
        "name": Column(str, checks=Check.str_length(min_value=1)),
        "email": Column(str, checks=Check.str_matches(r"[^@]+@[^@]+\.[^@]+")),
        "signup_date": Column(pa.DateTime),
    })

def validate_pre_customer_schema(customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the customers DataFrame against the pre-customer schema.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame to be validated.

    Returns:
        pd.DataFrame: The validated customers DataFrame.
    """
    try:
        return pre_customer_schema.validate(customers_df)
    except SchemaError as e:
        logging.warning(f"Pre-customer schema validation failed: {e.failure_cases}")
        return customers_df
    

    
def validate_post_customer_schema(customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the customers DataFrame against the post-customer schema.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame to be validated.

    Returns:
        pd.DataFrame: The validated customers DataFrame.
    """
    try:
        return post_customer_schema.validate(customers_df)
    except SchemaError as e:
        logging.error(f"Post-customer schema validation failed: {e.failure_cases}")
        raise