DROP TABLE IF EXISTS analytics.dim_customer CASCADE;

CREATE TABLE analytics.dim_customer AS
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    city,
    state,
    region,
    customer_segment,
    signup_date
FROM clean.customers;

ALTER TABLE analytics.dim_customer
    ADD CONSTRAINT pk_dim_customer
    PRIMARY KEY (customer_id);

DROP TABLE IF EXISTS analytics.dim_product CASCADE;

CREATE TABLE analytics.dim_product AS
SELECT
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_cost,
    unit_price,
    supplier_id,
    launch_date,
    product_status
FROM clean.products;

ALTER TABLE analytics.dim_product
    ADD CONSTRAINT pk_dim_product
    PRIMARY KEY (product_id);

DROP TABLE IF EXISTS analytics.dim_date CASCADE;

CREATE TABLE analytics.dim_date AS
SELECT
    calendar_date::DATE AS date_key,
    EXTRACT(YEAR FROM calendar_date)::INTEGER AS year,
    EXTRACT(QUARTER FROM calendar_date)::INTEGER AS quarter,
    EXTRACT(MONTH FROM calendar_date)::INTEGER AS month_number,
    TO_CHAR(calendar_date, 'Month') AS month_name,
    TO_CHAR(calendar_date, 'YYYY-MM') AS year_month,
    EXTRACT(DAY FROM calendar_date)::INTEGER AS day_of_month,
    EXTRACT(ISODOW FROM calendar_date)::INTEGER AS day_of_week,
    TO_CHAR(calendar_date, 'Day') AS day_name,
    CASE
        WHEN EXTRACT(ISODOW FROM calendar_date) IN (6, 7)
            THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM generate_series(
    DATE '2023-01-01',
    DATE '2026-01-31',
    INTERVAL '1 day'
) AS calendar_date;

ALTER TABLE analytics.dim_date
    ADD CONSTRAINT pk_dim_date
    PRIMARY KEY (date_key);

DROP TABLE IF EXISTS analytics.fact_sales CASCADE;

CREATE TABLE analytics.fact_sales AS
SELECT
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    oi.product_id,
    o.order_date AS date_key,
    o.sales_channel,
    o.order_status,
    o.payment_method,
    o.shipping_city,
    o.shipping_state,
    o.shipping_region,

    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    oi.unit_cost,

    ROUND(
        oi.quantity * oi.unit_price,
        2
    ) AS gross_sales,

    ROUND(
        oi.quantity * oi.unit_price * oi.discount_pct,
        2
    ) AS discount_amount,

    ROUND(
        oi.quantity * oi.unit_price
        * (1 - oi.discount_pct),
        2
    ) AS net_sales,

    ROUND(
        oi.quantity * oi.unit_cost,
        2
    ) AS total_cost,

    ROUND(
        (
            oi.quantity * oi.unit_price
            * (1 - oi.discount_pct)
        )
        - (oi.quantity * oi.unit_cost),
        2
    ) AS gross_profit

