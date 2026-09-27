import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check the .env file.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
def load_daily_sales():
    """Load daily sales metrics from the trusted clean data layer."""

    query = text(
        """
        SELECT
            o.order_date,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_pct)
            ) AS net_sales
        FROM clean.orders o
        JOIN clean.order_items oi
            ON o.order_id = oi.order_id
        GROUP BY o.order_date
        ORDER BY o.order_date
        """
    )

    with engine.connect() as connection:
        daily_sales = pd.read_sql(query, connection)

    return daily_sales

def add_sales_baseline_features(daily_sales, window=28):
    """Add rolling baseline statistics for daily net sales."""

    df = daily_sales.copy()

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["net_sales"] = pd.to_numeric(df["net_sales"])

    df["rolling_mean"] = (
        df["net_sales"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .mean()
    )

    df["rolling_std"] = (
        df["net_sales"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .std()
    )

    df["sales_z_score"] = (
        (df["net_sales"] - df["rolling_mean"])
        / df["rolling_std"]
    )

    return df

def detect_sales_anomalies(daily_sales, window=28, threshold=3.0):
    """Detect unusual daily sales using a rolling Z-score baseline."""

    df = add_sales_baseline_features(
        daily_sales,
        window=window
    )

    df["is_sales_anomaly"] = (
        df["sales_z_score"].abs() >= threshold
    )

    df["anomaly_direction"] = "Normal"

    df.loc[
        df["sales_z_score"] >= threshold,
        "anomaly_direction"
    ] = "Spike"

    df.loc[
        df["sales_z_score"] <= -threshold,
        "anomaly_direction"
    ] = "Drop"

    return df

def add_anomaly_severity(anomaly_df):
    """Classify statistical anomaly magnitude based on absolute Z-score."""

    df = anomaly_df.copy()

    abs_z = df["sales_z_score"].abs()

    df["anomaly_severity"] = "Normal"

    df.loc[
        (abs_z >= 3.0) & (abs_z < 3.5),
        "anomaly_severity"
    ] = "High"

    df.loc[
        abs_z >= 3.5,
        "anomaly_severity"
    ] = "Critical"

    return df

def add_baseline_deviation(anomaly_df):
    """Calculate the percentage difference between sales and the rolling baseline."""

    df = anomaly_df.copy()

    df["baseline_deviation_pct"] = (
        (df["net_sales"] - df["rolling_mean"])
        / df["rolling_mean"]
        * 100
    )

    return df

def run_sales_anomaly_detection(window=28, threshold=3.0):
    """Run the complete daily sales anomaly detection workflow."""

    daily_sales = load_daily_sales()

    results = detect_sales_anomalies(
        daily_sales,
        window=window,
        threshold=threshold,
    )

    results = add_anomaly_severity(results)
    results = add_baseline_deviation(results)

    return results

def add_order_volume_anomalies(anomaly_df, window=28, threshold=3.0):
    """Detect unusual daily order volume using a rolling Z-score baseline."""

    df = anomaly_df.copy()

    df["order_count_rolling_mean"] = (
        df["order_count"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .mean()
    )

    df["order_count_rolling_std"] = (
        df["order_count"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .std()
    )

    df["order_count_z_score"] = (
        (df["order_count"] - df["order_count_rolling_mean"])
        / df["order_count_rolling_std"]
    )

    df["is_order_volume_anomaly"] = (
        df["order_count_z_score"].abs() >= threshold
    )

    return df

def add_average_order_value_features(
    anomaly_df,
    window=28,
    threshold=3.0,
):
    """Add AOV baseline features and detect unusual average order values."""

    df = anomaly_df.copy()

    df["average_order_value"] = (
        df["net_sales"] / df["order_count"]
    )

    df["aov_rolling_mean"] = (
        df["average_order_value"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .mean()
    )

    df["aov_rolling_std"] = (
        df["average_order_value"]
        .shift(1)
        .rolling(window=window, min_periods=window)
        .std()
    )

    df["aov_z_score"] = (
        (df["average_order_value"] - df["aov_rolling_mean"])
        / df["aov_rolling_std"]
    )

    df["is_aov_anomaly"] = (
        df["aov_z_score"].abs() >= threshold
    )

    return df

def run_complete_anomaly_detection(window=28, threshold=3.0):
    """Run sales, order-volume, and AOV anomaly analysis."""

    results = run_sales_anomaly_detection(
        window=window,
        threshold=threshold,
    )

    results = add_order_volume_anomalies(
        results,
        window=window,
        threshold=threshold,
    )

    results = add_average_order_value_features(
        results,
        window=window,
        threshold=threshold,
    )
    results = add_combined_anomaly_flag(results)

    return results

def add_combined_anomaly_flag(anomaly_df):
    """Flag dates where any monitored business metric is anomalous."""

    df = anomaly_df.copy()

    df["is_any_anomaly"] = (
        df["is_sales_anomaly"]
        | df["is_order_volume_anomaly"]
        | df["is_aov_anomaly"]
    )

    return df

def save_anomaly_results(anomaly_df):
    """Save daily anomaly detection results to PostgreSQL."""

    output = anomaly_df.copy()

    output = output.rename(
        columns={
            "order_date": "anomaly_date",
            "rolling_mean": "sales_rolling_mean",
            "baseline_deviation_pct": "sales_deviation_pct",
        }
    )

    columns_to_save = [
        "anomaly_date",
        "order_count",
        "net_sales",
        "average_order_value",
        "sales_rolling_mean",
        "sales_z_score",
        "sales_deviation_pct",
        "is_sales_anomaly",
        "order_count_rolling_mean",
        "order_count_z_score",
        "is_order_volume_anomaly",
        "aov_rolling_mean",
        "aov_z_score",
        "is_aov_anomaly",
        "is_any_anomaly",
        "anomaly_direction",
        "anomaly_severity",
    ]

    output = output[columns_to_save]

    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE analytics.daily_anomalies")
        )

        output.to_sql(
            "daily_anomalies",
            connection,
            schema="analytics",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

    return len(output)