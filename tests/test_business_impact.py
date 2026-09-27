from src.impact.impact_analyzer import (
    run_business_impact_analysis,
    summarize_business_impact,
    prepare_impact_results_for_storage,
)

def test_business_impact_analysis_returns_all_anomaly_days():
    """Business impact analysis should cover every detected anomaly day."""

    impact_df = run_business_impact_analysis()

    assert len(impact_df) == 27

    assert impact_df["anomaly_date"].nunique() == 27

    assert impact_df["anomaly_date"].isna().sum() == 0

def test_business_impact_summary_matches_verified_results():
    """Business impact summary should match verified pipeline results."""

    impact_df = run_business_impact_analysis()

    summary = summarize_business_impact(
        impact_df
    )

    assert summary["anomaly_days"] == 27
    assert summary["critical_impact_days"] == 1
    assert summary["high_impact_days"] == 5
    assert summary["moderate_impact_days"] == 16
    assert summary["low_impact_days"] == 5

    assert (
        summary["absolute_revenue_deviation"]
        == 1667897.78
    )

def test_business_impact_storage_structure():
    """Storage-ready impact results should have the expected structure."""

    impact_df = run_business_impact_analysis()

    storage_df = prepare_impact_results_for_storage(
        impact_df
    )

    assert storage_df.shape == (27, 20)

    assert set(storage_df["business_impact_magnitude"]) == {
        "Low",
        "Moderate",
        "High",
        "Critical",
    }

    assert storage_df["anomaly_date"].nunique() == 27

    assert storage_df["revenue_impact"].isna().sum() == 0
    assert storage_df["order_volume_impact"].isna().sum() == 0
    assert storage_df["aov_impact"].isna().sum() == 0

