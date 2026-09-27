from src.reliability.metric_reliability import (
    run_metric_reliability_analysis,
    add_reliability_status,
)
import pandas as pd

def test_metric_reliability_analysis_returns_expected_structure():
    """Metric reliability analysis should cover all configured KPIs."""

    dependency_df, reliability_df = (
        run_metric_reliability_analysis()
    )

    assert len(dependency_df) == 14
    assert len(reliability_df) == 5

    assert reliability_df["kpi_name"].nunique() == 5

    assert reliability_df["reliability_score"].isna().sum() == 0

    assert reliability_df["reliability_status"].isna().sum() == 0

def test_metric_reliability_scores_match_verified_results():
    """KPI reliability scores should match the verified audit results."""

    _, reliability_df = run_metric_reliability_analysis()

    scores = reliability_df.set_index(
        "kpi_name"
    )["reliability_score"].to_dict()

    assert scores["Revenue"] == 99.68
    assert scores["Order Volume"] == 99.92
    assert scores["Average Order Value"] == 99.74
    assert scores["Gross Profit"] == 99.68
    assert scores["Return Rate"] == 99.15

def test_reliability_status_thresholds():
    """Reliability status should follow the configured thresholds."""

    test_df = pd.DataFrame(
        {
            "kpi_name": [
                "Trusted KPI",
                "Monitor KPI",
                "At Risk KPI",
            ],
            "reliability_score": [
                99.80,
                99.50,
                98.99,
            ],
            "rules_monitored": [
                1,
                1,
                1,
            ],
        }
    )

    result_df = add_reliability_status(
        test_df
    )

    statuses = result_df.set_index(
        "kpi_name"
    )["reliability_status"].to_dict()

    assert statuses["Trusted KPI"] == "Trusted"
    assert statuses["Monitor KPI"] == "Monitor"
    assert statuses["At Risk KPI"] == "At Risk"