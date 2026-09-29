# DataTrust

## Automated Data Quality & Metric Reliability Analytics Platform

DataTrust is a production-style analytics platform that transforms multi-source retail data into validated, reconciled, and analytics-ready datasets before business metrics are consumed by reporting systems.

The project simulates an omnichannel retailer operating across website, mobile app, and physical-store channels. It processes **606,279 source records** across customers, products, orders, order items, payments, and returns.

Unlike a traditional dashboard project that assumes the underlying data is trustworthy, DataTrust evaluates the reliability of the data and the KPIs built from it. The platform combines configurable data-quality rules, automated cleaning and quarantine, source-to-warehouse reconciliation, statistical anomaly detection, root-cause diagnostics, business-impact analysis, and KPI-level reliability scoring.

The complete workflow is orchestrated through a **13-stage automated pipeline**, producing a PostgreSQL analytics warehouse and **14 dashboard-ready reporting datasets** for downstream BI analysis.

## Project Objectives

- Build a realistic multi-source retail analytics environment
- Ingest and validate customer, product, order, payment, and return data
- Detect data-quality issues across completeness, validity, uniqueness, consistency, referential integrity, and freshness dimensions
- Apply configurable YAML-based data-quality rules
- Separate invalid records through automated quarantine and dependency-aware cleaning
- Reconcile source records with clean and excluded records to ensure complete data accountability
- Monitor historical data-quality performance
- Detect statistically unusual revenue, order-volume, and average-order-value behavior
- Diagnose likely contributors to anomalous business metrics
- Quantify deviations from expected business performance
- Calculate reliability scores for critical KPIs such as Revenue, Gross Profit, Order Volume, Average Order Value, and Return Rate
- Build an analytics star schema for customer, product, sales, and returns analysis
- Perform advanced SQL analysis including growth, profitability, customer segmentation, cohort retention, and return behavior
- Produce dashboard-ready datasets for executive, business-performance, data-quality, anomaly, and reliability reporting


## Technology Stack

| Area | Technologies |
|---|---|
| Programming & Data Processing | Python 3.12, Pandas, NumPy |
| Database & Analytics | PostgreSQL, SQL |
| Database Connectivity | SQLAlchemy, psycopg2 |
| Data Sources | CSV, Excel |
| Data Quality Configuration | YAML |
| Testing | pytest |
| Business Intelligence | Power BI |
| Version Control | Git, GitHub |
| Development Environment | VS Code, Jupyter Notebook |

### Key Analytical Techniques

- Data profiling and rule-based validation
- Data cleaning and quarantine management
- Referential-integrity validation
- Source-to-warehouse reconciliation
- Rolling statistical baselines and Z-score anomaly detection
- Root-cause contributor analysis
- Business-impact analysis
- KPI dependency mapping and reliability scoring
- Dimensional modeling and star-schema design
- Window functions, CTEs, ranking, cohort analysis, and RFM segmentation

## Project Status

**Core Analytics Platform: Complete**

The end-to-end DataTrust backend currently includes:

- 13-stage automated analytics pipeline
- 606,279 multi-source input records
- 31 configurable data-quality rules
- 6 data-quality dimensions
- Automated cleaning, quarantine, and dependency exclusions
- Source-to-final reconciliation with zero unaccounted records
- Statistical anomaly detection across 1,096 daily observations
- Root-cause contributor analysis
- Business-impact analysis
- KPI-level reliability scoring
- PostgreSQL analytics star schema
- 12 advanced SQL business analyses
- 14 Power BI reporting views
- 14 dashboard-ready CSV exports
- Automated pytest validation suite

**Dashboard Design Status:** Four-page Power BI dashboard specifications are complete, covering Executive Overview, Customer & Product Analytics, Data Trust Center, and Reliability & Incidents.

**Next Phase:** Build the final `.pbix` report in a Windows environment, capture dashboard screenshots, and complete the final portfolio presentation.

## Verified Project Results

