CREATE TABLE IF NOT EXISTS analytics.anomaly_root_causes (
    root_cause_id BIGSERIAL PRIMARY KEY,

    anomaly_date DATE NOT NULL,

    signal_type VARCHAR(50) NOT NULL,
    signal_direction VARCHAR(20),

    dimension_type VARCHAR(50) NOT NULL,
    contributor_id VARCHAR(100),
    contributor_name VARCHAR(255) NOT NULL,

    metric_name VARCHAR(100) NOT NULL,
    actual_value NUMERIC(18, 4),
    baseline_value NUMERIC(18, 4),
    absolute_change NUMERIC(18, 4),
    percentage_change NUMERIC(18, 4),

    contributor_rank INTEGER NOT NULL,

    baseline_window_days INTEGER NOT NULL DEFAULT 28,

    analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomaly_root_causes_date
    ON analytics.anomaly_root_causes(anomaly_date);

CREATE INDEX IF NOT EXISTS idx_anomaly_root_causes_signal
    ON analytics.anomaly_root_causes(signal_type);

CREATE INDEX IF NOT EXISTS idx_anomaly_root_causes_dimension
    ON analytics.anomaly_root_causes(dimension_type);

CREATE INDEX IF NOT EXISTS idx_anomaly_root_causes_date_signal
    ON analytics.anomaly_root_causes(
        anomaly_date,
        signal_type
    );