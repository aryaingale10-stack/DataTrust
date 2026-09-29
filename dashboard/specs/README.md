# DataTrust — Power BI Dashboard Specification

## Dashboard Overview

The DataTrust Power BI dashboard is designed as a four-page analytical experience that combines traditional business intelligence with data-quality monitoring, KPI reliability assessment, anomaly detection, diagnostic analysis, and business-impact evaluation.

The dashboard is built on the trusted analytics and reporting layers produced by the DataTrust pipeline.

## Dashboard Pages

### Page 1 — Executive Overview

Provides a high-level view of NovaRetail business performance.

Key areas:
- Net Sales
- Gross Profit
- Gross Margin
- Total Orders
- Total Customers
- Average Order Value
- Monthly Revenue Trends
- Channel Performance
- Regional Performance
- KPI Reliability Summary

Specification:
`01_executive_overview.md`

---

### Page 2 — Customer & Product Analytics

Provides deeper analysis of customer value and product performance.

Key areas:
- Customer Segmentation
- Repeat vs. One-Time Customers
- Customer Lifetime Revenue
- Top Customers
- Product Revenue
- Product Profitability
- Category Performance
- Gross Margin Analysis

Specification:
`02_customer_product_analytics.md`

---

### Page 3 — Data Trust Center

Provides visibility into the quality and reliability of the underlying analytical data.

Key areas:
- Overall Data Quality Score
- Audit Status
- Quality Dimensions
- Table-Level Quality
- Rule-Level Failures
- Failure Counts and Rates
- Data Quality Investigation

Specification:
`03_data_trust_center.md`

---

### Page 4 — Reliability & Incidents

Provides an analytical investigation workspace for unusual business activity.

Key areas:
- Statistical Anomaly Detection
- Incident Prioritization
- Root-Cause Contributor Analysis
- Baseline Business Impact
- KPI Reliability

Investigation workflow:

**Detect → Prioritize → Diagnose → Quantify → Assess Reliability**

Specification:
`04_reliability_incidents.md`

## Dashboard Story

The four pages are designed to answer progressively deeper analytical questions:

**Page 1 — What is happening in the business?**

**Page 2 — Which customers and products are driving performance?**

**Page 3 — Can the underlying data be trusted?**

**Page 4 — What unusual events occurred, what contributed to them, and how reliable are the affected KPIs?**

This structure allows DataTrust to function as more than a traditional business dashboard. It connects business performance with the quality, reliability, and diagnostic context of the data supporting those decisions.

## Power BI Reporting Data Sources

DataTrust produces 14 dashboard-ready reporting datasets from the PostgreSQL analytics layer.

### Business Performance

- `pbi_executive_monthly`
- `pbi_channel_performance`
- `pbi_regional_performance`
- `pbi_product_performance`
- `pbi_customer_performance`
- `pbi_returns_performance`

### Data Quality

- `pbi_data_quality_overview`
- `pbi_quality_dimensions`
- `pbi_table_quality`
- `pbi_quality_rules`

### Reliability & Incident Analytics

- `pbi_metric_reliability`
- `pbi_business_anomalies`
- `pbi_anomaly_root_causes`
- `pbi_business_impact`

## Dashboard Data Delivery

The reporting datasets are available through two delivery methods:

1. PostgreSQL reporting views in the `analytics` schema.
2. Dashboard-ready CSV exports in `data/dashboard_exports/`.

The DataTrust pipeline automatically refreshes these CSV datasets during the dashboard export stage.

This allows the analytical backend to remain fully reproducible even when Power BI Desktop is not available in the current development environment.

## Current Dashboard Status

The analytical backend, reporting views, dashboard exports, and four-page dashboard specifications are complete.

The Power BI `.pbix` implementation is intentionally separated from the backend development because Power BI Desktop requires a supported Windows environment.

The dashboard specifications define the required:

- Visuals
- KPIs
- Data sources
- Filters
- Interactions
- Analytical interpretation
- Page layouts

This provides a complete implementation blueprint for building the final Power BI report when a Windows environment is available.