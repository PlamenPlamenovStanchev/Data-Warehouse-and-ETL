import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)

segmented_customer_schema = pa.DataFrameSchema({
    "customer_id": Column(int, Check.greater_than_or_equal_to(0), unique=True),
    "total_spent": Column(float, Check.greater_than_or_equal_to(0), nullable=False),
    "customer_segment": Column(str, Check.isin(["Low", "Medium", "High", "Very High"]), nullable=False),
    "segmentation_date": Column(pd.Timestamp, Check(lambda x: x <= pd.Timestamp.now()), nullable=False)
})

def validate_segmented_schema(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return segmented_customer_schema.validate(df)
    except SchemaError as e:
        logging.error(f"Schema validation failed: {e}")
        raise