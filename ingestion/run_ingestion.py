from ingestion.ingest_orders import ingest_orders
from ingestion.ingest_inventory import ingest_inventory
from ingestion.ingest_customers import ingest_customers
from ingestion.ingest_products import ingest_products


def run():

    print("=" * 60)
    print("RETAIL DATA INGESTION STARTED")
    print("=" * 60)

    ingest_customers()
    ingest_products()
    ingest_orders()
    ingest_inventory()

    print("=" * 60)
    print("RETAIL DATA INGESTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run()