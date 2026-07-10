import logging
import pandas as pd
from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError


weather_schema = DataFrameSchema({
    "city": Column(str, Check(lambda x: x.isalpha()), nullable=False),
    "temperature": Column(float, Check(lambda x: x >= -50 and x <= 60), nullable=False),
    "feels_like": Column(float, Check(lambda x: x >= -50 and x <= 60), nullable=False)
    })

def validate_weather_data(weather_df: pd.DataFrame, lazy: bool = True) -> bool:
    """
    Validate the weather data DataFrame against the defined schema.

    Args:
        weather_df (pd.DataFrame): The weather data DataFrame to validate.

    Returns:
        bool: True if the DataFrame is valid, False otherwise.
    """

    logging.info("Validating weather data...")
    try:
        validated_df = weather_schema.validate(weather_df)
        logging.info("Weather data validation passed.")
    except SchemaError as e:
        logging.error(f"Weather data validation failed: {e}")
        raise
    
    return validated_df