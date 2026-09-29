# Page 3 — Data Trust Center

## Purpose

The Data Trust Center provides visibility into the quality, completeness, validity, consistency, uniqueness, and referential integrity of the data supporting NovaRetail's analytics.

Unlike a traditional business dashboard that only displays final KPIs, this page allows analysts to examine the reliability of the underlying data before using it for decision-making.

The page is designed to answer five questions:

1. What is the overall quality of the data?
2. Which data-quality dimensions have the strongest or weakest scores?
3. Which source tables contain the most significant quality issues?
4. Which validation rules are failing and how frequently?
5. How has data quality changed across audit runs?

## Primary Data Sources

- `pbi_data_quality_overview`
- `pbi_quality_dimensions`
- `pbi_table_quality`
- `pbi_quality_rules`

## Data Quality Dimensions

The DataTrust quality framework evaluates:

- Completeness
- Validity
- Uniqueness
- Consistency
- Referential Integrity

The framework also supports Freshness as a quality dimension, although the current rule configuration does not include an active freshness validation rule.

## Page Layout

The page will contain four main sections:

1. Overall Data Quality
2. Quality by Dimension
3. Quality by Source Table
4. Rule-Level Failure Analysis

## Overall Data Quality

### KPI Summary

The top section of the Data Trust Center will display four primary indicators.

| KPI | Current Value | Source Field |
|---|---:|---|
| Overall Quality Score | 99.75% | `quality_score` |
| Rules Configured | 31 | `rules_configured` |
| Rules Executed | 31 | `rules_executed` |
| Latest Audit Status | SUCCESS | `run_status` |

The values should be taken from the most recent audit run based on `run_timestamp`.

### Quality Status

Current quality classification:

**Good**

Source field:
- `quality_status`

### Audit History

**Visual Type:** Compact Line Chart

**X-Axis:**
- `run_timestamp`

**Y-Axis:**
- `quality_score`

**Tooltip Fields:**
- `run_id`
- `rules_configured`
- `rules_executed`
- `run_status`
- `quality_status`

### Business Question

Is the overall quality of the analytics data stable across DataTrust audit runs?

### Current Audit Snapshot

- Historical audit runs available: 13
- Latest audit run: Run 16
- Rules configured: 31
- Rules executed: 31
- Latest run status: SUCCESS
- Overall quality score: 99.75%
- Quality status: Good

### Interpretation Note

The available audit runs currently report the same overall quality score of 99.75%.

Therefore, the audit-history visual represents monitoring capability and quality stability rather than a meaningful upward or downward trend at this stage.

## Quality by Dimension

### Primary Visual — Data Quality Score by Dimension

**Visual Type:** Horizontal Bar Chart

**Category:**
- `dimension`

**Value:**
- `quality_score`

**Tooltip Fields:**
- `quality_status`
- `run_id`
- `run_timestamp`
- `run_status`

### Business Question

Which dimensions of data quality are strongest, and which require the most attention?

### Latest Audit Snapshot — Run 16

| Quality Dimension | Quality Score | Status |
|---|---:|---|
| Uniqueness | 99.90% | Excellent |
| Referential Integrity | 99.89% | Good |
| Validity | 99.87% | Good |
| Completeness | 99.52% | Good |
| Consistency | 99.52% | Good |

### Interpretation

Uniqueness currently has the highest quality score at 99.90%.

Completeness and Consistency have the lowest scores at 99.52%, making them the dimensions with the greatest relative opportunity for investigation within the current audit results.

All five actively measured dimensions remain above 99%.

### Freshness Note

Freshness is supported conceptually by the DataTrust quality framework but is not included in this visual because the current rule configuration does not contain an active freshness rule.

The chart must therefore display only dimensions actually present in `pbi_quality_dimensions`.

## Quality by Source Table

### Primary Visual — Data Quality Score by Source Table

**Visual Type:** Horizontal Bar Chart

**Category:**
- `table_name`

**Value:**
- `quality_score`

**Tooltip Fields:**
- `quality_status`
- `run_id`
- `run_timestamp`
- `run_status`

### Business Question

Which source tables have the highest and lowest data quality, and where should analysts focus their investigation?

### Latest Audit Snapshot — Run 16

| Source Table | Quality Score | Status |
|---|---:|---|
| Orders | 99.86% | Good |
| Order Items | 99.79% | Good |
| Payments | 99.77% | Good |
| Customers | 99.30% | Monitor |
| Products | 99.30% | Monitor |
| Returns | 98.42% | Needs Attention |

### Interpretation

Orders currently has the highest table-level quality score at 99.86%.

Returns has the lowest score at 98.42% and is classified as `Needs Attention`, making it the highest-priority source table for further rule-level investigation.

Customers and Products are classified as `Monitor`, while Orders, Order Items, and Payments are currently classified as `Good`.

The chart should be sorted by `quality_score` in ascending order so the tables requiring the most attention appear first.

## Rule-Level Failure Analysis

