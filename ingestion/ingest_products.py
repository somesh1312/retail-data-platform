import os
from datetime import datetime, timezone

import pandas as pd
import requests

from dotenv import load_dotenv

from ingestion.database import get_postgres_engine


load_dotenv()


def ingest_products():

    print("Starting product API ingestion...")

    api_url = os.getenv(
        "PRODUCT_API_URL"
    )

    response = requests.get(
        api_url,
        timeout=30
    )

    response.raise_for_status()

    products = response.json()

    if not products:
        raise ValueError(
            "Product API returned no data."
        )

    df = pd.DataFrame(products)

    print(
        f"Received {len(df)} products from API."
    )

    df["loaded_at"] = datetime.now(
        timezone.utc
    )

    engine = get_postgres_engine()

    df.to_sql(
        "products",
        engine,
        schema="raw",
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {len(df)} rows into raw.products."
    )


if __name__ == "__main__":
    ingest_products()