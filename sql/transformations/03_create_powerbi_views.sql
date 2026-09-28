-- ============================================================
-- DATATRUST: POWER BI REPORTING VIEWS
-- View 1: Executive Monthly Trends
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_executive_monthly;

CREATE VIEW analytics.pbi_executive_monthly AS

WITH monthly_sales AS (
    SELECT
        d.year,
        d.quarter,
        d.month_number,
        d.month_name,
        d.year_month,
        DATE_TRUNC('month', d.date_key)::DATE AS month_start_date,

        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS total_customers,
        SUM(f.quantity) AS units_sold,

        ROUND(SUM(f.gross_sales), 2) AS gross_sales,
        ROUND(SUM(f.discount_amount), 2) AS discount_amount,
        ROUND(SUM(f.net_sales), 2) AS net_sales,
        ROUND(SUM(f.total_cost), 2) AS total_cost,
        ROUND(SUM(f.gross_profit), 2) AS gross_profit,

        ROUND(
            SUM(f.net_sales)
            / NULLIF(COUNT(DISTINCT f.order_id), 0),
            2
        ) AS average_order_value,

        ROUND(
            SUM(f.gross_profit)
            / NULLIF(SUM(f.net_sales), 0) * 100,
            2
        ) AS gross_margin_pct

    FROM analytics.fact_sales AS f

    INNER JOIN analytics.dim_date AS d
        ON f.date_key = d.date_key

    GROUP BY
        d.year,
        d.quarter,
        d.month_number,
        d.month_name,
        d.year_month,
        DATE_TRUNC('month', d.date_key)::DATE
),

monthly_growth AS (
    SELECT
        *,

        LAG(net_sales, 1) OVER (
            ORDER BY month_start_date
        ) AS previous_month_sales,

        LAG(net_sales, 12) OVER (
            ORDER BY month_start_date
        ) AS previous_year_sales

    FROM monthly_sales
)

SELECT
    year,
    quarter,
    month_number,
    month_name,
    year_month,
    month_start_date,

    total_orders,
    total_customers,
    units_sold,

    gross_sales,
    discount_amount,
    net_sales,
    total_cost,
    gross_profit,

    average_order_value,
    gross_margin_pct,

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

FROM monthly_growth;

-- ============================================================
-- View 2: Sales Channel Performance
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_channel_performance;

CREATE VIEW analytics.pbi_channel_performance AS

SELECT
    sales_channel,

    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(quantity) AS units_sold,

    ROUND(SUM(gross_sales), 2) AS gross_sales,
    ROUND(SUM(discount_amount), 2) AS discount_amount,
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
    ) AS gross_margin_pct,

    ROUND(
        SUM(net_sales)
        / NULLIF(SUM(SUM(net_sales)) OVER (), 0) * 100,
        2
    ) AS revenue_share_pct

FROM analytics.fact_sales

GROUP BY sales_channel;

-- ============================================================
-- View 3: Regional Performance
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_regional_performance;

CREATE VIEW analytics.pbi_regional_performance AS

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
    ) AS gross_margin_pct,

    ROUND(
        SUM(net_sales)
        / NULLIF(SUM(SUM(net_sales)) OVER (), 0) * 100,
        2
    ) AS revenue_share_pct

FROM analytics.fact_sales

GROUP BY shipping_region;

-- ============================================================
-- View 4: Product Performance
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_product_performance;

CREATE VIEW analytics.pbi_product_performance AS

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,

    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_id) AS total_customers,
    SUM(f.quantity) AS units_sold,

    ROUND(SUM(f.gross_sales), 2) AS gross_sales,
    ROUND(SUM(f.discount_amount), 2) AS discount_amount,
    ROUND(SUM(f.net_sales), 2) AS net_sales,
    ROUND(SUM(f.total_cost), 2) AS total_cost,
    ROUND(SUM(f.gross_profit), 2) AS gross_profit,

    ROUND(
        SUM(f.gross_profit)
        / NULLIF(SUM(f.net_sales), 0) * 100,
        2
    ) AS gross_margin_pct,

    DENSE_RANK() OVER (
        ORDER BY SUM(f.net_sales) DESC
    ) AS overall_revenue_rank,

    DENSE_RANK() OVER (
        PARTITION BY p.category
        ORDER BY SUM(f.net_sales) DESC
    ) AS category_revenue_rank

