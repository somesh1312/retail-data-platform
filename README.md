# Retail Data Platform

A production-style batch data platform demonstrating how daily retail data can be ingested from heterogeneous sources, orchestrated through Apache Airflow, transformed and tested with dbt, containerized with Docker, and automatically deployed to AWS through CI/CD.

The project focuses not only on moving data, but on the operational concerns that make pipelines reliable: incremental processing, idempotency, data quality, orchestration, automated testing, reproducible environments, and deployment automation.

---

## Architecture

```text
                     RETAIL SOURCE SYSTEMS
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
      Orders CSV         Product JSON/API     Customer DB
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    Python Ingestion Layer
                              │
                              ▼
                       PostgreSQL Warehouse
                              │
                 ┌────────────┴────────────┐
                 │                         │
               RAW                       dbt
                 │                         │
                 ▼                         ▼
              SILVER                  Transform
                 │                         │
                 └────────────┬────────────┘
                              ▼
                             GOLD
                              │
              ┌───────────────┼────────────────┐
              │               │                │
        dim_customers    dim_products      fct_orders
                                              │
                              ┌───────────────┴──────────────┐
                              ▼                              ▼
                     mart_daily_sales            mart_inventory_health
```

### Orchestration

```text
find_order_file
       │
       ▼
ingest_orders
       │
       ▼
run_dbt
       │
       ▼
archive_order_file
```

Apache Airflow coordinates the complete daily workflow and ensures downstream processing only occurs after upstream dependencies succeed.

---

## Engineering Goals

This project was designed around several production data-engineering concerns:

- Multi-source ingestion
- Incremental data processing
- Idempotent pipeline execution
- Automated data quality testing
- Layered warehouse modeling
- Workflow orchestration
- Failure-safe file handling
- Containerized runtime environments
- Continuous integration
- Automated deployment
- Reproducible infrastructure

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python, SQL |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Warehouse | PostgreSQL |
| Containerization | Docker / Docker Compose |
| CI/CD | GitHub Actions |
| Cloud Runtime | AWS EC2 |
| Container Registry | GitHub Container Registry |
| Source Control | Git / GitHub |

---

## Data Sources

The platform intentionally uses different source formats to simulate a heterogeneous business environment.

### Orders

Daily order batches arrive as CSV files.

```text
landing/orders/
└── orders_YYYY-MM-DD.csv
```

### Products

Product information is ingested from a JSON/API-style source.

### Customers

Customer information originates from a separate operational database.

### Inventory

Inventory data is independently ingested and joined with product information downstream.

The different source systems converge in PostgreSQL before dbt applies standardized transformation and modeling logic.

---

## Warehouse Layers

### Raw

Source-aligned data loaded with minimal transformation.

```text
raw.customers
raw.inventory
raw.orders
raw.products
```

### Silver

Cleaned and standardized dbt staging models.

```text
silver.stg_customers
silver.stg_inventory
silver.stg_orders
silver.stg_products
```

### Gold

Business-ready analytical models.

```text
gold.dim_customers
gold.dim_products
gold.fct_orders
gold.mart_daily_sales
gold.mart_inventory_health
```

This separation keeps ingestion concerns independent from transformation and analytical modeling.

---

## Incremental Processing

`fct_orders` is implemented as an incremental dbt model.

Rather than rebuilding the complete historical fact table on every execution, the pipeline processes new data incrementally while maintaining order-level uniqueness.

This becomes increasingly important as historical order volume grows.

---

## Idempotent Ingestion

Daily ingestion protects the warehouse from duplicate processing.

Before loading an incoming order file, the ingestion layer determines whether that file has already completed successfully.

Example:

```text
Incoming file: orders_2026-08-23.csv
File has already been successfully processed.
Skipping to protect against duplicate loading.
```

This allows pipeline retries and accidental file redelivery without duplicating previously processed data.

---

## Data Quality

Data quality checks are executed as part of the dbt build.

Tests validate properties including:

- Primary-key uniqueness
- Required/non-null fields
- Referential integrity
- Positive order amounts
- Model assumptions

Example successful execution:

```text
PASS=23
WARN=0
ERROR=0
SKIP=0
TOTAL=23
```

A failed quality check causes the transformation stage to fail rather than silently publishing invalid analytical data.

---

## Airflow Pipeline

Apache Airflow orchestrates daily processing.

```text
Incoming order file
        │
        ▼
Find eligible file
        │
        ▼
Ingest into PostgreSQL
        │
        ▼
Execute dbt build
        │
        ▼
Run transformations + tests
        │
        ▼
Archive successfully processed file
```

Files are archived only after successful downstream processing.

This prevents an unsuccessful batch from being incorrectly treated as completed.

---

## CI Pipeline

Pull requests and code changes are validated automatically through GitHub Actions.

The CI workflow performs:

```text
Code Change
    │
    ├── Python Tests
    │
    ├── dbt Validation
    │
    └── Docker Build
```

