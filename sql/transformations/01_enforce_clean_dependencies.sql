BEGIN;

DELETE FROM clean.orders o
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.customers c
    WHERE c.customer_id = o.customer_id
);

DELETE FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = oi.order_id
);

DELETE FROM clean.order_items oi
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.products p
    WHERE p.product_id = oi.product_id
);

DELETE FROM clean.payments p
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = p.order_id
);

DELETE FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.order_items oi
    WHERE oi.order_item_id = r.order_item_id
);

DELETE FROM clean.returns r
WHERE NOT EXISTS (
    SELECT 1
    FROM clean.orders o
    WHERE o.order_id = r.order_id
);

COMMIT;