"""
Step 12 of the retail project: cohort retention.
A cohort = all customers whose FIRST purchase happened in the same month.
Retention in month k = share of that cohort that bought again k months after their first purchase month.
Run:  python 06_cohort_retention.py
Creates: cohort_retention_matrix.csv and retention_overall.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
df = pd.read_csv(FOLDER / "clean_sales.csv", parse_dates=["InvoiceDate"])

# 1. Turn every purchase date into a month number (so we can subtract months easily)
month_num = df["InvoiceDate"].dt.year * 12 + df["InvoiceDate"].dt.month
df["cohort_num"] = month_num.groupby(df["Customer ID"]).transform("min")   # month of first purchase
df["month_index"] = month_num - df["cohort_num"]                           # 0 = first month, 1 = next month...
last_month = month_num.max()

# 2. How many different customers bought in each cohort / month_index
active = (df.groupby(["cohort_num", "month_index"])["Customer ID"].nunique()
            .unstack(fill_value=0))
cohort_size = active[0]                                   # customers in each cohort (month 0)
retention = active.div(cohort_size, axis=0) * 100         # as percentages

# Months that have not happened yet (after the end of the data) must be EMPTY, not 0%
for c in retention.index:
    for k in retention.columns:
        if c + k > last_month:
            retention.loc[c, k] = np.nan

# 3. Readable cohort labels like 2010-03
labels = [f"{(n - 1) // 12}-{(n - 1) % 12 + 1:02d}" for n in retention.index]
matrix = retention.round(1)
matrix.index = labels
matrix.insert(0, "Cohort_size", cohort_size.values)
matrix.to_csv(FOLDER / "cohort_retention_matrix.csv")

# 4. Overall retention: for each month k, use only cohorts old enough to have been observed for k months
rows = []
for k in [1, 2, 3, 6, 9, 12]:
    eligible = [c for c in active.index if last_month - c >= k]
    returned = sum(active.loc[c, k] for c in eligible if k in active.columns)
    total = sum(cohort_size[c] for c in eligible)
    rows.append({"Months_after_first_purchase": k,
                 "Cohorts_included": len(eligible),
                 "Customers_in_those_cohorts": int(total),
                 "Retention_pct": round(returned / total * 100, 1)})
overall = pd.DataFrame(rows)
overall.to_csv(FOLDER / "retention_overall.csv", index=False)

print("=== OVERALL RETENTION (share of customers who bought again k months after their first month) ===")
print(overall.to_string(index=False))
print("\n=== COHORT SIZES (first 6 cohorts) ===")
print(matrix[["Cohort_size", 1, 2, 3]].head(6).to_string())
print("\nSaved: cohort_retention_matrix.csv and retention_overall.csv")
