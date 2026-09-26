import os
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "quality_rules.yaml"

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check the .env file.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# State-to-region reference mapping
STATE_REGION_MAP = {
    # Northeast
    "MA": "Northeast",
    "NJ": "Northeast",
    "NY": "Northeast",
    "PA": "Northeast",

    # Midwest
    "IL": "Midwest",
    "IN": "Midwest",
    "MI": "Midwest",
    "MN": "Midwest",
    "MO": "Midwest",
    "OH": "Midwest",

    # South
    "FL": "South",
    "GA": "South",
    "NC": "South",
    "TX": "South",

    # West
    "AZ": "West",
    "CA": "West",
    "CO": "West",
    "WA": "West"
}
ORDER_PAYMENT_STATUS_MAP = {
    "Completed": "Successful",
    "Cancelled": "Failed",
    "Returned": "Refunded"
}
CATEGORY_SUBCATEGORY_MAP = {
    "Clothing": {
        "Accessories",
        "Activewear",
        "Footwear",
        "Men's Clothing",
        "Women's Clothing"
    },
    "Electronics": {
        "Headphones",
        "Laptops",
        "Monitors",
        "Smartphones",
        "Tablets"
    },
    "Home & Kitchen": {
        "Cookware",
        "Furniture",
        "Home Decor",
        "Kitchen Appliances",
        "Storage"
    },
    "Office Supplies": {
        "Desk Accessories",
        "Office Furniture",
        "Paper",
        "Printers",
        "Writing Supplies"
    },
    "Sports & Outdoors": {
        "Camping",
        "Cycling",
        "Fitness Equipment",
        "Outdoor Gear",
        "Sports Accessories"
    }
}

def load_quality_rules():
    """Load data quality rules from the YAML configuration file."""

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        rules = yaml.safe_load(file)

    return rules

def count_quality_rules(quality_rules):
    """Count the total number of configured data quality rules."""

    total_rules = 0

    for table_config in quality_rules["tables"].values():
        total_rules += len(table_config["rules"])

    return total_rules

def build_rule_result(
    table_name,
    rule,
    total_records,
    failed_records,
    evaluated_records=None
):
    """Create a standardized result for a data quality rule."""

    if evaluated_records is None:
        evaluated_records = total_records

    skipped_records = total_records - evaluated_records
    passed_records = evaluated_records - failed_records

    pass_rate = (
        (passed_records / evaluated_records) * 100
        if evaluated_records > 0
        else 0
    )

    return {
        "table_name": table_name,
        "rule_id": rule["rule_id"],
        "rule_name": rule["name"],
        "dimension": rule["dimension"],
        "severity": rule["severity"],
        "total_records": total_records,
        "evaluated_records": evaluated_records,
        "passed_records": passed_records,
        "failed_records": failed_records,         
        "skipped_records": skipped_records,
        "pass_rate": round(pass_rate, 2)
    }

def create_audit_run(rules_configured):
    """Create a new quality audit run and return its run ID."""

    query = text(
        """
        INSERT INTO quality.audit_runs (
            rules_configured,
            rules_executed,
            run_status
        )
        VALUES (
            :rules_configured,
            0,
            'RUNNING'
        )
        RETURNING run_id;
        """
    )

    with engine.begin() as connection:
        run_id = connection.execute(
            query,
            {"rules_configured": rules_configured}
        ).scalar_one()

    return run_id

def save_rule_results(run_id, results):
    """Save all rule-level quality results for an audit run."""

    query = text(
        """
        INSERT INTO quality.rule_results (
            run_id,
            rule_id,
            table_name,
            rule_name,
            dimension,
            severity,
            total_records,
            evaluated_records,
            skipped_records,
            passed_records,
            failed_records,
            pass_rate
        )
        VALUES (
            :run_id,
            :rule_id,
            :table_name,
            :rule_name,
            :dimension,
            :severity,
            :total_records,
            :evaluated_records,
            :skipped_records,
            :passed_records,
            :failed_records,
            :pass_rate
        );
        """
    )

    rows = []

    for result in results:
        rows.append({
            "run_id": run_id,
            "rule_id": result["rule_id"],
            "table_name": result["table_name"],
            "rule_name": result["rule_name"],
            "dimension": result["dimension"],
            "severity": result["severity"],
            "total_records": result["total_records"],
            "evaluated_records": result["evaluated_records"],
            "skipped_records": result["skipped_records"],
            "passed_records": result["passed_records"],
            "failed_records": result["failed_records"],
            "pass_rate": result["pass_rate"]
        })

    with engine.begin() as connection:
        connection.execute(query, rows)
