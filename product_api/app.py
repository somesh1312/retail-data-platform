import json
import os

from fastapi import FastAPI


app = FastAPI(
    title="Retail Product API",
    version="1.0"
)


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


def load_products():

    with open(PRODUCT_FILE, "r") as file:
        return json.load(file)


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.get("/products")
def get_products():

    return load_products()