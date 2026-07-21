import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)


pre_product_schema = pa.DataFrameSchema(
    {   
        "product_id": Column(int),
        "product_name": Column(str),
        "category": Column(str),
        "price": Column(float)
    })

post_product_schema = pa.DataFrameSchema(
    {   
        "product_id": Column(int, Check.greater_than_or_equal_to(0)),
        "product_name": Column(str, Check.str_length(min_value=1)),
        "category": Column(str, Check.str_length(min_value=1)),
        "price": Column(float, Check.greater_than_or_equal_to(0))
    })

def validate_pre_product_schema(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the products DataFrame against the pre-defined schema before cleaning.

    Args:
        products_df (pd.DataFrame): The products DataFrame to be validated. 
    """
    
    try:
        return pre_product_schema.validate(products_df)
    except SchemaError as e:
        logging.warning(f"Pre-validation failed for products data: {e.failure_cases}")
        return products_df
    

def validate_post_product_schema(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the products DataFrame against the post-defined schema after cleaning.

    Args:
        products_df (pd.DataFrame): The products DataFrame to be validated. 
    """
    
    try:
        return post_product_schema.validate(products_df)
    except SchemaError as e:
        logging.error(f"Post-validation failed for products data: {e.failure_cases}")
        raise