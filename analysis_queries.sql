-- analysis_queries.sql
-- A set of business questions answered in SQL, written with readable CTEs
-- (preferred style: CTEs over deeply nested subqueries).
-- Tested against PostgreSQL / MySQL syntax; minor tweaks may be needed for SQLite.

-- =========================================================
-- Q1. Month-over-month net revenue growth
-- =========================================================
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS order_month,
        SUM(net_amount) AS net_revenue
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY 1
),
revenue_with_growth AS (
    SELECT
        order_month,
        net_revenue,
        LAG(net_revenue) OVER (ORDER BY order_month) AS prev_month_revenue
    FROM monthly_revenue
)
SELECT
    order_month,
    net_revenue,
    prev_month_revenue,
    ROUND(
        100.0 * (net_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0), 2
    ) AS mom_growth_pct
FROM revenue_with_growth
ORDER BY order_month;


-- =========================================================
-- Q2. Top 10 customers by lifetime value (delivered orders only)
-- =========================================================
WITH customer_revenue AS (
    SELECT
        o.customer_id,
        c.city,
        c.city_tier,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.net_amount) AS lifetime_value
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id, c.city, c.city_tier
)
SELECT *
FROM customer_revenue
ORDER BY lifetime_value DESC
LIMIT 10;


-- =========================================================
-- Q3. Category performance: revenue, orders, avg order value, return rate
-- =========================================================
WITH category_orders AS (
    SELECT
        category,
        order_status,
        net_amount
    FROM orders
),
category_summary AS (
    SELECT
        category,
        COUNT(*) FILTER (WHERE order_status = 'Delivered') AS delivered_orders,
        COUNT(*) FILTER (WHERE order_status = 'Returned')  AS returned_orders,
        COUNT(*) AS total_orders,
        SUM(net_amount) FILTER (WHERE order_status = 'Delivered') AS total_revenue
    FROM category_orders
    GROUP BY category
)
SELECT
    category,
    total_orders,
    delivered_orders,
    total_revenue,
    ROUND(total_revenue / NULLIF(delivered_orders, 0), 2) AS avg_order_value,
    ROUND(100.0 * returned_orders / NULLIF(total_orders, 0), 2) AS return_rate_pct
FROM category_summary
ORDER BY total_revenue DESC;


-- =========================================================
-- Q4. Customer RFM-style ranking using window functions
-- (recency in days, frequency, monetary, each ranked into quintiles)
-- =========================================================
WITH customer_stats AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(net_amount) AS monetary,
        (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') AS snapshot_date
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT
        customer_id,
        snapshot_date - last_order_date AS recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY snapshot_date - last_order_date DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_stats
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score + f_score + m_score AS rfm_score
FROM rfm_scored
ORDER BY rfm_score DESC
LIMIT 20;


-- =========================================================
-- Q5. City tier contribution to revenue (% of total)
-- =========================================================
WITH tier_revenue AS (
    SELECT
        c.city_tier,
        SUM(o.net_amount) AS revenue
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.city_tier
)
SELECT
    city_tier,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS pct_of_total_revenue
FROM tier_revenue
ORDER BY revenue DESC;


-- =========================================================
-- Q6. Repeat purchase rate: % of customers with more than 1 delivered order
-- =========================================================
WITH order_counts AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS orders_count
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE orders_count > 1) AS repeat_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE orders_count > 1) / COUNT(*), 2) AS repeat_purchase_rate_pct
FROM order_counts;
