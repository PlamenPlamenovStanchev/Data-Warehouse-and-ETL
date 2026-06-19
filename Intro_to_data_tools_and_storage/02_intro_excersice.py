import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

orders_df = pd.read_csv(DATA_DIR / "large_orders.csv")

#print(orders_df) - just for testing if the data is loaded correctly


customers_reviews_df = pd.read_json(DATA_DIR / "large_customer_reviews.json")


reviews_df = pd.concat([
    customers_reviews_df.drop(columns=["review_data"]),
    pd.json_normalize(customers_reviews_df["review_data"])
], axis=1)

#print(reviews_df) - just for testing if the data is loaded correctly

#print(orders_df.shape)
#print(reviews_df.shape)

#print(orders_df.head())
#print(reviews_df.head())

#print(orders_df.info())
#print(reviews_df.info())

#print(orders_df.describe())
#print(reviews_df.describe())

#print(orders_df.dtypes)
#print(reviews_df.dtypes)



category_summary = (orders_df.groupby(["category", "subcategory"])
                    .agg(total_amount=("amount", "sum"), 
                        total_profit=("profit", "sum"),
                        avg_quantity=("quantity", "mean")).reset_index().sort_values(by='total_profit', ascending=False))

#print(category_summary) - just for testing if the data is loaded correctly


merged_df = orders_df.merge(reviews_df, on='customer_id', how='inner')

#print(merged_df.head()) - just for testing if the data is loaded correctly

high_value_customers = (merged_df[(merged_df['verified'] == True) & (merged_df['rating']>=4)].
                        groupby('customer_id').
                        agg(total_spent=('amount', 'sum'),
                            avg_rating=('rating', 'mean'),
                            orders_count=('order_id', 'count')).reset_index().sort_values(by='total_spent', ascending=False))

print(high_value_customers)
