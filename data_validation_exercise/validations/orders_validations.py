import logging
import pandas as pd
from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError

orders_schema = DataFrameSchema(
    {
        "order_id": Column(int, Check(lambda x: x > 0), nullable=False),
        "customer_id": Column(int, Check(lambda x: x > 0), nullable=False),
        "product": Column(str, Check(lambda x: x.str.len() > 0), nullable=False),
        "quantity": Column(int, Check(lambda x: x > 0), nullable=False),
        "price": Column(float, Check(lambda x: x > 0), nullable=False),
    }
)

def validate_orders_data(orders_df: pd.DataFrame, lazy: bool = True) -> bool:
    """Validate order data against the order schema."""
    logging.info("Starting validation of orders data.")
    try:
        validated_df = orders_schema.validate(orders_df, lazy=lazy)
        logging.info("Orders data validation successful.")
    except SchemaError as e:
        logging.error(f"Orders data validation failed: {e}")
        raise
    
    return validated_df

