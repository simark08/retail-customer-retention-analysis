-- Retail Customer Retention Analysis: RFM segmentation in SQL (MySQL)
-- Table: clean_sales (loaded by 09_load_to_mysql.py), snapshot date = 2011-12-10 (day after the last transaction)

USE retail_analysis;

-- Query 1: Recency, frequency and monetary value per customer (top 10 spenders)
WITH rfm AS (
  SELECT customer_id,
         TIMESTAMPDIFF(DAY, MAX(invoice_date), '2011-12-10') AS recency_days,
         COUNT(DISTINCT invoice) AS frequency,
         SUM(revenue) AS monetary
  FROM clean_sales
  GROUP BY customer_id
)
SELECT customer_id, recency_days, frequency, ROUND(monetary, 2) AS monetary
FROM rfm
ORDER BY monetary DESC
LIMIT 10;

-- Query 2: Score customers 1-5 with NTILE and name the segments
WITH rfm AS (
  SELECT customer_id,
         TIMESTAMPDIFF(DAY, MAX(invoice_date), '2011-12-10') AS recency_days,
         COUNT(DISTINCT invoice) AS frequency,
         SUM(revenue) AS monetary
  FROM clean_sales
  GROUP BY customer_id
),
scored AS (
  SELECT customer_id, recency_days, frequency, monetary,
         6 - NTILE(5) OVER (ORDER BY recency_days, customer_id) AS r_score,   -- recent = high score
         NTILE(5) OVER (ORDER BY frequency, customer_id) AS f_score
  FROM rfm
),
segmented AS (
  SELECT *,
         CASE
           WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
           WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
           WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
           WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
           WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'
           ELSE 'Needs Attention'
         END AS segment
  FROM scored
)
SELECT segment,
       COUNT(*) AS customers,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 1) AS pct_customers,
       ROUND(SUM(monetary) * 100 / SUM(SUM(monetary)) OVER (), 1) AS pct_revenue
FROM segmented
GROUP BY segment
ORDER BY pct_revenue DESC;
