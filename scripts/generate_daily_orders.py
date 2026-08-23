import argparse
import json
import os
import random
from datetime import datetime, timedelta


import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PRODUCT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "products.json"
)

LANDING_DIR = os.path.join(
    BASE_DIR,
    "landing",
    "orders"
)


def get_current_max_order_id():

    from ingestion.database import get_postgres_engine

    engine = get_postgres_engine()

    query = """
        SELECT COALESCE(MAX(order_id), 0)
        AS max_order_id
        FROM raw.orders
    """

    result = pd.read_sql(
        query,
        engine
    )

    return int(
        result["max_order_id"].iloc[0]
    )


def generate_orders(
    order_date: str,
    number_of_orders: int
):

    os.makedirs(
        LANDING_DIR,
        exist_ok=True
    )

    with open(PRODUCT_FILE, "r") as file:
        products = json.load(file)

    product_lookup = {
        product["product_id"]: product
        for product in products
    }

    max_order_id = get_current_max_order_id()

    print(
        f"Current maximum order ID: "
        f"{max_order_id}"
    )

    requested_date = datetime.strptime(
        order_date,
        "%Y-%m-%d"
    )

    statuses = [
        "completed",
        "completed",
        "completed",
        "shipped",
        "processing",
        "cancelled",
    ]

    records = []

    for i in range(1, number_of_orders + 1):

        order_id = max_order_id + i

        customer_id = random.randint(
            1,
            500
        )

        product_id = random.randint(
            1,
            100
        )

        product = product_lookup[
            product_id
        ]

        quantity = random.randint(
            1,
            5
        )

        unit_price = float(
            product["price"]
        )

        discount_pct = random.choice(
            [
                0,
                0,
                0,
                5,
                10,
                15,
                20,
            ]
        )

        subtotal = (
            quantity * unit_price
        )

        total_amount = (
            subtotal *
            (1 - discount_pct / 100)
        )

        seconds_into_day = random.randint(
            0,
            86399
        )

        timestamp = (
            requested_date +
            timedelta(
                seconds=seconds_into_day
            )
        )

        records.append(
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_pct": discount_pct,
                "total_amount": round(
                    total_amount,
                    2
                ),
                "status": random.choice(
                    statuses
                ),
                "order_date":
                    timestamp.isoformat(),
                "updated_at":
                    timestamp.isoformat(),
            }
        )

    df = pd.DataFrame(
        records
    )

    output_file = os.path.join(
        LANDING_DIR,
        f"orders_{order_date}.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()
    print(
        f"Generated {len(df)} orders."
    )
    print(
        f"Created: {output_file}"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--date",
        required=True,
        help="Order date YYYY-MM-DD"
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=100,
        help="Number of orders"
    )

    args = parser.parse_args()

    generate_orders(
        order_date=args.date,
        number_of_orders=args.rows
    )