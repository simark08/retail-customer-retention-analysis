"""
Step 10 of the retail project: segment customers with RFM.
  R = Recency   (days since the customer's last purchase; smaller is better)
  F = Frequency (number of different invoices)
  M = Monetary  (total money spent)
Run:  python 05_rfm_segmentation.py
Creates: rfm_customers.csv (one row per customer) and rfm_segments_summary.csv
"""
import sys
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
df = pd.read_csv(FOLDER / "clean_sales.csv", parse_dates=["InvoiceDate"])

# 1. The "today" for recency: the day after the last transaction in the data
snapshot = df["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
print("Snapshot date used to measure recency:", snapshot.date())

# 2. One row per customer with R, F and M values
rfm = df.groupby("Customer ID").agg(
    Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
    Frequency=("Invoice", "nunique"),
    Monetary=("Revenue", "sum"),
).reset_index()
print("Customers:", len(rfm))

# 3. Score each customer 1 (worst) to 5 (best) using quintiles.
#    rank(method="first") breaks ties so every score group gets about 20% of customers.
rfm["R_score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)


# 4. Turn scores into named segments (rules are checked in this order)
def segment(row):
    r, f = row["R_score"], row["F_score"]
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / Promising"
    if r <= 2 and f >= 3:
        return "At Risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs Attention"


rfm["Segment"] = rfm.apply(segment, axis=1)
rfm.to_csv(FOLDER / "rfm_customers.csv", index=False)

# 5. Summary per segment: how many customers, how much revenue
summary = rfm.groupby("Segment").agg(
    Customers=("Customer ID", "count"),
    Revenue=("Monetary", "sum"),
    Avg_Recency_days=("Recency", "mean"),
    Avg_Orders=("Frequency", "mean"),
    Avg_Spend=("Monetary", "mean"),
).reset_index()
summary["Pct_Customers"] = (summary["Customers"] / summary["Customers"].sum() * 100).round(1)
summary["Pct_Revenue"] = (summary["Revenue"] / summary["Revenue"].sum() * 100).round(1)
summary = summary.sort_values("Revenue", ascending=False).round(1)
summary.to_csv(FOLDER / "rfm_segments_summary.csv", index=False)

print("\n=== RFM SEGMENTS ===")
print(summary[["Segment", "Customers", "Pct_Customers", "Pct_Revenue",
               "Avg_Recency_days", "Avg_Orders", "Avg_Spend"]].to_string(index=False))
print("\nSaved: rfm_customers.csv and rfm_segments_summary.csv")
