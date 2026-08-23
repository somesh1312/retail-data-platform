import os
from datetime import datetime, timezone

import pandas as pd

from ingestion.database import get_postgres_engine


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INVENTORY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "inventory.csv"
)


def ingest_inventory():

    print("Starting inventory ingestion...")

    df = pd.read_csv(INVENTORY_FILE)

    if df.empty:
        raise ValueError(
            "Inventory file contains no records."
        )

    print(
        f"Read {len(df)} inventory records."
    )

    df["loaded_at"] = datetime.now(
        timezone.utc
    )

    engine = get_postgres_engine()

    df.to_sql(
        "inventory",
        engine,
        schema="raw",
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {len(df)} rows into raw.inventory."
    )


if __name__ == "__main__":
    ingest_inventory()