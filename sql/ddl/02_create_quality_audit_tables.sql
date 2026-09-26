CREATE SCHEMA IF NOT EXISTS quality;

CREATE TABLE IF NOT EXISTS quality.audit_runs (
    run_id BIGSERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rules_configured INTEGER NOT NULL,
    rules_executed INTEGER NOT NULL,
    run_status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS quality.rule_results (
    result_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,
    rule_id VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    dimension VARCHAR(100) NOT NULL,
    total_records BIGINT NOT NULL,
    evaluated_records BIGINT NOT NULL,
    skipped_records BIGINT NOT NULL,
    passed_records BIGINT NOT NULL,
    failed_records BIGINT NOT NULL,
    pass_rate NUMERIC(6,2) NOT NULL,

    CONSTRAINT fk_rule_results_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rule_results_run_id
ON quality.rule_results(run_id);

CREATE TABLE IF NOT EXISTS quality.table_scores (
    score_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    quality_score NUMERIC(6,2) NOT NULL,

    CONSTRAINT fk_table_scores_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_table_scores_run_table
        UNIQUE (run_id, table_name)
);

CREATE TABLE IF NOT EXISTS quality.dimension_scores (
    score_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL,
    dimension VARCHAR(100) NOT NULL,
    quality_score NUMERIC(6,2) NOT NULL,

    CONSTRAINT fk_dimension_scores_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_dimension_scores_run_dimension
        UNIQUE (run_id, dimension)
);

CREATE TABLE IF NOT EXISTS quality.overall_scores (
    score_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL UNIQUE,
    quality_score NUMERIC(6,2) NOT NULL,

    CONSTRAINT fk_overall_scores_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_table_scores_run_id
ON quality.table_scores(run_id);

CREATE INDEX IF NOT EXISTS idx_dimension_scores_run_id
ON quality.dimension_scores(run_id);