import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError


seasonal_sales_pattern_output_schema = pa.DataFrameSchema(
    {
        "quarter": Column(int, checks=Check.in_range(1, 4)),
        "category": Column(str),
        "total_sales": Column(float, checks=Check.greater_than_or_equal_to(0.0)),
    }
)

def validate_seasonal_sales_pattern_output_schema(seasonal_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the seasonal sales pattern output DataFrame against the defined schema.

    :param seasonal_df: The seasonal sales pattern output DataFrame to validate.
    :return: The validated seasonal sales pattern output DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return seasonal_sales_pattern_output_schema.validate(seasonal_df)
    except SchemaError as e:
        print(f"Seasonal sales pattern output DataFrame validation failed: {e}")
        raise