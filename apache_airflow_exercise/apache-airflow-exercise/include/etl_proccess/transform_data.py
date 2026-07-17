import pandas as pd

from include.logger import setup_logger

logging = setup_logger(__name__)

def clean_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the sales data by removing duplicates and handling missing values.

    Args:
        sales_df (pd.DataFrame): The sales DataFrame to be cleaned.
        """
    
    logging.info("Cleaning sales data...")
    sales_df.columns = sales_df.columns.str.strip().str.lower().str.replace(" ", "_")
    sales_df.drop_duplicates(inplace=True)
    sales_df["order_date"] = pd.to_datetime(sales_df["order_date"],format="mixed", errors="coerce")
    sales_df["total_revenue"] = sales_df["amount"] * sales_df["quantity"]

    logging.info(f"Cleanning sales data completed. Number of records after cleaning: {len(sales_df)}" )
    return sales_df

def clean_customers_data(customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the customers data by removing duplicates and handling missing values.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame to be cleaned.
    """
    
    logging.info("Cleaning customers data...")
    customers_df.columns = customers_df.columns.str.strip().str.lower().str.replace(" ", "_")
    customers_df.drop_duplicates(inplace=True)
    customers_df["signup_date"] = pd.to_datetime(customers_df["signup_date"],format="mixed", errors="coerce")

    logging.info(f"Cleanning customers data completed. Number of records after cleaning: {len(customers_df)}" )
    return customers_df

def clean_products_data(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the products data by removing duplicates and handling missing values.

    Args:
        products_df (pd.DataFrame): The products DataFrame to be cleaned.
    """
    
    logging.info("Cleaning products data...")
    products_df.columns = products_df.columns.str.strip().str.lower().str.replace(" ", "_")
    products_df.drop_duplicates(inplace=True)

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

    merged_df["order_date"] = pd.to_datetime(merged_df["order_date"], format="mixed", errors="coerce")
    aggregated_df = merged_df.groupby(pd.Grouper(key="order_date", freq="M")).agg(
        total_sales=("total_revenue", "sum"),
        unique_customers=("customer_id", "nunique")
    ).reset_index().copy()

    logging.info(f"Computing monthly aggregates completed. Number of records after aggregation: {len(aggregated_df)}" )
    return aggregated_df