import pandas as pd
from pandas.tests.groupby.conftest import as_index

from include.validations.enrich_schema import validate_enrich_output_schema
from include.validations.hourly_trend_schema import validate_hourly_sales_trend_schema
from include.validations.product_sales_ranking_output_schema import validate_product_sales_ranking_output_schema
from include.validations.product_schema import validate_input_product_schema, validate_output_product_schema
from include.validations.revenue_concentration_output_schema import validate_revenue_concentration_output_schema
from include.validations.sales_schema import validate_input_sales_schema, validate_output_sales_schema
from include.validations.seasonal_sales_patterns_output_schema import validate_seasonal_sales_pattern_output_schema


def transform_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the sales DataFrame by calculating total sales.

    :param sales_df: The input sales DataFrame.
    :return: The transformed sales DataFrame with an additional 'total_sales' column.
    """
    # Validate the input sales DataFrame
    validated_sales_df = validate_input_sales_schema(sales_df)

    sales_df.columns = sales_df.columns.str.strip().str.lower().replace(" ", "_")
    sales_df["region"] = sales_df["region"].str.strip().str.lower()
    sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"], format="mixed", errors="coerce")
    sales_df = sales_df.dropna(subset=["timestamp", "region"])
    sales_df = sales_df[(sales_df["quantity"] >= 0) & (sales_df["price"] >= 0.0)].copy()
    sales_df = sales_df["total_sales"] = sales_df["quantity"] * sales_df["price"]

    # Validate the output sales DataFrame
    validated_output_sales_df = validate_output_sales_schema(validated_sales_df)

    return validated_output_sales_df

def transform_product_data(product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the product DataFrame by cleaning and standardizing the data.

    :param product_df: The input product DataFrame.
    :return: The transformed product DataFrame.
    """
    # Validate the input product DataFrame
    validated_product_df = validate_input_product_schema(product_df)

    product_df.columns = product_df.columns.str.strip().str.lower().replace(" ", "_")
    product_df["category"] = product_df["category"].str.strip().str.lower()
    product_df["brand"] = product_df["brand"].str.strip().str.upper()
    product_df = product_df.dropna(subset=["product_id", "rating"])
    product_df = product_df.drop_duplicates()

    # Validate the output product DataFrame
    validated_output_product_df = validate_output_product_schema(validated_product_df)

    return validated_output_product_df

def merge_sales_product_data(sales_df: pd.DataFrame, product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the sales and product DataFrames on the 'product_id' column.

    :param sales_df: The transformed sales DataFrame.
    :param product_df: The transformed product DataFrame.
    :return: The merged DataFrame containing sales and product information.
    """
    merged_df = sales_df.merge(product_df, on="product_id", how="inner")
    return merged_df

def enrich_merged_data(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the merged DataFrame with additional calculated fields.

    :param merged_df: The merged DataFrame containing sales and product information.
    :return: The enriched DataFrame with additional calculated fields.
    """
    merged_df["timestamp"] = pd.to_datetime(merged_df["timestamp"], format="mixed", errors="coerce")
    merged_df["month"] = merged_df["timestamp"].dt.to_period("M").astype(str)
    merged_df["week"] = merged_df["timestamp"].dt.isocalendar().week
    merged_df["weekday"] = merged_df["timestamp"].dt.day_name()
    merged_df["hour"] = merged_df["timestamp"].dt.hour.astype("Int64")
    merged_df["sales_bucket"] = pd.cut(merged_df["total_sales"], bins=[0, 100, 500, float("inf")], labels=["Low", "Medium", "High"])

    return validate_enrich_output_schema(merged_df)


def hourly_sales_trend(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the hourly sales trend from the enriched DataFrame.

    :param enriched_df: The enriched DataFrame containing sales and product information.
    :return: A DataFrame containing the hourly sales trend.
    """
    agg = (
        enriched_df.groupby(["region", "hour", "category"], as_index=False).agg(hourly_sales_trend=("total_sales", "sum")))

    idx = agg.groupby(["region", "category"])["hourly_sales_trend"].idmax()

    peaks = agg.loc[idx].reset_index(drop=True)

    return validate_hourly_sales_trend_schema(peaks)

def product_ranking_with_brand(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the product ranking with brand from the enriched DataFrame.

    :param enriched_df: The enriched DataFrame containing sales and product information.
    :return: A DataFrame containing the product ranking with brand.
    """
    summary = enriched_df.groupby(["product_id", "brand", "category", "rating"], as_index=False).agg(
        revenue=("total_sales", "sum"),
        sales_count=("product_id", "size"))

    revenue_rank = summary["revenue"].rank(
        method="average",
        pct=True,
    )

    sales_count_rank = summary["sales_count"].rank(
        method="average",
        pct=True ,
    )

    performance_score = revenue_rank * 0.5 + sales_count_rank * 0.5

    summary["value_bucket"] =pd.cut(
        performance_score,
        bins=[0, 0.20, 0.80, 1],
        labels=["Low performance", "Average performance", "Best seller"],
        include_lowest=True,
    )

    return validate_product_sales_ranking_output_schema(summary)

def seasonal_sales_pattern(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the seasonal sales pattern from the enriched DataFrame.

    :param enriched_df: The enriched DataFrame containing sales and product information.
    :return: A DataFrame containing the seasonal sales pattern.
    """
    seasonal_df = enriched_df.copy()

    seasonal_df["timestamp"] = pd.to_datetime(seasonal_df["timestamp"], format="mixed", errors="coerce")
    seasonal_df["quarter"] = seasonal_df["timestamp"].dt.to_period("Q").astype(str)
    seasonal_patterns = seasonal_df.groupby(["quarter", "category"], as_index=False).agg(
        total_sales=("total_sales", "sum")
    )

    return validate_seasonal_sales_pattern_output_schema(seasonal_patterns)

def revenue_concentration(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the revenue concentration from the enriched DataFrame.

    :param enriched_df: The enriched DataFrame containing sales and product information.
    :return: A DataFrame containing the revenue concentration.
    """
    summary = enriched_df.groupby(["region"], as_index=False).agg(
        region_revenue=("total_sales", "sum"))

    summary = summary.sort_values(by="region_revenue", ascending=False).reset_index(drop=True)
    total = summary["region_revenue"].sum()

    if total == 0:
        raise ValueError("Total revenue is zero, cannot calculate revenue concentration.")

    summary["revenue_share"] = summary["region_revenue"] / total

    summary["cumulative_revenue_share"] = summary["revenue_share"].cumsum()

    return validate_revenue_concentration_output_schema(summary)


