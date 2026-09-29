# Page 4 — Reliability & Incidents

## Purpose

The Reliability & Incidents page connects data reliability with unusual business behavior detected by the DataTrust analytics platform.

This page allows analysts to identify statistically unusual business activity, investigate the strongest contributing dimensions, quantify deviation from expected baseline performance, and review the reliability of the KPIs involved.

The page is designed to answer five questions:

1. When did unusual business activity occur?
2. Which business metrics triggered anomaly alerts?
3. What dimensions were the strongest contributors to each anomaly?
4. How large was the observed deviation from the historical baseline?
5. How reliable are the underlying data inputs supporting the affected KPIs?

## Primary Data Sources

- `pbi_business_anomalies`
- `pbi_anomaly_root_causes`
- `pbi_business_impact`
- `pbi_metric_reliability`

## Analytical Layers

This page combines four DataTrust capabilities:

1. Statistical anomaly detection
2. Root-cause contributor analysis
3. Business-impact estimation
4. KPI data-reliability scoring

## Interpretation Principle

An anomaly indicates statistically unusual behavior relative to the historical baseline. It does not automatically indicate a business problem.

Root-cause records identify the strongest contributing dimensions associated with an anomaly but should not be interpreted as proof of causation.

Business-impact values represent deviations from the calculated baseline rather than confirmed causal gains or losses.

## Page Layout

The page will contain four main sections:

1. Incident Summary
2. Anomaly Timeline
3. Root-Cause Diagnostics
4. Business Impact & KPI Reliability

## Anomaly Timeline

### Primary Visual — Daily Net Sales with Anomaly Markers

**Visual Type:** Line Chart with Anomaly Overlay

**X-Axis:**
- `anomaly_date`

**Primary Y-Axis:**
- `net_sales`

**Baseline:**
- `sales_rolling_mean`

**Anomaly Indicators:**
- `sales_anomaly_flag`
- `order_volume_anomaly_flag`
- `aov_anomaly_flag`

### Business Question

When did statistically unusual business activity occur, and which business metric triggered each anomaly?

### Current Detection Summary

- Daily observations analyzed: 1,096
- Total anomaly days: 27
- Sales anomaly days: 10
- Order-volume anomaly days: 12
- Average-order-value anomaly days: 6

A single date can trigger more than one anomaly type, so anomaly-type counts should not be summed to calculate the number of unique anomaly days.

### Tooltip Fields

- `anomaly_date`
- `net_sales`
- `sales_rolling_mean`
- `sales_z_score`
- `sales_deviation_pct`
- `order_count`
- `order_count_rolling_mean`
- `order_count_z_score`
- `average_order_value`
- `aov_rolling_mean`
- `aov_z_score`
- `is_sales_anomaly`
- `is_order_volume_anomaly`
- `is_aov_anomaly`

### Detection Method

DataTrust compares daily business metrics against a prior 28-day rolling baseline.

An anomaly is triggered when the absolute standardized deviation reaches the configured statistical threshold.

The rolling baseline excludes the current observation from its historical comparison.

### Interpretation

The individual anomaly flags should be used to identify the type of incident.

`anomaly_direction` and `anomaly_severity` should not be used as universal classifications for every anomaly type because a date may contain an Order Volume or AOV anomaly even when the sales-specific classification remains `Normal`.

An anomaly represents unusual statistical behavior and does not by itself establish a business problem or causal event.

## Root-Cause Diagnostics

### Primary Visual — Top Anomaly Contributors

**Visual Type:** Horizontal Bar Chart

**Category:**
- `contributor_name`

**Value:**
- `absolute_change`

**Context Fields:**
- `signal_type`
- `dimension_type`

**Tooltip Fields:**
- `anomaly_date`
- `signal_type`
- `signal_direction`
- `dimension_type`
- `contributor_name`
- `metric_name`
- `absolute_change`
- `percentage_change`
- `contributor_rank`
- `baseline_window_days`

### Business Question

Which channels, regions, categories, or products contributed most strongly to the unusual business activity detected on a selected anomaly date?

### Contributor Dimensions

The root-cause analysis can identify contributors from:

- Channel
- Region
- Category
- Product

### Diagnostic Workflow

Users should first select an anomaly date from the anomaly timeline.

The contributor visual should then display the strongest available contributors associated with that incident.

Additional filters should allow investigation by:

- `signal_type`
- `dimension_type`
- `signal_direction`

### Example Interpretation

For the Sales anomaly detected on June 3, 2023, the root-cause analysis identified contributors including:

