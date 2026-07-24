import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

sales_input_schema = pa.DataFrameSchema(
    {
        "sales_id": Column(int),
        "product_id": Column(int),
        "region": Column(str),
        "quantity": Column(int),
        "price": Column(float),
        "timestamp": Column(pa.DateTime),
        "total_sales" : Column(float)
        })

sales_output_schema = pa.DataFrameSchema(
    {
        "sales_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "product_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "region": Column(str),
        "quantity": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "price": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "timestamp": Column(pa.DateTime),
        "total_sales" : Column(float, checks=Check.greater_than_or_equal_to(0.0))
    })

def validate_input_sales_schema(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the input sales DataFrame against the defined schema.

    :param sales_df: The input sales DataFrame to validate.
    :return: The validated sales DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return sales_input_schema.validate(sales_df)
    except SchemaError as e:
        print(f"Input sales DataFrame validation failed: {e}")
        return  sales_df


def validate_output_sales_schema(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the output sales DataFrame against the defined schema.
    """
    try:
        return sales_output_schema.validate(sales_df)
    except SchemaError as e:
        print(f"Output sales DataFrame validation failed: {e}")
        raise