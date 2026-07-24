import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

revenue_concentration_output_schema = pa.DataFrameSchema(
    {
        "region": Column(str, Check(lambda  s: s.str.len()>0)),
        "region_revenue": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
        "revenue_share": Column(float, Check.in_range(0.0, 1.0)),
        "cumulative_revenue_share": Column(float, Check.in_range(0.0, 1.0))
    }
)

def validate_revenue_concentration_output_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the revenue concentration output DataFrame against the defined schema.

    :param df: The revenue concentration output DataFrame to validate.
    :return: The validated DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return revenue_concentration_output_schema.validate(df)
    except SchemaError as e:
        print(f"Revenue concentration output DataFrame validation failed: {e}")
        raise