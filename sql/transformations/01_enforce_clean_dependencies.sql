BEGIN;

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'orders',
    o.order_id,
    'customers',
    o.customer_id,
    'Customer excluded from clean layer'
FROM clean.orders o
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.customers c
    WHERE c.customer_id = o.customer_id
);

DELETE FROM clean.orders o
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.customers c
    WHERE c.customer_id = o.customer_id
);

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'order_items',
    oi.order_item_id,
    'orders',
    oi.order_id,
    'Order excluded from clean layer'
FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = oi.order_id
);

DELETE FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = oi.order_id
);

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'order_items',
    oi.order_item_id,
    'products',
    oi.product_id,
    'Product excluded from clean layer'
FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.products p
    WHERE p.product_id = oi.product_id
);

DELETE FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.products p
    WHERE p.product_id = oi.product_id
);

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'payments',
    p.payment_id,
    'orders',
    p.order_id,
    'Order excluded from clean layer'
FROM clean.payments p
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = p.order_id
);

DELETE FROM clean.payments p
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = p.order_id
);

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'returns',
    r.return_id,
    'order_items',
    r.order_item_id,
    'Order item excluded from clean layer'
FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.order_items oi
    WHERE oi.order_item_id = r.order_item_id
);

DELETE FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.order_items oi
    WHERE oi.order_item_id = r.order_item_id
);

INSERT INTO quality.dependency_exclusions (
    run_id,
    table_name,
    record_identifier,
    parent_table,
    parent_identifier,
    exclusion_reason
)
SELECT
    %(run_id)s,
    'returns',
    r.return_id,
    'orders',
    r.order_id,
    'Order excluded from clean layer'
FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = r.order_id
);

DELETE FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = r.order_id
);

COMMIT;