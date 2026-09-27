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
    """Load dates flagged by the anomaly detection layer."""

    query = text(
        """
        SELECT
            anomaly_date,
            net_sales,
            average_order_value,
            sales_z_score,
            order_count_z_score,
            aov_z_score,
            is_sales_anomaly,
            is_order_volume_anomaly,
            is_aov_anomaly,
            anomaly_direction,
            anomaly_severity
        FROM analytics.daily_anomalies
        WHERE is_any_anomaly = TRUE
        ORDER BY anomaly_date
        """
    )

    with engine.connect() as connection:
        anomaly_days = pd.read_sql(
            query,
            connection,
        )

    return anomaly_days

def load_channel_sales_for_date(anomaly_date):
    """Load net sales and order volume by sales channel for a specific date."""

    query = text(
        """
        SELECT
            o.sales_channel,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_pct)
            ) AS net_sales
        FROM clean.orders o
        JOIN clean.order_items oi
            ON o.order_id = oi.order_id
        WHERE o.order_date = :anomaly_date
        GROUP BY o.sales_channel
        ORDER BY net_sales DESC
        """
    )

    with engine.connect() as connection:
        channel_sales = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    return channel_sales

def load_channel_baseline(anomaly_date, window=28):
    """Calculate prior-period channel averages before an anomaly date."""

    query = text(
        """
        WITH daily_channel_sales AS (
            SELECT
                o.order_date,
                o.sales_channel,
                COUNT(DISTINCT o.order_id) AS order_count,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_pct)
                ) AS net_sales
            FROM clean.orders o
            JOIN clean.order_items oi
                ON o.order_id = oi.order_id
            WHERE o.order_date < :anomaly_date
              AND o.order_date >= CAST(:anomaly_date AS DATE) - :window
            GROUP BY
                o.order_date,
                o.sales_channel
        )

        SELECT
            sales_channel,
            AVG(order_count) AS baseline_order_count,
            AVG(net_sales) AS baseline_net_sales
        FROM daily_channel_sales
        GROUP BY sales_channel
        ORDER BY sales_channel
        """
    )

    with engine.connect() as connection:
        baseline = pd.read_sql(
            query,
            connection,
            params={
                "anomaly_date": anomaly_date,
                "window": window,
            },
        )

    return baseline

def compare_channel_to_baseline(anomaly_date, window=28):
    """Compare anomaly-day channel performance with its prior baseline."""

    actual = load_channel_sales_for_date(anomaly_date)
    baseline = load_channel_baseline(
        anomaly_date,
        window=window,
    )

    comparison = actual.merge(
        baseline,
        on="sales_channel",
        how="left",
    )

    comparison["sales_change"] = (
        comparison["net_sales"]
        - comparison["baseline_net_sales"]
    )

    comparison["sales_change_pct"] = (
        comparison["sales_change"]
        / comparison["baseline_net_sales"]
        * 100
    )

    comparison["order_change"] = (
        comparison["order_count"]
        - comparison["baseline_order_count"]
    )

    comparison["order_change_pct"] = (
        comparison["order_change"]
        / comparison["baseline_order_count"]
        * 100
    )

    comparison = comparison.sort_values(
        "sales_change",
        ascending=False,
    )

    return comparison

def load_region_sales_for_date(anomaly_date):
    """Load net sales and order volume by shipping region for a specific date."""

    query = text(
        """
        SELECT
            o.shipping_region,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_pct)
            ) AS net_sales
        FROM clean.orders o
        JOIN clean.order_items oi
            ON o.order_id = oi.order_id
        WHERE o.order_date = :anomaly_date
        GROUP BY o.shipping_region
        ORDER BY net_sales DESC
        """
    )

    with engine.connect() as connection:
        region_sales = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    return region_sales

def load_region_baseline(anomaly_date, window=28):
    """Calculate prior-period regional averages before an anomaly date."""

    query = text(
        """
        WITH daily_region_sales AS (
            SELECT
                o.order_date,
                o.shipping_region,
                COUNT(DISTINCT o.order_id) AS order_count,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_pct)
                ) AS net_sales
            FROM clean.orders o
            JOIN clean.order_items oi
                ON o.order_id = oi.order_id
            WHERE o.order_date < :anomaly_date
              AND o.order_date >= CAST(:anomaly_date AS DATE) - :window
            GROUP BY
                o.order_date,
                o.shipping_region
        )

        SELECT
            shipping_region,
            AVG(order_count) AS baseline_order_count,
            AVG(net_sales) AS baseline_net_sales
        FROM daily_region_sales
        GROUP BY shipping_region
        ORDER BY shipping_region
        """
    )

    with engine.connect() as connection:
        baseline = pd.read_sql(
            query,
            connection,
            params={
                "anomaly_date": anomaly_date,
                "window": window,
            },
        )

    return baseline

