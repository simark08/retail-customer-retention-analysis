"""
Step 3 of the retail project: read the Excel file and save it as one CSV.
Run:  python 01_load_data.py
"""
import sys
from pathlib import Path

import pandas as pd

FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\retail-project")
XLSX = FOLDER / "online_retail_II.xlsx"

print("Reading the Excel file... this can take 1-3 minutes, please wait.")
sheets = pd.read_excel(XLSX, sheet_name=None)   # None = read every sheet in the file

print("\nSheets found:")
for name, df in sheets.items():
    print(f"  {name}: {df.shape[0]} rows, {df.shape[1]} columns")

raw = pd.concat(sheets.values(), ignore_index=True)   # stack the sheets into one table
raw.to_csv(FOLDER / "retail_raw.csv", index=False)

print("\nCombined table:", raw.shape[0], "rows,", raw.shape[1], "columns")
print("Saved as:", FOLDER / "retail_raw.csv")