| Metric | Result |
|---|---:|
| Source Records Processed | 606,279 |
| Final Clean Records | 571,133 |
| Directly Quarantined Records | 8,252 |
| Dependency Exclusions | 26,894 |
| Unaccounted Records After Reconciliation | 0 |
| Data Quality Rules | 31 |
| Overall Data Quality Score | 99.75% |
| Daily Business Observations Analyzed | 1,096 |
| Detected Anomaly Days | 27 |
| Root-Cause Contributor Records | 82 |
| Business-Impact Days Analyzed | 27 |
| Absolute Revenue Deviation vs. Baseline | $1,667,897.78 |
| KPI Reliability Scores Generated | 5 |
| Trusted Sales Fact Records | 285,029 |
| Dashboard Reporting Views | 14 |
| Dashboard-Ready CSV Exports | 14 |
| Automated Tests Passing | 15 / 15 |

> **Note:** Revenue impact represents deviation from the historical rolling baseline on detected anomaly days. It should not be interpreted as proven causal revenue gain or loss.

## End-to-End Pipeline

```text
Multi-Source Business Data
        │
        ▼
1. Data Quality Audit
        │
        ▼
2. Quarantine Invalid Records
        │
        ▼
3. Build First-Pass Clean Layer
        │
        ▼
4. Dependency-Aware Cleanup
        │
        ▼
5. Validate Clean Data
        │
        ▼
6. Source-to-Final Reconciliation
        │
        ▼
7. Business Anomaly Detection
        │
        ▼
8. Root-Cause Analysis
        │
        ▼
9. Business-Impact Analysis
        │
        ▼
10. KPI Reliability Scoring
        │
        ▼
11. Analytics Star Schema
        │
        ▼
12. Power BI Reporting Views
        │
        ▼
13. Dashboard Dataset Export
        │
        ▼
Analytics & BI Consumption
```

## Data Quality Framework

DataTrust evaluates source data across six quality dimensions:

| Dimension | Purpose |
|---|---|
| Completeness | Detect missing required values |
| Validity | Identify values that violate expected formats, ranges, or business rules |
| Uniqueness | Detect duplicate business identifiers and records |
| Consistency | Identify conflicting values and cross-field inconsistencies |
| Referential Integrity | Validate relationships between related datasets |
| Freshness | Support monitoring of data timeliness and recency |

The platform uses **31 configurable YAML-based rules** rather than hard-coding validation logic directly into the pipeline. Each audit run stores rule-level results, table-level scores, dimension-level scores, and an overall data-quality score for historical monitoring.

## KPI Reliability Layer

DataTrust does not stop at identifying bad records. It evaluates how underlying data-quality issues affect the trustworthiness of business metrics.

A dependency map connects each KPI to the source fields and data-quality rules required to calculate it. The platform then uses the latest audit results to generate a reliability score and monitoring status for each KPI.

| KPI | Reliability Score | Status |
|---|---:|---|
| Order Volume | 99.92% | Trusted |
| Average Order Value | 99.74% | Monitor |
| Revenue | 99.68% | Monitor |
| Gross Profit | 99.68% | Monitor |
| Return Rate | 99.15% | Monitor |

Currently monitored KPIs include **Revenue, Gross Profit, Order Volume, Average Order Value, and Return Rate**.

This allows analysts and dashboard users to evaluate not only **what a metric says**, but also **how reliable the underlying data used to calculate that metric is**.

## Analytics Data Model

DataTrust transforms validated operational data into a PostgreSQL dimensional model designed for business analysis and BI reporting.

### Dimension Tables

- `analytics.dim_customer` — 48,600 customer records
- `analytics.dim_product` — 1,930 product records
- `analytics.dim_date` — 1,127 calendar records

### Fact Tables

- `analytics.fact_sales` — 285,029 trusted order-item transactions
- `analytics.fact_returns` — 5,555 trusted return transactions

The sales fact table contains calculated measures including:

- Gross Sales
- Discount Amount
- Net Sales
- Total Cost
- Gross Profit

The model supports analysis across customers, products, categories, brands, sales channels, geographic regions, and time while maintaining validated relationships between fact and dimension tables.

