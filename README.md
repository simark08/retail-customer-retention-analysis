# Retail Customer Retention Analysis

Customer segmentation (RFM) and cohort retention analysis on 1M+ real retail transactions, built with Python and Power BI.

**Business question:** Which customers should the business focus on to increase repeat purchases, and what should it do for each group?

> **Status: work in progress.** Data cleaning, RFM segmentation, cohort retention, a statistical test and the first version of the Power BI dashboard are done. SQL analysis and dashboard polish are still to come (see "Next steps").

## Data
UCI **Online Retail II**: transactions of a UK-based online retailer, 1 December 2009 to 9 December 2011.
Download it from https://archive.ics.uci.edu/dataset/502/online+retail+ii (the raw data is not stored in this repository).

## Project steps and scripts
| Script | What it does |
|---|---|
| `01_load_data.py` | Reads both Excel sheets and saves one CSV (1,067,371 rows) |
| `02_audit_data.py`, `03_investigate.py` | Audit: missing values, duplicates, cancellations, bad prices |
| `04_clean_data.py` | Cleans the data one documented rule at a time (`cleaning_log.csv`) |
| `05_rfm_segmentation.py` | RFM scores and customer segments |
| `06_cohort_retention.py` | Retention by first-purchase month |
| `07_stat_test.py` | Repeat purchase rate and a Mann-Whitney U test (Loyal vs At Risk) |
| `08_export_powerbi_tables.py` | Tidy tables for the dashboard |

## Data quality findings and cleaning
| Step | Rows left |
|---|---|
| Raw data (both sheets) | 1,067,371 |
| Removed copies caused by the two sheets overlapping (1-9 Dec 2010) | 1,044,848 |
| Set aside cancelled invoices (kept in a separate returns table) | 1,025,683 |
| Removed rows with price <= 0 or quantity <= 0 (look like stock adjustments) | 1,019,654 |
| Kept rows with a Customer ID for customer analysis | 791,045 |

- 22.77% of rows had no Customer ID, but they account for about 15% of revenue, so customer-level analysis covers about 85% of revenue.
- Of the 34,335 exact duplicate rows, 22,844 fall in the sheet overlap window and were removed; the rest look like genuine repeated invoice lines and were kept.
- Result: 5,878 customers and 36,969 invoices.

## Key findings
**1. A quarter of customers bring in most of the revenue (RFM segments)**

| Segment | Customers | % of customers | % of revenue |
|---|---|---|---|
| Champions | 1,473 | 25.1% | 69.0% |
| Loyal | 1,230 | 20.9% | 14.6% |
| At Risk | 824 | 14.0% | 9.2% |
| Hibernating | 1,527 | 26.0% | 3.8% |
| New / Promising | 441 | 7.5% | 2.3% |
| Needs Attention | 383 | 6.5% | 1.2% |

**2. Retention is modest.** The share of customers who bought again in a given month after their first purchase month was 23.1% (month 1), 24.5% (month 3), 21.8% (month 6) and 22.3% (month 12). This counts customers active in that exact month, so it understates customers who return at some point. The first cohort (Dec 2009) includes customers who were already buying before the data starts and is left out of the dashboard heatmap.

**3. Repeat purchase rate is 72.4%.** 27.6% of customers placed only one order (recent customers have had less time to repeat).

**4. At Risk customers spend less than Loyal ones, but still a lot.** Mean spend is 1,937 vs 2,075 and median spend 1,026 vs 1,213; the difference is statistically significant (Mann-Whitney U, p < 0.0001). At Risk customers are far more valuable than Hibernating ones (mean about 432).

## Recommendations (to be tested, not proven)
1. **Protect Champions:** 25% of customers generate 69% of revenue. Prioritise service and track days since their last order.
2. **Test a win-back offer for At Risk customers** on a sample first. They have high past spend, but their average time since last order is about 369 days, so many may already be lost.
3. **Encourage a second order early:** 27.6% of customers bought only once. Test a nudge in the first 30 to 60 days.
4. **Keep spending low on Hibernating customers** (26% of customers, 3.8% of revenue), for example with automated emails only.

## Limitations
- One UK retailer over two years; findings may not apply elsewhere.
- Cancelled invoices are kept aside, so customer spend is gross of returns.
- Segments are defined from quintile scores, so they depend on the rules chosen.
- The data describes what happened, not why.

## Next steps
- Add SQL analysis (load the cleaned data into MySQL and reproduce RFM and cohort retention with SQL window functions)
- Fix the cohort label sorting in the dashboard heatmap and polish the layout
- Add the dashboard screenshot and final summary
