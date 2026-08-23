import os
import sqlite3
from datetime import datetime, timezone

import pandas as pd

from ingestion.database import get_postgres_engine


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CUSTOMER_DB = os.path.join(
    BASE_DIR,
    "source_db",
    "customers.db"
)


def ingest_customers():

    print("Starting customer ingestion...")

    sqlite_connection = sqlite3.connect(
        CUSTOMER_DB
    )

    query = """
        SELECT *
        FROM customers
    """

    df = pd.read_sql(
        query,
        sqlite_connection
    )

    sqlite_connection.close()

    if df.empty:
        raise ValueError(
            "Customer source returned no records."
        )

    print(
        f"Read {len(df)} customers from CRM."
    )

    df["loaded_at"] = datetime.now(
        timezone.utc
    )

    postgres_engine = get_postgres_engine()

    df.to_sql(
        "customers",
        postgres_engine,
        schema="raw",
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {len(df)} rows into raw.customers."
    )


if __name__ == "__main__":
    ingest_customers()