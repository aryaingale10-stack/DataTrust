import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Check the .env file."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

def load_anomaly_days():
    """Load detected anomaly days for business impact analysis."""

    query = text(
        """
        SELECT
            anomaly_date,
            order_count,
            order_count_rolling_mean,
            net_sales,
            average_order_value,
            aov_rolling_mean,
            sales_rolling_mean,
            sales_z_score,
            sales_deviation_pct,
            is_sales_anomaly,
            is_order_volume_anomaly,
            is_aov_anomaly
        FROM analytics.daily_anomalies
        WHERE is_any_anomaly = TRUE
        ORDER BY anomaly_date;
        """
    )

    with engine.connect() as connection:
        anomaly_days = pd.read_sql(
            query,
            connection,
        )

    return anomaly_days

def add_revenue_impact(anomaly_df):
    """Estimate revenue impact relative to the rolling sales baseline."""

    result = anomaly_df.copy()

    result["expected_sales"] = result[
        "sales_rolling_mean"
    ]

    result["revenue_impact"] = (
        result["net_sales"]
        - result["expected_sales"]
    )

    result["absolute_revenue_impact"] = (
        result["revenue_impact"].abs()
    )

    return result

def add_revenue_impact_direction(impact_df):
    """Classify whether revenue is above or below its baseline."""

    result = impact_df.copy()

    result["revenue_impact_direction"] = "Above Baseline"

    result.loc[
        result["revenue_impact"] < 0,
        "revenue_impact_direction"
    ] = "Below Baseline"

    result.loc[
        result["revenue_impact"] == 0,
        "revenue_impact_direction"
    ] = "At Baseline"

    return result

def add_order_volume_impact(impact_df):
    """Estimate order-volume impact relative to the rolling baseline."""

    result = impact_df.copy()

    result["expected_order_count"] = result[
        "order_count_rolling_mean"
    ]

    result["order_volume_impact"] = (
        result["order_count"]
        - result["expected_order_count"]
    )

    result["absolute_order_volume_impact"] = (
        result["order_volume_impact"].abs()
    )

    return result

def add_order_volume_impact_direction(impact_df):
    """Classify whether order volume is above or below its baseline."""

    result = impact_df.copy()

    result["order_volume_impact_direction"] = "Above Baseline"

    result.loc[
        result["order_volume_impact"] < 0,
        "order_volume_impact_direction"
    ] = "Below Baseline"

    result.loc[
        result["order_volume_impact"] == 0,
        "order_volume_impact_direction"
    ] = "At Baseline"

    return result

def add_aov_impact(impact_df):
    """Estimate AOV impact relative to the rolling baseline."""

    result = impact_df.copy()

    result["expected_aov"] = result[
        "aov_rolling_mean"
    ]

    result["aov_impact"] = (
        result["average_order_value"]
        - result["expected_aov"]
    )

    result["absolute_aov_impact"] = (
        result["aov_impact"].abs()
    )

    return result

def add_aov_impact_direction(impact_df):
    """Classify whether AOV is above or below its baseline."""

    result = impact_df.copy()

    result["aov_impact_direction"] = "Above Baseline"

    result.loc[
        result["aov_impact"] < 0,
        "aov_impact_direction"
    ] = "Below Baseline"

    result.loc[
        result["aov_impact"] == 0,
        "aov_impact_direction"
    ] = "At Baseline"

    return result

def run_business_impact_analysis():
    """Run the complete business impact analysis workflow."""

    impact_df = load_anomaly_days()

    impact_df = add_revenue_impact(
        impact_df
    )

    impact_df = add_revenue_impact_direction(
        impact_df
    )

    impact_df = add_order_volume_impact(
        impact_df
    )

    impact_df = add_order_volume_impact_direction(
        impact_df
    )

    impact_df = add_aov_impact(
        impact_df
    )

    impact_df = add_aov_impact_direction(
        impact_df
    )

    impact_df = add_impact_percentages(
        impact_df
    )
    impact_df = add_business_impact_magnitude(
        impact_df
    ) 

    return impact_df