FROM clean.order_items AS oi
INNER JOIN clean.orders AS o
    ON oi.order_id = o.order_id;

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT pk_fact_sales
    PRIMARY KEY (order_item_id);

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT fk_fact_sales_customer
    FOREIGN KEY (customer_id)
    REFERENCES analytics.dim_customer(customer_id);

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT fk_fact_sales_product
    FOREIGN KEY (product_id)
    REFERENCES analytics.dim_product(product_id);

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT fk_fact_sales_date
    FOREIGN KEY (date_key)
    REFERENCES analytics.dim_date(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_date
    ON analytics.fact_sales(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_sales_customer
    ON analytics.fact_sales(customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_product
    ON analytics.fact_sales(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_order
    ON analytics.fact_sales(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_region
    ON analytics.fact_sales(shipping_region);

DROP TABLE IF EXISTS analytics.fact_returns CASCADE;

CREATE TABLE analytics.fact_returns AS
SELECT
    r.return_id,
    r.order_id,
    r.order_item_id,
    o.customer_id,
    oi.product_id,
    r.return_date AS date_key,

    r.return_quantity,
    r.return_reason,
    r.refund_amount,

    oi.unit_price,

    ROUND(
        r.return_quantity * oi.unit_price,
        2
    ) AS returned_sales_value

FROM clean.returns AS r
INNER JOIN clean.orders AS o
    ON r.order_id = o.order_id
INNER JOIN clean.order_items AS oi
    ON r.order_item_id = oi.order_item_id;

ALTER TABLE analytics.fact_returns
    ADD CONSTRAINT pk_fact_returns
    PRIMARY KEY (return_id);

ALTER TABLE analytics.fact_returns
    ADD CONSTRAINT fk_fact_returns_customer
    FOREIGN KEY (customer_id)
    REFERENCES analytics.dim_customer(customer_id);

ALTER TABLE analytics.fact_returns
    ADD CONSTRAINT fk_fact_returns_product
    FOREIGN KEY (product_id)
    REFERENCES analytics.dim_product(product_id);

ALTER TABLE analytics.fact_returns
    ADD CONSTRAINT fk_fact_returns_date
    FOREIGN KEY (date_key)
    REFERENCES analytics.dim_date(date_key);

ALTER TABLE analytics.fact_returns
    ADD CONSTRAINT fk_fact_returns_sales_item
    FOREIGN KEY (order_item_id)
    REFERENCES analytics.fact_sales(order_item_id);

CREATE INDEX IF NOT EXISTS idx_fact_returns_date
    ON analytics.fact_returns(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_returns_customer
    ON analytics.fact_returns(customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_returns_product
    ON analytics.fact_returns(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_returns_order
    ON analytics.fact_returns(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_returns_sales_item
    ON analytics.fact_returns(order_item_id);

DROP VIEW IF EXISTS analytics.vw_daily_sales_kpis;

CREATE VIEW analytics.vw_daily_sales_kpis AS
SELECT
    d.date_key,
    d.year,
    d.quarter,
    d.month_number,
    d.month_name,
    d.year_month,

    COUNT(DISTINCT f.order_id) AS order_count,
    COUNT(DISTINCT f.customer_id) AS customer_count,

    SUM(f.quantity) AS units_sold,

    ROUND(
        SUM(f.gross_sales),
        2
    ) AS gross_sales,

    ROUND(
        SUM(f.discount_amount),
        2
    ) AS discount_amount,

    ROUND(
        SUM(f.net_sales),
        2
    ) AS net_sales,

    ROUND(
        SUM(f.total_cost),
        2
    ) AS total_cost,

    ROUND(
        SUM(f.gross_profit),
        2
    ) AS gross_profit,

    ROUND(
        SUM(f.net_sales)
        / NULLIF(COUNT(DISTINCT f.order_id), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales AS f
INNER JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key

GROUP BY
    d.date_key,
    d.year,
    d.quarter,
    d.month_number,
    d.month_name,
    d.year_month;

DROP VIEW IF EXISTS analytics.vw_product_performance;

CREATE VIEW analytics.vw_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,

    COUNT(DISTINCT f.order_id) AS order_count,
    COUNT(DISTINCT f.customer_id) AS customer_count,

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

    ROUND(
        SUM(f.net_sales)
        / NULLIF(SUM(f.quantity), 0),
        2
    ) AS revenue_per_unit

FROM analytics.fact_sales AS f
INNER JOIN analytics.dim_product AS p
    ON f.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand;

DROP VIEW IF EXISTS analytics.vw_customer_performance;

CREATE VIEW analytics.vw_customer_performance AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.customer_segment,
    c.city,
    c.state,
    c.region,

    COUNT(DISTINCT f.order_id) AS order_count,

    COUNT(DISTINCT f.date_key) AS active_days,

    SUM(f.quantity) AS units_purchased,

    ROUND(SUM(f.net_sales), 2) AS net_sales,

    ROUND(SUM(f.total_cost), 2) AS total_cost,

    ROUND(SUM(f.gross_profit), 2) AS gross_profit,

    ROUND(
        SUM(f.gross_profit)
        / NULLIF(SUM(f.net_sales), 0) * 100,
        2
    ) AS gross_margin_pct,

    ROUND(
        SUM(f.net_sales)
        / NULLIF(COUNT(DISTINCT f.order_id), 0),
        2
    ) AS average_order_value

FROM analytics.fact_sales AS f
INNER JOIN analytics.dim_customer AS c
    ON f.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.customer_segment,
    c.city,
    c.state,
    c.region;

DROP VIEW IF EXISTS analytics.vw_returns_performance;

CREATE VIEW analytics.vw_returns_performance AS
SELECT
    d.date_key,
    d.year,
    d.quarter,
    d.month_number,
    d.month_name,
    d.year_month,

    COUNT(DISTINCT r.return_id) AS return_count,

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
    ) AS returned_sales_value

FROM analytics.fact_returns AS r
INNER JOIN analytics.dim_date AS d
    ON r.date_key = d.date_key

GROUP BY
    d.date_key,
    d.year,
    d.quarter,
    d.month_number,
    d.month_name,
    d.year_month;

DROP VIEW IF EXISTS analytics.vw_executive_kpis;

CREATE VIEW analytics.vw_executive_kpis AS
SELECT
    sales.total_orders,
    sales.total_customers,
    sales.total_units_sold,
    sales.total_net_sales,
    sales.total_gross_profit,

    ROUND(
        sales.total_gross_profit
        / NULLIF(sales.total_net_sales, 0) * 100,
        2
    ) AS gross_margin_pct,

    ROUND(
        sales.total_net_sales
        / NULLIF(sales.total_orders, 0),
        2
    ) AS average_order_value,

    returns.total_returns,
    returns.total_returned_units,
    returns.total_refund_amount,
    returns.total_returned_sales_value,

    ROUND(
        returns.total_returns::NUMERIC
        / NULLIF(sales.total_orders, 0) * 100,
        2
    ) AS return_rate_pct

FROM (
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(net_sales), 2) AS total_net_sales,
        ROUND(SUM(gross_profit), 2) AS total_gross_profit
    FROM analytics.fact_sales
) AS sales

CROSS JOIN (
    SELECT
        COUNT(DISTINCT return_id) AS total_returns,
        SUM(return_quantity) AS total_returned_units,
        ROUND(SUM(refund_amount), 2) AS total_refund_amount,
        ROUND(SUM(returned_sales_value), 2) AS total_returned_sales_value
    FROM analytics.fact_returns
) AS returns;