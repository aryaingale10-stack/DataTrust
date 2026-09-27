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


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEPENDENCY_SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "transformations"
    / "01_enforce_clean_dependencies.sql"
)

def enforce_clean_dependencies():
    """Remove records from the clean layer that have invalid dependencies."""

    sql_script = DEPENDENCY_SQL_PATH.read_text()

    raw_connection = engine.raw_connection()

    try:
        cursor = raw_connection.cursor()
        cursor.execute(sql_script)
        raw_connection.commit()
        cursor.close()

    except Exception:
        raw_connection.rollback()
        raise

    finally:
        raw_connection.close()

def enforce_clean_dependencies():
    """Remove records from the clean layer that have invalid dependencies."""

    sql_script = DEPENDENCY_SQL_PATH.read_text()

    raw_connection = engine.raw_connection()

    try:
        cursor = raw_connection.cursor()
        cursor.execute(sql_script)
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

    print("\n[1/5] Running data quality audit...")
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

    print("\n[2/5] Saving flagged records to quarantine...")

    quarantine_counts = save_all_flagged_records(run_id)

    print("Quarantine layer completed.")

    print("\n[3/5] Loading trusted records into clean layer...")

    clean_counts = save_all_trusted_records(run_id)

    print("First-pass clean layer completed.")

    return quarantine_counts, clean_counts

def run_dependency_cleanup():
    """Enforce dependency integrity across the clean data layer."""

    print("\n[4/5] Enforcing clean-layer dependencies...")

    enforce_clean_dependencies()

    print("Dependency cleanup completed.")

def run_clean_validation():
    """Validate the final clean layer and return validation results."""

    print("\n[5/5] Validating final clean layer...")

    validation_results = validate_clean_layer()
    clean_summary = get_clean_layer_summary()

    if not validation_results["overall_passed"]:
        raise RuntimeError(
            "Clean-layer validation failed. "
            "Check primary-key and referential-integrity results."
        )

    print("Clean-layer validation passed.")

    return validation_results, clean_summary

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
    run_dependency_cleanup()

    # Stage 5: Validate the final clean layer.
    validation_results, clean_summary = run_clean_validation()

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(f"Audit Run ID: {run_id}")

    return {
        "run_id": run_id,
        "validation_results": validation_results,
        "clean_summary": clean_summary,
    }


if __name__ == "__main__":
    run_pipeline()