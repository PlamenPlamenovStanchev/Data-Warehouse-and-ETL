import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError


product_sales_ranking_output_schema = pa.DataFrameSchema(
    {
        "product_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "revenue": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "sales_count": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "value_bucket": Column(str, checks=Check.isin(["Low performance", "Average performance", "Best seller"]))
    })

def validate_product_sales_ranking_output_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the product sales ranking output DataFrame against the defined schema.

    :param df: The product sales ranking output DataFrame to validate.
    :return: The validated DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return product_sales_ranking_output_schema.validate(df)
    except SchemaError as e:
        print(f"Product sales ranking output DataFrame validation failed: {e}")
        raise

