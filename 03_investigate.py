"""
Step 5-6 of the retail project: look closely at the messy rows BEFORE deleting anything.
Run:  python 03_investigate.py
"""
import sys
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
df = pd.read_csv(FOLDER / "retail_raw.csv", parse_dates=["InvoiceDate"])

# ---------- A. Where do the duplicate rows come from? ----------
print("=== A. DUPLICATE ROWS BY MONTH ===")
dup = df[df.duplicated()]
print("Total duplicate rows:", len(dup))
print(dup["InvoiceDate"].dt.to_period("M").value_counts().sort_index().to_string())

overlap = (dup["InvoiceDate"] >= "2010-12-01") & (dup["InvoiceDate"] < "2010-12-10")
print("\nDuplicates inside 1-9 Dec 2010 (where the two sheets overlap):", int(overlap.sum()))
print("Duplicates everywhere else:", int((~overlap).sum()))

# ---------- B. What do rows with Price <= 0 look like? ----------
print("\n=== B. SAMPLE ROWS WITH PRICE <= 0 ===")
bad_price = df[df["Price"] <= 0]
print(bad_price.head(5)[["Invoice", "StockCode", "Description", "Quantity", "Price", "Customer ID"]])
print("\nOf these rows, how many have no Customer ID:", int(bad_price["Customer ID"].isna().sum()), "of", len(bad_price))
print("Of these rows, how many have no Description:", int(bad_price["Description"].isna().sum()), "of", len(bad_price))

# ---------- C. What do cancellations look like? ----------
print("\n=== C. SAMPLE CANCELLATIONS (Invoice starts with C) ===")
cancel = df[df["Invoice"].astype(str).str.startswith("C")]
print(cancel.head(5)[["Invoice", "StockCode", "Description", "Quantity", "Price", "Customer ID"]])
print("\nCancellations: all have negative quantity?", bool((cancel["Quantity"] < 0).all()))

# ---------- D. Rows with missing Customer ID ----------
print("\n=== D. ROWS WITH NO CUSTOMER ID ===")
no_id = df[df["Customer ID"].isna()]
print("Rows:", len(no_id), "| Share of total revenue (Quantity x Price, positive rows only):")
pos = df[(df["Quantity"] > 0) & (df["Price"] > 0)].copy()
pos["Revenue"] = pos["Quantity"] * pos["Price"]
print(round(pos.loc[pos["Customer ID"].isna(), "Revenue"].sum() / pos["Revenue"].sum() * 100, 1), "%")
