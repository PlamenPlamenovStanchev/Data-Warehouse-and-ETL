import pandas as pd

from include.logger import setup_logger
from include.validation.aggregate_schema import validate_post_aggregate_schema, validate_pre_aggregate_schema
from include.validation.anomalies_schema import validate_anomalies_schema
from include.validation.customer_schema import validate_post_customer_schema, validate_pre_customer_schema
from include.validation.forecasted_schema import validate_forecasted_sales_schema
from include.validation.forecasted_schema import validate_forecasted_sales_schema
from include.validation.product_schema import validate_post_product_schema, validate_pre_product_schema
from include.validation.sales_schema import validate_post_sales_schema, validate_pre_sales_schema
from include.validation.segmented_schema import validate_segmented_schema

logging = setup_logger(__name__)

def clean_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the sales data by removing duplicates and handling missing values.

    Args:
        sales_df (pd.DataFrame): The sales DataFrame to be cleaned.
        """
    
    logging.info("Cleaning sales data...")

    sales_df = validate_pre_sales_schema(sales_df)

    sales_df.columns = sales_df.columns.str.strip().str.lower().str.replace(" ", "_")
    sales_df.drop_duplicates(inplace=True)
    sales_df["order_date"] = pd.to_datetime(sales_df["order_date"],format="mixed", errors="coerce")
    sales_df["total_revenue"] = sales_df["amount"] * sales_df["quantity"]

    sales_df = validate_post_sales_schema(sales_df)

    logging.info(f"Cleanning sales data completed. Number of records after cleaning: {len(sales_df)}" )
    return sales_df

def clean_customers_data(customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the customers data by removing duplicates and handling missing values.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame to be cleaned.
    """
    
    logging.info("Cleaning customers data...")

    customers_df = validate_pre_customer_schema(customers_df)

    customers_df.columns = customers_df.columns.str.strip().str.lower().str.replace(" ", "_")
    customers_df.drop_duplicates(inplace=True)
    customers_df["signup_date"] = pd.to_datetime(customers_df["signup_date"],format="mixed", errors="coerce")

    customers_df = validate_post_customer_schema(customers_df)
    
    return customers_df