def compare_region_to_baseline(anomaly_date, window=28):
    """Compare anomaly-day regional performance with its prior baseline."""

    actual = load_region_sales_for_date(anomaly_date)

    baseline = load_region_baseline(
        anomaly_date,
        window=window,
    )

    comparison = actual.merge(
        baseline,
        on="shipping_region",
        how="left",
    )

    comparison["sales_change"] = (
        comparison["net_sales"]
        - comparison["baseline_net_sales"]
    )

    comparison["sales_change_pct"] = (
        comparison["sales_change"]
        / comparison["baseline_net_sales"]
        * 100
    )

    comparison["order_change"] = (
        comparison["order_count"]
        - comparison["baseline_order_count"]
    )

    comparison["order_change_pct"] = (
        comparison["order_change"]
        / comparison["baseline_order_count"]
        * 100
    )

    comparison = comparison.sort_values(
        "sales_change",
        ascending=False,
    )

    return comparison

def load_category_sales_for_date(anomaly_date):
    """Load net sales and units sold by product category for a specific date."""

    query = text(
        """
        SELECT
            p.category,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(oi.quantity) AS units_sold,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_pct)
            ) AS net_sales
        FROM clean.orders o
        JOIN clean.order_items oi
            ON o.order_id = oi.order_id
        JOIN clean.products p
            ON oi.product_id = p.product_id
        WHERE o.order_date = :anomaly_date
        GROUP BY p.category
        ORDER BY net_sales DESC
        """
    )

    with engine.connect() as connection:
        category_sales = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    return category_sales

def load_category_baseline(anomaly_date, window=28):
    """Calculate prior-period category averages before an anomaly date."""

    query = text(
        """
        WITH daily_category_sales AS (
            SELECT
                o.order_date,
                p.category,
                COUNT(DISTINCT o.order_id) AS order_count,
                SUM(oi.quantity) AS units_sold,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_pct)
                ) AS net_sales
            FROM clean.orders o
            JOIN clean.order_items oi
                ON o.order_id = oi.order_id
            JOIN clean.products p
                ON oi.product_id = p.product_id
            WHERE o.order_date < :anomaly_date
              AND o.order_date >= CAST(:anomaly_date AS DATE) - :window
            GROUP BY
                o.order_date,
                p.category
        )

        SELECT
            category,
            AVG(order_count) AS baseline_order_count,
            AVG(units_sold) AS baseline_units_sold,
            AVG(net_sales) AS baseline_net_sales
        FROM daily_category_sales
        GROUP BY category
        ORDER BY category
        """
    )

    with engine.connect() as connection:
        baseline = pd.read_sql(
            query,
            connection,
            params={
                "anomaly_date": anomaly_date,
                "window": window,
            },
        )

    return baseline

def compare_category_to_baseline(anomaly_date, window=28):
    """Compare anomaly-day category performance with its prior baseline."""

    actual = load_category_sales_for_date(anomaly_date)

    baseline = load_category_baseline(
        anomaly_date,
        window=window,
    )

    comparison = actual.merge(
        baseline,
        on="category",
        how="left",
    )

    comparison["sales_change"] = (
        comparison["net_sales"]
        - comparison["baseline_net_sales"]
    )

    comparison["sales_change_pct"] = (
        comparison["sales_change"]
        / comparison["baseline_net_sales"]
        * 100
    )

    comparison["units_change"] = (
        comparison["units_sold"]
        - comparison["baseline_units_sold"]
    )

    comparison["units_change_pct"] = (
        comparison["units_change"]
        / comparison["baseline_units_sold"]
        * 100
    )

    comparison["order_change_pct"] = (
        (
            comparison["order_count"]
            - comparison["baseline_order_count"]
        )
        / comparison["baseline_order_count"]
        * 100
    )

    comparison = comparison.sort_values(
        "sales_change",
        ascending=False,
    )

    return comparison

