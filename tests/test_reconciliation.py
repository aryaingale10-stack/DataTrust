from src.quality.reconciliation import (
    get_raw_record_count,
    get_clean_record_count,
    get_quarantine_record_count,
    get_dependency_exclusion_count,
    reconcile_run,
    validate_reconciliation,
)


def test_run_9_reconciles():
    """Run 9 should account for every raw source record."""

    result = reconcile_run(9)

    assert result["raw_records"] == 606279
    assert result["final_clean_records"] == 571133
    assert result["direct_quarantine_records"] == 8252
    assert result["dependency_exclusions"] == 26894
    assert result["accounted_records"] == 606279
    assert result["difference"] == 0
    assert result["reconciled"] is True

def test_validate_reconciliation_passes_for_balanced_run():
    """Validator should return a reconciled result for a balanced run."""

    result = validate_reconciliation(9)

    assert result["difference"] == 0
    assert result["reconciled"] is True

def test_reconciliation_component_counts():
    """Individual reconciliation components should match verified Run 9 counts."""

    assert get_raw_record_count() == 606279
    assert get_clean_record_count() == 571133
    assert get_quarantine_record_count(9) == 8252
    assert get_dependency_exclusion_count(9) == 26894