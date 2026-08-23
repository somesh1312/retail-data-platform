import os
import shutil
import subprocess
import glob

from datetime import timedelta

import pendulum

from airflow.sdk import dag, task


PROJECT_ROOT = "/opt/retail-data-platform"

LANDING_DIR = os.path.join(
    PROJECT_ROOT,
    "landing",
    "orders",
)

ARCHIVE_DIR = os.path.join(
    PROJECT_ROOT,
    "archive",
    "orders",
)


@dag(
    dag_id="retail_daily_pipeline",
    schedule="0 19 * * *",
    start_date=pendulum.datetime(
        2026,
        8,
        23,
        tz="America/Chicago",
    ),
    catchup=False,
    max_active_runs=1,
    tags=[
        "retail",
        "dbt",
        "production",
    ],
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
)
def retail_daily_pipeline():

    # ==================================================
    # FIND ORDER FILE
    # ==================================================

    @task()
    def find_order_file():

        pattern = os.path.join(
            LANDING_DIR,
            "orders_*.csv",
        )

        files = sorted(
            glob.glob(pattern)
        )

        if not files:
            raise FileNotFoundError(
                "No order files found in "
                f"{LANDING_DIR}"
            )

        file_path = files[0]

        print(
            f"Found incoming file: {file_path}"
        )

        return file_path


    # ==================================================
    # INGEST ORDERS
    # ==================================================

    @task()
    def ingest_orders(file_path):

        from ingestion.ingest_daily_orders import ingest_daily_orders

        print(
            f"Starting ingestion for: {file_path}"
        )

        ingest_daily_orders(
            file_path
        )

        print(
            f"Ingestion completed for: {file_path}"
        )

        return file_path


    # ==================================================
    # RUN DBT BUILD
    # ==================================================

    @task()
    def run_dbt():

        dbt_project_dir = os.path.join(
            PROJECT_ROOT,
            "retail_analytics",
        )

        command = [
            "dbt",
            "build",
            "--project-dir",
            dbt_project_dir,
            "--profiles-dir",
            dbt_project_dir,
        ]

        print(
            "Running dbt build..."
        )

        result = subprocess.run(
            command,
            cwd=dbt_project_dir,
            check=True,
            text=True,
        )

        print(
            "dbt build completed successfully."
        )

        return result.returncode


    # ==================================================
    # ARCHIVE SUCCESSFUL FILE
    # ==================================================

    @task()
    def archive_order_file(file_path):

        os.makedirs(
            ARCHIVE_DIR,
            exist_ok=True,
        )

        destination = os.path.join(
            ARCHIVE_DIR,
            os.path.basename(file_path),
        )

        shutil.move(
            file_path,
            destination,
        )

        print(
            f"Archived file to: {destination}"
        )

        return destination


    # ==================================================
    # TASK DEPENDENCIES
    # ==================================================

    order_file = find_order_file()

    ingested_file = ingest_orders(
        order_file
    )

    dbt_result = run_dbt()

    archived_file = archive_order_file(
        ingested_file
    )

    ingested_file >> dbt_result >> archived_file


retail_daily_pipeline()