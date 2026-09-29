-- Part 1: SQL Business Query Engine (SQLite)
-- Run against data/meesho_reseller.db. Results were exported to part1_sql/output/*.csv

-- name: monthly_category_revenue
-- Q1: Monthly revenue by category (no status filter: totals cover all 900 orders).
-- Output columns are the input contract for Part 2 and Part 4.
SELECT month,
       category,
       ROUND(SUM(quantity * unit_price), 2) AS revenue,
       COUNT(*)                             AS n_orders
FROM orders
GROUP BY month, category
ORDER BY CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 WHEN 'June' THEN 3 END,
         CASE category WHEN 'Ethnic Wear' THEN 1 WHEN 'Western Wear' THEN 2
                       WHEN 'Kids Wear' THEN 3 WHEN 'Home & Kitchen' THEN 4
                       ELSE 5 END;

-- name: region_revenue
-- Q2: Region-wise total revenue and order count.
SELECT r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS revenue,
       COUNT(*) AS n_orders
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.region
ORDER BY revenue DESC;

-- name: top_resellers
-- Q3: Top 5 resellers by total spend, only those above 50000.
SELECT r.reseller_id, r.reseller_name, r.region,
       ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders o
JOIN resellers r ON r.reseller_id = o.reseller_id
GROUP BY r.reseller_id
HAVING total_spend > 50000
ORDER BY total_spend DESC
LIMIT 5;

-- name: never_ordered
-- Q4a: Resellers with zero orders. LEFT JOIN keeps every reseller; unmatched ones
-- have NULL in every orders column, so we test order_id IS NULL.
SELECT r.reseller_id, r.reseller_name, r.region
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE o.order_id IS NULL;

-- name: count_star_vs_count_col
-- Q4b: Why COUNT(*) cannot detect the zero-match case.
-- The LEFT JOIN keeps RS024 as ONE row with all orders columns NULL.
-- COUNT(*) counts that row, so it returns 1.
-- COUNT(o.order_id) skips NULLs, so it returns 0 (the true number of orders).
-- Therefore COUNT(*) is the wrong way to test for a zero-match LEFT JOIN row.
SELECT r.reseller_id,
       COUNT(*) AS count_star,
       COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o ON o.reseller_id = r.reseller_id
WHERE r.reseller_id = 'RS024'
GROUP BY r.reseller_id;

-- name: june_delivered_aov
-- Q5: Average order value for June, Delivered orders only.
SELECT ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS aov_june_delivered
FROM orders
WHERE month = 'June' AND status = 'Delivered';