### Primary Visual — Top Data Quality Rules by Failed Records

**Visual Type:** Horizontal Bar Chart

**Category:**
- `rule_name`

**Value:**
- `failed_records`

**Default Display:**
- Top 10 rules by `failed_records`

**Tooltip Fields:**
- `rule_id`
- `table_name`
- `dimension`
- `severity`
- `evaluated_records`
- `skipped_records`
- `pass_rate`
- `failure_rate_pct`
- `rule_status`

### Business Question

Which data-quality rules are generating the largest number of failed records, and which source tables and quality dimensions are affected?

### Leading Rule Failures — Run 16

| Rule | Table | Failed Records | Failure Rate | Severity |
|---|---|---:|---:|---|
| ITEM_004 — Order Item Price Matches Product | Order Items | 2,462 | 0.80% | High |
| PAY_004 — Payment Amount Matches Order Total | Payments | 947 | 0.79% | Critical |
| CUST_001 — Customer Region Not Null | Customers | 500 | 1.00% | High |
| CUST_002 — Customer Email Valid Format | Customers | 400 | 0.80% | High |
| ORD_001 — Order Customer ID Not Null | Orders | 300 | 0.25% | Critical |
| ITEM_001 — Order Item Quantity Positive | Order Items | 300 | 0.10% | High |
| CUST_004 — Customer State Region Consistency | Customers | 300 | 0.60% | Medium |

### Important Interpretation

Failed-record count and failure rate measure different aspects of a quality issue.

A rule evaluated against a large table can generate many failed records while still having a relatively small failure rate.

For example:

- `ITEM_004` has the largest failure count at 2,462 records but a failure rate of 0.80%.
- `RET_002` has only 205 failed records but a substantially higher failure rate of 3.16%.

Therefore, analysts should consider both failure volume and failure rate when prioritizing investigation.

### Rule Filters

The rule-level analysis should support filtering by:

- `table_name`
- `dimension`
- `severity`
- `rule_status`

The dashboard should retain the complete rule-level table for detailed investigation rather than displaying only the Top 10 chart.

## Page Filters and Slicers

The Data Trust Center will provide filters that allow analysts to move from the overall quality score to specific quality issues.

### Audit Filters

- `run_id`
- `run_timestamp`

These filters allow users to inspect historical audit runs.

### Quality Filters

- `dimension`
- `table_name`
- `severity`
- `rule_status`

### Interaction Behavior

Selecting a quality dimension should filter applicable rule-level analysis.

Selecting a source table should allow analysts to focus on the validation rules associated with that table.

Selecting a severity level should allow analysts to prioritize:

- Critical
- High
- Medium

Selecting an audit run should update visuals that contain historical run-level data.

### Default View

The page should default to the **latest successful audit run** so that users initially see the most recent available data-quality assessment.

Historical audit runs remain available for comparison.

### Modeling Note

The four Power BI reporting datasets contain different levels of aggregation.

Cross-filtering should only be enabled where valid relationships exist in the final semantic model. The dashboard must not imply relationships between fields simply because they appear on the same page.

## Dashboard Layout Blueprint

### Header

**Title:** DataTrust — Data Trust Center

**Subtitle:** Data Quality Monitoring, Validation & Rule Diagnostics

### Row 1 — Data Quality KPI Cards

Four cards displayed horizontally:

1. Overall Quality Score
2. Rules Configured
3. Rules Executed
4. Latest Audit Status

A compact Quality Status indicator should also display the latest classification.

### Row 2 — Quality Monitoring

**Left:**
- Data Quality Score by Dimension

**Center:**
- Data Quality Score by Source Table

**Right:**
- Audit History / Overall Quality Score Trend

### Row 3 — Rule-Level Diagnostics

**Left / Main Area:**
- Top Data Quality Rules by Failed Records

**Right:**
- Rule filters for Dimension, Table, Severity, and Status

### Row 4 — Detailed Rule Table

Display a detailed table containing:

- Rule ID
- Rule Name
- Source Table
- Quality Dimension
- Severity
- Evaluated Records
- Failed Records
- Failure Rate
- Pass Rate
- Rule Status

### Conceptual Layout

----------------------------------------------------------------
| DataTrust — Data Trust Center                    Audit Filter |
----------------------------------------------------------------
| Quality Score | Rules Configured | Executed | Audit Status    |
----------------------------------------------------------------
| Quality by       | Quality by       | Audit Quality          |
| Dimension        | Source Table     | History                |
----------------------------------------------------------------
|                                      |                       |
| Top Rules by Failed Records          | Rule Filters          |
|                                      |                       |
----------------------------------------------------------------
|                                                              |
| Detailed Data Quality Rule Table                             |
|                                                              |
----------------------------------------------------------------

### Design Goal

The page should allow an analyst to move through a clear diagnostic path:

**Overall Quality → Quality Dimension → Source Table → Failed Rule**

This creates an investigation workflow rather than simply displaying disconnected data-quality metrics.