def load_product_sales_for_date(anomaly_date):
    """Load product-level sales performance for a specific date."""

    query = text(
        """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            p.subcategory,
            SUM(oi.quantity) AS units_sold,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_pct)
            ) AS net_sales
        FROM clean.orders o
        JOIN clean.order_items oi
            ON o.order_id = oi.order_id
        JOIN clean.products p
            ON oi.product_id = p.product_id
        WHERE o.order_date = :anomaly_date
        GROUP BY
            p.product_id,
            p.product_name,
            p.category,
            p.subcategory
        ORDER BY net_sales DESC
        """
    )

    with engine.connect() as connection:
        product_sales = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    return product_sales

def load_product_baseline(anomaly_date, window=28):
    """Calculate prior-period product sales averages before an anomaly date."""

    query = text(
        """
        WITH daily_product_sales AS (
            SELECT
                o.order_date,
                p.product_id,
                SUM(oi.quantity) AS units_sold,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_pct)
                ) AS net_sales
            FROM clean.orders o
            JOIN clean.order_items oi
                ON o.order_id = oi.order_id
            JOIN clean.products p
                ON oi.product_id = p.product_id
            WHERE o.order_date < :anomaly_date
              AND o.order_date >= CAST(:anomaly_date AS DATE) - :window
            GROUP BY
                o.order_date,
                p.product_id
        )

        SELECT
       dps.product_id,
       p.product_name,
       p.category,
       p.subcategory,
       COUNT(*) AS active_sales_days,
            SUM(units_sold) / CAST(:window AS NUMERIC)
                AS baseline_units_sold,
            SUM(net_sales) / CAST(:window AS NUMERIC)
                AS baseline_net_sales
        FROM daily_product_sales dps
        JOIN clean.products p
          ON dps.product_id = p.product_id
        GROUP BY
          dps.product_id,
          p.product_name,
          p.category,
          p.subcategory
        """
    )

    with engine.connect() as connection:
        baseline = pd.read_sql(
            query,
            connection,
            params={
                "anomaly_date": anomaly_date,
                "window": window,
            },
        )

    return baseline

def compare_product_to_baseline(anomaly_date, window=28):
    """Compare anomaly-day product sales with prior calendar-day baselines."""

    actual = load_product_sales_for_date(anomaly_date)

    baseline = load_product_baseline(
        anomaly_date,
        window=window,
    )

    comparison = actual.merge(
        baseline,
        on="product_id",
        how="outer",
    )
    comparison["product_name"] = (
    comparison["product_name_x"]
    .combine_first(comparison["product_name_y"])
)

    comparison["category"] = (
    comparison["category_x"]
    .combine_first(comparison["category_y"])
)

    comparison["subcategory"] = (
    comparison["subcategory_x"]
    .combine_first(comparison["subcategory_y"])
)

    comparison = comparison.drop(
    columns=[
        "product_name_x",
        "product_name_y",
        "category_x",
        "category_y",
        "subcategory_x",
        "subcategory_y",
    ]
)


    comparison["units_sold"] = (
       comparison["units_sold"].fillna(0)
    )

    comparison["net_sales"] = (
    comparison["net_sales"].fillna(0)
)
    comparison["active_sales_days"] = (
    comparison["active_sales_days"].fillna(0).astype(int)
    )

    comparison["baseline_units_sold"] = (
        comparison["baseline_units_sold"].fillna(0)
    )

    comparison["baseline_net_sales"] = (
        comparison["baseline_net_sales"].fillna(0)
    )

    comparison["sales_change"] = (
        comparison["net_sales"]
        - comparison["baseline_net_sales"]
    )

    comparison["units_change"] = (
        comparison["units_sold"]
        - comparison["baseline_units_sold"]
    )

    comparison = comparison.sort_values(
        "sales_change",
        ascending=False,
    )

    return comparison

