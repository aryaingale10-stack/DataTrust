CREATE TABLE IF NOT EXISTS quality.dependency_exclusions (
    exclusion_id BIGSERIAL PRIMARY KEY,

    run_id BIGINT NOT NULL,

    table_name VARCHAR(100) NOT NULL,
    record_identifier VARCHAR(255) NOT NULL,

    parent_table VARCHAR(100) NOT NULL,
    parent_identifier VARCHAR(255) NOT NULL,

    exclusion_reason VARCHAR(255) NOT NULL,

    excluded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dependency_exclusions_run
        FOREIGN KEY (run_id)
        REFERENCES quality.audit_runs(run_id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_dependency_exclusions_run_id
    ON quality.dependency_exclusions(run_id);


CREATE INDEX IF NOT EXISTS idx_dependency_exclusions_table_name
    ON quality.dependency_exclusions(table_name);


CREATE INDEX IF NOT EXISTS idx_dependency_exclusions_record_identifier
    ON quality.dependency_exclusions(record_identifier);