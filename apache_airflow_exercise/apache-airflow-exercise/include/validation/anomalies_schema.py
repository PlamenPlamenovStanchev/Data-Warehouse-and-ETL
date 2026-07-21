import pandas as pd
import pandera.pandas as pa

from pandera import Column, Check
from pandera.errors import SchemaError

from ..logger import setup_logger
logging = setup_logger(__name__)

anomalies_schema = pa.DataFrameSchema({
    "order_id": Column(str,unique=True),
    "customer_id": Column(int, Check.greater_than_or_equal_to(0), nullable=False),
    "product_id": Column(int, Check.greater_than_or_equal_to(0), nullable=False),
    "order_date": Column(pd.Timestamp, Check(lambda x: x <= pd.Timestamp.now()), nullable=False),
    "total_revenue": Column(float, Check.greater_than_or_equal_to(0), nullable=False)
})

def validate_anomalies_schema(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return anomalies_schema.validate(df)
    except SchemaError as e:
        logging.error(f"Schema validation failed: {e.failure_cases}")
        raise