def calculate_product_concentration(
    anomaly_date,
    window=28,
    direction="positive",
):
    """Calculate product-level sales deviation concentration."""

    comparison = compare_product_to_baseline(
        anomaly_date,
        window=window,
    )

    if direction == "positive":
        relevant = comparison[
            comparison["sales_change"] > 0
        ].sort_values(
            "sales_change",
            ascending=False,
        )

    elif direction == "negative":
        relevant = comparison[
            comparison["sales_change"] < 0
        ].sort_values(
            "sales_change",
            ascending=True,
        )

    else:
        raise ValueError(
            "direction must be 'positive' or 'negative'"
        )

    total_change = abs(
        relevant["sales_change"].sum()
    )

    if total_change == 0:
        return {
            "total_change": 0.0,
            "top_1_share_pct": 0.0,
            "top_5_share_pct": 0.0,
            "top_10_share_pct": 0.0,
        }

    return {
        "total_change": float(
            round(total_change, 2)
        ),
        "top_1_share_pct": float(
            round(
                abs(relevant.head(1)["sales_change"].sum())
                / total_change * 100,
                2,
            )
        ),
        "top_5_share_pct": float(
            round(
                abs(relevant.head(5)["sales_change"].sum())
                / total_change * 100,
                2,
            )
        ),
        "top_10_share_pct": float(
            round(
                abs(relevant.head(10)["sales_change"].sum())
                / total_change * 100,
                2,
            )
        ),
    }

def get_anomaly_signal(anomaly_date):
    """Return the anomaly signals detected for a specific date."""

    query = text(
        """
        SELECT
            anomaly_date,
            is_sales_anomaly,
            is_order_volume_anomaly,
            is_aov_anomaly,
            anomaly_direction,
            anomaly_severity
        FROM analytics.daily_anomalies
        WHERE anomaly_date = :anomaly_date
          AND is_any_anomaly = TRUE
        """
    )

    with engine.connect() as connection:
        result = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    if result.empty:
        raise ValueError(
            f"No anomaly found for {anomaly_date}"
        )

    row = result.iloc[0]

    signals = []

    if row["is_sales_anomaly"]:
        signals.append(
            f"Sales {row['anomaly_direction']}"
        )

    if row["is_order_volume_anomaly"]:
        signals.append("Order Volume")

    if row["is_aov_anomaly"]:
        signals.append("Average Order Value")

    return {
        "anomaly_date": str(row["anomaly_date"]),
        "signals": signals,
        "sales_direction": (
            row["anomaly_direction"]
            if row["is_sales_anomaly"]
            else None
        ),
        "sales_severity": (
            row["anomaly_severity"]
            if row["is_sales_anomaly"]
            else None
        ),
    }

def get_sales_analysis_direction(anomaly_date):
    """Determine the product contribution direction for a sales anomaly."""

    signal = get_anomaly_signal(anomaly_date)

    if signal["sales_direction"] == "Spike":
        return "positive"

    if signal["sales_direction"] == "Drop":
        return "negative"

    return None

def rank_sales_contributors(comparison_df, direction):
    """Rank sales contributors according to anomaly direction."""

    if direction == "positive":
        return comparison_df.sort_values(
            "sales_change",
            ascending=False,
        ).reset_index(drop=True)

    if direction == "negative":
        return comparison_df.sort_values(
            "sales_change",
            ascending=True,
        ).reset_index(drop=True)

    raise ValueError(
        "direction must be 'positive' or 'negative'"
    )

def build_sales_root_cause_summary(anomaly_date, window=28):
    """Build a contributor summary for a sales spike or drop."""

    signal = get_anomaly_signal(anomaly_date)
    direction = get_sales_analysis_direction(anomaly_date)

    if direction is None:
        raise ValueError(
            f"{anomaly_date} is not a sales anomaly."
        )

    channel = rank_sales_contributors(
        compare_channel_to_baseline(
            anomaly_date,
            window=window,
        ),
        direction,
    )

    region = rank_sales_contributors(
        compare_region_to_baseline(
            anomaly_date,
            window=window,
        ),
        direction,
    )

    category = rank_sales_contributors(
        compare_category_to_baseline(
            anomaly_date,
            window=window,
        ),
        direction,
    )

    product = rank_sales_contributors(
        compare_product_to_baseline(
            anomaly_date,
            window=window,
        ),
        direction,
    )

    concentration = calculate_product_concentration(
        anomaly_date,
        window=window,
        direction=direction,
    )

    return {
        "anomaly_date": anomaly_date,
        "signals": signal["signals"],
        "sales_direction": signal["sales_direction"],
        "sales_severity": signal["sales_severity"],

        "top_channel": channel.iloc[0]["sales_channel"],
        "top_channel_sales_change": float(
            round(channel.iloc[0]["sales_change"], 2)
        ),

        "top_region": region.iloc[0]["shipping_region"],
        "top_region_sales_change": float(
            round(region.iloc[0]["sales_change"], 2)
        ),

        "top_category": category.iloc[0]["category"],
        "top_category_sales_change": float(
            round(category.iloc[0]["sales_change"], 2)
        ),

        "top_product_id": product.iloc[0]["product_id"],
        "top_product_name": product.iloc[0]["product_name"],
        "top_product_sales_change": float(
            round(product.iloc[0]["sales_change"], 2)
        ),

        "product_top_10_share_pct": (
            concentration["top_10_share_pct"]
        ),
    }