- Mobile App — Channel
- West — Region
- Electronics — Category
- TrailForge Sports Accessories 0841 — Product

These should be described as leading contributors associated with the anomaly, not as proven causal explanations.

### Data Availability Note

Some root-cause records do not populate `actual_value`, `baseline_value`, or `percentage_change`.

The dashboard should therefore use `absolute_change` as the primary comparison value and display optional fields only when values are available.

### Interpretation Principle

Root-cause diagnostics identify dimensions with the strongest observed changes around an anomaly.

They provide evidence for investigation but do not establish causation.

## Business Impact Analysis

### Primary Visual — Revenue Deviation from Baseline

**Visual Type:** Column Chart

**X-Axis:**
- `anomaly_date`

**Value:**
- `revenue_impact`

**Supporting Fields:**
- `expected_sales`
- `net_sales`
- `revenue_impact_pct`
- `revenue_impact_direction`
- `business_impact_magnitude`

### Business Question

How far did business performance deviate from its expected historical baseline on detected anomaly days?

### Impact Summary Cards

The section should include:

1. Total Absolute Revenue Deviation
2. Above-Baseline Revenue Deviation
3. Below-Baseline Revenue Deviation
4. Critical / High Impact Incident Count

### Current Impact Snapshot

Across the 27 detected anomaly days:

- Total absolute revenue deviation: **$1,667,897.78**
- Above-baseline revenue deviation: **$1,579,028.65**
- Below-baseline revenue deviation: **-$88,869.13**
- Critical impact incidents: **1**
- High impact incidents: **5**
- Moderate impact incidents: **16**
- Low impact incidents: **5**

### Incident Detail Fields

For a selected anomaly date, display:

- `net_sales`
- `expected_sales`
- `revenue_impact`
- `revenue_impact_pct`
- `order_count`
- `expected_order_count`
- `order_volume_impact`
- `order_volume_impact_pct`
- `average_order_value`
- `expected_aov`
- `aov_impact`
- `aov_impact_pct`
- `business_impact_magnitude`

### Interpretation Principle

`revenue_impact`, `order_volume_impact`, and `aov_impact` represent differences between observed values and the calculated historical baseline.

They should be described as **baseline deviations**, not as confirmed financial gains, losses, or causal business impact.

For example, a positive `revenue_impact` means revenue was above the historical baseline for that date. It does not establish that the anomaly caused additional revenue.

## Incident Summary

### Summary KPI Cards

The top of the Reliability & Incidents page should provide an immediate overview of detected analytical incidents.

**Card 1 — Anomaly Days**
- Value: 27
- Definition: Unique dates where at least one monitored business metric triggered an anomaly.

**Card 2 — Sales Anomaly Days**
- Value: 10
- Source: `is_sales_anomaly`

**Card 3 — Order Volume Anomaly Days**
- Value: 12
- Source: `is_order_volume_anomaly`

**Card 4 — AOV Anomaly Days**
- Value: 6
- Source: `is_aov_anomaly`

**Card 5 — Critical / High Impact Incidents**
- Value: 6
- Definition: Incidents classified as either Critical or High business-impact magnitude.

**Card 6 — Absolute Revenue Deviation**
- Value: $1,667,897.78
- Source: Sum of `absolute_revenue_impact`

### Impact Severity Breakdown

**Visual Type:** Donut Chart

**Legend:**
- `business_impact_magnitude`

**Value:**
- Count of `anomaly_date`

Current distribution:

- Critical: 1
- High: 5
- Moderate: 16
- Low: 5

### Important Counting Rule

Sales, Order Volume, and AOV anomaly counts are not mutually exclusive.

A single anomaly date can trigger multiple metric-level anomaly flags. Therefore, the three anomaly-type counts must not be added together to calculate total anomaly days.

The authoritative total incident count is the number of unique anomaly dates where `is_any_anomaly = True`.

## KPI Reliability

### Primary Visual — KPI Reliability Scores

**Visual Type:** Horizontal Bar Chart

**Category:**
- `kpi_name`

**Value:**
- `reliability_score`

**Supporting Fields:**
- `rules_monitored`
- `reliability_status`

### Business Question

How reliable are the underlying data inputs used to calculate important business KPIs?

### Current KPI Reliability

| KPI | Reliability Score | Rules Monitored | Status |
|---|---:|---:|---|
| Order Volume | 99.92% | 1 | Trusted |
| Average Order Value | 99.74% | 4 | Monitor |
| Revenue | 99.68% | 3 | Monitor |
| Gross Profit | 99.68% | 3 | Monitor |
| Return Rate | 99.15% | 2 | Monitor |

