import pandas as pd
import pandera.pandas as pa
from numpy.core.tests.examples.cython.setup import checks
from pandera import Column, Check
from pandera.errors import SchemaError


product_input_schema = pa.DataFrameSchema(
    {
        "product_id": Column(int),
        "category": Column(str),
        "brand": Column(str),
        "rating": Column(float)
    }
)

product_output_schema = pa.DataFrameSchema(
    {
        "product_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "category": Column(str, checks=Check(lambda x: x.str.islower())),
        "brand": Column(str, checks=Check(lambda x: x.str.isupper())),
        "rating": Column(float, checks=Check.greater_than_or_equal_to(0.0))
    })


def validate_input_product_schema(product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the input product DataFrame against the defined schema.

    :param product_df: The input product DataFrame to validate.
    :return: The validated product DataFrame.
    :raises SchemaError: If the DataFrame does not conform to the schema.
    """
    try:
        return product_input_schema.validate(product_df)
    except SchemaError as e:
        print(f"Input product DataFrame validation failed: {e}")
        return  product_df


def validate_output_product_schema(product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the output product DataFrame against the defined schema.
    """
    try:
        return product_output_schema.validate(product_df)
    except SchemaError as e:
        print(f"Output product DataFrame validation failed: {e}")
        raise