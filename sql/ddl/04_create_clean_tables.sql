CREATE TABLE IF NOT EXISTS clean.customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    region VARCHAR(50),
    customer_segment VARCHAR(50),
    signup_date DATE
);
CREATE TABLE IF NOT EXISTS clean.products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_cost NUMERIC(12,2),
    unit_price NUMERIC(12,2),
    supplier_id VARCHAR(20),
    launch_date DATE,
    product_status VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS clean.orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    order_date DATE,
    sales_channel VARCHAR(50),
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_region VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS clean.order_items (
    order_item_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    discount_pct NUMERIC(6,4),
    unit_cost NUMERIC(12,2)
);
CREATE TABLE IF NOT EXISTS clean.payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20),
    payment_date DATE,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    payment_amount NUMERIC(14,2)
);
CREATE TABLE IF NOT EXISTS clean.returns (
    return_id VARCHAR(20) PRIMARY KEY,
    order_item_id VARCHAR(20),
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    return_date DATE,
    return_quantity INTEGER,
    return_reason VARCHAR(100),
    refund_amount NUMERIC(14,2)
);
CREATE INDEX IF NOT EXISTS idx_clean_orders_customer_id
ON clean.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_clean_order_items_order_id
ON clean.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_clean_order_items_product_id
ON clean.order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_clean_payments_order_id
ON clean.payments(order_id);

CREATE INDEX IF NOT EXISTS idx_clean_returns_order_item_id
ON clean.returns(order_item_id);

CREATE INDEX IF NOT EXISTS idx_clean_returns_order_id
ON clean.returns(order_id);

CREATE INDEX IF NOT EXISTS idx_clean_returns_product_id
ON clean.returns(product_id);