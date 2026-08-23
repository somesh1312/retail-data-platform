# Retail Data Platform

A production-style end-to-end data engineering platform that ingests daily retail data, orchestrates data pipelines with Apache Airflow, transforms warehouse data using dbt, validates data quality, and deploys through a CI/CD workflow.

The project is designed to simulate how a retail organization could process daily transactional data from operational systems into analytics-ready datasets.

---

## Overview

Retail organizations generate data across multiple operational systems including orders, customers, products, and inventory.

This project implements a data platform that:

- Ingests data from multiple retail sources
- Processes newly arriving order files incrementally
- Loads raw data into PostgreSQL
- Transforms data using dbt
- Organizes transformations into staging, intermediate, and marts layers
- Applies automated data quality tests
- Orchestrates the pipeline with Apache Airflow
- Archives successfully processed files
- Runs infrastructure locally using Docker Compose
- Validates code automatically with GitHub Actions
- Supports automated deployment to an EC2 environment

The goal is to model a realistic production data engineering workflow rather than a one-time batch transformation.

---

## Architecture

```text
                  RETAIL SOURCE SYSTEMS
                          |
        +-----------------+------------------+
        |                 |                  |
     Orders            Customers         Products/
      CSV               Source           Inventory
        |                 |                  |
        +-----------------+------------------+
                          |
                          v
                  Python Ingestion
                          |
                          v
                  PostgreSQL Warehouse
                          |
                    raw / bronze
                          |
                          v
                         dbt
                          |
              +-----------+-----------+
              |                       |
           Staging                Intermediate
           / Silver                    |
              |                        |
              +-----------+------------+
                          |
                          v
                     Data Marts
                       / Gold
                          |
                          v
                 Analytics-Ready Data


                    ORCHESTRATION

                  Apache Airflow
                        |
        +---------------+---------------+
        |               |               |
 Find New File  ->  Ingest Orders -> Run dbt
                                      |
                                      v
                                 Archive File


                     DEVOPS

Developer -> Git -> GitHub -> GitHub Actions
                              |
                        +-----+------+
                        |            |
                       CI            CD
                        |            |
                 Python Tests       EC2
                 dbt Validation      |
                 Docker Build        v
                                  Docker
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Transformation | dbt |
| Database / Warehouse | PostgreSQL |
| Orchestration | Apache Airflow |
| Containers | Docker, Docker Compose |
| Testing | pytest, dbt tests |
| CI/CD | GitHub Actions |
| Cloud Deployment | AWS EC2 |
| Version Control | Git / GitHub |
| API | FastAPI |
| Data Format | CSV / SQL |

---

## Project Structure

```text
retail-data-platform/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── airflow/
│   └── dags/
│       └── retail_daily_pipeline.py
│
├── archive/
│   └── orders/
│
├── ingestion/
│   ├── database.py
│   ├── ingest_customers.py
│   ├── ingest_daily_orders.py
│   ├── ingest_inventory.py
│   ├── ingest_orders.py
│   ├── ingest_products.py
│   └── run_ingestion.py
│
├── landing/
│   └── orders/
│
├── product_api/
│
├── retail_analytics/
│   ├── models/
│   ├── macros/
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── scripts/
│   ├── generate_data.py
│   └── generate_daily_orders.py
│
├── tests/
│
├── Dockerfile.airflow
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
├── requirements-airflow.txt
└── README.md
```

---

## Daily Pipeline

The platform simulates daily retail order processing.

A new order file arrives in:

```text
landing/orders/
```

For example:

```text
orders_2026-08-23.csv
```

Airflow orchestrates the complete lifecycle.

### 1. Detect incoming order file

Airflow checks the landing directory for a new order file.

```text
landing/orders/
        |
        v
find_order_file
```

### 2. Ingest orders

The ingestion layer reads the file and loads the records into the PostgreSQL warehouse.

```text
CSV
 |
 v
Python ingestion
 |
 v
PostgreSQL raw tables
```

The ingestion process is designed to append newly arriving transactional data instead of recreating the raw table on every execution.

### 3. Transform with dbt

After ingestion succeeds, Airflow executes the dbt transformation workflow.

```text
Raw Data
   |
   v
Staging
   |
   v
Intermediate
   |
   v