def summarize_business_impact(impact_df):
    """Create a high-level summary of anomaly-related business impact."""

    summary = {
        "anomaly_days": int(len(impact_df)),

        "above_baseline_revenue": float(round(
            impact_df.loc[
                impact_df["revenue_impact"] > 0,
                "revenue_impact"
            ].sum(),
            2,
        )),

        "below_baseline_revenue": float(round(
            impact_df.loc[
                impact_df["revenue_impact"] < 0,
                "revenue_impact"
            ].sum(),
            2,
        )),

        "absolute_revenue_deviation": float(round(
            impact_df[
                "absolute_revenue_impact"
            ].sum(),
            2,
        )),

        "above_baseline_orders": float(round(
            impact_df.loc[
                impact_df["order_volume_impact"] > 0,
                "order_volume_impact"
            ].sum(),
            2,
        )),

        "below_baseline_orders": float(round(
            impact_df.loc[
                impact_df["order_volume_impact"] < 0,
                "order_volume_impact"
            ].sum(),
            2,
        )),
        "critical_impact_days": int(
    (
        impact_df["business_impact_magnitude"]
        == "Critical"
        ).sum()
),

       "high_impact_days": int(
    (
        impact_df["business_impact_magnitude"]
        == "High"
        ).sum()
),

       "moderate_impact_days": int(
    (
        impact_df["business_impact_magnitude"]
        == "Moderate"
       ).sum()
),

      "low_impact_days": int(
    (
        impact_df["business_impact_magnitude"]
        == "Low"
        ).sum()
),
    }

    return summary

def add_impact_percentages(impact_df):
    """Calculate percentage deviations from expected business baselines."""

    result = impact_df.copy()

    result["revenue_impact_pct"] = (
        result["revenue_impact"]
        / result["expected_sales"]
        * 100
    )

    result["order_volume_impact_pct"] = (
        result["order_volume_impact"]
        / result["expected_order_count"]
        * 100
    )

    result["aov_impact_pct"] = (
        result["aov_impact"]
        / result["expected_aov"]
        * 100
    )

    return result

def add_business_impact_magnitude(impact_df):
    """Classify business impact using absolute revenue deviation."""

    result = impact_df.copy()

    absolute_pct = result[
        "revenue_impact_pct"
    ].abs()

    result["business_impact_magnitude"] = "Low"

    result.loc[
        absolute_pct >= 20,
        "business_impact_magnitude"
    ] = "Moderate"

    result.loc[
        absolute_pct >= 40,
        "business_impact_magnitude"
    ] = "High"

    result.loc[
        absolute_pct >= 60,
        "business_impact_magnitude"
    ] = "Critical"

    return result

def prepare_impact_results_for_storage(impact_df):
    """Prepare business impact results for database persistence."""

    storage_df = impact_df[
        [
            "anomaly_date",
            "net_sales",
            "expected_sales",
            "revenue_impact",
            "revenue_impact_pct",
            "revenue_impact_direction",
            "order_count",
            "expected_order_count",
            "order_volume_impact",
            "order_volume_impact_pct",
            "order_volume_impact_direction",
            "average_order_value",
            "expected_aov",
            "aov_impact",
            "aov_impact_pct",
            "aov_impact_direction",
            "business_impact_magnitude",
            "is_sales_anomaly",
            "is_order_volume_anomaly",
            "is_aov_anomaly",
        ]
    ].copy()

    return storage_df

def save_business_impact_results(impact_df):
    """Save the current business impact snapshot to PostgreSQL."""

    storage_df = prepare_impact_results_for_storage(
        impact_df
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE analytics.business_impact;
                """
            )
        )

        storage_df.to_sql(
            name="business_impact",
            con=connection,
            schema="analytics",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

    return len(storage_df)

def run_and_save_business_impact_analysis():
    """Run business impact analysis and persist the current snapshot."""

    impact_df = run_business_impact_analysis()

    rows_saved = save_business_impact_results(
        impact_df
    )

    summary = summarize_business_impact(
        impact_df
    )

    return impact_df, rows_saved, summary