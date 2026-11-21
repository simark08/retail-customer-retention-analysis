"""
Step 16 of the retail project: prepare small, tidy tables for the Power BI dashboard.
Run:  python 08_export_powerbi_tables.py
Creates: monthly_revenue.csv and cohort_retention_long.csv
"""
import sys
from pathlib import Path

import pandas as pd

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")

# ---- 1. Monthly revenue (all valid sales, including customers with no ID) ----
sales = pd.read_csv(FOLDER / "sales_all_customers.csv", parse_dates=["InvoiceDate"])
monthly = sales.groupby("InvoiceMonth").agg(
    Revenue=("Revenue", "sum"),
    Invoices=("Invoice", "nunique"),
    Customers=("Customer ID", "nunique"),
).reset_index().round(0)
# the data stops on 9 Dec 2011, so that month is incomplete
monthly["Is_Partial_Month"] = monthly["InvoiceMonth"] == "2011-12"
monthly.to_csv(FOLDER / "monthly_revenue.csv", index=False)

# ---- 2. Cohort retention in "long" format (easier for a Power BI matrix) ----
wide = pd.read_csv(FOLDER / "cohort_retention_matrix.csv")
wide = wide.rename(columns={wide.columns[0]: "Cohort"})
long = wide.melt(id_vars=["Cohort", "Cohort_size"],
                 var_name="Months_after_first_purchase", value_name="Retention_pct")
long = long.dropna(subset=["Retention_pct"])            # drop months that have not happened yet
long["Months_after_first_purchase"] = long["Months_after_first_purchase"].astype(int)
long = long.sort_values(["Cohort", "Months_after_first_purchase"])
long.to_csv(FOLDER / "cohort_retention_long.csv", index=False)

print("monthly_revenue.csv:", len(monthly), "rows")
print(monthly.head(3).to_string(index=False))
print("\ncohort_retention_long.csv:", len(long), "rows")
print(long.head(3).to_string(index=False))
print("\nSaved in:", FOLDER)
