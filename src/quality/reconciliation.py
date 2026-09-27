import os
from pathlib import Path

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


TABLES = (
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "returns",
)

def get_raw_record_count():
    """Return the total number of records across all raw tables."""

    total_records = 0

    with engine.connect() as connection:
        for table_name in TABLES:
            query = text(
                f"SELECT COUNT(*) FROM raw.{table_name}"
            )

            count = connection.execute(query).scalar_one()
            total_records += count

    return total_records

def get_clean_record_count():
    """Return the total number of records across all final clean tables."""

    total_records = 0

    with engine.connect() as connection:
        for table_name in TABLES:
            query = text(
                f"SELECT COUNT(*) FROM clean.{table_name}"
            )

            count = connection.execute(query).scalar_one()
            total_records += count

    return total_records

def get_quarantine_record_count(run_id):
    """Return the total number of directly quarantined records for an audit run."""

    total_records = 0

    with engine.connect() as connection:
        for table_name in TABLES:
            query = text(
                f"""
                SELECT COUNT(*)
                FROM quarantine.{table_name}
                WHERE run_id = :run_id
                """
            )

            count = connection.execute(
                query,
                {"run_id": run_id}
            ).scalar_one()

            total_records += count

    return total_records

def get_dependency_exclusion_count(run_id):
    """Return the number of dependency-propagated exclusions for an audit run."""

    query = text(
        """
        SELECT COUNT(*)
        FROM quality.dependency_exclusions
        WHERE run_id = :run_id
        """
    )

    with engine.connect() as connection:
        count = connection.execute(
            query,
            {"run_id": run_id}
        ).scalar_one()

    return count

def reconcile_run(run_id):
    """Reconcile raw records against their final DataTrust disposition."""

    raw_records = get_raw_record_count()
    clean_records = get_clean_record_count()
    quarantine_records = get_quarantine_record_count(run_id)
    dependency_exclusions = get_dependency_exclusion_count(run_id)

    accounted_records = (
        clean_records
        + quarantine_records
        + dependency_exclusions
    )

    difference = raw_records - accounted_records

    return {
        "run_id": run_id,
        "raw_records": raw_records,
        "final_clean_records": clean_records,
        "direct_quarantine_records": quarantine_records,
        "dependency_exclusions": dependency_exclusions,
        "accounted_records": accounted_records,
        "difference": difference,
        "reconciled": difference == 0,
    }

def print_reconciliation_report(run_id):
    """Print a readable reconciliation summary for an audit run."""

    result = reconcile_run(run_id)

    print("\nDATA RECONCILIATION")
    print("-" * 45)
    print(f"Audit Run ID:             {result['run_id']}")
    print(f"Raw Records:              {result['raw_records']:,}")
    print(f"Final Clean Records:      {result['final_clean_records']:,}")
    print(f"Direct Quarantine:        {result['direct_quarantine_records']:,}")
    print(f"Dependency Exclusions:    {result['dependency_exclusions']:,}")
    print(f"Accounted Records:        {result['accounted_records']:,}")
    print(f"Reconciliation Difference:{result['difference']:,}")
    print(f"Reconciled:               {result['reconciled']}")

def validate_reconciliation(run_id):
    """Validate that every raw record has exactly one final disposition."""

    result = reconcile_run(run_id)

    if not result["reconciled"]:
        raise RuntimeError(
            "Data reconciliation failed. "
            f"Run ID: {run_id}, "
            f"Difference: {result['difference']}"
        )

    return result