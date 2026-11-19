"""
Step 7 of the retail project: clean the data, one documented rule at a time.
Run:  python 04_clean_data.py

Creates (in the same folder):
  sales_all_customers.csv  - valid sales, including rows with no Customer ID (for revenue/product/country analysis)
  clean_sales.csv          - valid sales that have a Customer ID (for customer analysis: RFM, retention)
  returns.csv              - cancelled invoices, kept aside for return analysis
  cleaning_log.csv         - how many rows were left after each rule
"""
import sys
from pathlib import Path

import pandas as pd

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
df = pd.read_csv(FOLDER / "retail_raw.csv", parse_dates=["InvoiceDate"])

log = []


def note(step, data):
    log.append({"step": step, "rows_left": len(data)})
    print(f"{step:<58}{len(data):>10,}")


print(f"{'Cleaning step':<58}{'Rows left':>10}")
note("0. Raw data (both sheets combined)", df)

# ---- Rule 1: remove the copies caused by the two Excel sheets overlapping ----
# Sheet 1 and sheet 2 both contain 1-9 Dec 2010, so every row in that window appears twice.
# If a row appears 2 times we keep 1; if it appears 4 times (a genuine repeat) we keep 2.
cols = list(df.columns)
window = (df["InvoiceDate"] >= "2010-12-01") & (df["InvoiceDate"] < "2010-12-10")
inside = df[window].copy()
groups = inside.groupby(cols, dropna=False)
inside["_k"] = groups.cumcount()                      # 0, 1, 2... within each identical group
inside["_r"] = groups.cumcount(ascending=False)       # counts down from the end
inside["_n"] = inside["_k"] + inside["_r"] + 1        # size of the identical group
inside = inside[inside["_k"] < inside["_n"] // 2].drop(columns=["_k", "_r", "_n"])
df = pd.concat([df[~window], inside], ignore_index=True)
note("1. Removed copies from the overlapping sheets", df)

# ---- Rule 2: set cancellations aside (invoice numbers starting with C) ----
is_cancel = df["Invoice"].astype(str).str.startswith("C")
returns = df[is_cancel].copy()
df = df[~is_cancel]
note("2. Set aside cancelled invoices (saved as returns.csv)", df)
odd = int((returns["Quantity"] >= 0).sum())
print(f"   (cancellations with quantity >= 0, which look like errors: {odd})")

# ---- Rule 3: remove rows that are not real sales ----
# Price <= 0 or Quantity <= 0 looked like stock adjustments (no customer, negative quantity).
bad = (df["Price"] <= 0) | (df["Quantity"] <= 0)
df = df[~bad].copy()
note("3. Removed rows with price <= 0 or quantity <= 0", df)

# ---- Add helpful columns ----
df["Revenue"] = df["Quantity"] * df["Price"]
df["Description"] = df["Description"].str.strip()
df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
df.to_csv(FOLDER / "sales_all_customers.csv", index=False)

# ---- Rule 4: keep only rows with a Customer ID for customer-level analysis ----
clean = df[df["Customer ID"].notna()].copy()
clean["Customer ID"] = clean["Customer ID"].astype(int)
note("4. Kept only rows with a Customer ID (clean_sales.csv)", clean)
clean.to_csv(FOLDER / "clean_sales.csv", index=False)
returns.to_csv(FOLDER / "returns.csv", index=False)
pd.DataFrame(log).to_csv(FOLDER / "cleaning_log.csv", index=False)

print("\n=== CHECK THE RESULT ===")
print("Total revenue, all valid sales: ", f"{df['Revenue'].sum():,.0f}")
print("Total revenue, rows with Customer ID:", f"{clean['Revenue'].sum():,.0f}",
      f"({clean['Revenue'].sum() / df['Revenue'].sum() * 100:.1f}% of all revenue)")
print("Unique customers in clean data:", clean["Customer ID"].nunique())
print("Unique invoices in clean data: ", clean["Invoice"].nunique())
print("Date range:", clean["InvoiceDate"].min(), "to", clean["InvoiceDate"].max())
print("\nSaved: sales_all_customers.csv, clean_sales.csv, returns.csv, cleaning_log.csv")
