"""
Step 4 of the retail project: audit the raw data (find the mess before cleaning it).
Run:  python 02_audit_data.py
"""
import sys
from pathlib import Path

import pandas as pd

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
df = pd.read_csv(FOLDER / "retail_raw.csv", parse_dates=["InvoiceDate"])

print("=== 1. SIZE AND COLUMNS ===")
print("Rows:", len(df), "| Columns:", df.shape[1])
print(df.dtypes)

print("\n=== 2. FIRST 5 ROWS ===")
print(df.head())

print("\n=== 3. MISSING VALUES ===")
missing = df.isna().sum()
print(pd.DataFrame({"missing": missing, "percent": (missing / len(df) * 100).round(2)}))

print("\n=== 4. THE MESS (counts of problem rows) ===")
is_cancel = df["Invoice"].astype(str).str.startswith("C")
print("Cancelled invoices (start with C):", int(is_cancel.sum()))
print("Quantity <= 0 (not cancellations):", int(((df["Quantity"] <= 0) & ~is_cancel).sum()))
print("Price <= 0:", int((df["Price"] <= 0).sum()))
print("Exact duplicate rows:", int(df.duplicated().sum()))

print("\n=== 5. THE BASICS ===")
print("Date range:", df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())
print("Unique customers:", df["Customer ID"].nunique())
print("Unique products (StockCode):", df["StockCode"].nunique())
print("Countries:", df["Country"].nunique())
print("\nTop 5 countries by number of rows:")
print(df["Country"].value_counts().head(5))
