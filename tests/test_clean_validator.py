
from src.quality.clean_validator import (
    validate_primary_keys,
    validate_referential_integrity,
    validate_clean_layer,
)

def test_clean_primary_keys_are_unique():
    """Final clean tables should contain no duplicate primary keys."""

    results = validate_primary_keys()

    for table_name, metrics in results.items():
        assert metrics["duplicate_ids"] == 0, (
            f"{table_name} contains "
            f"{metrics['duplicate_ids']} duplicate primary keys"
        )

        assert metrics["passed"] is True, (
            f"Primary-key validation failed for {table_name}"
        )

def test_clean_referential_integrity():
    """Final clean tables should contain no orphaned foreign-key relationships."""

    results = validate_referential_integrity()

    for relationship, metrics in results.items():
        assert metrics["orphan_rows"] == 0, (
            f"{relationship} contains "
            f"{metrics['orphan_rows']} orphaned records"
        )

        assert metrics["passed"] is True, (
            f"Referential-integrity validation failed for {relationship}"
        )

def test_clean_layer_overall_validation_passes():
    """Final clean layer should pass all integrity validations."""

    result = validate_clean_layer()

    assert result["overall_passed"] is True