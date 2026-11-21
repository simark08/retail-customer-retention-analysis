-- Retail Customer Retention Analysis: overall cohort retention in SQL (MySQL)
-- A cohort = customers whose first purchase fell in the same month.
-- Retention at month k = share of a cohort that bought again exactly k months after its first month.
-- Only cohorts old enough to be observed for k months are included.

USE retail_analysis;

WITH purchases AS (                       -- one row per customer per month in which they bought
  SELECT DISTINCT customer_id,
         YEAR(invoice_date) * 12 + MONTH(invoice_date) AS month_num
  FROM clean_sales
),
cohorts AS (                              -- first purchase month of each customer
  SELECT customer_id, MIN(month_num) AS cohort_num
  FROM purchases
  GROUP BY customer_id
),
activity AS (                             -- active customers per cohort and months since first purchase
  SELECT c.cohort_num,
         p.month_num - c.cohort_num AS month_index,
         COUNT(DISTINCT p.customer_id) AS active_customers
  FROM purchases p
  JOIN cohorts c ON p.customer_id = c.customer_id
  GROUP BY c.cohort_num, p.month_num - c.cohort_num
),
cohort_size AS (                          -- customers in each cohort (month 0)
  SELECT cohort_num, active_customers AS size
  FROM activity
  WHERE month_index = 0
),
last_month AS (
  SELECT MAX(month_num) AS last_num FROM purchases
),
months AS (
  SELECT 1 AS k UNION ALL SELECT 2 UNION ALL SELECT 3
  UNION ALL SELECT 6 UNION ALL SELECT 9 UNION ALL SELECT 12
)
SELECT m.k AS months_after_first_purchase,
       COUNT(*) AS cohorts_included,
       SUM(cs.size) AS customers_in_those_cohorts,
       ROUND(SUM(COALESCE(a.active_customers, 0)) * 100.0 / SUM(cs.size), 1) AS retention_pct
FROM months m
JOIN cohort_size cs ON cs.cohort_num + m.k <= (SELECT last_num FROM last_month)
LEFT JOIN activity a ON a.cohort_num = cs.cohort_num AND a.month_index = m.k
GROUP BY m.k
ORDER BY m.k;
