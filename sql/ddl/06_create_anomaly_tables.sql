CREATE TABLE IF NOT EXISTS analytics.daily_anomalies (
    anomaly_date DATE PRIMARY KEY,

    order_count INTEGER NOT NULL,
    net_sales NUMERIC(14, 2) NOT NULL,
    average_order_value NUMERIC(14, 2),

    sales_rolling_mean NUMERIC(14, 2),
    sales_z_score NUMERIC(12, 6),
    sales_deviation_pct NUMERIC(12, 4),
    is_sales_anomaly BOOLEAN NOT NULL,

    order_count_rolling_mean NUMERIC(14, 4),
    order_count_z_score NUMERIC(12, 6),
    is_order_volume_anomaly BOOLEAN NOT NULL,

    aov_rolling_mean NUMERIC(14, 2),
    aov_z_score NUMERIC(12, 6),
    is_aov_anomaly BOOLEAN NOT NULL,

    is_any_anomaly BOOLEAN NOT NULL,

    anomaly_direction VARCHAR(20),
    anomaly_severity VARCHAR(20),

    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_anomalies_any
    ON analytics.daily_anomalies(is_any_anomaly);

CREATE INDEX IF NOT EXISTS idx_daily_anomalies_date
    ON analytics.daily_anomalies(anomaly_date);