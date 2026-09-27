from pathlib import Path

from sqlalchemy import text

from src.quality.quality_engine import (
    calculate_dimension_scores,
    calculate_overall_score,
    calculate_table_scores,
    complete_audit_run,
    count_quality_rules,
    create_audit_run,
    engine,
    fail_audit_run,
    load_quality_rules,
    run_supported_quality_rules,
    save_dimension_scores,
    save_issue_details,
    save_overall_score,
    save_rule_results,
    save_table_scores,
)

from src.quality.quarantine_engine import (
    save_all_flagged_records,
    save_all_trusted_records,
)

from src.quality.clean_validator import (
    get_clean_layer_summary,
    validate_clean_layer,
)
from src.quality.reconciliation import (
    print_reconciliation_report,
    validate_reconciliation,
)

from src.anomaly.anomaly_detector import (
    run_complete_anomaly_detection,
    save_anomaly_results,
)

from src.root_cause.root_cause_analyzer import (
    run_root_cause_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEPENDENCY_SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "transformations"
    / "01_enforce_clean_dependencies.sql"
)

def enforce_clean_dependencies(run_id):
    """Remove records from the clean layer that have invalid dependencies."""

    sql_script = DEPENDENCY_SQL_PATH.read_text()

    raw_connection = engine.raw_connection()

    try:
        cursor = raw_connection.cursor()
        cursor.execute(
          sql_script,
          {"run_id": run_id}
)
        raw_connection.commit()
        cursor.close()

    except Exception:
        raw_connection.rollback()
        raise

    finally:
        raw_connection.close()


def run_quality_audit():
    """Run the full data quality audit and return the audit run ID."""

    quality_rules = load_quality_rules()
    rules_configured = count_quality_rules(quality_rules)

    print("\n[1/8] Running data quality audit...")
    print(f"Configured rules: {rules_configured}")

    run_id = create_audit_run(rules_configured)

    try:
        results = run_supported_quality_rules(quality_rules)

        save_rule_results(run_id, results)
        save_issue_details(run_id, results)

        table_scores = calculate_table_scores(results)
        dimension_scores = calculate_dimension_scores(results)
        overall_score = calculate_overall_score(results)

        save_table_scores(run_id, table_scores)
        save_dimension_scores(run_id, dimension_scores)
        save_overall_score(run_id, overall_score)

        complete_audit_run(
            run_id,
            len(results),
            rules_configured
        )

        print(f"Audit Run ID: {run_id}")
        print(f"Rules executed: {len(results)}")
        print(f"Overall Quality Score: {overall_score}%")

        return run_id

    except Exception:
        fail_audit_run(run_id)
        raise

def build_clean_and_quarantine_layers(run_id):
    """Build quarantine and first-pass clean layers for an audit run."""

    print("\n[2/8] Saving flagged records to quarantine...")

    quarantine_counts = save_all_flagged_records(run_id)

    print("Quarantine layer completed.")

    print("\n[3/8] Loading trusted records into clean layer...")

    clean_counts = save_all_trusted_records(run_id)

    print("First-pass clean layer completed.")

    return quarantine_counts, clean_counts

def run_dependency_cleanup(run_id):
    """Enforce dependency integrity across the clean data layer."""

    print("\n[4/8] Enforcing clean-layer dependencies...")

    enforce_clean_dependencies(run_id)

    print("Dependency cleanup completed.")

def run_clean_validation():
    """Validate the final clean layer and return validation results."""

    print("\n[5/8] Validating final clean layer...")

    validation_results = validate_clean_layer()
    clean_summary = get_clean_layer_summary()

    if not validation_results["overall_passed"]:
        raise RuntimeError(
            "Clean-layer validation failed. "
            "Check primary-key and referential-integrity results."
        )

    print("Clean-layer validation passed.")

    return validation_results, clean_summary

def run_reconciliation(run_id):
    """Validate that all raw records are accounted for."""

    
    print("\n[6/8] Reconciling source-to-final record counts...")
    result = validate_reconciliation(run_id)
    print_reconciliation_report(run_id)

    print("Data reconciliation passed.")

    return result

def run_pipeline():
    """Run the complete DataTrust data quality pipeline."""

    print("=" * 70)
    print("DATATRUST DATA QUALITY PIPELINE")
    print("=" * 70)

    # Stage 1: Run data quality audit.
    run_id = run_quality_audit()

    # Stages 2 and 3: Build quarantine and first-pass clean layers.
    build_clean_and_quarantine_layers(run_id)

    # Stage 4: Remove dependency-propagated invalid records.
    run_dependency_cleanup(run_id)

    # Stage 5: Validate the final clean layer.
    validation_results, clean_summary = run_clean_validation()

    # Stage 6: Reconcile source-to-final record counts.
    reconciliation_result = run_reconciliation(run_id)

    # Stage 7: Run business anomaly detection.
    print("\n[7/8] Running business anomaly detection...")

    anomaly_results = run_complete_anomaly_detection()

    anomaly_rows_saved = save_anomaly_results(
        anomaly_results
    )

    anomaly_days = int(
        anomaly_results["is_any_anomaly"].sum()
    )

    print(f"Daily observations analyzed: {len(anomaly_results):,}")
    print(f"Anomaly days detected:       {anomaly_days:,}")
    print(f"Anomaly rows saved:          {anomaly_rows_saved:,}")
    print("Anomaly detection completed.")

    print("\n[8/8] Running anomaly root-cause analysis...")

    root_cause_results, root_cause_rows_saved = (
    run_root_cause_analysis()
)

    print(
    f"Root-cause rows generated: "
    f"{len(root_cause_results):,}"
)
    print(
    f"Root-cause rows saved:     "
    f"{root_cause_rows_saved:,}"
)

    if len(root_cause_results) != root_cause_rows_saved:
     raise ValueError(
        "Root-cause persistence validation failed."
    )

    print("Root-cause analysis completed.")
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(f"Audit Run ID: {run_id}")

    return {
        "run_id": run_id,
        "validation_results": validation_results,
        "clean_summary": clean_summary,
        "reconciliation_result": reconciliation_result,
        "anomaly_results": anomaly_results,
        "anomaly_rows_saved": anomaly_rows_saved,
        "root_cause_results": root_cause_results,
        "root_cause_rows_saved": root_cause_rows_saved,
    }

if __name__ == "__main__":
    run_pipeline()