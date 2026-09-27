CREATE TABLE IF NOT EXISTS analytics.metric_reliability (
    kpi_name VARCHAR(100) PRIMARY KEY,

    reliability_score NUMERIC(6, 2) NOT NULL,
    rules_monitored INTEGER NOT NULL,
    reliability_status VARCHAR(20) NOT NULL,

    analyzed_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metric_reliability_status
    ON analytics.metric_reliability(reliability_status);