## Advanced SQL Business Analytics

DataTrust includes a dedicated SQL analytics layer containing 12 business analyses built using PostgreSQL CTEs, window functions, ranking functions, aggregation, and time-based comparisons.

The analyses include:

1. Monthly Revenue and MoM/YoY Growth
2. Product and Category Profitability
3. Sales Channel Performance
4. Regional Performance
5. Discount Impact Analysis
6. Customer Repeat-Purchase Analysis
7. RFM Customer Segmentation
8. Monthly Cohort Retention
9. Return Rate by Product Category
10. Return Reason Analysis
11. State-Level Performance
12. Top Products Within Each Category

These analyses convert the trusted warehouse data into decision-oriented insights covering revenue growth, profitability, customer behavior, retention, product performance, returns, channels, and geographic performance.

## Anomaly Detection & Root-Cause Analysis

DataTrust continuously evaluates trusted daily business metrics to identify unusual behavior that may require analyst investigation.

The anomaly-detection layer monitors:

- Net Sales
- Order Volume
- Average Order Value (AOV)

It uses a **28-day historical rolling baseline** and Z-score-based detection to compare each day's performance with prior business behavior.

Across **1,096 daily observations**, the system identified **27 anomaly days**:

- 10 sales anomaly days
- 12 order-volume anomaly days
- 6 AOV anomaly days

After an anomaly is detected, DataTrust performs contributor analysis across business dimensions to identify the products, categories, channels, or regions associated with the change. The current analysis produced **82 ranked root-cause contributor records** across the 27 anomaly dates.

The business-impact layer then compares anomalous performance with the historical baseline to quantify the magnitude and direction of the deviation.

> Root-cause results represent analytical contributors and diagnostic signals rather than proof of causal relationships.

## Dashboard & Reporting Layer

DataTrust includes a dedicated reporting layer that separates dashboard consumption from the underlying transactional and analytical tables.

The pipeline automatically builds **14 PostgreSQL reporting views** and exports each view as a dashboard-ready CSV dataset.

Reporting datasets cover:

- Executive monthly KPIs
- Sales channel performance
- Regional performance
- Product performance
- Customer performance
- Returns analysis
- Overall data-quality performance
- Quality-dimension performance
- Table-level quality scores
- Rule-level validation results
- KPI reliability
- Business anomalies
- Root-cause contributors
- Business-impact analysis

The planned Power BI report contains four primary pages:

1. **Executive Overview** — revenue, profit, orders, AOV, growth, channel, and regional performance
2. **Customer & Product Analytics** — customer behavior, product profitability, segmentation, and returns
3. **Data Trust Center** — quality scores, rule failures, quality dimensions, and KPI reliability
4. **Reliability & Incidents** — anomalies, root-cause contributors, and estimated business-impact deviations

Because the reporting layer is decoupled from the warehouse, the same curated datasets can be consumed by Power BI or other visualization tools without modifying the core analytics pipeline.

## Automated Testing & Validation

DataTrust includes a pytest-based automated validation suite to verify critical analytics and data-engineering behavior.

The current suite contains **15 automated tests**, covering:

- Clean-layer primary-key uniqueness
- Clean-layer referential integrity
- Overall clean-layer validation
- Source-to-final reconciliation
- Reconciliation component counts
- Root-cause analysis structure and anomaly handling
- Business-impact calculations and storage structure
- KPI reliability calculations
- Reliability-status thresholds

Current verified result:

```text
15 passed
```


## Project Structure

