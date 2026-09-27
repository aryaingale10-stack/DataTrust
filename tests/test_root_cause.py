from src.root_cause.root_cause_analyzer import (
    build_root_cause_rows,
    build_all_root_cause_rows,
    get_aov_analysis_direction,
)


def test_combined_sales_and_aov_anomaly_builds_expected_rows():
    """A multi-signal anomaly should preserve both analyses."""

    rows = build_root_cause_rows("2023-08-15")

    assert len(rows) == 5

    assert set(rows["signal_type"]) == {
        "Sales",
        "Average Order Value",
    }

    assert (
        len(rows[rows["signal_type"] == "Sales"])
        == 4
    )

    assert (
        len(
            rows[
                rows["signal_type"]
                == "Average Order Value"
            ]
        )
        == 1
    )


def test_aov_direction_handles_high_low_and_non_aov():
    """AOV direction should distinguish high, low, and non-AOV dates."""

    assert (
        get_aov_analysis_direction("2023-11-26")
        == "positive"
    )

    assert (
        get_aov_analysis_direction("2024-10-04")
        == "negative"
    )

    assert (
        get_aov_analysis_direction("2023-04-02")
        is None
    )


def test_all_root_cause_rows_have_expected_structure():
    """All detected anomalies should produce normalized root-cause rows."""

    rows = build_all_root_cause_rows()

    assert len(rows) == 82

    assert set(rows["signal_type"]) == {
        "Sales",
        "Order Volume",
        "Average Order Value",
    }

    assert set(rows["dimension_type"]) == {
        "Channel",
        "Region",
        "Category",
        "Product",
    }

    assert rows["anomaly_date"].nunique() == 27