import pandas as pd
from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError
import logging

customers_schema = DataFrameSchema(
    {"name": Column(str, checks=Check.str_length(min_value=1), nullable=False),
     "email": Column(str, checks=Check.str_matches(r"[^@]+@[^@]+\.[^@]+"), nullable=False),
     "customer_id": Column(int, checks=Check.greater_than_or_equal_to(0), nullable=False)}
)


def validate_customers_data(customers_df: pd.DataFrame, lazy: bool = True) -> pd.DataFrame:
    """Validate customer data against the customer schema."""
    logging.info("Validating customers data...")
    try:
        validated_df = customers_schema.validate(customers_df, lazy=lazy)
        logging.info("Customers data validation successful.")
        return validated_df
    except SchemaError as e:
        logging.error(f"Customers data validation failed: {e}")
        raise
        
       
