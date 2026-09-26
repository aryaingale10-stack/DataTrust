CREATE TABLE IF NOT EXISTS quarantine.customers (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    customer_id VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    region VARCHAR(50),
    customer_segment VARCHAR(50),
    signup_date DATE,

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_customers_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarantine.products (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    product_id VARCHAR(20),
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_cost NUMERIC(12,2),
    unit_price NUMERIC(12,2),
    supplier_id VARCHAR(20),
    launch_date DATE,
    product_status VARCHAR(50),

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_products_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarantine.orders (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    order_id VARCHAR(20),
    customer_id VARCHAR(20),
    order_date DATE,
    sales_channel VARCHAR(50),
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_region VARCHAR(50),

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_orders_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarantine.order_items (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    order_item_id VARCHAR(20),
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    discount_pct NUMERIC(6,4),
    unit_cost NUMERIC(12,2),

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_order_items_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarantine.payments (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    payment_id VARCHAR(20),
    order_id VARCHAR(20),
    payment_date DATE,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    payment_amount NUMERIC(14,2),

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_payments_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quarantine.returns (
    quarantine_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,

    return_id VARCHAR(20),
    order_item_id VARCHAR(20),
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    return_date DATE,
    return_quantity INTEGER,
    return_reason VARCHAR(100),
    refund_amount NUMERIC(14,2),

    quarantined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_returns_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quarantine_customers_run_id
ON quarantine.customers(run_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_products_run_id
ON quarantine.products(run_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_orders_run_id
ON quarantine.orders(run_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_order_items_run_id
ON quarantine.order_items(run_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_payments_run_id
ON quarantine.payments(run_id);

CREATE INDEX IF NOT EXISTS idx_quarantine_returns_run_id
ON quarantine.returns(run_id);