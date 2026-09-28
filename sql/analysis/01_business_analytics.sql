-- ============================================================
-- DATATRUST: ADVANCED BUSINESS ANALYTICS
-- Analysis 1: Monthly Revenue & Growth Trends
-- ============================================================

WITH monthly_sales AS (
    SELECT
        d.year,
        d.month_number,
        d.month_name,
        d.year_month,

        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS total_customers,
        SUM(f.quantity) AS units_sold,

        ROUND(SUM(f.net_sales), 2) AS net_sales,
        ROUND(SUM(f.gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(f.net_sales)
            / NULLIF(COUNT(DISTINCT f.order_id), 0),
            2
        ) AS average_order_value

    FROM analytics.fact_sales AS f
    INNER JOIN analytics.dim_date AS d
        ON f.date_key = d.date_key

    GROUP BY
        d.year,
        d.month_number,
        d.month_name,
        d.year_month
),

growth_analysis AS (
    SELECT
        *,

        LAG(net_sales, 1) OVER (
            ORDER BY year, month_number
        ) AS previous_month_sales,

        LAG(net_sales, 12) OVER (
            ORDER BY year, month_number
        ) AS previous_year_sales

    FROM monthly_sales
)

SELECT
    year,
    month_number,
    month_name,
    year_month,
    total_orders,
    total_customers,
    units_sold,
    net_sales,
    gross_profit,
    average_order_value,

    ROUND(
        (net_sales - previous_month_sales)
        / NULLIF(previous_month_sales, 0) * 100,
        2
    ) AS mom_revenue_growth_pct,

    ROUND(
        (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0) * 100,
        2
    ) AS yoy_revenue_growth_pct

FROM growth_analysis

ORDER BY
    year,
    month_number;

-- ============================================================
-- Analysis 2: Product & Category Profitability
-- ============================================================

WITH category_performance AS (
    SELECT
        p.category,
        p.subcategory,

        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.product_id) AS products_sold,
        SUM(f.quantity) AS units_sold,

        ROUND(SUM(f.net_sales), 2) AS net_sales,
        ROUND(SUM(f.gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(f.gross_profit)
            / NULLIF(SUM(f.net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales AS f
    INNER JOIN analytics.dim_product AS p
        ON f.product_id = p.product_id

    GROUP BY
        p.category,
        p.subcategory
),

ranked_categories AS (
    SELECT
        *,

        DENSE_RANK() OVER (
            ORDER BY net_sales DESC
        ) AS revenue_rank,

        DENSE_RANK() OVER (
            ORDER BY gross_profit DESC
        ) AS profit_rank

    FROM category_performance
)

SELECT
    category,
    subcategory,
    total_orders,
    products_sold,
    units_sold,
    net_sales,
    gross_profit,
    gross_margin_pct,
    revenue_rank,
    profit_rank

FROM ranked_categories

ORDER BY revenue_rank;

-- ============================================================
-- Analysis 3: Sales Channel Performance
-- ============================================================

WITH channel_performance AS (
    SELECT
        sales_channel,

        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(quantity) AS units_sold,

        ROUND(SUM(net_sales), 2) AS net_sales,
        ROUND(SUM(gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(net_sales)
            / NULLIF(COUNT(DISTINCT order_id), 0),
            2
        ) AS average_order_value,

        ROUND(
            SUM(gross_profit)
            / NULLIF(SUM(net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales

    GROUP BY sales_channel
)

SELECT
    *,
    
    ROUND(
        net_sales
        / NULLIF(SUM(net_sales) OVER (), 0) * 100,
        2
    ) AS revenue_share_pct,

    DENSE_RANK() OVER (
        ORDER BY net_sales DESC
    ) AS revenue_rank

FROM channel_performance

ORDER BY revenue_rank;

-- ============================================================
-- Analysis 4: Regional Performance
-- ============================================================

WITH regional_performance AS (
    SELECT
        shipping_region,

        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(quantity) AS units_sold,

        ROUND(SUM(net_sales), 2) AS net_sales,
        ROUND(SUM(gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(net_sales)
            / NULLIF(COUNT(DISTINCT order_id), 0),
            2
        ) AS average_order_value,

        ROUND(
            SUM(gross_profit)
            / NULLIF(SUM(net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales

    GROUP BY shipping_region
)

SELECT
    shipping_region,
    total_orders,
    total_customers,
    units_sold,
    net_sales,
    gross_profit,
    average_order_value,
    gross_margin_pct,

    ROUND(
        net_sales
        / NULLIF(SUM(net_sales) OVER (), 0) * 100,
        2
    ) AS revenue_share_pct,

    DENSE_RANK() OVER (
        ORDER BY net_sales DESC
    ) AS revenue_rank

FROM regional_performance

ORDER BY revenue_rank;

-- ============================================================
-- Analysis 5: Discount Impact on Revenue & Profitability
-- ============================================================

WITH discount_analysis AS (
    SELECT
        CASE
            WHEN discount_pct = 0 THEN 'No Discount'
            WHEN discount_pct <= 0.10 THEN 'Low Discount (1-10%)'
            WHEN discount_pct <= 0.20 THEN 'Medium Discount (11-20%)'
            ELSE 'High Discount (>20%)'
        END AS discount_band,

        CASE
            WHEN discount_pct = 0 THEN 1
            WHEN discount_pct <= 0.10 THEN 2
            WHEN discount_pct <= 0.20 THEN 3
            ELSE 4
        END AS discount_band_order,

        COUNT(DISTINCT order_id) AS total_orders,
        SUM(quantity) AS units_sold,

        ROUND(AVG(discount_pct) * 100, 2)
            AS average_discount_pct,

        ROUND(SUM(gross_sales), 2)
            AS gross_sales,

        ROUND(SUM(discount_amount), 2)
            AS discount_amount,

        ROUND(SUM(net_sales), 2)
            AS net_sales,

        ROUND(SUM(gross_profit), 2)
            AS gross_profit,

        ROUND(
            SUM(gross_profit)
            / NULLIF(SUM(net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales

    GROUP BY
        discount_band,
        discount_band_order
)

SELECT
    discount_band,
    total_orders,
    units_sold,
    average_discount_pct,
    gross_sales,
    discount_amount,
    net_sales,
    gross_profit,
    gross_margin_pct

FROM discount_analysis

ORDER BY discount_band_order;

-- ============================================================
-- Analysis 6: Customer Repeat-Purchase Analysis
-- ============================================================

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(net_sales), 2) AS lifetime_revenue,
        ROUND(SUM(gross_profit), 2) AS lifetime_profit
    FROM analytics.fact_sales
    GROUP BY customer_id
),

customer_segments AS (
    SELECT
        customer_id,
        total_orders,
        lifetime_revenue,
        lifetime_profit,

        CASE
            WHEN total_orders = 1 THEN 'One-Time Customer'
            ELSE 'Repeat Customer'
        END AS customer_type

    FROM customer_orders
)

SELECT
    customer_type,

    COUNT(*) AS customer_count,

    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF(SUM(COUNT(*)) OVER (), 0) * 100,
        2
    ) AS customer_share_pct,

    SUM(total_orders) AS total_orders,

    ROUND(SUM(lifetime_revenue), 2)
        AS total_revenue,

    ROUND(AVG(lifetime_revenue), 2)
        AS average_customer_revenue,

    ROUND(SUM(lifetime_profit), 2)
        AS total_profit

FROM customer_segments

GROUP BY customer_type

ORDER BY customer_count DESC;

-- ============================================================
-- Analysis 7: RFM Customer Segmentation
-- ============================================================

WITH customer_rfm AS (
    SELECT
        customer_id,

        (DATE '2026-01-01' - MAX(date_key)) AS recency_days,

        COUNT(DISTINCT order_id) AS frequency,

        ROUND(SUM(net_sales), 2) AS monetary_value

    FROM analytics.fact_sales

    GROUP BY customer_id
),

rfm_scores AS (
    SELECT
        *,

        NTILE(5) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,

        NTILE(5) OVER (
            ORDER BY frequency ASC
        ) AS frequency_score,

        NTILE(5) OVER (
            ORDER BY monetary_value ASC
        ) AS monetary_score

    FROM customer_rfm
),

rfm_segments AS (
    SELECT
        *,

        CASE
            WHEN recency_score >= 4
                 AND frequency_score >= 4
                 AND monetary_score >= 4
                THEN 'Champions'

            WHEN recency_score >= 3
                 AND frequency_score >= 3
                THEN 'Loyal Customers'

            WHEN recency_score >= 4
                 AND frequency_score <= 2
                THEN 'Recent Customers'

            WHEN recency_score <= 2
                 AND frequency_score >= 3
                THEN 'At Risk'

            WHEN recency_score <= 2
                 AND frequency_score <= 2
                THEN 'Inactive'

            ELSE 'Potential Loyalists'
        END AS customer_segment

    FROM rfm_scores
)

SELECT
    customer_segment,

    COUNT(*) AS customer_count,

    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF(SUM(COUNT(*)) OVER (), 0) * 100,
        2
    ) AS customer_share_pct,

    ROUND(AVG(recency_days), 2)
        AS average_recency_days,

    ROUND(AVG(frequency), 2)
        AS average_orders,

    ROUND(AVG(monetary_value), 2)
        AS average_customer_value,

    ROUND(SUM(monetary_value), 2)
        AS total_revenue

FROM rfm_segments

GROUP BY customer_segment

ORDER BY total_revenue DESC;

-- ============================================================
-- Analysis 8: Monthly Customer Cohort Retention
-- ============================================================

WITH customer_monthly_activity AS (
    SELECT DISTINCT
        customer_id,
        DATE_TRUNC('month', date_key)::DATE AS activity_month
    FROM analytics.fact_sales
),

customer_cohorts AS (
    SELECT
        customer_id,
        MIN(activity_month) AS cohort_month
    FROM customer_monthly_activity
    GROUP BY customer_id
),

cohort_activity AS (
    SELECT
        a.customer_id,
        c.cohort_month,
        a.activity_month,

        (
            (EXTRACT(YEAR FROM a.activity_month)
             - EXTRACT(YEAR FROM c.cohort_month)) * 12
            +
            (EXTRACT(MONTH FROM a.activity_month)
             - EXTRACT(MONTH FROM c.cohort_month))
        )::INTEGER AS months_since_first_purchase

    FROM customer_monthly_activity AS a
    INNER JOIN customer_cohorts AS c
        ON a.customer_id = c.customer_id
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),

retention AS (
    SELECT
        cohort_month,
        months_since_first_purchase,
        COUNT(DISTINCT customer_id) AS retained_customers
    FROM cohort_activity
    GROUP BY
        cohort_month,
        months_since_first_purchase
)

SELECT
    r.cohort_month,
    r.months_since_first_purchase,
    c.cohort_size,
    r.retained_customers,

    ROUND(
        r.retained_customers::NUMERIC
        / NULLIF(c.cohort_size, 0) * 100,
        2
    ) AS retention_rate_pct

FROM retention AS r
INNER JOIN cohort_sizes AS c
    ON r.cohort_month = c.cohort_month

ORDER BY
    r.cohort_month,
    r.months_since_first_purchase;

-- ============================================================
-- Analysis 9: Return Rate by Product Category
-- ============================================================

WITH category_sales AS (
    SELECT
        p.category,

        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.net_sales), 2) AS net_sales

    FROM analytics.fact_sales AS f
    INNER JOIN analytics.dim_product AS p
        ON f.product_id = p.product_id

    GROUP BY p.category
),

category_returns AS (
    SELECT
        p.category,

        COUNT(DISTINCT r.return_id) AS total_returns,
        SUM(r.return_quantity) AS returned_units,
        ROUND(SUM(r.refund_amount), 2) AS refund_amount,
        ROUND(SUM(r.returned_sales_value), 2)
            AS returned_sales_value

    FROM analytics.fact_returns AS r
    INNER JOIN analytics.dim_product AS p
        ON r.product_id = p.product_id

    GROUP BY p.category
)

SELECT
    s.category,
    s.units_sold,
    COALESCE(r.returned_units, 0) AS returned_units,

    ROUND(
        COALESCE(r.returned_units, 0)::NUMERIC
        / NULLIF(s.units_sold, 0) * 100,
        2
    ) AS unit_return_rate_pct,

    s.net_sales,

    COALESCE(r.refund_amount, 0)
        AS refund_amount,

    COALESCE(r.returned_sales_value, 0)
        AS returned_sales_value,

    ROUND(
        COALESCE(r.refund_amount, 0)
        / NULLIF(s.net_sales, 0) * 100,
        2
    ) AS refund_to_sales_pct

FROM category_sales AS s
LEFT JOIN category_returns AS r
    ON s.category = r.category

ORDER BY unit_return_rate_pct DESC;

-- ============================================================
-- Analysis 10: Return Reason Analysis
-- ============================================================

WITH return_reason_analysis AS (
    SELECT
        return_reason,

        COUNT(DISTINCT return_id) AS total_returns,
        COUNT(DISTINCT order_id) AS affected_orders,
        SUM(return_quantity) AS returned_units,

        ROUND(SUM(refund_amount), 2)
            AS total_refund_amount,

        ROUND(SUM(returned_sales_value), 2)
            AS returned_sales_value

    FROM analytics.fact_returns

    GROUP BY return_reason
)

SELECT
    return_reason,
    total_returns,
    affected_orders,
    returned_units,
    total_refund_amount,
    returned_sales_value,

    ROUND(
        total_returns::NUMERIC
        / NULLIF(SUM(total_returns) OVER (), 0) * 100,
        2
    ) AS return_share_pct,

    ROUND(
        total_refund_amount
        / NULLIF(SUM(total_refund_amount) OVER (), 0) * 100,
        2
    ) AS refund_share_pct,

    DENSE_RANK() OVER (
        ORDER BY total_refund_amount DESC
    ) AS refund_impact_rank

FROM return_reason_analysis

ORDER BY refund_impact_rank;

-- ============================================================
-- Analysis 11: State-Level Sales Performance
-- ============================================================

WITH state_performance AS (
    SELECT
        shipping_region,
        shipping_state,

        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(quantity) AS units_sold,

        ROUND(SUM(net_sales), 2) AS net_sales,
        ROUND(SUM(gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(net_sales)
            / NULLIF(COUNT(DISTINCT order_id), 0),
            2
        ) AS average_order_value,

        ROUND(
            SUM(gross_profit)
            / NULLIF(SUM(net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales

    GROUP BY
        shipping_region,
        shipping_state
)

SELECT
    shipping_region,
    shipping_state,
    total_orders,
    total_customers,
    units_sold,
    net_sales,
    gross_profit,
    average_order_value,
    gross_margin_pct,

    DENSE_RANK() OVER (
        ORDER BY net_sales DESC
    ) AS overall_revenue_rank,

    DENSE_RANK() OVER (
        PARTITION BY shipping_region
        ORDER BY net_sales DESC
    ) AS regional_revenue_rank

FROM state_performance

ORDER BY
    overall_revenue_rank,
    shipping_state;


-- ============================================================
-- Analysis 12: Top Products Within Each Category
-- ============================================================

WITH product_performance AS (
    SELECT
        p.category,
        p.subcategory,
        p.product_id,
        p.product_name,

        COUNT(DISTINCT f.order_id) AS total_orders,
        SUM(f.quantity) AS units_sold,

        ROUND(SUM(f.net_sales), 2) AS net_sales,
        ROUND(SUM(f.gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(f.gross_profit)
            / NULLIF(SUM(f.net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales AS f
    INNER JOIN analytics.dim_product AS p
        ON f.product_id = p.product_id

    GROUP BY
        p.category,
        p.subcategory,
        p.product_id,
        p.product_name
),

product_rankings AS (
    SELECT
        *,

        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY net_sales DESC
        ) AS category_revenue_rank,

        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY gross_profit DESC
        ) AS category_profit_rank

    FROM product_performance
)

SELECT
    category,
    subcategory,
    product_id,
    product_name,
    total_orders,
    units_sold,
    net_sales,
    gross_profit,
    gross_margin_pct,
    category_revenue_rank,
    category_profit_rank

FROM product_rankings

WHERE category_revenue_rank <= 5

ORDER BY
    category,
    category_revenue_rank,
    product_id;