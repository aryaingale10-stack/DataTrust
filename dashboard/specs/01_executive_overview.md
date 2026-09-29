# Page 1 — Executive Overview

## Purpose

The Executive Overview provides a high-level view of NovaRetail's business performance using trusted, analytics-ready data produced by the DataTrust pipeline.

The page is designed to answer five executive questions:

1. How much revenue and profit is the business generating?
2. Are revenue and order volume growing or declining?
3. How efficiently is the business converting orders into revenue?
4. Which sales channels and geographic regions contribute the most?
5. Are the KPIs being displayed supported by reliable underlying data?

## Primary Data Sources

- `pbi_executive_monthly`
- `pbi_channel_performance`
- `pbi_regional_performance`
- `pbi_metric_reliability`

## Page Layout

The page will contain four main sections:

1. KPI Summary
2. Revenue & Growth Trends
3. Channel Performance
4. Regional Performance

## KPI Summary Cards

The top section of the Executive Overview will contain six KPI cards.

| KPI Card | Source Field | Display Format |
|---|---|---|
| Net Sales | `net_sales` | Currency |
| Gross Profit | `gross_profit` | Currency |
| Gross Margin | `gross_margin_pct` | Percentage |
| Total Orders | `total_orders` | Whole Number |
| Total Customers | `total_customers` | Whole Number |
| Average Order Value | `average_order_value` | Currency |

### Supporting Growth Indicators

The dashboard will also use:

- `mom_revenue_growth_pct` — Month-over-Month revenue growth
- `yoy_revenue_growth_pct` — Year-over-Year revenue growth

These indicators provide context for whether current revenue performance is improving or declining over time.

## Channel Performance

### Primary Visual — Net Sales by Sales Channel

**Visual Type:** Horizontal Bar Chart

**Category:**
- `sales_channel`

**Primary Value:**
- `net_sales`

**Tooltip Fields:**
- `revenue_share_pct`
- `total_orders`
- `total_customers`
- `average_order_value`
- `gross_profit`
- `gross_margin_pct`

### Business Question

Which sales channels generate the most revenue, and how do their order volume, customer reach, profitability, and average order value compare?

### Current Dataset Snapshot

| Sales Channel | Net Sales | Revenue Share |
|---|---:|---:|
| Website | $76.89M | 45.17% |
| Mobile App | $59.09M | 34.72% |
| Physical Store | $34.23M | 20.11% |

The chart should be sorted by `net_sales` in descending order.

## Regional Performance

### Primary Visual — Net Sales by Region

**Visual Type:** Horizontal Bar Chart

**Category:**
- `shipping_region`

**Primary Value:**
- `net_sales`

**Tooltip Fields:**
- `revenue_share_pct`
- `total_orders`
- `total_customers`
- `units_sold`
- `gross_profit`
- `average_order_value`
- `gross_margin_pct`

### Business Question

Which geographic regions contribute the most revenue, and how do their sales volume, customer base, profitability, and average order value compare?

### Current Dataset Snapshot

| Region | Net Sales | Revenue Share |
|---|---:|---:|
| South | $48.01M | 28.21% |
| West | $41.44M | 24.35% |
| Midwest | $40.72M | 23.93% |
| Northeast | $40.03M | 23.52% |

The chart should be sorted by `net_sales` in descending order.

## Revenue & Growth Trends

### Primary Visual — Monthly Net Sales Trend

**Visual Type:** Line Chart

**X-Axis:**
- `month_start_date`

**Y-Axis:**
- `net_sales`

**Tooltip Fields:**
- `year_month`
- `total_orders`
- `average_order_value`
- `gross_profit`
- `gross_margin_pct`
- `mom_revenue_growth_pct`
- `yoy_revenue_growth_pct`

### Business Question

How is NovaRetail's revenue changing over time, and what changes in order volume, average order value, and profitability accompany that trend?

### Time Coverage

- January 2023 through December 2025
- 36 monthly observations

### Growth Interpretation

- `mom_revenue_growth_pct` compares each month with the immediately preceding month.
- `yoy_revenue_growth_pct` compares each month with the corresponding month one year earlier.
- January 2023 has no MoM comparison.
- The 2023 months have no YoY comparison because no prior-year data is available.

The chart should use `month_start_date` as a continuous chronological axis rather than sorting by month name.

## KPI Reliability Indicator

### Visual — KPI Reliability Summary

**Visual Type:** Compact Table / Status Indicator

**Fields:**
- `kpi_name`
- `reliability_score`
- `reliability_status`

**Tooltip / Supporting Field:**
- `rules_monitored`
- `analyzed_at`

### Business Question

How reliable are the underlying data inputs used to calculate the business KPIs displayed on the dashboard?

### Current Reliability Snapshot

| KPI | Reliability Score | Status |
|---|---:|---|
| Order Volume | 99.92% | Trusted |
| Average Order Value | 99.74% | Monitor |
| Revenue | 99.68% | Monitor |
| Gross Profit | 99.68% | Monitor |
| Return Rate | 99.15% | Monitor |

### Interpretation

A high reliability score indicates that the data fields and quality rules supporting the KPI have a high pass rate.

`Trusted` and `Monitor` should be treated as data-quality reliability classifications produced by the DataTrust reliability engine, not as measures of business performance.

Detailed rule-level reliability analysis will be presented on the dedicated Reliability & Incidents dashboard page.

## Page Filters and Slicers

The Executive Overview will provide the following interactive filters:

### Date Filters

- `year`
- `quarter`
- `month_name`

These fields come from `pbi_executive_monthly`.

### Interaction Behavior

Selecting a time period should update the applicable KPI cards and monthly trend visual.

Channel and regional visuals use aggregated reporting datasets and should not be assumed to respond to monthly filters unless the reporting model is later extended to include time-level fields in those datasets.

### Default View

The dashboard should initially display the complete available business period:

**January 2023 – December 2025**

### Design Principle

Keep the number of visible slicers small so the Executive Overview remains focused on business performance rather than detailed exploration.

More granular filtering will be available on the Customer & Product Analytics page.

## Dashboard Layout Blueprint

### Header

**Title:** DataTrust — Executive Overview

**Subtitle:** Trusted Business Performance & KPI Reliability

### Row 1 — Executive KPI Cards

Six KPI cards displayed horizontally:

1. Net Sales
2. Gross Profit
3. Gross Margin
4. Total Orders
5. Total Customers
6. Average Order Value

### Row 2 — Revenue Trend

**Left / Main Area:**
- Monthly Net Sales Trend
- This should be the largest visual on the page.

**Right Area:**
- KPI Reliability Summary
- Displays KPI name, reliability score, and reliability status.

### Row 3 — Performance Breakdown

**Left:**
- Net Sales by Sales Channel

**Right:**
- Net Sales by Region

### Filter Area

Place compact date slicers near the top-right of the dashboard:

- Year
- Quarter
- Month

### Conceptual Layout

--------------------------------------------------------------
| DataTrust — Executive Overview                Filters       |
--------------------------------------------------------------
| Net Sales | Gross Profit | Margin | Orders | Customers | AOV |
--------------------------------------------------------------
|                                      |                     |
| Monthly Net Sales Trend              | KPI Reliability     |
|                                      | Summary             |
--------------------------------------------------------------
|                                      |                     |
| Net Sales by Channel                 | Net Sales by Region |
|                                      |                     |
--------------------------------------------------------------

### Design Goal

The page should allow a viewer to understand overall business performance within a few seconds while also communicating whether the underlying KPIs are supported by reliable data.