### Interpretation

KPI reliability measures the quality of the underlying data fields and quality rules associated with each metric.

It should not be interpreted as:

- KPI business performance
- Forecast accuracy
- Statistical confidence
- Probability that a KPI is correct

For example, Revenue having a reliability score of 99.68% means that its dependent data elements performed strongly against the configured data-quality rules. It does not mean that revenue performance itself is 99.68%.

### Analytical Value

This section connects the Data Quality layer with the Business Analytics layer.

Instead of only reporting that a source table contains data-quality issues, DataTrust shows which business KPIs depend on those fields and provides a metric-level reliability assessment.

This allows analysts and decision-makers to evaluate whether a KPI should be treated as Trusted or monitored more carefully before using it for business decisions.

## Filters and Interactions

### Page-Level Filters

The page should provide the following filters:

- `anomaly_date`
- `signal_type`
- `dimension_type`
- `business_impact_magnitude`

### Anomaly Type Filters

Users should also be able to isolate incidents involving:

- Sales anomalies
- Order Volume anomalies
- Average Order Value anomalies

These filters should use the individual anomaly flags rather than relying only on `anomaly_severity` or `anomaly_direction`.

## Cross-Filtering Behavior

### Anomaly Timeline → Root-Cause Diagnostics

Selecting an anomaly date should filter the root-cause contributor analysis to the same `anomaly_date`.

### Anomaly Timeline → Business Impact

Selecting an anomaly date should display the corresponding actual-versus-baseline business impact metrics.

### Business Impact Severity → Incident Analysis

Selecting a business-impact magnitude such as Critical or High should restrict the incident analysis to dates with that classification.

### Root-Cause Filters

Selecting a `dimension_type` should allow analysts to investigate contributors specifically by:

- Channel
- Region
- Category
- Product

## KPI Reliability Interaction

KPI reliability is a current metric-level reliability snapshot rather than a daily incident dataset.

It should therefore be presented as contextual information and should not be assumed to filter dynamically by `anomaly_date`.

## Relationship Principle

Cross-filtering should only be enabled where the reporting datasets share a valid analytical key.

The primary incident relationship across the anomaly, root-cause, and business-impact datasets is:

`anomaly_date`

Relationships should not be created solely to force unrelated dashboard visuals to cross-filter.

## Recommended Page Layout

### Row 1 — Page Header

**Title:** Reliability & Incidents

**Subtitle:** Statistical anomaly monitoring, diagnostic contributors, baseline business impact, and KPI data reliability.

Place the primary page filters near the header.

---

### Row 2 — Incident Summary

Display six KPI cards:

1. Anomaly Days
2. Sales Anomaly Days
3. Order Volume Anomaly Days
4. AOV Anomaly Days
5. Critical / High Impact Incidents
6. Absolute Revenue Deviation

This row should provide an immediate incident-level summary.

---

### Row 3 — Anomaly Monitoring

**Left / Large Visual:**
Daily Net Sales with Anomaly Markers

Show:
- Daily Net Sales
- 28-Day Rolling Sales Baseline
- Detected anomaly dates

**Right / Smaller Visual:**
Impact Severity Breakdown

Show:
- Critical
- High
- Moderate
- Low

---

### Row 4 — Diagnostic Investigation

**Left Visual:**
Top Anomaly Contributors

Allow investigation across:
- Channel
- Region
- Category
- Product

**Right Visual:**
Revenue Deviation from Baseline

Compare observed revenue deviation across anomaly dates.

Selecting an anomaly date should help connect the incident with its diagnostic contributors and business-impact metrics.

---

### Row 5 — KPI Reliability

Display KPI Reliability Scores for:

- Revenue
- Gross Profit
- Order Volume
- Average Order Value
- Return Rate

Include:
- Reliability Score
- Reliability Status
- Number of Rules Monitored

This section connects business monitoring with the quality of the underlying data used by each KPI.

---

## Recommended Investigation Flow

The page should guide the analyst through the following sequence:

**Detect → Prioritize → Diagnose → Quantify → Assess Reliability**

1. **Detect** unusual activity from the anomaly timeline.
2. **Prioritize** incidents using business-impact magnitude.
3. **Diagnose** the strongest associated contributors.
4. **Quantify** deviation from the historical baseline.
5. **Assess Reliability** of the underlying KPI data before interpreting the result.

## Page Design Principle

The page should function as an analytical investigation workspace rather than simply a collection of charts.

An analyst should be able to move from detecting an unusual event to understanding its associated contributors, estimated baseline deviation, and underlying KPI data reliability within one dashboard page.