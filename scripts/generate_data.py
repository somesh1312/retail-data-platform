import os
import random
import sqlite3
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


fake = Faker()
random.seed(42)
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_DB_DIR = os.path.join(BASE_DIR, "source_db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SOURCE_DB_DIR, exist_ok=True)


# ---------------------------------------------------------
# 1. CUSTOMERS
# ---------------------------------------------------------

customers = []

for customer_id in range(1, 501):

    created_at = fake.date_between(
        start_date="-3y",
        end_date="today"
    )

    customers.append({
        "customer_id": customer_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "state": fake.state_abbr(),
        "membership_tier": random.choice(
            ["Bronze", "Silver", "Gold"]
        ),
        "created_at": created_at.isoformat()
    })


customers_df = pd.DataFrame(customers)


# ---------------------------------------------------------
# SAVE CUSTOMERS TO SQLITE
# ---------------------------------------------------------

customer_db_path = os.path.join(
    SOURCE_DB_DIR,
    "customers.db"
)

conn = sqlite3.connect(customer_db_path)

customers_df.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

conn.close()


# ---------------------------------------------------------
# 2. PRODUCTS
# ---------------------------------------------------------

products = []

categories = [
    "Handbags",
    "Jewelry",
    "Wallets",
    "Accessories",
    "Footwear"
]

for product_id in range(1, 101):

    products.append({
        "product_id": product_id,
        "product_name": f"Product {product_id}",
        "category": random.choice(categories),
        "price": round(random.uniform(10, 250), 2),
        "active": random.choice([True, True, True, False])
    })


products_df = pd.DataFrame(products)

products_df.to_json(
    os.path.join(DATA_DIR, "products.json"),
    orient="records",
    indent=2
)


# ---------------------------------------------------------
# 3. ORDERS
# ---------------------------------------------------------

orders = []

statuses = [
    "completed",
    "completed",
    "completed",
    "shipped",
    "processing",
    "cancelled"
]

start_date = datetime.now() - timedelta(days=180)

for order_id in range(1, 5001):

    customer_id = random.randint(1, 500)
    product_id = random.randint(1, 100)

    quantity = random.randint(1, 5)

    product_price = float(
        products_df.loc[
            products_df["product_id"] == product_id,
            "price"
        ].iloc[0]
    )

    discount = random.choice([
        0,
        0,
        0,
        5,
        10,
        15,
        20
    ])

    subtotal = quantity * product_price

    total_amount = subtotal * (
        1 - discount / 100
    )

    order_date = start_date + timedelta(
        minutes=random.randint(
            0,
            180 * 24 * 60
        )
    )

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": product_price,
        "discount_pct": discount,
        "total_amount": round(total_amount, 2),
        "status": random.choice(statuses),
        "order_date": order_date.isoformat(),
        "updated_at": order_date.isoformat()
    })


orders_df = pd.DataFrame(orders)

orders_df.to_csv(
    os.path.join(DATA_DIR, "orders.csv"),
    index=False
)


# ---------------------------------------------------------
# 4. INVENTORY
# ---------------------------------------------------------

inventory = []

warehouses = [
    "Los Angeles",
    "Dallas",
    "Chicago"
]

for product_id in range(1, 101):

    for warehouse in warehouses:

        inventory.append({
            "product_id": product_id,
            "warehouse": warehouse,
            "quantity_on_hand": random.randint(0, 250),
            "reorder_level": random.randint(10, 50),
            "last_updated": datetime.now().isoformat()
        })


inventory_df = pd.DataFrame(inventory)

inventory_df.to_csv(
    os.path.join(DATA_DIR, "inventory.csv"),
    index=False
)


print("Retail data generated successfully.")
print()
print(f"Customers: {len(customers_df)}")
print(f"Products: {len(products_df)}")
print(f"Orders: {len(orders_df)}")
print(f"Inventory rows: {len(inventory_df)}")