import os
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from ingestion.database import get_postgres_engine


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ORDER_FILE = os.path.join(
    BASE_DIR,
    "data",
    "orders.csv"
)


def ingest_orders():

    print("Starting orders ingestion...")

    # --------------------------------------------------
    # 1. READ SOURCE FILE
    # --------------------------------------------------

    df = pd.read_csv(ORDER_FILE)

    print(
        f"Read {len(df)} orders from CSV."
    )

    if df.empty:
        raise ValueError(
            "Orders file contains no records."
        )


    # --------------------------------------------------
    # 2. VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------

    required_columns = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_pct",
        "total_amount",
        "status",
        "order_date",
        "updated_at"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )


    # --------------------------------------------------
    # 3. ADD INGESTION METADATA
    # --------------------------------------------------

    df["loaded_at"] = datetime.now(
        timezone.utc
    )


    # --------------------------------------------------
    # 4. CONNECT TO POSTGRES
    # --------------------------------------------------

    engine = get_postgres_engine()


    # --------------------------------------------------
    # 5. CLEAR EXISTING RAW DATA
    #
    # IMPORTANT:
    # We use TRUNCATE instead of pandas
    # if_exists="replace".
    #
    # replace would DROP raw.orders.
    # dbt's silver.stg_orders depends on that table,
    # so PostgreSQL would reject the DROP.
    #
    # TRUNCATE removes rows while preserving the table.
    # --------------------------------------------------

    with engine.begin() as connection:

        connection.execute(
            text(
                "TRUNCATE TABLE raw.orders"
            )
        )

        print(
            "Cleared existing rows from raw.orders."
        )


    # --------------------------------------------------
    # 6. LOAD NEW DATA
    # --------------------------------------------------

    df.to_sql(
        "orders",
        engine,
        schema="raw",

        # IMPORTANT:
        # append because the table already exists.
        if_exists="append",

        index=False,

        # Insert rows in batches.
        chunksize=1000
    )


    print(
        f"Loaded {len(df)} rows into raw.orders."
    )


if __name__ == "__main__":
    ingest_orders()