DataTrust/
├── config/                    # Data-quality rule configuration
├── dashboard/                 # Dashboard-related assets
├── data/
│   ├── dashboard_exports/     # Generated dashboard-ready CSV datasets
│   ├── incoming/              # Incoming source data
│   ├── processed/             # Processed datasets
│   ├── raw/                   # Generated raw source files
│   └── rejected/              # Rejected data artifacts
├── docs/                      # Project documentation
├── notebooks/                 # Data generation and exploratory work
├── reports/                   # Reporting artifacts
├── sql/
│   ├── analysis/              # Advanced business SQL analyses
│   ├── ddl/                   # Database object definitions
│   ├── transformations/       # Analytics and reporting transformations
│   └── views/                 # SQL view definitions
├── src/
│   ├── anomaly/               # Statistical anomaly detection
│   ├── impact/                # Business-impact analysis
│   ├── ingestion/             # Source-data ingestion
│   ├── pipeline/              # End-to-end pipeline orchestration
│   ├── quality/               # Quality, cleaning, validation & reconciliation logic
│   ├── reliability/           # KPI reliability scoring
│   ├── reporting/             # Dashboard dataset exports
│   └── root_cause/            # Root-cause contributor analysis
├── tests/                     # Automated pytest suite
├── README.md
└── requirements.txt
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd DataTrust
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database for the project:

```sql
CREATE DATABASE datatrust;
```

Create a `.env` file in the project root and add your PostgreSQL connection string:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/datatrust
```

Replace `username` and `password` with your local PostgreSQL credentials.

> The `.env` file should remain excluded from version control because it contains database credentials.

### 5. Initialize the Database

Create the required PostgreSQL schemas and base tables by running:

```bash
python -m src.pipeline.setup_database
```

The setup module automatically:

- Creates the `raw`, `quality`, `quarantine`, `clean`, and `analytics` schemas
- Executes the nine database DDL scripts in the required order
- Uses idempotent table creation so existing tables are preserved

### 6. Generate the Source Data

The raw business datasets are synthetically generated and are not stored in Git because of their size.

Run the following notebook:

```text
notebooks/01_generate_business_data.ipynb
```

The notebook generates six source datasets representing the fictional NovaRetail business:

- `customers.csv`
- `orders.csv`
- `order_items.csv`
- `products.xlsx`
- `payments.csv`
- `returns.csv`

The generated files are placed in `data/incoming/`.

### 7. Load Source Data into PostgreSQL

After generating the datasets, load all six sources into the PostgreSQL `raw` schema:

```bash
python -m src.ingestion.load_raw_data
```

The ingestion process loads customers, products, orders, order items, payments, and returns into their corresponding raw database tables.

### 8. Run the Complete DataTrust Pipeline

After the database has been initialized and the source data has been loaded, run:

```bash
python -m src.pipeline.run_datatrust
```

The pipeline executes the following 13 stages automatically:

1. Data-quality audit
2. Invalid-record quarantine
3. First-pass clean-layer creation
4. Dependency-aware cleanup
5. Clean-layer validation
6. Source-to-final reconciliation
7. Business anomaly detection
8. Root-cause contributor analysis
9. Business-impact analysis
10. KPI reliability scoring
11. Analytics star-schema construction
12. Power BI reporting-view construction
13. Dashboard-ready dataset export

A successful run produces validated analytics tables, quality-monitoring results, business-analysis outputs, reporting views, and 14 dashboard-ready CSV datasets in:

```text
data/dashboard_exports/
```

### 9. Run Automated Tests

Run the complete validation suite with:

```bash
pytest -v
```

The current test suite contains **15 automated tests** covering clean-layer integrity, reconciliation, root-cause analysis, business-impact analysis, and KPI reliability.

Current verified result:

```text
15 passed
```

## Table of Contents

- [Project Objectives](#project-objectives)
- [Technology Stack](#technology-stack)
- [Project Status](#project-status)
- [Verified Project Results](#verified-project-results)
- [End-to-End Pipeline](#end-to-end-pipeline)
- [Data Quality Framework](#data-quality-framework)
- [KPI Reliability Layer](#kpi-reliability-layer)
- [Analytics Data Model](#analytics-data-model)
- [Advanced SQL Business Analytics](#advanced-sql-business-analytics)
- [Anomaly Detection & Root-Cause Analysis](#anomaly-detection--root-cause-analysis)
- [Dashboard & Reporting Layer](#dashboard--reporting-layer)
- [Automated Testing & Validation](#automated-testing--validation)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)