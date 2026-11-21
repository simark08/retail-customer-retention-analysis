"""
Step 22 of the retail project: load the cleaned sales into MySQL for SQL analysis.
Run:  python 09_load_to_mysql.py
Creates database 'retail_analysis' with one table 'clean_sales' (about 791,000 rows).
"""
import getpass
import sys
from pathlib import Path

import mysql.connector
import pandas as pd

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
HOST, USER, DATABASE = "localhost", "root", "retail_analysis"

print("Reading clean_sales.csv ...")
df = pd.read_csv(FOLDER / "clean_sales.csv", dtype={"Invoice": str, "StockCode": str},
                 parse_dates=["InvoiceDate"])
df = df.rename(columns={"Invoice": "invoice", "StockCode": "stock_code", "Description": "description",
                        "Quantity": "quantity", "InvoiceDate": "invoice_date", "Price": "price",
                        "Customer ID": "customer_id", "Country": "country", "Revenue": "revenue",
                        "InvoiceMonth": "invoice_month"})
df = df[["invoice", "stock_code", "description", "quantity", "invoice_date", "price",
         "customer_id", "country", "revenue", "invoice_month"]]
df["invoice_date"] = df["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
df = df.astype(object).where(pd.notnull(df), None)     # MySQL needs None, not NaN
print("Rows to load:", len(df))

password = getpass.getpass("Enter your MySQL password (typing stays invisible, then press Enter): ")
conn = mysql.connector.connect(host=HOST, user=USER, password=password)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
cur.execute(f"USE {DATABASE}")
cur.execute("DROP TABLE IF EXISTS clean_sales")
cur.execute("""
    CREATE TABLE clean_sales (
        invoice VARCHAR(20), stock_code VARCHAR(20), description VARCHAR(255),
        quantity INT, invoice_date DATETIME, price DOUBLE,
        customer_id INT, country VARCHAR(60), revenue DOUBLE, invoice_month VARCHAR(7)
    )""")

insert_sql = ("INSERT INTO clean_sales (invoice, stock_code, description, quantity, invoice_date, "
              "price, customer_id, country, revenue, invoice_month) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
rows = [tuple(r) for r in df.itertuples(index=False, name=None)]
batch = 5000
for i in range(0, len(rows), batch):
    cur.executemany(insert_sql, rows[i:i + batch])
    conn.commit()
    print(f"  loaded {min(i + batch, len(rows)):,} of {len(rows):,} rows")

cur.execute("SELECT COUNT(*) FROM clean_sales")
print("\nRows in MySQL table clean_sales:", cur.fetchone()[0])
cur.close()
conn.close()
print("Done. Database:", DATABASE)