Marts
```

dbt handles transformation logic, dependency management, documentation, and data quality validation.

### 4. Archive processed file

Only after successful ingestion and transformation is the processed file moved from:

```text
landing/orders/
```

to:

```text
archive/orders/
```

This prevents successfully processed files from being repeatedly ingested and provides a basic processing history.

---

## Airflow DAG

The daily pipeline follows:

```text
find_order_file
       |
       v
 ingest_orders
       |
       v
    run_dbt
       |
       v
archive_order_file
```

A task failure prevents downstream processing.

This ensures, for example, that a source file is not archived when ingestion or transformation fails.

---

## dbt Transformation Architecture

The dbt project separates transformations into logical layers.

### Raw / Bronze

Raw source data is loaded into PostgreSQL with minimal transformation.

Examples include:

```text
raw.orders
raw.customers
raw.products
raw.inventory
```

### Staging / Silver

Staging models clean and standardize source data.

Typical operations include:

- column renaming
- type casting
- null handling
- standardization
- basic validation

### Intermediate

Intermediate models contain reusable business transformation logic used by downstream models.

### Marts / Gold

Mart models expose analytics-ready business datasets.

These models are intended to support reporting, dashboards, and downstream analytical applications.

---

## Data Quality

Data quality is validated through dbt tests and Python tests.

Examples include:

- primary identifiers must not be null
- identifiers expected to be unique are validated
- relationships between models are tested
- ingestion logic is tested independently
- dbt project parsing is validated during CI

Run Python tests with:

```bash
pytest -v
```

Run dbt tests with:

```bash
dbt test \
  --project-dir retail_analytics \
  --profiles-dir retail_analytics
```

---

## Local Development

### Prerequisites

Install:

- Python 3.11+
- Docker Desktop
- Git
- dbt-postgres

Clone the repository:

```bash
git clone https://github.com/somesh1312/retail-data-platform.git
cd retail-data-platform
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Platform

Start the Docker environment:

```bash
docker compose up -d
```

Check running services:

```bash
docker compose ps
```

The environment contains separate PostgreSQL services for application/data workloads and Airflow metadata.

Open the Airflow UI and locate:

```text
retail_daily_pipeline
```

The DAG can then be triggered manually for development and testing.

---

## Simulating Daily Orders

Daily order files can be generated to simulate an upstream retail system publishing new transactions.

Run:

```bash
python scripts/generate_daily_orders.py
```

A new file is placed into:

```text
landing/orders/
```

Airflow can then process the file through the normal pipeline.

After successful processing:

```text
landing/orders/
        |
        v
PostgreSQL
        |
        v
dbt transformations
        |
        v
archive/orders/
```

---

## CI Pipeline

Every pull request is validated using GitHub Actions.

The CI workflow performs multiple independent checks:

```text
Pull Request
     |
     +------> Python Tests
     |
     +------> dbt Validation
     |
     +------> Docker Build
```

### Python Tests

Validates Python application and ingestion logic.

### dbt Validation

Ensures that the dbt project and model dependency graph can be successfully parsed.

### Docker Build

Confirms that the Airflow runtime image can be built successfully.

Code should pass all CI checks before being merged into `main`.

---

## Continuous Deployment

Changes merged into `main` can trigger the CD workflow.

```text
Pull Request
      |
      v
CI Validation
      |
      v
Merge to main
      |
      v
Build Production Image
      |
      v
Container Registry
      |
      v
AWS EC2
      |
      v
Docker Compose
      |
      v
Production Services
```

The deployment workflow connects to the EC2 host and updates the production environment using Docker Compose.

> The cloud deployment portion of this project is currently being finalized and hardened.

---

## Development Workflow

Changes are developed using feature branches rather than directly on `main`.

Example:

```bash
git checkout -b feature/new-feature
```

After development:

```bash
git add .
git commit -m "Add new feature"
git push -u origin feature/new-feature
```

A pull request is then opened against `main`.

GitHub Actions validates the change before merge.

This workflow provides:

```text
Feature Branch
      |
      v
Pull Request
      |
      v
Automated CI
      |
      v
Code Review / Validation
      |
      v
main
      |
      v
Deployment
```

---

## Production Engineering Concepts Demonstrated

This project demonstrates more than SQL transformations.

It includes:

- End-to-end pipeline ownership
- Multi-source data ingestion
- Incremental daily data processing
- Workflow orchestration
- Pipeline dependency management
- Containerized runtime environments
- Data quality testing
- Failure handling