def rank_volume_contributors(comparison_df):
    """Rank contributors by positive order-volume deviation."""

    if "order_change" not in comparison_df.columns:
        raise ValueError(
            "comparison_df must contain an order_change column."
        )

    return comparison_df.sort_values(
        "order_change",
        ascending=False,
    ).reset_index(drop=True)

def build_volume_root_cause_summary(anomaly_date, window=28):
    """Build a contributor summary for an order-volume anomaly."""

    signal = get_anomaly_signal(anomaly_date)

    if "Order Volume" not in signal["signals"]:
        raise ValueError(
            f"{anomaly_date} is not an order-volume anomaly."
        )

    channel = rank_volume_contributors(
        compare_channel_to_baseline(
            anomaly_date,
            window=window,
        )
    )

    region = rank_volume_contributors(
        compare_region_to_baseline(
            anomaly_date,
            window=window,
        )
    )

    category = compare_category_to_baseline(
        anomaly_date,
        window=window,
    ).sort_values(
        "units_change",
        ascending=False,
    ).reset_index(drop=True)

    return {
        "anomaly_date": anomaly_date,
        "signals": signal["signals"],

        "top_volume_channel": (
            channel.iloc[0]["sales_channel"]
        ),
        "top_channel_order_change": float(
            round(channel.iloc[0]["order_change"], 2)
        ),
        "top_channel_order_change_pct": float(
            round(channel.iloc[0]["order_change_pct"], 2)
        ),

        "top_volume_region": (
            region.iloc[0]["shipping_region"]
        ),
        "top_region_order_change": float(
            round(region.iloc[0]["order_change"], 2)
        ),
        "top_region_order_change_pct": float(
            round(region.iloc[0]["order_change_pct"], 2)
        ),

        "top_volume_category": (
            category.iloc[0]["category"]
        ),
        "top_category_units_change": float(
            round(category.iloc[0]["units_change"], 2)
        ),
        "top_category_units_change_pct": float(
            round(category.iloc[0]["units_change_pct"], 2)
        ),
    }

def add_category_value_per_order_features(comparison_df):
    """Add category-level value-per-participating-order diagnostics."""

    result = comparison_df.copy()

    result["sales_per_order"] = (
        result["net_sales"]
        / result["order_count"]
    )

    result["baseline_sales_per_order"] = (
        result["baseline_net_sales"]
        / result["baseline_order_count"]
    )

    result["sales_per_order_change"] = (
        result["sales_per_order"]
        - result["baseline_sales_per_order"]
    )

    result["sales_per_order_change_pct"] = (
        result["sales_per_order_change"]
        / result["baseline_sales_per_order"]
        * 100
    )

    return result

def get_aov_analysis_direction(anomaly_date):
    """Determine whether an AOV anomaly is unusually high or low."""

    query = text(
        """
        SELECT
            is_aov_anomaly,
            aov_z_score
        FROM analytics.daily_anomalies
        WHERE anomaly_date = :anomaly_date
          AND is_any_anomaly = TRUE
        """
    )

    with engine.connect() as connection:
        result = pd.read_sql(
            query,
            connection,
            params={"anomaly_date": anomaly_date},
        )

    if result.empty:
        raise ValueError(
            f"No anomaly found for {anomaly_date}"
        )

    row = result.iloc[0]

    if not row["is_aov_anomaly"]:
        return None

    if row["aov_z_score"] > 0:
        return "positive"

    if row["aov_z_score"] < 0:
        return "negative"

    return None