def complete_audit_run(run_id, rules_executed, rules_configured):
    """Mark an audit run as successful only when all configured rules executed."""

    if rules_executed != rules_configured:
        raise ValueError(
            f"Audit run incomplete: "
            f"{rules_executed} of {rules_configured} rules executed."
        )

    query = text(
        """
        UPDATE quality.audit_runs
        SET rules_executed = :rules_executed,
            run_status = 'SUCCESS'
        WHERE run_id = :run_id;
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "rules_executed": rules_executed
            }
        )

def fail_audit_run(run_id, rules_executed=0):
    """Mark a quality audit run as failed."""

    query = text(
        """
        UPDATE quality.audit_runs
        SET rules_executed = :rules_executed,
            run_status = 'FAILED'
        WHERE run_id = :run_id;
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "rules_executed": rules_executed
            }
        )

def calculate_table_scores(results):
    """Calculate weighted quality scores for each source table."""

    results_df = pd.DataFrame(results)

    table_scores = (
        results_df
        .groupby("table_name", as_index=False)
        .agg(
            evaluated_records=("evaluated_records", "sum"),
            passed_records=("passed_records", "sum")
        )
    )

    table_scores["quality_score"] = (
        table_scores["passed_records"]
        / table_scores["evaluated_records"]
        * 100
    ).round(2)

    return table_scores

def calculate_dimension_scores(results):
    """Calculate weighted quality scores for each quality dimension."""

    results_df = pd.DataFrame(results)

    dimension_scores = (
        results_df
        .groupby("dimension", as_index=False)
        .agg(
            evaluated_records=("evaluated_records", "sum"),
            passed_records=("passed_records", "sum")
        )
    )

    dimension_scores["quality_score"] = (
        dimension_scores["passed_records"]
        / dimension_scores["evaluated_records"]
        * 100
    ).round(2)

    return dimension_scores

def calculate_overall_score(results):
    """Calculate the weighted overall data quality score."""

    results_df = pd.DataFrame(results)

    total_evaluated = results_df["evaluated_records"].sum()
    total_passed = results_df["passed_records"].sum()

    quality_score = (
        (total_passed / total_evaluated) * 100
        if total_evaluated > 0
        else 0
    )

    return round(quality_score, 2)

def save_table_scores(run_id, table_scores):
    """Save table-level quality scores for an audit run."""

    query = text(
        """
        INSERT INTO quality.table_scores (
            run_id,
            table_name,
            quality_score
        )
        VALUES (
            :run_id,
            :table_name,
            :quality_score
        );
        """
    )

    rows = []

    for _, row in table_scores.iterrows():
        rows.append({
            "run_id": run_id,
            "table_name": row["table_name"],
            "quality_score": float(row["quality_score"])
        })

    with engine.begin() as connection:
        connection.execute(query, rows)

def save_dimension_scores(run_id, dimension_scores):
    """Save dimension-level quality scores for an audit run."""

    query = text(
        """
        INSERT INTO quality.dimension_scores (
            run_id,
            dimension,
            quality_score
        )
        VALUES (
            :run_id,
            :dimension,
            :quality_score
        );
        """
    )

    rows = []

    for _, row in dimension_scores.iterrows():
        rows.append({
            "run_id": run_id,
            "dimension": row["dimension"],
            "quality_score": float(row["quality_score"])
        })

    with engine.begin() as connection:
        connection.execute(query, rows)

