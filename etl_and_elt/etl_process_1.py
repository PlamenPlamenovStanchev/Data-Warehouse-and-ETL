import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

df_data_raw = pd.read_csv('sales_data.csv')
#print(df_data_raw.head(10))
#print(df_data_raw.info())
#print(df_data_raw.columns)

df_data_raw.columns = df_data_raw.columns.str.lower().str.replace(' ', '_')
df_data_raw = df_data_raw.rename(columns={'amount': 'sales_amount', 'diskount': 'discount'})
df_data_raw['sales_amount'] = df_data_raw['sales_amount'].fillna(0)
df_data_raw['total_revenue'] = df_data_raw['sales_amount'] * df_data_raw['quantity']
df_cleaned_data = df_data_raw[df_data_raw['total_revenue'] > 0]

#print(df_cleaned_data.head(10))
#print(df_cleaned_data.info())
#print(df_cleaned_data.columns)

connection = psycopg2.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"))

cursor = connection.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales_summary (product_id INT, quantity INT, total_revenue NUMERIC(10, 2))
               ''')

for index, row in df_cleaned_data.iterrows():
    cursor.execute("""
        INSERT INTO sales_summary (product_id, quantity, total_revenue)
        VALUES (%s, %s, %s)
    """, (row["product_id"], row["quantity"], row["total_revenue"]))


connection.commit()
cursor.close()
connection.close()
print("Data loaded into the database successfully")