FROM analytics.fact_sales AS f

INNER JOIN analytics.dim_product AS p
    ON f.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand;

-- ============================================================
-- View 5: Customer Performance
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_customer_performance;

CREATE VIEW analytics.pbi_customer_performance AS

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.city,
    c.state,
    c.region,

    MIN(f.date_key) AS first_purchase_date,
    MAX(f.date_key) AS last_purchase_date,

    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.date_key) AS active_days,
    SUM(f.quantity) AS units_purchased,

    ROUND(SUM(f.net_sales), 2) AS lifetime_revenue,
    ROUND(SUM(f.gross_profit), 2) AS lifetime_profit,

    ROUND(
        SUM(f.net_sales)
        / NULLIF(COUNT(DISTINCT f.order_id), 0),
        2
    ) AS average_order_value,

    ROUND(
        SUM(f.gross_profit)
        / NULLIF(SUM(f.net_sales), 0) * 100,
        2
    ) AS gross_margin_pct,

    CASE
        WHEN COUNT(DISTINCT f.order_id) = 1
            THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END AS customer_type

FROM analytics.fact_sales AS f

INNER JOIN analytics.dim_customer AS c
    ON f.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.city,
    c.state,
    c.region;

-- ============================================================
-- View 6: Returns Performance
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_returns_performance;

CREATE VIEW analytics.pbi_returns_performance AS

SELECT
    p.category,
    p.subcategory,
    r.return_reason,

    COUNT(DISTINCT r.return_id) AS total_returns,
    COUNT(DISTINCT r.order_id) AS affected_orders,
    COUNT(DISTINCT r.customer_id) AS affected_customers,

    SUM(r.return_quantity) AS returned_units,

    ROUND(
        SUM(r.refund_amount),
        2
    ) AS refund_amount,

    ROUND(
        SUM(r.returned_sales_value),
        2
    ) AS returned_sales_value,

    ROUND(
        AVG(r.refund_amount),
        2
    ) AS average_refund_amount

FROM analytics.fact_returns AS r

INNER JOIN analytics.dim_product AS p
    ON r.product_id = p.product_id

GROUP BY
    p.category,
    p.subcategory,
    r.return_reason;

-- ============================================================
-- View 7: Data Quality Overview
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_data_quality_overview;

CREATE VIEW analytics.pbi_data_quality_overview AS

SELECT
    a.run_id,
    a.run_timestamp,
    a.rules_configured,
    a.rules_executed,
    a.run_status,
    o.quality_score,

    CASE
        WHEN o.quality_score >= 99.90 THEN 'Excellent'
        WHEN o.quality_score >= 99.50 THEN 'Good'
        WHEN o.quality_score >= 99.00 THEN 'Monitor'
        ELSE 'Needs Attention'
    END AS quality_status

FROM quality.audit_runs AS a

INNER JOIN quality.overall_scores AS o
    ON a.run_id = o.run_id;

-- ============================================================
-- View 8: Data Quality Dimension Scores
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_quality_dimensions;

CREATE VIEW analytics.pbi_quality_dimensions AS

SELECT
    d.run_id,
    a.run_timestamp,
    a.run_status,
    d.dimension,
    d.quality_score,

    CASE
        WHEN d.quality_score >= 99.90 THEN 'Excellent'
        WHEN d.quality_score >= 99.50 THEN 'Good'
        WHEN d.quality_score >= 99.00 THEN 'Monitor'
        ELSE 'Needs Attention'
    END AS quality_status

FROM quality.dimension_scores AS d

INNER JOIN quality.audit_runs AS a
    ON d.run_id = a.run_id;

-- ============================================================
-- View 9: Table-Level Data Quality Scores
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_table_quality;

CREATE VIEW analytics.pbi_table_quality AS

SELECT
    t.run_id,
    a.run_timestamp,
    a.run_status,
    t.table_name,
    t.quality_score,

    CASE
        WHEN t.quality_score >= 99.90 THEN 'Excellent'
        WHEN t.quality_score >= 99.50 THEN 'Good'
        WHEN t.quality_score >= 99.00 THEN 'Monitor'
        ELSE 'Needs Attention'
    END AS quality_status

FROM quality.table_scores AS t

INNER JOIN quality.audit_runs AS a
    ON t.run_id = a.run_id;

-- ============================================================
-- View 10: Rule-Level Data Quality Results
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_quality_rules;