def save_overall_score(run_id, quality_score):
    """Save the overall quality score for an audit run."""

    query = text(
        """
        INSERT INTO quality.overall_scores (
            run_id,
            quality_score
        )
        VALUES (
            :run_id,
            :quality_score
        );
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "quality_score": quality_score
            }
        )

def execute_not_null_rule(table_name, rule):
    """Execute a not-null quality rule against a raw PostgreSQL table."""

    column = rule["column"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NULL;
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records
    )

def execute_regex_rule(table_name, rule):
    """Execute a regex validation rule against a raw PostgreSQL table."""

    column = rule["column"]
    pattern = rule["pattern"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL;
        """
    )

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL
          AND {column} !~ :pattern;
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()

        evaluated_records = connection.execute(
            evaluated_query
        ).scalar_one()

        failed_records = connection.execute(
            failure_query,
            {"pattern": pattern}
        ).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_unique_rule(table_name, rule):
    """Detect extra duplicate occurrences for a column."""

    column = rule["column"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL;
        """
    )

    failure_query = text(
        f"""
        SELECT COALESCE(SUM(duplicate_count - 1), 0)
        FROM (
            SELECT {column}, COUNT(*) AS duplicate_count
            FROM raw.{table_name}
            WHERE {column} IS NOT NULL
            GROUP BY {column}
            HAVING COUNT(*) > 1
        ) AS duplicates;
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()

        evaluated_records = connection.execute(
            evaluated_query
        ).scalar_one()

        failed_records = connection.execute(
            failure_query
        ).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_greater_than_rule(table_name, rule):
    """Execute a greater-than validation rule."""

    column = rule["column"]
    threshold = rule["threshold"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name}
    WHERE {column} IS NOT NULL;
    """
)

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL
          AND {column} <= :threshold;
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(
            failure_query,
            {"threshold": threshold}
        ).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_between_rule(table_name, rule):
    """Execute a numeric range validation rule."""

    column = rule["column"]
    min_value = rule["min_value"]
    max_value = rule["max_value"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL;
        """
    )

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL
          AND ({column} < :min_value OR {column} > :max_value);
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()

        evaluated_records = connection.execute(
            evaluated_query
        ).scalar_one()

        failed_records = connection.execute(
            failure_query,
            {
                "min_value": min_value,
                "max_value": max_value
            }
        ).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_allowed_values_rule(table_name, rule):
    """Validate that column values belong to an approved set."""

    column = rule["column"]
    allowed_values = rule["allowed_values"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL;
        """
    )

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {column} IS NOT NULL
          AND {column} NOT IN :allowed_values;
        """
    ).bindparams(
        bindparam(
            "allowed_values",
            expanding=True
        )
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()

        evaluated_records = connection.execute(
            evaluated_query
        ).scalar_one()

        failed_records = connection.execute(
            failure_query,
            {"allowed_values": allowed_values}
        ).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )



def execute_foreign_key_rule(table_name, rule):
    """Check whether non-null foreign key values exist in a reference table."""

    column = rule["column"]
    reference_table = rule["reference_table"]
    reference_column = rule["reference_column"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
      f"""
      SELECT COUNT(*)
      FROM raw.{table_name}
      WHERE {column} IS NOT NULL;
      """
)
    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name} AS source
        WHERE source.{column} IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{reference_column} = source.{column}
          );
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
)

def execute_column_comparison_rule(table_name, rule):
    """Compare two numeric columns within the same table."""

    left_column, right_column = rule["columns"]
    operator = rule["operator"]

    operator_map = {
        "greater_than_or_equal": ">=",
        "greater_than": ">",
        "less_than_or_equal": "<=",
        "less_than": "<",
        "equal": "="
    }

    if operator not in operator_map:
        raise ValueError(
            f"Unsupported comparison operator: {operator}"
        )

    sql_operator = operator_map[operator]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name}
    WHERE {left_column} IS NOT NULL
      AND {right_column} IS NOT NULL;
    """
)

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {left_column} IS NOT NULL
          AND {right_column} IS NOT NULL
          AND NOT ({left_column} {sql_operator} {right_column});
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_state_region_match_rule(table_name, rule):
    """Validate that each state is assigned to the correct region."""

    state_column, region_column = rule["columns"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name}
        WHERE {state_column} IS NOT NULL
          AND {region_column} IS NOT NULL
          AND {state_column} IN :valid_states;
        """
    ).bindparams(bindparam("valid_states", expanding=True))

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()

        evaluated_records = connection.execute(
            evaluated_query,
            {"valid_states": list(STATE_REGION_MAP.keys())}
        ).scalar_one()

        failed_records = 0

        for state, expected_region in STATE_REGION_MAP.items():
            failure_query = text(
                f"""
                SELECT COUNT(*)
                FROM raw.{table_name}
                WHERE {state_column} = :state
                  AND {region_column} IS NOT NULL
                  AND {region_column} <> :expected_region;
                """
            )

            failures = connection.execute(
                failure_query,
                {
                    "state": state,
                    "expected_region": expected_region
                }
            ).scalar_one()

            failed_records += failures

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )



