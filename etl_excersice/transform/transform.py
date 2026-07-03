from functools import reduce

import pandas as pd
import numpy as np


def rename_columns(dataframes: list[pd.DataFrame], old_column: str, new_column: str) -> list[pd.DataFrame]:
    """
    Rename a column in each dataframe when that column exists.
    """
    return [
        df.rename(columns={old_column: new_column}) if old_column in df.columns else df
        for df in dataframes
    ]


def convert_to_datetime(dataframes: list[pd.DataFrame], columns: list[str]) -> list[pd.DataFrame]:
    """
    Convert matching columns to datetime in each dataframe.
    """
    converted_dfs = []

    for df in dataframes:
        converted_df = df.copy()
        for column in columns:
            if column in converted_df.columns:
                converted_df[column] = pd.to_datetime(converted_df[column], errors="coerce")
        converted_dfs.append(converted_df)

    return converted_dfs


def remove_duplicates(
    dataframes: list[pd.DataFrame],
    subset: list[str] | None = None,
    keep: str = "first",
) -> list[pd.DataFrame]:
    """
    Remove duplicate rows from each dataframe.
    """
    return [df.drop_duplicates(subset=subset, keep=keep) for df in dataframes]


def clean_data(dataframes: list[pd.DataFrame], old_column: str, new_column: str) -> list[pd.DataFrame]:
    """
    Apply the cleaning steps used by the ELT runner.
    """
    cleaned_dfs = [df.dropna().copy() for df in dataframes]
    cleaned_dfs = rename_columns(cleaned_dfs, old_column=old_column, new_column=new_column)
    cleaned_dfs = [
        df.rename(
            columns={
                "Order ID": "order_id",
                "Customer Id": "customer_id",
                "product id": "product_id",
                "Order Date": "order_date",
                "shipping Days": "shipping_days",
            }
        )
        for df in cleaned_dfs
    ]
    cleaned_dfs = convert_to_datetime(cleaned_dfs, columns=["order_date", "signup_date", "delivery_date"])

    return cleaned_dfs


def merge_dataframes(
    dataframes: list[pd.DataFrame],
    merge_column: list[tuple[str, str]],
    how: str = "inner",
) -> pd.DataFrame:
    """
    Merge dataframes in order using matching left and right column names.
    """
    if not dataframes:
        raise ValueError("No dataframes provided for merging.")

    if len(merge_column) != len(dataframes) - 1:
        raise ValueError("merge_column must contain one pair for each merge operation.")

    def merge_pair(left_df: pd.DataFrame, merge_info: tuple[pd.DataFrame, tuple[str, str]]) -> pd.DataFrame:
        right_df, (left_column, right_column) = merge_info
        return left_df.merge(right_df, left_on=left_column, right_on=right_column, how=how)

    return reduce(merge_pair, zip(dataframes[1:], merge_column), dataframes[0])



def compute_derived_columns(merge_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute derived columns for the merged dataframe.
    """
    required_columns = {"amount", "quantity", "profit", "discount"}
    missing_columns = required_columns - set(merge_df.columns)

    if missing_columns:
        raise KeyError(f"Missing required columns for derived calculations: {missing_columns}")
    
    merge_df["total_revenue"] = merge_df["amount"] * merge_df["quantity"]

    merge_df["profit_margin"] = merge_df["profit"] / merge_df["total_revenue"]

    merge_df["discounted_price"] = merge_df["amount"] * (1 - merge_df["discount"])

    return merge_df


def segment_deliveries(merge_df: pd.DataFrame, fast_delivery_threshold: int = 3, slow_delivery_threshold: int = 10) -> pd.DataFrame:
    """
    Segment deliveries based on shipping days.
    """
    if "shipping_days" not in merge_df.columns:
        raise KeyError("Missing required column 'shipping_days' for delivery segmentation.")

    conditions = [
        merge_df["shipping_days"] < fast_delivery_threshold,
        merge_df["shipping_days"] > slow_delivery_threshold,
        ]
    
    choices = ["fast", "slow"]

    merge_df["delivery_segment"] = np.select(conditions, choices, default="normal")

    return merge_df


def categorized_products(merge_df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize products based on their price.
    """
    if "amount" not in merge_df.columns:
        raise KeyError("Missing required column 'amount' for product categorization.")

    bins = [0, 50, 200, float("inf")]
    
    labels = ["low", "medium", "high"]

    merge_df["product_category"] = pd.cut(merge_df["amount"], bins=bins, labels=labels, include_lowest=True)

    return merge_df