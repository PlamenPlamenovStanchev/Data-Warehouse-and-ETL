import logging
import pandas as pd
from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError

sales_schema = DataFrameSchema(
    {
        "sale_id": Column(int, Check(lambda x: x > 0), nullable=False),
        "customer_id": Column(int, Check(lambda x: x > 0), nullable=False),
        "amount": Column(float, Check(lambda x: x >= 0), nullable=False),
        "quantity": Column(int, Check(lambda x: x >= 0), nullable=False),
        "order_date": Column(pd.Timestamp, Check(lambda x: x <= pd.Timestamp.now()), nullable=False),

    }
)

def validate_sales_data(sales_df: pd.DataFrame) -> bool:
    """
    Validate the sales data DataFrame against the defined schema.

    Args:
        sales_df (pd.DataFrame): The sales data DataFrame to validate.

    Returns:
        bool: True if the DataFrame is valid, False otherwise.
    """

    logging.info("Validating sales data...")
    try:
        validated_df = sales_schema.validate(sales_df)
        logging.info("Sales data validation passed.")
    except SchemaError as e:
        logging.error(f"Sales data validation failed: {e}")
        raise
    
    return validated_df