CREATE VIEW analytics.pbi_quality_rules AS

SELECT
    r.run_id,
    a.run_timestamp,
    a.run_status,

    r.rule_id,
    r.rule_name,
    r.table_name,
    r.dimension,
    r.severity,

    r.total_records,
    r.evaluated_records,
    r.skipped_records,
    r.passed_records,
    r.failed_records,
    r.pass_rate,

    ROUND(
        r.failed_records::NUMERIC
        / NULLIF(r.evaluated_records, 0) * 100,
        2
    ) AS failure_rate_pct,

    CASE
        WHEN r.failed_records = 0 THEN 'Passed'
        ELSE 'Failed'
    END AS rule_status

FROM quality.rule_results AS r

INNER JOIN quality.audit_runs AS a
    ON r.run_id = a.run_id;

-- ============================================================
-- View 11: KPI Metric Reliability
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_metric_reliability;

CREATE VIEW analytics.pbi_metric_reliability AS

SELECT
    kpi_name,
    reliability_score,
    rules_monitored,
    reliability_status,
    analyzed_at,

    CASE
        WHEN reliability_status = 'Trusted' THEN 1
        WHEN reliability_status = 'Monitor' THEN 2
        ELSE 3
    END AS status_sort_order

FROM analytics.metric_reliability;

-- ============================================================
-- View 12: Business Anomalies / Incidents
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_business_anomalies;

CREATE VIEW analytics.pbi_business_anomalies AS

SELECT
    anomaly_date,
    order_count,
    net_sales,
    average_order_value,

    sales_rolling_mean,
    sales_z_score,
    sales_deviation_pct,
    is_sales_anomaly,

    order_count_rolling_mean,
    order_count_z_score,
    is_order_volume_anomaly,

    aov_rolling_mean,
    aov_z_score,
    is_aov_anomaly,

    is_any_anomaly,
    anomaly_direction,
    anomaly_severity,
    detected_at,

    CASE
        WHEN is_sales_anomaly THEN 1
        ELSE 0
    END AS sales_anomaly_flag,

    CASE
        WHEN is_order_volume_anomaly THEN 1
        ELSE 0
    END AS order_volume_anomaly_flag,

    CASE
        WHEN is_aov_anomaly THEN 1
        ELSE 0
    END AS aov_anomaly_flag

FROM analytics.daily_anomalies;

-- ============================================================
-- View 13: Anomaly Root-Cause Diagnostics
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_anomaly_root_causes;

CREATE VIEW analytics.pbi_anomaly_root_causes AS

SELECT
    r.root_cause_id,
    r.anomaly_date,

    r.signal_type,
    r.signal_direction,

    r.dimension_type,
    r.contributor_id,
    r.contributor_name,

    r.metric_name,
    r.actual_value,
    r.baseline_value,
    r.absolute_change,
    r.percentage_change,

    r.contributor_rank,
    r.baseline_window_days,
    r.analyzed_at,

    a.anomaly_severity,
    a.is_sales_anomaly,
    a.is_order_volume_anomaly,
    a.is_aov_anomaly

FROM analytics.anomaly_root_causes AS r

INNER JOIN analytics.daily_anomalies AS a
    ON r.anomaly_date = a.anomaly_date;

-- ============================================================
-- View 14: Business Impact of Detected Anomalies
-- ============================================================

DROP VIEW IF EXISTS analytics.pbi_business_impact;

CREATE VIEW analytics.pbi_business_impact AS

SELECT
    anomaly_date,

    net_sales,
    expected_sales,
    revenue_impact,
    revenue_impact_pct,
    revenue_impact_direction,

    order_count,
    expected_order_count,
    order_volume_impact,
    order_volume_impact_pct,
    order_volume_impact_direction,

    average_order_value,
    expected_aov,
    aov_impact,
    aov_impact_pct,
    aov_impact_direction,

    business_impact_magnitude,

    is_sales_anomaly,
    is_order_volume_anomaly,
    is_aov_anomaly,

    analyzed_at,

    ABS(revenue_impact) AS absolute_revenue_impact,

    CASE
        WHEN revenue_impact > 0 THEN 'Above Baseline'
        WHEN revenue_impact < 0 THEN 'Below Baseline'
        ELSE 'At Baseline'
    END AS revenue_baseline_status

FROM analytics.business_impact;