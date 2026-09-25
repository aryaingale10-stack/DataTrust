# =========================================================
# DataTrust
# Raw Data Ingestion Pipeline
# =========================================================
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
INCOMING_DIR = PROJECT_ROOT / "data" / "incoming"


# ---------------------------------------------------------
# PostgreSQL Configuration
# ---------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Check the .env file."
    )

# ---------------------------------------------------------
# Database Engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# ---------------------------------------------------------
# Database Connection Test
# ---------------------------------------------------------

def test_database_connection():
    """Verify that the ingestion pipeline can connect to PostgreSQL."""

    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as connection:
            print("PostgreSQL connection successful.")
            print("Database: datatrust")

    except Exception as error:
        print("PostgreSQL connection failed.")
        print(f"Error: {error}")
        raise

    finally:
        engine.dispose()

# ---------------------------------------------------------
# Customers Ingestion
# ---------------------------------------------------------

def load_customers():
    """Load customers.csv into the raw.customers PostgreSQL table."""

    file_path = INCOMING_DIR / "customers.csv"

    print(f"Reading: {file_path.name}")

    customers_df = pd.read_csv(file_path)

    print(f"Source rows: {len(customers_df):,}")
    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.customers;"))

    print("Cleared existing rows from raw.customers.")
    customers_df.to_sql(
        name="customers",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(f"Loaded {len(customers_df):,} rows into raw.customers.")

    # ---------------------------------------------------------
# Products Ingestion
# ---------------------------------------------------------

def load_products():
    """Load products.xlsx into the raw.products PostgreSQL table."""

    file_path = INCOMING_DIR / "products.xlsx"

    print(f"Reading: {file_path.name}")

    products_df = pd.read_excel(file_path)

    print(f"Source rows: {len(products_df):,}")
    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.products;"))

    print("Cleared existing rows from raw.products.")
    products_df.to_sql(
        name="products",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(f"Loaded {len(products_df):,} rows into raw.products.")

 # ---------------------------------------------------------
# Orders Ingestion
# ---------------------------------------------------------

def load_orders():
    """Load orders.csv into the raw.orders PostgreSQL table."""

    file_path = INCOMING_DIR / "orders.csv"

    print(f"Reading: {file_path.name}")

    orders_df = pd.read_csv(file_path)

    print(f"Source rows: {len(orders_df):,}")
    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.orders;"))

    print("Cleared existing rows from raw.orders.")
    orders_df.to_sql(
        name="orders",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(f"Loaded {len(orders_df):,} rows into raw.orders.")   

# ---------------------------------------------------------
# Order Items Ingestion
# ---------------------------------------------------------

def load_order_items():
    """Load order_items.csv into the raw.order_items PostgreSQL table."""

    file_path = INCOMING_DIR / "order_items.csv"

    print(f"Reading: {file_path.name}")

    order_items_df = pd.read_csv(file_path)

    print(f"Source rows: {len(order_items_df):,}")

    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.order_items;"))

    print("Cleared existing rows from raw.order_items.")
    order_items_df.to_sql(
        name="order_items",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(
        f"Loaded {len(order_items_df):,} rows "
        "into raw.order_items."
    )

# ---------------------------------------------------------
# Payments Ingestion
# ---------------------------------------------------------

def load_payments():
    """Load payments.csv into the raw.payments PostgreSQL table."""

    file_path = INCOMING_DIR / "payments.csv"

    print(f"Reading: {file_path.name}")

    payments_df = pd.read_csv(file_path)

    print(f"Source rows: {len(payments_df):,}")
    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.payments;"))

    print("Cleared existing rows from raw.payments.")
    payments_df.to_sql(
        name="payments",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(f"Loaded {len(payments_df):,} rows into raw.payments.")

# ---------------------------------------------------------
# Returns Ingestion
# ---------------------------------------------------------

def load_returns():
    """Load returns.csv into the raw.returns PostgreSQL table."""

    file_path = INCOMING_DIR / "returns.csv"

    print(f"Reading: {file_path.name}")

    returns_df = pd.read_csv(file_path)

    print(f"Source rows: {len(returns_df):,}")
    # Clear existing raw data before reloading
    with engine.begin() as connection:
     connection.execute(text("TRUNCATE TABLE raw.returns;"))

    print("Cleared existing rows from raw.returns.")
    returns_df.to_sql(
        name="returns",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000
    )

    print(f"Loaded {len(returns_df):,} rows into raw.returns.")

if __name__ == "__main__":
    test_database_connection()

    print("\nStarting raw data ingestion...\n")

    load_customers()
    load_products()
    load_orders()
    load_order_items()
    load_payments()
    load_returns()

    print("\nRaw data ingestion completed successfully.")
   