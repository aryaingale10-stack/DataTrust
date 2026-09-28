from pathlib import Path

from src.quality.quality_engine import engine
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DDL_DIR = PROJECT_ROOT / "sql" / "ddl"

DDL_FILES = [
    "01_create_raw_tables.sql",
    "02_create_quality_audit_tables.sql",
    "03_create_quarantine_tables.sql",
    "04_create_clean_tables.sql",
    "05_create_dependency_exclusions.sql",
    "06_create_anomaly_tables.sql",
    "07_create_root_cause_tables.sql",
    "08_create_business_impact_tables.sql",
    "09_create_metric_reliability_tables.sql",
]

def create_schemas():
    """Create the PostgreSQL schemas required by DataTrust."""

    schemas = [
        "raw",
        "quality",
        "quarantine",
        "clean",
        "analytics",
    ]

    with engine.begin() as connection:
        for schema in schemas:
            connection.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            )

    print("Required schemas verified.")


def execute_sql_file(sql_path):
    """Execute one SQL file as a single transaction."""

    sql_script = sql_path.read_text()

    raw_connection = engine.raw_connection()

    try:
        cursor = raw_connection.cursor()
        cursor.execute(sql_script)
        raw_connection.commit()
        cursor.close()

    except Exception:
        raw_connection.rollback()
        raise

    finally:
        raw_connection.close()


def setup_database():
    """Create the database objects required by DataTrust."""

    print("\nSetting up DataTrust database...")
    create_schemas()
    for file_name in DDL_FILES:
        sql_path = DDL_DIR / file_name

        if not sql_path.exists():
            raise FileNotFoundError(
                f"Required DDL file not found: {sql_path}"
            )

        print(f"Running {file_name}...")
        execute_sql_file(sql_path)

    print("\nDatabase setup completed successfully.")


if __name__ == "__main__":
    setup_database()