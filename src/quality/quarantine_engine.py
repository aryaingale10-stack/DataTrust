import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from sqlalchemy import bindparam, create_engine, text

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
PRIMARY_KEY_MAP = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "returns": "return_id"
}

def validate_table_name(table_name):
    """Validate that the table is supported by the quarantine engine."""

    if table_name not in PRIMARY_KEY_MAP:
        raise ValueError(
            f"Unsupported table name: {table_name}"
        )
    
def get_latest_successful_run_id():
    """Return the most recent successful data quality audit run."""

    query = text(
        """
        SELECT run_id
        FROM quality.audit_runs
        WHERE run_status = 'SUCCESS'
        ORDER BY run_id DESC
        LIMIT 1;
        """
    )

    with engine.connect() as connection:
        run_id = connection.execute(query).scalar_one_or_none()

    if run_id is None:
        raise ValueError(
            "No successful data quality audit run was found."
        )

    return run_id

def get_table_issue_identifiers(run_id, table_name):
    """Return record identifiers flagged for a table in an audit run."""
    validate_table_name(table_name)
    query = text(
        """
        SELECT DISTINCT record_identifier
        FROM quality.issue_details
        WHERE run_id = :run_id
          AND table_name = :table_name
          AND record_identifier IS NOT NULL;
        """
    )

    with engine.connect() as connection:
        identifiers = connection.execute(
            query,
            {
                "run_id": run_id,
                "table_name": table_name
            }
        ).scalars().all()

    return [
        str(identifier)
        for identifier in identifiers
    ]

def load_flagged_records(run_id, table_name):
    """Load raw records that were flagged by the quality audit."""

    validate_table_name(table_name)

    primary_key = PRIMARY_KEY_MAP[table_name]

    identifiers = get_table_issue_identifiers(
        run_id,
        table_name
    )

    if not identifiers:
        return pd.DataFrame()

    query = text(
        f"""
        SELECT *
        FROM raw.{table_name}
        WHERE {primary_key} IN :identifiers;
        """
    ).bindparams(
        bindparam(
            "identifiers",
            expanding=True
        )
    )

    with engine.connect() as connection:
        flagged_records = pd.read_sql(
            query,
            connection,
            params={
                "identifiers": identifiers
            }
        )

    return flagged_records

def load_trusted_records(run_id, table_name):
    """Load raw records that were not flagged by the quality audit."""

    validate_table_name(table_name)

    primary_key = PRIMARY_KEY_MAP[table_name]

    flagged_identifiers = get_table_issue_identifiers(
        run_id,
        table_name
    )

    if not flagged_identifiers:
        query = text(
            f"""
            SELECT *
            FROM raw.{table_name};
            """
        )

        with engine.connect() as connection:
            return pd.read_sql(query, connection)

    query = text(
        f"""
        SELECT *
        FROM raw.{table_name}
        WHERE {primary_key} NOT IN :flagged_identifiers;
        """
    ).bindparams(
        bindparam(
            "flagged_identifiers",
            expanding=True
        )
    )

    with engine.connect() as connection:
        trusted_records = pd.read_sql(
            query,
            connection,
            params={
                "flagged_identifiers": flagged_identifiers
            }
        )

    return trusted_records

def build_quarantine_summary(run_id):
    """Build record-level quarantine statistics for all raw tables."""

    summary_rows = []

    for table_name in PRIMARY_KEY_MAP:
        flagged_records = load_flagged_records(
            run_id,
            table_name
        )

        trusted_records = load_trusted_records(
            run_id,
            table_name
        )

        flagged_count = len(flagged_records)
        trusted_count = len(trusted_records)
        total_count = flagged_count + trusted_count

        quarantine_rate = (
            (flagged_count / total_count) * 100
            if total_count > 0
            else 0
        )

        summary_rows.append({
            "table_name": table_name,
            "total_records": total_count,
            "trusted_records": trusted_count,
            "quarantined_records": flagged_count,
            "quarantine_rate": round(
                quarantine_rate,
                2
            )
        })

    return pd.DataFrame(summary_rows)

def save_flagged_records(run_id, table_name):
    """Save flagged raw records into the quarantine schema."""

    validate_table_name(table_name)

    flagged_records = load_flagged_records(
        run_id,
        table_name
    )

    if flagged_records.empty:
        return 0

    delete_query = text(
        f"""
        DELETE FROM quarantine.{table_name}
        WHERE run_id = :run_id;
        """
    )

    flagged_records = flagged_records.copy()

    flagged_records.insert(
        0,
        "run_id",
        run_id
    )

    with engine.begin() as connection:
        connection.execute(
            delete_query,
            {"run_id": run_id}
        )

        flagged_records.to_sql(
            name=table_name,
            con=connection,
            schema="quarantine",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )

    return len(flagged_records)

def save_all_flagged_records(run_id):
    """Save flagged records for all supported tables."""

    saved_counts = {}

    for table_name in PRIMARY_KEY_MAP:
        saved_count = save_flagged_records(
            run_id,
            table_name
        )

        saved_counts[table_name] = saved_count

    return saved_counts

def save_trusted_records(run_id, table_name):
    """Save trusted records into the clean schema."""

    validate_table_name(table_name)

    trusted_records = load_trusted_records(
        run_id,
        table_name
    )

    if trusted_records.empty:
        return 0

    with engine.begin() as connection:
        connection.execute(
            text(
                f"""
                TRUNCATE TABLE clean.{table_name};
                """
            )
        )

        trusted_records.to_sql(
            name=table_name,
            con=connection,
            schema="clean",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )

    return len(trusted_records)

def save_all_trusted_records(run_id):
    """Save trusted records for all supported tables."""

    saved_counts = {}

    for table_name in PRIMARY_KEY_MAP:
        saved_count = save_trusted_records(
            run_id,
            table_name
        )

        saved_counts[table_name] = saved_count

    return saved_counts