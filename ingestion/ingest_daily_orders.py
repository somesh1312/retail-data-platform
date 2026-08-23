import os
from datetime import datetime, timezone

import pandas as pd

from sqlalchemy import text

from ingestion.database import (
    get_postgres_engine
)


REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "discount_pct",
    "total_amount",
    "status",
    "order_date",
    "updated_at",
]


def validate_dataframe(df):

    if df.empty:
        raise ValueError(
            "Daily orders file is empty."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    if df["order_id"].isna().any():

        raise ValueError(
            "order_id contains NULL values."
        )

    if df["order_id"].duplicated().any():

        raise ValueError(
            "Duplicate order_id values "
            "exist inside incoming file."
        )


def has_file_been_processed(
    connection,
    file_name
):

    result = connection.execute(
        text(
            """
            SELECT status
            FROM raw.ingestion_control

            WHERE file_name = :file_name
            """
        ),
        {
            "file_name": file_name
        }
    ).fetchone()

    return (
        result is not None
        and result[0] == "SUCCESS"
    )


def ingest_daily_orders(
    file_path
):

    file_name = os.path.basename(
        file_path
    )

    print("=" * 60)
    print("DAILY ORDER INGESTION")
    print("=" * 60)

    print(
        f"Incoming file: {file_name}"
    )

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            f"File not found: "
            f"{file_path}"
        )

    engine = get_postgres_engine()

    # ------------------------------------------------
    # CHECK WHETHER FILE ALREADY RAN
    # ------------------------------------------------

    with engine.begin() as connection:

        if has_file_been_processed(
            connection,
            file_name
        ):

            print(
                "File has already been "
                "successfully processed."
            )

            print(
                "Skipping to protect "
                "against duplicate loading."
            )

            return

    # ------------------------------------------------
    # RECORD START
    # ------------------------------------------------

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                INSERT INTO
                raw.ingestion_control
                (
                    file_name,
                    source_name,
                    status,
                    started_at
                )

                VALUES
                (
                    :file_name,
                    'orders',
                    'RUNNING',
                    NOW()
                )

                ON CONFLICT (file_name)
                DO UPDATE

                SET
                    status = 'RUNNING',
                    started_at = NOW(),
                    completed_at = NULL,
                    error_message = NULL
                """
            ),
            {
                "file_name": file_name
            }
        )

    try:

        # --------------------------------------------
        # READ FILE
        # --------------------------------------------

        df = pd.read_csv(
            file_path
        )

        print(
            f"Rows received: {len(df)}"
        )

        # --------------------------------------------
        # VALIDATE
        # --------------------------------------------

        validate_dataframe(df)

        print(
            "Input validation passed."
        )

        # --------------------------------------------
        # NORMALIZE TYPES
        # --------------------------------------------

        df["order_date"] = (
            pd.to_datetime(
                df["order_date"]
            )
        )

        df["updated_at"] = (
            pd.to_datetime(
                df["updated_at"]
            )
        )

        df["loaded_at"] = (
            datetime.now(
                timezone.utc
            )
        )

        # --------------------------------------------
        # LOAD INTO TEMPORARY STAGING TABLE
        # --------------------------------------------

        staging_table = (
            "orders_daily_stage"
        )

        df.to_sql(
            staging_table,
            engine,
            schema="raw",
            if_exists="replace",
            index=False,
            chunksize=1000
        )

        print(
            "Loaded incoming data into "
            "raw.orders_daily_stage."
        )

        # --------------------------------------------
        # UPSERT INTO RAW.ORDERS
        # --------------------------------------------

        upsert_sql = """
        INSERT INTO raw.orders
        (
            order_id,
            customer_id,
            product_id,
            quantity,
            unit_price,
            discount_pct,
            total_amount,
            status,
            order_date,
            updated_at,
            loaded_at
        )

        SELECT

            order_id,
            customer_id,
            product_id,
            quantity,
            unit_price,
            discount_pct,
            total_amount,
            status,
            order_date,
            updated_at,
            loaded_at

        FROM raw.orders_daily_stage

        ON CONFLICT (order_id)

        DO UPDATE SET

            customer_id =
                EXCLUDED.customer_id,

            product_id =
                EXCLUDED.product_id,

            quantity =
                EXCLUDED.quantity,

            unit_price =
                EXCLUDED.unit_price,

            discount_pct =
                EXCLUDED.discount_pct,

            total_amount =
                EXCLUDED.total_amount,

            status =
                EXCLUDED.status,

            order_date =
                EXCLUDED.order_date,

            updated_at =
                EXCLUDED.updated_at,

            loaded_at =
                EXCLUDED.loaded_at;
        """

        with engine.begin() as connection:

            connection.execute(
                text(upsert_sql)
            )

        print(
            f"Upserted {len(df)} rows "
            f"into raw.orders."
        )

        # --------------------------------------------
        # MARK SUCCESS
        # --------------------------------------------

        with engine.begin() as connection:

            connection.execute(
                text(
                    """
                    UPDATE
                    raw.ingestion_control

                    SET
                        status = 'SUCCESS',
                        row_count = :row_count,
                        completed_at = NOW()

                    WHERE
                        file_name = :file_name
                    """
                ),
                {
                    "row_count": len(df),
                    "file_name": file_name,
                }
            )

        print(
            "Ingestion completed successfully."
        )

    except Exception as error:

        # --------------------------------------------
        # MARK FAILURE
        # --------------------------------------------

        with engine.begin() as connection:

            connection.execute(
                text(
                    """
                    UPDATE
                    raw.ingestion_control

                    SET
                        status = 'FAILED',
                        completed_at = NOW(),
                        error_message =
                            :error_message

                    WHERE
                        file_name =
                            :file_name
                    """
                ),
                {
                    "error_message":
                        str(error),

                    "file_name":
                        file_name,
                }
            )

        print(
            f"Ingestion FAILED: {error}"
        )

        raise