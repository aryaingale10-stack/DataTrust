from pathlib import Path

import pandas as pd

from src.quality.quality_engine import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "dashboard_exports"
)


POWERBI_VIEWS = [
    "pbi_anomaly_root_causes",
    "pbi_business_anomalies",
    "pbi_business_impact",
    "pbi_channel_performance",
    "pbi_customer_performance",
    "pbi_data_quality_overview",
    "pbi_executive_monthly",
    "pbi_metric_reliability",
    "pbi_product_performance",
    "pbi_quality_dimensions",
    "pbi_quality_rules",
    "pbi_regional_performance",
    "pbi_returns_performance",
    "pbi_table_quality",
]


def export_dashboard_data():
    """Export Power BI reporting views to CSV files."""

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    exported_files = []

    with engine.connect() as connection:
        for view_name in POWERBI_VIEWS:
            query = f"SELECT * FROM analytics.{view_name}"

            dataframe = pd.read_sql_query(
                query,
                connection,
            )

            output_path = EXPORT_DIR / f"{view_name}.csv"

            dataframe.to_csv(
                output_path,
                index=False,
            )

            exported_files.append(output_path)

            print(
                f"Exported {view_name}: "
                f"{len(dataframe):,} rows"
            )

    print(
        f"\nDashboard exports completed: "
        f"{len(exported_files)} files"
    )

    return exported_files


if __name__ == "__main__":
    export_dashboard_data()