def clean_products_data(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the products data by removing duplicates and handling missing values.

    Args:
        products_df (pd.DataFrame): The products DataFrame to be cleaned.
    """
    
    logging.info("Cleaning products data...")

    products_df = validate_pre_product_schema(products_df)

    products_df.columns = products_df.columns.str.strip().str.lower().str.replace(" ", "_")
    products_df.drop_duplicates(inplace=True)

    products_df = validate_post_product_schema(products_df)

    logging.info(f"Cleanning products data completed. Number of records after cleaning: {len(products_df)}" )
    return products_df  


def merge_dataframes(sales_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the sales, customers, and products DataFrames into a single DataFrame.

    Args:
        sales_df (pd.DataFrame): The cleaned sales DataFrame.
        customers_df (pd.DataFrame): The cleaned customers DataFrame.
        products_df (pd.DataFrame): The cleaned products DataFrame.

    Returns:
        pd.DataFrame: The merged DataFrame containing sales, customer, and product information.
    """
    
    logging.info("Merging dataframes...")
    merged_df = sales_df.merge(customers_df, on="customer_id", how="inner").copy()
    merged_df = merged_df.merge(products_df, on="product_id", how="inner").copy()
    merged_df["profit_margin"] = merged_df["profit"] / merged_df["amount"]

    logging.info(f"Merging dataframes completed. Number of records after merging: {len(merged_df)}" )
    return merged_df    


def compute_monthly_aggregates(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly aggregates for the merged DataFrame.

    Args:
        merged_df (pd.DataFrame): The merged DataFrame containing sales, customer, and product information. 
    """

    logging.info("Computing monthly aggregates...")

    merged_df = validate_pre_aggregate_schema(merged_df)

    merged_df["order_date"] = pd.to_datetime(merged_df["order_date"], format="mixed", errors="coerce")
    aggregated_df = merged_df.groupby(pd.Grouper(key="order_date", freq="M")).agg(
        total_sales=("total_revenue", "sum"),
        unique_customers=("customer_id", "nunique")
    ).reset_index().copy()

    aggregated_df = validate_post_aggregate_schema(aggregated_df)

    logging.info(f"Computing monthly aggregates completed. Number of records after aggregation: {len(aggregated_df)}" )
    return aggregated_df


def segment_customers(sales_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Segments customers based on their total revenue.

    Args:
        sales_df (pd.DataFrame): The sales DataFrame.
        customers_df (pd.DataFrame): The customers DataFrame.
    """

    logging.info("Segmenting customers...")

    total_spent_df = sales_df.groupby("customer_id")["total_revenue"].sum().reset_index()
    total_spent_df.rename(columns={"total_revenue": "total_spent"}, inplace=True)

    segmented_df = customers_df.merge(total_spent_df, on="customer_id", how="left").copy()
    segmented_df.dropna(subset=["total_spent"], inplace=True)

    segmented_df["customer_segment"] = pd.cut(
        segmented_df["total_spent"],
        bins=[0, 1000, 5000, 10000, float("inf")],
        labels=["Low", "Medium", "High", "Very High"],
        include_lowest=True
    )

    segmented_df["segmentation_date"] = pd.to_datetime(segmented_df["signup_date"], format="mixed", errors="coerce")

    allowed_columns = ["customer_id", "customer_segment", "segmentation_date", "total_spent"]

    df_segmented = drop_extra_columns(segmented_df, allowed_columns)

    df_segmented = validate_segmented_schema(df_segmented)

    logging.info(f"Segmenting customers completed. Number of records after segmentation: {len(df_segmented)}" )
    return df_segmented


def detect_sales_anomalies(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects anomalies in the sales data using the IQR method.

    Args:
        sales_df (pd.DataFrame): The sales DataFrame containing monthly sales data.
    """

    logging.info("Detecting sales anomalies...")

    threshold = sales_df["total_revenue"].mean() + 3 * sales_df["total_revenue"].std()
    anomalies_df = sales_df[sales_df["total_revenue"] > threshold].copy()
    anomalies_df["order_date"] = pd.to_datetime(anomalies_df["order_date"], format="mixed", errors="coerce")

    allowed_columns = ["order_id", "customer_id", "product_id", "order_date", "total_revenue"]

    anomalies_df = drop_extra_columns(anomalies_df, allowed_columns)

    anomalies_df = validate_anomalies_schema(anomalies_df)

    logging.info(f"Detecting sales anomalies completed. Number of anomalies detected: {len(anomalies_df)}" )
    return anomalies_df


def forecast_sales(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Forecasts future sales based on historical sales data.

    Args:
        sales_df (pd.DataFrame): The sales DataFrame containing historical sales data.
    """

    logging.info("Forecasting future sales...")

    forecast_df = sales_df.copy()
    forecast_df["order_date"] = pd.to_datetime(forecast_df["order_date"], format="mixed", errors="coerce")
    forecast_df.dropna(subset=["order_date"], inplace=True)
    forecast_df.sort_values("order_date", inplace=True)
    forecast_df.set_index("order_date", inplace=True)
    forecast_df["forecasted_sales"] = forecast_df["total_revenue"].rolling(window=7, min_periods=1).mean()
    forecast_df.reset_index(inplace=True)
    allowed_columns = ["order_date", "total_revenue", "forecasted_sales"]

    forecast_df = drop_extra_columns(forecast_df, allowed_columns)

    forecast_df = validate_forecasted_sales_schema(forecast_df)

    logging.info(f"Forecasting future sales completed. Number of records in forecasted data: {len(forecast_df)}" )
    return forecast_df


def drop_extra_columns(df: pd.DataFrame, allowed_columns: list) -> pd.DataFrame:
    """
    Drops extra columns from the DataFrame, keeping only the allowed columns.

    Args:
        df (pd.DataFrame): The DataFrame from which to drop extra columns.
        allowed_columns (list): The list of allowed column names to keep in the DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with only the allowed columns.
    """
    
    return df.loc[:, df.columns.isin(allowed_columns)].copy()