Changes must pass automated validation before they are considered deployable.

---

## Continuous Deployment

Changes merged to `main` trigger the deployment workflow.

```text
Merge to main
      │
      ▼
GitHub Actions
      │
      ▼
Build Docker Image
      │
      ▼
Publish to GHCR
      │
      ▼
Deploy to AWS EC2
      │
      ▼
Docker Compose
      │
      ├── Airflow API Server
      ├── Airflow Scheduler
      ├── Airflow DAG Processor
      ├── Airflow Triggerer
      ├── Airflow Metadata PostgreSQL
      └── Retail Warehouse PostgreSQL
```

This creates a repeatable deployment process instead of relying on manual server configuration after every code change.

---

## Repository Structure

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
├── ingestion/
│   ├── database.py
│   ├── ingest_customers.py
│   ├── ingest_daily_orders.py
│   ├── ingest_inventory.py
│   ├── ingest_orders.py
│   ├── ingest_products.py
│   └── run_ingestion.py
│
├── retail_analytics/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── tests/
│   ├── macros/
│   └── dbt_project.yml
│
├── landing/
│   └── orders/
│
├── archive/
│   └── orders/
│
├── failed/
│   └── orders/
│
├── product_api/
├── scripts/
├── tests/
│
├── Dockerfile.airflow
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md
```

---

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd retail-data-platform
```

### 2. Create environment configuration

```bash
cp .env.example .env
```

Update the required local environment variables.

Never commit `.env` or production credentials.

### 3. Start the platform

```bash
docker compose up -d --build
```

### 4. Verify containers

```bash
docker compose ps
```

### 5. Access Airflow

Open the locally configured Airflow port in your browser and trigger:

```text
retail_daily_pipeline
```

---

## Running dbt

Validate connectivity:

```bash
dbt debug \
  --project-dir retail_analytics \
  --profiles-dir retail_analytics
```

Build models and execute tests:

```bash
dbt build \
  --project-dir retail_analytics \
  --profiles-dir retail_analytics
```

Generate documentation:

```bash
dbt docs generate \
  --project-dir retail_analytics \
  --profiles-dir retail_analytics
```

Serve documentation locally:

```bash
dbt docs serve \
  --project-dir retail_analytics \
  --profiles-dir retail_analytics
```

---

## Example Daily Lifecycle

A new file arrives:

```text
landing/orders/orders_2026-08-24.csv
```

Airflow detects the batch and initiates ingestion.

Python loads eligible records into the raw warehouse.

dbt then transforms the data through:

```text
raw
 ↓
silver
 ↓
gold
```

Tests validate the resulting models.

After successful completion:

```text
landing/orders/orders_2026-08-24.csv
```

is moved to:

```text
archive/orders/orders_2026-08-24.csv
```

If the same completed batch is submitted again, duplicate-processing protection prevents it from being loaded twice.

---

## Reliability Features

The project deliberately includes operational behaviors commonly required in production pipelines.

**Idempotency**

Previously completed batches are not loaded twice.

**Incremental processing**

Historical fact data does not need to be rebuilt for every daily batch.

**Data quality gates**

Invalid data can prevent downstream analytical models from being published.

**Dependency management**

Airflow controls task execution order.

**Failure-safe archival**

Source files are archived only after successful processing.

**Reproducible environments**

Docker ensures development and deployment use consistent runtime dependencies.

**Automated validation**

GitHub Actions validates code before deployment.

**Automated delivery**

Successful main-branch changes can be built and deployed without manually rebuilding the production environment.

---

## What This Project Demonstrates

This repository is intentionally focused on the complete lifecycle of a data pipeline rather than only SQL transformation.

It demonstrates how I approach:

- designing ingestion workflows
- integrating heterogeneous data sources
- modeling analytical datasets
- implementing data-quality controls
- designing pipelines for safe retries
- orchestrating dependencies
- troubleshooting containerized data services
- automating validation
- deploying reproducible environments
- operating a data pipeline beyond local development

---

## Future Improvements

Potential production-scale extensions include:

- S3-based landing zone
- Amazon RDS or managed cloud warehouse
- Secrets Manager / Parameter Store
- Terraform-managed infrastructure
- centralized observability and alerting
- data freshness monitoring
- dead-letter/quarantine workflows
- remote Airflow logging
- larger-volume performance testing
- distributed Airflow execution

These are intentionally treated as scaling improvements rather than requirements for the current single-node implementation.

---

## Status

```text
Python ingestion       ✅
Multi-source loading   ✅
Incremental dbt        ✅
Idempotent ingestion   ✅
dbt transformations    ✅
dbt tests              ✅
Airflow orchestration  ✅
Docker                 ✅
CI                     ✅
CD                     ✅
AWS deployment         ✅
```

---

## Author

**Somesh Kumar**

Data Engineering • Cloud • Data Platforms