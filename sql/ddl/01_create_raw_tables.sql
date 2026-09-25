-- =========================================================
-- DataTrust
-- Raw Layer Database Schema
-- =========================================================

-- ---------------------------------------------------------
-- RAW CUSTOMERS
-- Source: data/incoming/customers.csv
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id        VARCHAR(20),
    first_name         VARCHAR(100),
    last_name          VARCHAR(100),
    email              VARCHAR(255),
    phone              VARCHAR(50),
    city               VARCHAR(100),
    state              VARCHAR(100),
    region             VARCHAR(50),
    customer_segment   VARCHAR(50),
    signup_date        DATE
);
-- ---------------------------------------------------------
-- RAW PRODUCTS
-- Source: data/incoming/products.xlsx
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.products (
    product_id       VARCHAR(20),
    product_name     VARCHAR(255),
    category         VARCHAR(100),
    subcategory      VARCHAR(100),
    brand            VARCHAR(100),
    unit_cost        NUMERIC(12, 2),
    unit_price       NUMERIC(12, 2),
    supplier_id      VARCHAR(20),
    launch_date      DATE,
    product_status   VARCHAR(50)
);
-- ---------------------------------------------------------
-- RAW ORDERS
-- Source: data/incoming/orders.csv
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id          VARCHAR(20),
    customer_id       VARCHAR(20),
    order_date        DATE,
    sales_channel     VARCHAR(50),
    order_status      VARCHAR(50),
    payment_method    VARCHAR(50),
    shipping_city     VARCHAR(100),
    shipping_state    VARCHAR(100),
    shipping_region   VARCHAR(50)
);

-- ---------------------------------------------------------
-- RAW ORDER ITEMS
-- Source: data/incoming/order_items.csv
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id   VARCHAR(20),
    order_id        VARCHAR(20),
    product_id      VARCHAR(20),
    quantity        INTEGER,
    unit_price      NUMERIC(12, 2),
    discount_pct    NUMERIC(6, 4),
    unit_cost       NUMERIC(12, 2)
);

-- ---------------------------------------------------------
-- RAW PAYMENTS
-- Source: data/incoming/payments.csv
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.payments (
    payment_id       VARCHAR(20),
    order_id         VARCHAR(20),
    payment_date     DATE,
    payment_method   VARCHAR(50),
    payment_status   VARCHAR(50),
    payment_amount   NUMERIC(14, 2)
);

-- ---------------------------------------------------------
-- RAW RETURNS
-- Source: data/incoming/returns.csv
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw.returns (
    return_id         VARCHAR(20),
    order_item_id     VARCHAR(20),
    order_id          VARCHAR(20),
    product_id        VARCHAR(20),
    return_date       DATE,
    return_quantity   INTEGER,
    return_reason     VARCHAR(100),
    refund_amount     NUMERIC(14, 2)
);
