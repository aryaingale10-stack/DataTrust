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

KPI_DEPENDENCIES = {
    "Revenue": [
        ("order_items", "quantity"),
        ("order_items", "unit_price"),
        ("order_items", "discount_pct"),
    ],
    "Order Volume": [
        ("orders", "order_id"),
    ],
    "Average Order Value": [
        ("orders", "order_id"),
        ("order_items", "quantity"),
        ("order_items", "unit_price"),
        ("order_items", "discount_pct"),
    ],
    "Gross Profit": [
        ("order_items", "quantity"),
        ("order_items", "unit_price"),
        ("order_items", "discount_pct"),
        ("order_items", "unit_cost"),
    ],
    "Return Rate": [
        ("returns", "return_quantity"),
        ("order_items", "quantity"),
    ],
}

DEPENDENCY_RULE_MAP = {
    ("order_items", "quantity"): [
        "ITEM_001",
    ],
    ("order_items", "unit_price"): [
        "ITEM_004",
    ],
    ("order_items", "discount_pct"): [
        "ITEM_003",
    ],
    ("order_items", "unit_cost"): [
        "ITEM_004",
    ],
    ("orders", "order_id"): [
        "ORD_005",
    ],
    ("returns", "return_quantity"): [
        "RET_001",
    ],
}

def build_kpi_dependency_dataframe():
    """Convert KPI dependency definitions into a structured DataFrame."""

    dependency_rows = []

    for kpi_name, dependencies in KPI_DEPENDENCIES.items():
        for table_name, column_name in dependencies:
            dependency_rows.append(
                {
                    "kpi_name": kpi_name,
                    "source_table": table_name,
                    "source_column": column_name,
                }
            )

    return pd.DataFrame(dependency_rows)

def attach_quality_rules_to_dependencies(
    dependency_df
):
    """Attach relevant data quality rule IDs to KPI dependencies."""

    result_df = dependency_df.copy()

    result_df["quality_rule_ids"] = result_df.apply(
        lambda row: DEPENDENCY_RULE_MAP.get(
            (
                row["source_table"],
                row["source_column"],
            ),
            [],
        ),
        axis=1,
    )

    return result_df

def load_latest_quality_rule_results():
    """Load rule results from the latest successful quality audit."""

    query = text(
        """
        SELECT
            rr.run_id,
            rr.rule_id,
            rr.table_name,
            rr.dimension,
            rr.severity,
            rr.evaluated_records,
            rr.failed_records,
            rr.pass_rate
        FROM quality.rule_results AS rr
        INNER JOIN quality.audit_runs AS ar
            ON rr.run_id = ar.run_id
        WHERE ar.run_status = 'SUCCESS'
          AND rr.run_id = (
              SELECT MAX(run_id)
              FROM quality.audit_runs
              WHERE run_status = 'SUCCESS'
          )
        ORDER BY rr.rule_id;
        """
    )

    with engine.connect() as connection:
        rule_results = pd.read_sql(
            query,
            connection,
        )

    return rule_results

def attach_rule_results_to_dependencies(
    dependency_df,
    rule_results_df,
):
    """Attach latest quality audit performance to KPI dependencies."""

    expanded_df = dependency_df.explode(
        "quality_rule_ids"
    ).rename(
        columns={
            "quality_rule_ids": "rule_id"
        }
    )

    result_df = expanded_df.merge(
        rule_results_df[
            [
                "run_id",
                "rule_id",
                "dimension",
                "severity",
                "evaluated_records",
                "failed_records",
                "pass_rate",
            ]
        ],
        on="rule_id",
        how="left",
    )

    return result_df

def calculate_kpi_reliability_scores(
    dependency_results_df,
):
    """Calculate reliability scores for each KPI."""

    unique_rule_results = dependency_results_df[
        [
            "kpi_name",
            "rule_id",
            "pass_rate",
        ]
    ].drop_duplicates()

    reliability_df = (
        unique_rule_results
        .groupby(
            "kpi_name",
            as_index=False,
        )
        .agg(
            reliability_score=(
                "pass_rate",
                "mean",
            ),
            rules_monitored=(
                "rule_id",
                "nunique",
            ),
        )
    )

    reliability_df["reliability_score"] = (
        reliability_df["reliability_score"]
        .round(2)
    )

    return reliability_df

def add_reliability_status(
    reliability_df,
):
    """Assign an interpretable status to each KPI reliability score."""

    result_df = reliability_df.copy()

    result_df["reliability_status"] = "At Risk"

    result_df.loc[
        result_df["reliability_score"] >= 99.0,
        "reliability_status",
    ] = "Monitor"

    result_df.loc[
        result_df["reliability_score"] >= 99.8,
        "reliability_status",
    ] = "Trusted"

    return result_df

def run_metric_reliability_analysis():
    """Run the complete KPI metric reliability analysis."""

    dependency_df = build_kpi_dependency_dataframe()

    dependency_df = attach_quality_rules_to_dependencies(
        dependency_df
    )

    rule_results_df = load_latest_quality_rule_results()

    dependency_results_df = attach_rule_results_to_dependencies(
        dependency_df,
        rule_results_df,
    )

    reliability_df = calculate_kpi_reliability_scores(
        dependency_results_df
    )

    reliability_df = add_reliability_status(
        reliability_df
    )

    return dependency_results_df, reliability_df

def save_metric_reliability_results(
    reliability_df,
):
    """Persist the current KPI reliability snapshot."""

    storage_df = reliability_df[
        [
            "kpi_name",
            "reliability_score",
            "rules_monitored",
            "reliability_status",
        ]
    ].copy()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE analytics.metric_reliability;
                """
            )
        )

        storage_df.to_sql(
            "metric_reliability",
            connection,
            schema="analytics",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

    return len(storage_df)

def run_and_save_metric_reliability_analysis():
    """Run KPI reliability analysis and persist the current snapshot."""

    dependency_results_df, reliability_df = (
        run_metric_reliability_analysis()
    )

    rows_saved = save_metric_reliability_results(
        reliability_df
    )

    return (
        dependency_results_df,
        reliability_df,
        rows_saved,
    )