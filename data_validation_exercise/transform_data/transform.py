import pandas as pd


def transform_customers_data(customers_df: pd.DataFrame) -> pd.DataFrame:
    """Clean customer names, emails, and duplicate customer records."""
    transformed_df = customers_df.copy()

    transformed_df["name"] = transformed_df["name"].astype(str).str.strip().str.title()
    transformed_df["email"] = transformed_df["email"].astype(str).str.strip().str.lower()
    transformed_df["customer_id"] = transformed_df["customer_id"].astype(int)
    transformed_df = transformed_df.drop_duplicates(subset=["customer_id"])

    return transformed_df


def transform_orders_data(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Clean order lines and calculate each line total."""
    transformed_df = orders_df.copy()

    transformed_df["order_id"] = transformed_df["order_id"].astype(int)
    transformed_df["customer_id"] = transformed_df["customer_id"].astype(int)
    transformed_df["product"] = transformed_df["product"].astype(str).str.strip().str.title()
    transformed_df["quantity"] = transformed_df["quantity"].astype(int)
    transformed_df["price"] = transformed_df["price"].astype(float)
    transformed_df["line_total"] = transformed_df["quantity"] * transformed_df["price"]

    return transformed_df


def transform_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Clean sales data types and calculate total revenue."""
    transformed_df = sales_df.copy()

    if "customer.customer_id" in transformed_df.columns:
        transformed_df = transformed_df.rename(columns={"customer.customer_id": "customer_id"})

    if "customer.name" in transformed_df.columns:
        transformed_df = transformed_df.rename(columns={"customer.name": "customer_name"})
        transformed_df["customer_name"] = transformed_df["customer_name"].astype(str).str.strip().str.title()

    transformed_df["order_id"] = transformed_df["order_id"].astype(int)
    transformed_df["customer_id"] = transformed_df["customer_id"].astype(int)
    transformed_df["amount"] = transformed_df["amount"].astype(float)
    transformed_df["quantity"] = transformed_df["quantity"].astype(int)
    transformed_df["order_date"] = pd.to_datetime(transformed_df["order_date"])
    transformed_df["total_revenue"] = transformed_df["amount"] * transformed_df["quantity"]

    return transformed_df


def transform_weather_data(weather_df: pd.DataFrame) -> pd.DataFrame:
    """Clean weather city names and convert temperatures to numeric values."""
    transformed_df = weather_df.copy()

    transformed_df["city"] = transformed_df["city"].astype(str).str.strip().str.title()
    transformed_df["temperature"] = (
        transformed_df["temperature"].astype(str).str.replace("°", "", regex=False).str.strip()
    )
    transformed_df["feels_like"] = (
        transformed_df["feels_like"].astype(str).str.replace("°", "", regex=False).str.strip()
    )
    transformed_df["temperature"] = pd.to_numeric(transformed_df["temperature"], errors="coerce")
    transformed_df["feels_like"] = pd.to_numeric(transformed_df["feels_like"], errors="coerce")

    return transformed_df


def merge_customers_with_orders(customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    """Join cleaned customers with cleaned order line records."""
    return customers_df.merge(orders_df, on="customer_id", how="left")