def execute_cross_table_date_comparison_rule(table_name, rule):
    """Compare a source date with a date from a referenced table."""

    source_date_column = next(
    column
    for column in rule["columns"]
    if column != rule["join_column"]
)
    join_column = rule["join_column"]
    reference_table = rule["reference_table"]
    reference_date_column = rule["reference_date_column"]
    operator = rule["operator"]

    operator_map = {
        "greater_than_or_equal": ">=",
        "greater_than": ">",
        "less_than_or_equal": "<=",
        "less_than": "<",
        "equal": "=",
    }

    if operator not in operator_map:
        raise ValueError(
            f"Unsupported comparison operator: {operator}"
        )

    sql_operator = operator_map[operator]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.{source_date_column} IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.{reference_date_column} IS NOT NULL
      );
    """
)
    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name} AS source
        WHERE source.{join_column} IS NOT NULL
          AND source.{source_date_column} IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.{reference_date_column} IS NOT NULL
          )
          AND NOT EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.{reference_date_column} IS NOT NULL
                AND source.{source_date_column}
                    {sql_operator}
                    reference.{reference_date_column}
          );
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_cross_table_value_match_rule(table_name, rule):
    """Compare a source value with the corresponding value in a reference table."""

    join_column = rule["join_column"]
    source_value_column = rule["source_value_column"]
    reference_table = rule["reference_table"]
    reference_value_column = rule["reference_value_column"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.{source_value_column} IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.{reference_value_column} IS NOT NULL
      );
    """
)

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name} AS source
        WHERE source.{join_column} IS NOT NULL
          AND source.{source_value_column} IS NOT NULL

          AND EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.{reference_value_column} IS NOT NULL
          )

          AND NOT EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.{reference_value_column}
                    = source.{source_value_column}
          );
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(
            failure_query
        ).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_payment_order_status_match_rule(table_name, rule):
    """Validate payment status against the corresponding order status."""

    join_column = rule["join_column"]
    reference_table = rule["reference_table"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.payment_status IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.order_status IN ('Completed', 'Cancelled', 'Returned')
      );
    """
)

    failed_records = 0

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        for order_status, expected_payment_status in ORDER_PAYMENT_STATUS_MAP.items():

            failure_query = text(
                f"""
                SELECT COUNT(*)
                FROM raw.{table_name} AS source
                WHERE source.{join_column} IS NOT NULL
                  AND source.payment_status IS NOT NULL

                  AND EXISTS (
                      SELECT 1
                      FROM raw.{reference_table} AS reference
                      WHERE reference.{join_column} = source.{join_column}
                        AND reference.order_status = :order_status
                  )

                  AND source.payment_status <> :expected_payment_status;
                """
            )

            failures = connection.execute(
                failure_query,
                {
                    "order_status": order_status,
                    "expected_payment_status": expected_payment_status
                }
            ).scalar_one()

            failed_records += failures

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_return_quantity_check_rule(table_name, rule):
    """Validate that returned quantity does not exceed purchased quantity."""

    join_column = rule["join_column"]
    reference_table = rule["reference_table"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.return_quantity IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.quantity IS NOT NULL
      );
    """
)

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name} AS source
        WHERE source.{join_column} IS NOT NULL
          AND source.return_quantity IS NOT NULL

          AND EXISTS (
             SELECT 1
             FROM raw.{reference_table} AS reference
             WHERE reference.{join_column} = source.{join_column}
             AND reference.quantity IS NOT NULL
)

          AND NOT EXISTS (
             SELECT 1
             FROM raw.{reference_table} AS reference
             WHERE reference.{join_column} = source.{join_column}
             AND reference.quantity IS NOT NULL
             AND source.return_quantity <= reference.quantity
)
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
        table_name=table_name,
        rule=rule,
        total_records=total_records,
        failed_records=failed_records,
        evaluated_records=evaluated_records
    )

