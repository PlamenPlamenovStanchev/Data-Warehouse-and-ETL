import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)

forecasted_sales_schema = pa.DataFrameSchema(
    {
        "order_date": Column(pa.DateTime, nullable=False),
        "forecasted_sales": Column(pa.Float, nullable=False, checks=Check.ge(0)),
        "total_revenue": Column(pa.Float, nullable=False, checks=Check.ge(0)),
    }
)

def validate_forecasted_sales_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the forecasted sales DataFrame against the defined schema.

    Args:
        df (pd.DataFrame): The forecasted sales DataFrame to be validated.

    Returns:
        pd.DataFrame: The validated forecasted sales DataFrame.

    Raises:
        SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return forecasted_sales_schema.validate(df)
    except SchemaError as e:
        logging.error(f"Forecasted sales data validation failed: {e.failure_cases}")
        raise