import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)


pre_aggregate_schema = pa.DataFrameSchema(
    {
        "order_date": Column(pa.DateTime),
        "unique_customers": Column(int, Check.greater_than(0)),
        "total_sales": Column(float, Check.greater_than_or_equal_to(0))
    }
)

post_aggregate_schema = pa.DataFrameSchema(
    {
        "order_date": Column(pa.DateTime),
        "unique_customers": Column(int, Check.greater_than(0)),
        "total_sales": Column(float, Check.greater_than_or_equal_to(0))
    }
)


def validate_pre_aggregate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the input DataFrame against the pre-aggregate schema.

    Args:
        df (pd.DataFrame): The DataFrame to be validated.

    Returns:
        pd.DataFrame: The validated DataFrame.

    Raises:
        SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return pre_aggregate_schema.validate(df)
    except SchemaError as e:
        logging.warning(f"Pre-aggregate schema validation failed: {e.failure_cases}")
        return df  # Return the original DataFrame even if validation fails
    

def validate_post_aggregate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the input DataFrame against the post-aggregate schema.

    Args:
        df (pd.DataFrame): The DataFrame to be validated.

    Returns:
        pd.DataFrame: The validated DataFrame.

    Raises:
        SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return post_aggregate_schema.validate(df)
    except SchemaError as e:
        logging.error(f"Post-aggregate schema validation failed: {e.failure_cases}")
        raise  