def execute_refund_amount_reconciliation_rule(table_name, rule):
    """Validate refund amount against the original order-item transaction."""

    join_column = rule["join_column"]
    reference_table = rule["reference_table"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.return_quantity IS NOT NULL
      AND source.refund_amount IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.unit_price IS NOT NULL
            AND reference.discount_pct IS NOT NULL
      );
    """
)

    failure_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.return_quantity IS NOT NULL
      AND source.refund_amount IS NOT NULL

      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.unit_price IS NOT NULL
            AND reference.discount_pct IS NOT NULL
      )

      AND NOT EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.unit_price IS NOT NULL
            AND reference.discount_pct IS NOT NULL
            AND ABS(
                source.refund_amount -
                ROUND(
                    source.return_quantity
                    * reference.unit_price
                    * (1 - reference.discount_pct),
                    2
                )
            ) <= 0.01
      );
    """
)

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_return_window_check_rule(table_name, rule):
    """Validate that a return occurs within the allowed return window."""

    join_column = rule["join_column"]
    reference_table = rule["reference_table"]
    max_days = rule["max_days"]

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name} AS source
    WHERE source.{join_column} IS NOT NULL
      AND source.return_date IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM raw.{reference_table} AS reference
          WHERE reference.{join_column} = source.{join_column}
            AND reference.order_date IS NOT NULL
      );
    """
)

    failure_query = text(
        f"""
        SELECT COUNT(*)
        FROM raw.{table_name} AS source
        WHERE source.{join_column} IS NOT NULL
          AND source.return_date IS NOT NULL

          AND EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.order_date IS NOT NULL
          )

          AND NOT EXISTS (
              SELECT 1
              FROM raw.{reference_table} AS reference
              WHERE reference.{join_column} = source.{join_column}
                AND reference.order_date IS NOT NULL
                AND source.return_date >= reference.order_date
                AND source.return_date <=
                    reference.order_date + :max_days
          );
        """
    )

    with engine.connect() as connection:
     total_records = connection.execute(total_query).scalar_one()
     evaluated_records = connection.execute(evaluated_query).scalar_one()

     failed_records = connection.execute(
        failure_query,
        {"max_days": max_days}
     ).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_payment_amount_reconciliation_rule(table_name, rule):
    """Validate payment amount against the calculated order total."""

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )

    evaluated_query = text(
    """
    WITH order_totals AS (
        SELECT
            order_id
        FROM raw.order_items
        WHERE order_id IS NOT NULL
          AND quantity IS NOT NULL
          AND unit_price IS NOT NULL
          AND discount_pct IS NOT NULL
        GROUP BY order_id
    )

    SELECT COUNT(*)
    FROM raw.payments AS payment
    WHERE payment.order_id IS NOT NULL
      AND payment.payment_amount IS NOT NULL
      AND EXISTS (
          SELECT 1
          FROM order_totals AS totals
          WHERE totals.order_id = payment.order_id
      );
    """
)

    failure_query = text(
        """
        WITH order_totals AS (
            SELECT
                order_id,
                ROUND(
                    SUM(
                        quantity
                        * unit_price
                        * (1 - discount_pct)
                    ),
                    2
                ) AS expected_payment_amount
            FROM raw.order_items
            WHERE order_id IS NOT NULL
              AND quantity IS NOT NULL
              AND unit_price IS NOT NULL
              AND discount_pct IS NOT NULL
            GROUP BY order_id
        )

        SELECT COUNT(*)
        FROM raw.payments AS payment
        WHERE payment.order_id IS NOT NULL
          AND payment.payment_amount IS NOT NULL

          AND EXISTS (
              SELECT 1
              FROM order_totals AS totals
              WHERE totals.order_id = payment.order_id
          )

          AND NOT EXISTS (
              SELECT 1
              FROM order_totals AS totals
              WHERE totals.order_id = payment.order_id
                AND ABS(
                    payment.payment_amount
                    - totals.expected_payment_amount
                ) <= 0.01
          );
        """
    )

    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
)

def execute_category_subcategory_match_rule(table_name, rule):
    """Validate that each product category-subcategory pair is allowed."""

    total_query = text(
        f"SELECT COUNT(*) FROM raw.{table_name};"
    )
    evaluated_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name}
    WHERE category IS NOT NULL
      AND subcategory IS NOT NULL;
    """
    )

    failure_query = text(
    f"""
    SELECT COUNT(*)
    FROM raw.{table_name}
    WHERE category IS NOT NULL
      AND subcategory IS NOT NULL
      AND NOT (
            (category = 'Clothing'
                AND subcategory IN (
                    'Accessories',
                    'Activewear',
                    'Footwear',
                    'Men''s Clothing',
                    'Women''s Clothing'
                ))

         OR (category = 'Electronics'
                AND subcategory IN (
                    'Headphones',
                    'Laptops',
                    'Monitors',
                    'Smartphones',
                    'Tablets'
                ))

         OR (category = 'Home & Kitchen'
                AND subcategory IN (
                    'Cookware',
                    'Furniture',
                    'Home Decor',
                    'Kitchen Appliances',
                    'Storage'
                ))

         OR (category = 'Office Supplies'
                AND subcategory IN (
                    'Desk Accessories',
                    'Office Furniture',
                    'Paper',
                    'Printers',
                    'Writing Supplies'
                ))

         OR (category = 'Sports & Outdoors'
                AND subcategory IN (
                    'Camping',
                    'Cycling',
                    'Fitness Equipment',
                    'Outdoor Gear',
                    'Sports Accessories'
                ))
      );
    """
)
    with engine.connect() as connection:
        total_records = connection.execute(total_query).scalar_one()
        evaluated_records = connection.execute(evaluated_query).scalar_one()
        failed_records = connection.execute(failure_query).scalar_one()

    return build_rule_result(
    table_name=table_name,
    rule=rule,
    total_records=total_records,
    failed_records=failed_records,
    evaluated_records=evaluated_records
    )

