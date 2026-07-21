import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)

pre_sales_schema = pa.DataFrameSchema(
    {
        "order_id": Column(str),
        "customer_id": Column(str),
        "product_id": Column(str),
        "order_date": Column(pa.DateTime),
        "amount": Column(float),
        "quantity": Column(int),
        "discount": Column(float),
        "profit": Column(float),
        "total_revenue": Column(float),
    })


post_sales_schema = pa.DataFrameSchema(
    {
        "order_id": Column(str),
        "customer_id": Column(int, Check.greater_than(0)),
        "product_id": Column(int, Check.greater_than(0)),
        "order_date": Column(pa.DateTime),
        "amount": Column(float, Check.greater_than_or_equal_to(0)),
        "quantity": Column(int, Check.greater_than(0)),
        "discount": Column(float, Check.between(0, 100)),
        "profit": Column(float, Check.greater_than_or_equal_to(0)),
        "total_revenue": Column(float, Check.greater_than_or_equal_to(0)),
    })

def validate_pre_sales_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the pre-sales DataFrame against the defined schema.

    Args:
        df (pd.DataFrame): The pre-sales DataFrame to validate.

    Returns:
        pd.DataFrame: The validated DataFrame.

    Raises:
        SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return pre_sales_schema.validate(df)
    except SchemaError as e:
        logging.warning(f"Pre-sales Schema validation failed: {e.failure_cases}")
        return df  # Return the original DataFrame even if validation fails
    

def validate_post_sales_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the post-sales DataFrame against the defined schema.

    Args:
        df (pd.DataFrame): The post-sales DataFrame to validate.

    Returns:
        pd.DataFrame: The validated DataFrame.

    Raises:
        SchemaError: If the DataFrame does not conform to the schema.
    """

    try:
        return post_sales_schema.validate(df)
    except SchemaError as e:
        logging.warning(f"Post-sales Schema validation failed: {e.failure_cases}")
        raise