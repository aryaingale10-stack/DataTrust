CREATE TABLE IF NOT EXISTS analytics.business_impact (
    anomaly_date DATE PRIMARY KEY,

    net_sales NUMERIC(14, 2),
    expected_sales NUMERIC(14, 2),
    revenue_impact NUMERIC(14, 2),
    revenue_impact_pct NUMERIC(12, 4),
    revenue_impact_direction VARCHAR(30),

    order_count INTEGER,
    expected_order_count NUMERIC(14, 4),
    order_volume_impact NUMERIC(14, 4),
    order_volume_impact_pct NUMERIC(12, 4),
    order_volume_impact_direction VARCHAR(30),

    average_order_value NUMERIC(14, 2),
    expected_aov NUMERIC(14, 2),
    aov_impact NUMERIC(14, 2),
    aov_impact_pct NUMERIC(12, 4),
    aov_impact_direction VARCHAR(30),

    business_impact_magnitude VARCHAR(20),

    is_sales_anomaly BOOLEAN NOT NULL,
    is_order_volume_anomaly BOOLEAN NOT NULL,
    is_aov_anomaly BOOLEAN NOT NULL,

    analyzed_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_business_impact_magnitude
    ON analytics.business_impact(business_impact_magnitude);

CREATE INDEX IF NOT EXISTS idx_business_impact_revenue_direction
    ON analytics.business_impact(revenue_impact_direction);

CREATE INDEX IF NOT EXISTS idx_business_impact_anomaly_date
    ON analytics.business_impact(anomaly_date);