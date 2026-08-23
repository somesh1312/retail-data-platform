import pandas as pd
import pytest

from ingestion.ingest_daily_orders import (
    validate_dataframe
)


def valid_order():

    return {
        "order_id": 1,
        "customer_id": 1,
        "product_id": 1,
        "quantity": 1,
        "unit_price": 25.00,
        "discount_pct": 0,
        "total_amount": 25.00,
        "status": "completed",
        "order_date":
            "2026-08-23T12:00:00",
        "updated_at":
            "2026-08-23T12:00:00",
    }


def test_valid_order_passes():

    df = pd.DataFrame(
        [valid_order()]
    )

    validate_dataframe(df)


def test_missing_order_id_fails():

    order = valid_order()

    del order["order_id"]

    df = pd.DataFrame(
        [order]
    )

    with pytest.raises(
        ValueError
    ):

        validate_dataframe(df)


def test_duplicate_order_ids_fail():

    order_one = valid_order()

    order_two = valid_order()

    df = pd.DataFrame(
        [
            order_one,
            order_two
        ]
    )

    with pytest.raises(
        ValueError
    ):

        validate_dataframe(df)