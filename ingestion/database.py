import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


def get_postgres_engine():

    host = os.getenv("POSTGRES_HOST", "localhost")

    port = os.getenv(
        "POSTGRES_PORT",
        "5432"
    )

    database = os.getenv(
        "POSTGRES_DB",
        "retail_dw"
    )

    user = os.getenv(
        "POSTGRES_USER",
        "retail"
    )

    password = os.getenv(
        "POSTGRES_PASSWORD",
        "retail"
    )

    connection_string = (

        "postgresql+psycopg2://"

        f"{user}:{password}"

        f"@{host}:{port}/{database}"
    )

    return create_engine(
        connection_string,
        pool_pre_ping=True
    )