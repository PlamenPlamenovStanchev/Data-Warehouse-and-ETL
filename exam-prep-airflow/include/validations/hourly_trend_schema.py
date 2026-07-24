import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError



hourly_sales_trend_schema = pa.DataFrameSchema(
    {
        "hour": Column(int, checks=Check.in_range(0, 23)),
        "region": Column(str, Check(lambda s: s.str.len()>0)),
        "hourly_sales_trend": Column(float, checks=Check.greater_than_or_equal_to(0.0))
    }
)

def validate_hourly_sales_trend_schema(hourly_trend_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the hourly sales trend DataFrame against the defined schema.

    :param hourly_trend_df: The input hourly sales trend DataFrame to validate.
    :return: The validated hourly sales trend DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return hourly_sales_trend_schema.validate(hourly_trend_df)
    except SchemaError as e:
        print(f"Hourly sales trend DataFrame validation failed: {e}")
        raise