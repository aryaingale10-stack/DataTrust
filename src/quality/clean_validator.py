import os
from pathlib import Path

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
    pool_pre_ping=True
)

CLEAN_PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "returns": "return_id",
}

def validate_primary_keys():
    """Check that clean tables contain no duplicate primary identifiers."""

    results = {}

    for table_name, primary_key in CLEAN_PRIMARY_KEYS.items():
        query = text(
            f"""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(DISTINCT {primary_key}) AS distinct_ids
            FROM clean.{table_name};
            """
        )

        with engine.connect() as connection:
            total_rows, distinct_ids = connection.execute(
                query
            ).one()

        results[table_name] = {
            "total_rows": total_rows,
            "distinct_ids": distinct_ids,
            "duplicate_ids": total_rows - distinct_ids,
            "passed": total_rows == distinct_ids,
        }

    return results

def validate_referential_integrity():
    """Check that clean tables do not contain orphan foreign keys."""

    checks = {
        "orders_customer": """
            SELECT COUNT(*)
            FROM clean.orders o
            LEFT JOIN clean.customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
        """,

        "order_items_order": """
            SELECT COUNT(*)
            FROM clean.order_items oi
            LEFT JOIN clean.orders o
                ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """,

        "order_items_product": """
            SELECT COUNT(*)
            FROM clean.order_items oi
            LEFT JOIN clean.products p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL;
        """,

        "payments_order": """
            SELECT COUNT(*)
            FROM clean.payments p
            LEFT JOIN clean.orders o
                ON p.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """,

        "returns_order_item": """
            SELECT COUNT(*)
            FROM clean.returns r
            LEFT JOIN clean.order_items oi
                ON r.order_item_id = oi.order_item_id
            WHERE oi.order_item_id IS NULL;
        """,

        "returns_order": """
            SELECT COUNT(*)
            FROM clean.returns r
            LEFT JOIN clean.orders o
                ON r.order_id = o.order_id
            WHERE o.order_id IS NULL;
        """,

        "returns_product": """
            SELECT COUNT(*)
            FROM clean.returns r
            LEFT JOIN clean.products p
                ON r.product_id = p.product_id
            WHERE p.product_id IS NULL;
        """,
    }

    results = {}

    with engine.connect() as connection:
        for check_name, sql_query in checks.items():
            orphan_count = connection.execute(
                text(sql_query)
            ).scalar_one()

            results[check_name] = {
                "orphan_rows": orphan_count,
                "passed": orphan_count == 0,
            }

    return results

def validate_clean_layer():
    """Run all structural validations for the clean data layer."""

    primary_key_results = validate_primary_keys()
    referential_results = validate_referential_integrity()

    primary_keys_passed = all(
        result["passed"]
        for result in primary_key_results.values()
    )

    referential_integrity_passed = all(
        result["passed"]
        for result in referential_results.values()
    )

    return {
        "primary_keys": primary_key_results,
        "referential_integrity": referential_results,
        "overall_passed": (
            primary_keys_passed
            and referential_integrity_passed
        ),
    }

def get_clean_layer_summary():
    """Return row counts for all clean tables."""

    summary = {}

    with engine.connect() as connection:
        for table_name in CLEAN_PRIMARY_KEYS:
            query = text(
                f"""
                SELECT COUNT(*)
                FROM clean.{table_name};
                """
            )

            summary[table_name] = connection.execute(
                query
            ).scalar_one()

    return summary

if __name__ == "__main__":
    result = validate_clean_layer()

    print(
        "Overall clean-layer validation:",
        result["overall_passed"]
    )

    print("\nPrimary-key validation:")

    for table_name, check in result["primary_keys"].items():
        print(
            f"{table_name} | "
            f"rows: {check['total_rows']} | "
            f"distinct IDs: {check['distinct_ids']} | "
            f"duplicates: {check['duplicate_ids']} | "
            f"passed: {check['passed']}"
        )

    print("\nReferential-integrity validation:")

    for check_name, check in result[
        "referential_integrity"
    ].items():
        print(
            f"{check_name} | "
            f"orphan rows: {check['orphan_rows']} | "
            f"passed: {check['passed']}"
        )