def rank_aov_contributors(comparison_df, direction):
    """Rank category contributors to an AOV anomaly."""

    required_column = "sales_per_order_change"

    if required_column not in comparison_df.columns:
        raise ValueError(
            "comparison_df must contain "
            "sales_per_order_change."
        )

    if direction == "positive":
        return comparison_df.sort_values(
            required_column,
            ascending=False,
        ).reset_index(drop=True)

    if direction == "negative":
        return comparison_df.sort_values(
            required_column,
            ascending=True,
        ).reset_index(drop=True)

    raise ValueError(
        "direction must be 'positive' or 'negative'."
    )

def build_aov_root_cause_summary(anomaly_date, window=28):
    """Build a category contributor summary for an AOV anomaly."""

    signal = get_anomaly_signal(anomaly_date)
    direction = get_aov_analysis_direction(anomaly_date)

    if direction is None:
        raise ValueError(
            f"{anomaly_date} is not an AOV anomaly."
        )

    category = compare_category_to_baseline(
        anomaly_date,
        window=window,
    )

    category = add_category_value_per_order_features(
        category
    )

    category = rank_aov_contributors(
        category,
        direction,
    )

    top_category = category.iloc[0]

    return {
        "anomaly_date": anomaly_date,
        "signals": signal["signals"],
        "aov_direction": (
            "High" if direction == "positive" else "Low"
        ),
        "top_aov_category": top_category["category"],
        "top_category_sales_per_order": float(
            round(top_category["sales_per_order"], 2)
        ),
        "top_category_baseline_sales_per_order": float(
            round(
                top_category["baseline_sales_per_order"],
                2,
            )
        ),
        "top_category_sales_per_order_change": float(
            round(
                top_category["sales_per_order_change"],
                2,
            )
        ),
        "top_category_sales_per_order_change_pct": float(
            round(
                top_category["sales_per_order_change_pct"],
                2,
            )
        ),
    }

def analyze_anomaly_root_causes(anomaly_date, window=28):
    """Run the appropriate contributor analyses for an anomaly date."""

    signal = get_anomaly_signal(anomaly_date)

    result = {
        "anomaly_date": anomaly_date,
        "signals": signal["signals"],
    }

    if (
        "Sales Spike" in signal["signals"]
        or "Sales Drop" in signal["signals"]
    ):
        result["sales_analysis"] = (
            build_sales_root_cause_summary(
                anomaly_date,
                window=window,
            )
        )

    if "Order Volume" in signal["signals"]:
        result["volume_analysis"] = (
            build_volume_root_cause_summary(
                anomaly_date,
                window=window,
            )
        )

    if "Average Order Value" in signal["signals"]:
        result["aov_analysis"] = (
            build_aov_root_cause_summary(
                anomaly_date,
                window=window,
            )
        )

    return result

