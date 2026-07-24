import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError


enrich_output_schema = pa.DataFrameSchema(
    {
        "sales_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "product_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "region": Column(str),
        "quantity": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "price": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "timestamp": Column(pa.DateTime),
        "total_sales": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "category": Column(str),
        "brand": Column(str),
        "rating": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "month": Column(int, checks=Check.in_range(1, 12)),
        "hour": Column(int, checks=Check.in_range(0, 23)),
        "sales_bucket": Column(str, checks=Check.isin(["low", "medium", "high"])),
    }
)

def validate_enrich_output_schema(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the enriched output DataFrame against the defined schema.

    :param enriched_df: The enriched output DataFrame to validate.
    :return: The validated enriched DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return enrich_output_schema.validate(enriched_df)
    except SchemaError as e:
        print(f"Enriched output DataFrame validation failed: {e}")
        raise