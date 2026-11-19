"""
Step 14 of the retail project: two extra checks before we write recommendations.
  1. Repeat purchase rate: what share of customers ever placed a second order?
  2. Statistical test: is the spend of 'At Risk' customers really different from 'Loyal' customers?
Run:  python 07_stat_test.py       (needs:  pip install scipy)
"""
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
rfm = pd.read_csv(FOLDER / "rfm_customers.csv")

# ---- 1. Repeat purchase rate ----
repeat_rate = (rfm["Frequency"] >= 2).mean() * 100
print("=== 1. REPEAT PURCHASE RATE ===")
print(f"Customers: {len(rfm)}")
print(f"Customers with 2 or more orders: {repeat_rate:.1f}%")
print(f"Customers with exactly 1 order:  {100 - repeat_rate:.1f}%")

# ---- 2. Loyal vs At Risk: do they spend differently? ----
loyal = rfm.loc[rfm["Segment"] == "Loyal", "Monetary"]
at_risk = rfm.loc[rfm["Segment"] == "At Risk", "Monetary"]

print("\n=== 2. LOYAL vs AT RISK (total spend per customer) ===")
print(f"Loyal   : n={len(loyal):>5}  mean={loyal.mean():>9,.0f}  median={loyal.median():>9,.0f}")
print(f"At Risk : n={len(at_risk):>5}  mean={at_risk.mean():>9,.0f}  median={at_risk.median():>9,.0f}")

# Mann-Whitney U: compares two groups without assuming a bell-shaped distribution
stat, p_value = mannwhitneyu(loyal, at_risk, alternative="two-sided")
print(f"\nMann-Whitney U test p-value: {p_value:.4f}")
if p_value < 0.05:
    print("-> The difference in spend is statistically significant (p < 0.05).")
else:
    print("-> No statistically significant difference in spend (p >= 0.05).")