def build_sales_root_cause_rows(anomaly_date, window=28):
    """Convert sales root-cause analysis into normalized rows."""

    summary = build_sales_root_cause_summary(
        anomaly_date,
        window=window,
    )

    direction = summary["sales_direction"]

    rows = [
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Sales",
            "signal_direction": direction,
            "dimension_type": "Channel",
            "contributor_id": None,
            "contributor_name": summary["top_channel"],
            "metric_name": "Net Sales Change",
            "absolute_change": summary[
                "top_channel_sales_change"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Sales",
            "signal_direction": direction,
            "dimension_type": "Region",
            "contributor_id": None,
            "contributor_name": summary["top_region"],
            "metric_name": "Net Sales Change",
            "absolute_change": summary[
                "top_region_sales_change"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Sales",
            "signal_direction": direction,
            "dimension_type": "Category",
            "contributor_id": None,
            "contributor_name": summary["top_category"],
            "metric_name": "Net Sales Change",
            "absolute_change": summary[
                "top_category_sales_change"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Sales",
            "signal_direction": direction,
            "dimension_type": "Product",
            "contributor_id": summary["top_product_id"],
            "contributor_name": summary["top_product_name"],
            "metric_name": "Net Sales Change",
            "absolute_change": summary[
                "top_product_sales_change"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
    ]

    return pd.DataFrame(rows)

def build_volume_root_cause_rows(anomaly_date, window=28):
    """Convert order-volume root-cause analysis into normalized rows."""

    summary = build_volume_root_cause_summary(
        anomaly_date,
        window=window,
    )

    rows = [
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Order Volume",
            "signal_direction": "Spike",
            "dimension_type": "Channel",
            "contributor_id": None,
            "contributor_name": summary["top_volume_channel"],
            "metric_name": "Order Count Change",
            "absolute_change": summary[
                "top_channel_order_change"
            ],
            "percentage_change": summary[
                "top_channel_order_change_pct"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Order Volume",
            "signal_direction": "Spike",
            "dimension_type": "Region",
            "contributor_id": None,
            "contributor_name": summary["top_volume_region"],
            "metric_name": "Order Count Change",
            "absolute_change": summary[
                "top_region_order_change"
            ],
            "percentage_change": summary[
                "top_region_order_change_pct"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
        {
            "anomaly_date": anomaly_date,
            "signal_type": "Order Volume",
            "signal_direction": "Spike",
            "dimension_type": "Category",
            "contributor_id": None,
            "contributor_name": summary["top_volume_category"],
            "metric_name": "Units Sold Change",
            "absolute_change": summary[
                "top_category_units_change"
            ],
            "percentage_change": summary[
                "top_category_units_change_pct"
            ],
            "contributor_rank": 1,
            "baseline_window_days": window,
        },
    ]

    return pd.DataFrame(rows)

def build_aov_root_cause_rows(anomaly_date, window=28):
    """Convert AOV root-cause analysis into normalized rows."""

    summary = build_aov_root_cause_summary(
        anomaly_date,
        window=window,
    )

    return pd.DataFrame(
        [
            {
                "anomaly_date": anomaly_date,
                "signal_type": "Average Order Value",
                "signal_direction": summary["aov_direction"],
                "dimension_type": "Category",
                "contributor_id": None,
                "contributor_name": summary["top_aov_category"],
                "metric_name": "Sales Per Order Change",
                "actual_value": summary[
                    "top_category_sales_per_order"
                ],
                "baseline_value": summary[
                    "top_category_baseline_sales_per_order"
                ],
                "absolute_change": summary[
                    "top_category_sales_per_order_change"
                ],
                "percentage_change": summary[
                    "top_category_sales_per_order_change_pct"
                ],
                "contributor_rank": 1,
                "baseline_window_days": window,
            }
        ]
    )

def build_root_cause_rows(anomaly_date, window=28):
    """Build normalized root-cause rows for an anomaly date."""

    signal = get_anomaly_signal(anomaly_date)
    frames = []

    if (
        "Sales Spike" in signal["signals"]
        or "Sales Drop" in signal["signals"]
    ):
        frames.append(
            build_sales_root_cause_rows(
                anomaly_date,
                window=window,
            )
        )

    if "Order Volume" in signal["signals"]:
        frames.append(
            build_volume_root_cause_rows(
                anomaly_date,
                window=window,
            )
        )

    if "Average Order Value" in signal["signals"]:
        frames.append(
            build_aov_root_cause_rows(
                anomaly_date,
                window=window,
            )
        )

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )

def build_all_root_cause_rows(window=28):
    """Build normalized root-cause rows for all detected anomaly days."""

    anomaly_days = load_anomaly_days()
    frames = []

    for anomaly_date in anomaly_days["anomaly_date"]:
        rows = build_root_cause_rows(
            str(anomaly_date),
            window=window,
        )

        if not rows.empty:
            frames.append(rows)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )

def save_root_cause_results(root_cause_df):
    """Save the current root-cause analysis snapshot to PostgreSQL."""

    if root_cause_df.empty:
        return 0

    database_columns = [
        "anomaly_date",
        "signal_type",
        "signal_direction",
        "dimension_type",
        "contributor_id",
        "contributor_name",
        "metric_name",
        "actual_value",
        "baseline_value",
        "absolute_change",
        "percentage_change",
        "contributor_rank",
        "baseline_window_days",
    ]

    output = root_cause_df.copy()

    for column in database_columns:
        if column not in output.columns:
            output[column] = None

    output = output[database_columns]

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    analytics.anomaly_root_causes
                RESTART IDENTITY
                """
            )
        )

        output.to_sql(
            "anomaly_root_causes",
            connection,
            schema="analytics",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

    return len(output)

def run_root_cause_analysis(window=28):
    """Run root-cause analysis for all detected anomaly days."""

    root_cause_df = build_all_root_cause_rows(
        window=window,
    )

    rows_saved = save_root_cause_results(
        root_cause_df
    )

    return root_cause_df, rows_saved