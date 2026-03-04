-- AI BI Copilot — Analytical SQL Queries
-- All queries target the SQLite database at data/business_data.db

-- ============================================================
-- 1. Total revenue and cost by region
-- ============================================================
SELECT
    region,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(cost), 2)    AS total_cost
FROM transactions
GROUP BY region
ORDER BY total_revenue DESC;

-- ============================================================
-- 2. Monthly revenue trend (2024 vs 2025)
-- ============================================================
SELECT
    SUBSTR(date, 1, 7)     AS year_month,
    ROUND(SUM(revenue), 2) AS monthly_revenue
FROM transactions
GROUP BY year_month
ORDER BY year_month;

-- ============================================================
-- 3. Top 5 product categories by revenue
-- ============================================================
SELECT
    product_category,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM transactions
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 5;

-- ============================================================
-- 4. Average order value by customer segment
-- ============================================================
SELECT
    customer_segment,
    ROUND(AVG(revenue), 2) AS avg_order_value
FROM transactions
GROUP BY customer_segment
ORDER BY avg_order_value DESC;

-- ============================================================
-- 5. Revenue vs cost margin % by product category
-- ============================================================
SELECT
    product_category,
    ROUND(SUM(revenue), 2)                              AS total_revenue,
    ROUND(SUM(cost), 2)                                 AS total_cost,
    ROUND(
        CASE WHEN SUM(revenue) = 0 THEN NULL
             ELSE (SUM(revenue) - SUM(cost)) / SUM(revenue) * 100
        END,
        2
    ) AS margin_pct
FROM transactions
GROUP BY product_category
ORDER BY margin_pct DESC;

-- ============================================================
-- 6. Count of transactions by region and customer segment
--    (pivot-style cross-tab)
-- ============================================================
SELECT
    region,
    customer_segment,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY region, customer_segment
ORDER BY region, customer_segment;

-- ============================================================
-- 7. Top 10 sales reps by total revenue
-- ============================================================
SELECT
    sales_rep,
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(*)               AS num_transactions
FROM transactions
GROUP BY sales_rep
ORDER BY total_revenue DESC
LIMIT 10;

-- ============================================================
-- 8. Average process cycle time per case
--    (time from first event to last event in minutes)
-- ============================================================
SELECT
    case_id,
    ROUND(
        (JULIANDAY(MAX(timestamp)) - JULIANDAY(MIN(timestamp))) * 1440,
        2
    ) AS cycle_time_minutes
FROM process_events
GROUP BY case_id
ORDER BY cycle_time_minutes DESC;

-- ============================================================
-- 9. Activity with highest average duration (bottleneck query)
-- ============================================================
SELECT
    activity,
    ROUND(AVG(duration_minutes), 2)  AS avg_duration_minutes,
    ROUND(MAX(duration_minutes), 2)  AS max_duration_minutes,
    COUNT(*)                          AS event_count
FROM process_events
GROUP BY activity
ORDER BY avg_duration_minutes DESC;

-- ============================================================
-- 10. Average rating by product category
-- ============================================================
SELECT
    product_category,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*)              AS review_count
FROM customer_reviews
GROUP BY product_category
ORDER BY avg_rating DESC;

-- ============================================================
-- 11. Count of reviews by sentiment bucket
--     (1-2 = negative, 3 = neutral, 4-5 = positive)
-- ============================================================
SELECT
    CASE
        WHEN rating BETWEEN 1 AND 2 THEN 'Negative'
        WHEN rating = 3             THEN 'Neutral'
        WHEN rating BETWEEN 4 AND 5 THEN 'Positive'
    END AS sentiment_bucket,
    COUNT(*) AS review_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_reviews), 2) AS pct
FROM customer_reviews
GROUP BY sentiment_bucket
ORDER BY review_count DESC;

-- ============================================================
-- 12. Month-over-month revenue growth %
-- ============================================================
WITH monthly AS (
    SELECT
        SUBSTR(date, 1, 7) AS year_month,
        SUM(revenue)        AS revenue
    FROM transactions
    GROUP BY year_month
),
lagged AS (
    SELECT
        year_month,
        revenue,
        LAG(revenue) OVER (ORDER BY year_month) AS prev_revenue
    FROM monthly
)
SELECT
    year_month,
    ROUND(revenue, 2)                                                  AS revenue,
    ROUND(
        CASE WHEN prev_revenue = 0 OR prev_revenue IS NULL THEN NULL
             ELSE (revenue - prev_revenue) / prev_revenue * 100
        END,
        2
    ) AS mom_growth_pct
FROM lagged
WHERE prev_revenue IS NOT NULL
ORDER BY year_month;