def execute_rule(table_name, rule):
    """Route a quality rule to the correct executor."""

    rule_type = rule["rule_type"]

    executors = {
        "not_null": execute_not_null_rule,
        "regex": execute_regex_rule,
        "unique": execute_unique_rule,
        "greater_than": execute_greater_than_rule,
        "between": execute_between_rule,
        "allowed_values": execute_allowed_values_rule,
        "foreign_key_exists": execute_foreign_key_rule,
        "column_comparison": execute_column_comparison_rule,
        "state_region_match": execute_state_region_match_rule,
        "cross_table_date_comparison": execute_cross_table_date_comparison_rule,
        "cross_table_value_match": execute_cross_table_value_match_rule,
        "payment_order_status_match": execute_payment_order_status_match_rule,
        "return_quantity_check": execute_return_quantity_check_rule,
        "refund_amount_reconciliation": execute_refund_amount_reconciliation_rule,
        "return_window_check": execute_return_window_check_rule,
        "payment_amount_reconciliation": execute_payment_amount_reconciliation_rule,
        "category_subcategory_match": execute_category_subcategory_match_rule,
    }

    if rule_type not in executors:
        raise ValueError(
            f"Unsupported rule type: {rule_type}"
        )

    return executors[rule_type](
        table_name=table_name,
        rule=rule
    )

def run_supported_quality_rules(quality_rules):
    """Run all currently supported quality rules."""

    supported_rule_types = {
        "not_null",
        "regex",
        "unique",
        "greater_than",
        "between",
        "allowed_values",
        "foreign_key_exists",
        "column_comparison",
        "state_region_match",
        "cross_table_date_comparison",
        "cross_table_value_match",
        "payment_order_status_match",
        "return_quantity_check",
        "refund_amount_reconciliation",
        "return_window_check",
        "payment_amount_reconciliation",
        "category_subcategory_match",
    }

    results = []

    for table_name, table_config in quality_rules["tables"].items():

        for rule in table_config["rules"]:

            if rule["rule_type"] not in supported_rule_types:
                continue

            result = execute_rule(
                table_name=table_name,
                rule=rule
            )

            results.append(result)

    return results

if __name__ == "__main__":
    quality_rules = load_quality_rules()
    rules_configured = count_quality_rules(quality_rules)

    print("Quality rules loaded successfully.")
    print(f"Total configured rules: {rules_configured}")

    # Create a new historical audit run.
    run_id = create_audit_run(rules_configured)

    try:
        # Execute all configured data quality rules.
        results = run_supported_quality_rules(quality_rules)

        # Save rule-level results to PostgreSQL.
        save_rule_results(run_id, results)

        # Calculate quality scores.
        table_scores = calculate_table_scores(results)
        dimension_scores = calculate_dimension_scores(results)
        overall_score = calculate_overall_score(results)

        # Save quality scores to PostgreSQL.
        save_table_scores(run_id, table_scores)
        save_dimension_scores(run_id, dimension_scores)
        save_overall_score(run_id, overall_score)

        # Mark the audit run as successfully completed.
        complete_audit_run(
            run_id,
            len(results),
            rules_configured
        )

        print(f"Audit Run ID: {run_id}")
        print(f"Rules executed: {len(results)}")
        print(f"Overall Quality Score: {overall_score}%")

        print("\nData Quality Results")
        print("-" * 100)

        for result in results:
            print(
                f"{result['rule_id']} | "
                f"{result['table_name']} | "
                f"{result['rule_name']} | "
                f"Total: {result['total_records']} | "
                f"Evaluated: {result['evaluated_records']} | "
                f"Skipped: {result['skipped_records']} | "
                f"Failed: {result['failed_records']} | "
                f"Passed: {result['passed_records']} | "
                f"Pass Rate: {result['pass_rate']}%"
            )

    except Exception:
        fail_audit_run(run_id)
        raise