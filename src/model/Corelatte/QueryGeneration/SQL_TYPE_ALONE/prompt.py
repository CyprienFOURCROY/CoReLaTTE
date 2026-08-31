# prompt.py

from __future__ import annotations

import json
import random
from collections.abc import Callable, Sequence
from typing import Any

import pandas as pd



ADVERSARIAL_REQUIREMENT_BLOCK = """
### Mandatory semantic difficulty requirement

Every generated question must contain at least one subtle but valid semantic
distinction that can expose a reasoning mistake by an LLM.

Examples include:
- rows vs distinct entities;
- absence of a record vs an explicit zero or "No";
- existence of at least one qualifying record vs aggregation over all records;
- preserving the exact subset referred to by phrases such as "among those households";
- using the correct denominator in a proportion;
- comparing against a group-specific statistic rather than a global statistic;
- inclusive vs exclusive thresholds;
- selecting a specific record per entity before further computation.

This semantic trap is mandatory for every generated question.

The question must remain natural, precise, and unambiguous to a careful human reader.
Do not create difficulty through vague wording, convoluted grammar, or artificial ambiguity.
"""


ALLOWED_OPERATIONS = [
    "scan",
    "filter",
    "select",
    "join",
    "groupby",
    "sort",
    "limit",
    "semi_join",
    "anti_join",
    "scalar_filter",
]


QUERY_PLAN_TEMPLATE = {
    "question": "...",
    "query_plan": {
        "nodes": [
            {
                "id": "n1",
                "operation": "scan",
                "table": "<table_name>",
            },
            {
                "id": "n2",
                "operation": "filter",
                "input": "n1",
                "conditions": [
                    {
                        "column": "<column_name>",
                        "operator": "=",
                        "value": "<value>",
                    }
                ],
            },
        ],
        "output": "n2",
    },
}


JSON_RULES_PREAMBLE = """
STRICT JSON RULES
=================

You must return valid JSON only.

Do not return markdown.
Do not return explanations.
Do not return comments.
Do not use SQL strings.
Do not use pandas expressions.

The top-level JSON must have exactly this structure:

{
  "question": "...",
  "query_plan": {
    "nodes": [...],
    "output": "nX"
  }
}

NODE IDS
========

Use node ids: "n1", "n2", "n3", etc.

Every non-scan node must consume a previous node.

Correct:

{
  "id": "n2",
  "operation": "filter",
  "input": "n1",
  "conditions": [...]
}

Incorrect:

{
  "id": "n2",
  "operation": "filter",
  "input": "n9",
  "conditions": [...]
}

because "n9" was not defined before "n2".

IMPORTANT ABOUT ALL EXAMPLES BELOW
==================================

Table names, column names, aliases, values, and node ids shown in the node
documentation are illustrative only. Never copy an illustrative table or raw
column name into the generated query unless that exact name exists in the
supplied DATAFRAMES schema.
"""


# ---------------------------------------------------------------------------
# Flavor pools
# ---------------------------------------------------------------------------
#
# The examples below are illustrative only. They intentionally use several
# different mini-schemas so the model does not learn one fixed surface form.
# The real tables/columns available to the generated query are still injected
# later in DATAFRAMES + DATAFRAME DESCRIPTION.
#
# Flavor is split into several independent axes:
#   1. lexical / cosmetic: names, thresholds, aliases;
#   2. semantic: operators, aggregation functions, join types;
#   3. structural: one/two group keys, one/two aggregations, scalar-subquery
#      context, fan-out topology;
#   4. wording: equivalent instruction phrasing.
#
# Keeping these axes independent gives much more diversity than selecting one
# monolithic example bundle for the whole prompt.

SCAN_TABLE_EXAMPLES = [
    "people",
    "households",
    "visits",
    "schools",
    "transactions",
    "vehicles",
    "survey_responses",
    "employment_records",
]

FILTER_EXAMPLES = [
    {"column": "age", "operator": ">=", "value": 18},
    {"column": "income", "operator": ">", "value": 0},
    {"column": "status", "operator": "=", "value": 1},
    {"column": "region_code", "operator": "in", "value": [3, 4]},
    {"column": "category", "operator": "not_in", "value": [7, 9]},
    {"column": "score", "operator": "<", "value": 50},
    {"column": "year", "operator": "<=", "value": 2024},
    {"column": "occupation", "operator": "contains", "value": "farm"},
    {"column": "household_size", "operator": "!=", "value": 1},
]

SELECT_EXAMPLES = [
    ["household_id", "age"],
    ["region", "income"],
    ["person_id", "status", "score"],
    ["school_id", "district", "enrollment"],
    ["customer_id", "amount", "year"],
    ["vehicle_id", "region", "mileage"],
]

JOIN_EXAMPLES = [
    {
        "left_on": "household_id",
        "right_on": "household_id",
        "join_type": "inner",
    },
    {
        "left_on": "person_id",
        "right_on": "respondent_id",
        "join_type": "left",
    },
    {
        "left_on": "school_id",
        "right_on": "school_id",
        "join_type": "inner",
    },
    {
        "left_on": "customer_id",
        "right_on": "customer_id",
        "join_type": "right",
    },
    {
        "left_on": "region_code",
        "right_on": "region_id",
        "join_type": "outer",
    },
]

EXISTENCE_JOIN_EXAMPLES = [
    {"left_on": "household_id", "right_on": "household_id"},
    {"left_on": "person_id", "right_on": "respondent_id"},
    {"left_on": "school_id", "right_on": "school_id"},
    {"left_on": "customer_id", "right_on": "customer_id"},
    {"left_on": "region_code", "right_on": "region_id"},
]

GROUPBY_EXAMPLES = [
    {
        "by": ["region"],
        "aggregations": [
            {"column": "age", "function": "mean", "alias": "avg_age"},
        ],
    },
    {
        "by": ["state"],
        "aggregations": [
            {"column": "income", "function": "sum", "alias": "total_income"},
            {"column": "household_id", "function": "count", "alias": "n_households"},
        ],
    },
    {
        "by": ["district", "year"],
        "aggregations": [
            {"column": "score", "function": "mean", "alias": "avg_score"},
            {"column": "score", "function": "max", "alias": "max_score"},
        ],
    },
    {
        "by": ["category"],
        "aggregations": [
            {"column": "amount", "function": "min", "alias": "min_amount"},
        ],
    },
    {
        "by": ["region", "status"],
        "aggregations": [
            {"column": "person_id", "function": "count", "alias": "n_people"},
        ],
    },
]

SORT_EXAMPLES = [
    {"by": "avg_age", "ascending": False},
    {"by": "total_income", "ascending": False},
    {"by": "min_amount", "ascending": True},
    {"by": "n_people", "ascending": True},
    {"by": "avg_score", "ascending": False},
]

LIMIT_EXAMPLES = [3, 5, 7, 10, 15, 20]

SCALAR_NODE_EXAMPLES = [
    {
        "column": "age",
        "operator": ">",
        "scalar_column": "avg_age",
        "sql_agg": "AVG",
    },
    {
        "column": "income",
        "operator": ">=",
        "scalar_column": "mean_income",
        "sql_agg": "AVG",
    },
    {
        "column": "score",
        "operator": "<",
        "scalar_column": "avg_score",
        "sql_agg": "AVG",
    },
    {
        "column": "expense",
        "operator": ">",
        "scalar_column": "max_reference_expense",
        "sql_agg": "MAX",
    },
    {
        "column": "mileage",
        "operator": "<=",
        "scalar_column": "min_reference_mileage",
        "sql_agg": "MIN",
    },
]


# Backwards-compatible name retained for external code that may import it.
# The prompt builder itself now uses the compositional pools above.
EXAMPLE_FLAVORS = [
    {
        "table": "ii_portad",
        "filter_column": "edad",
        "filter_operator": ">=",
        "filter_value": 18,
        "select_columns": ["ent", "edad"],
        "join_key": "folio",
        "group_column": "ent",
        "agg_column": "edad",
        "agg_function": "mean",
        "agg_alias": "avg_age",
        "count_alias": "n_individuals",
        "limit_n": 10,
        "scalar_column": "edad",
        "scalar_operator": ">",
        "scalar_alias": "avg_age",
    },
    {
        "table": "ii_in",
        "filter_column": "in02a10",
        "filter_operator": ">",
        "filter_value": 0,
        "select_columns": ["folio", "in02a10"],
        "join_key": "folio",
        "group_column": "ent",
        "agg_column": "in02a10",
        "agg_function": "sum",
        "agg_alias": "total_income",
        "count_alias": "n_households",
        "limit_n": 5,
        "scalar_column": "in02a10",
        "scalar_operator": ">=",
        "scalar_alias": "avg_income",
    },
    {
        "table": "ii_su",
        "filter_column": "su01",
        "filter_operator": "=",
        "filter_value": 1,
        "select_columns": ["folio", "su01"],
        "join_key": "folio",
        "group_column": "ent",
        "agg_column": "su01",
        "agg_function": "count",
        "agg_alias": "n_farming_households",
        "count_alias": "n_households",
        "limit_n": 3,
        "scalar_column": "su234",
        "scalar_operator": "<",
        "scalar_alias": "avg_seed_expense",
    },
    {
        "table": "ii_vlh",
        "filter_column": "vlh04",
        "filter_operator": "in",
        "filter_value": [3, 4],
        "select_columns": ["folio", "vlh04"],
        "join_key": "folio",
        "group_column": "ent",
        "agg_column": "vlh04",
        "agg_function": "mean",
        "agg_alias": "avg_safety_score",
        "count_alias": "n_respondents",
        "limit_n": 10,
        "scalar_column": "vlh18a",
        "scalar_operator": ">",
        "scalar_alias": "avg_robbery_count",
    },
]


# Bias-specific semantic worlds. These are kept coherent within each block,
# while the node documentation above remains fully compositional.
HAVING_EXAMPLES = [
    {
        "group_by": ["state"],
        "aggregations": [
            {"column": "household_id", "function": "count", "alias": "n_households"},
            {"column": "safety_score", "function": "mean", "alias": "avg_safety"},
        ],
        "condition": {"column": "n_households", "operator": ">=", "value": 5},
        "question_hint": "among states represented by at least five households",
    },
    {
        "group_by": ["district"],
        "aggregations": [
            {"column": "test_score", "function": "mean", "alias": "avg_test_score"},
        ],
        "condition": {"column": "avg_test_score", "operator": ">", "value": 70},
        "question_hint": "for districts whose average test score exceeds 70",
    },
    {
        "group_by": ["region", "year"],
        "aggregations": [
            {"column": "amount", "function": "sum", "alias": "total_amount"},
            {"column": "transaction_id", "function": "count", "alias": "n_transactions"},
        ],
        "condition": {"column": "total_amount", "operator": ">=", "value": 10000},
        "question_hint": "for region-years with total amount of at least 10,000",
    },
    {
        "group_by": ["category"],
        "aggregations": [
            {"column": "price", "function": "max", "alias": "max_price"},
        ],
        "condition": {"column": "max_price", "operator": "<", "value": 500},
        "question_hint": "only for categories whose maximum price is below 500",
    },
]

SCALAR_BIAS_EXAMPLES = [
    {
        "main_table": "people",
        "scalar_table": "people",
        "column": "age",
        "operator": ">",
        "function": "mean",
        "scalar_alias": "avg_age",
        "subset_filter": None,
        "question_hint": "people older than the overall average age",
    },
    {
        "main_table": "workers",
        "scalar_table": "workers",
        "column": "income",
        "operator": ">=",
        "function": "mean",
        "scalar_alias": "avg_urban_income",
        "subset_filter": {"column": "area_type", "operator": "=", "value": "urban"},
        "question_hint": "workers whose income is at least the average income among urban workers",
    },
    {
        "main_table": "students",
        "scalar_table": "students",
        "column": "score",
        "operator": "<",
        "function": "mean",
        "scalar_alias": "avg_senior_score",
        "subset_filter": {"column": "grade", "operator": ">=", "value": 12},
        "question_hint": "students scoring below the average among grade-12-or-higher students",
    },
    {
        "main_table": "vehicles",
        "scalar_table": "vehicles",
        "column": "mileage",
        "operator": ">",
        "function": "max",
        "scalar_alias": "max_electric_mileage",
        "subset_filter": {"column": "fuel", "operator": "=", "value": "electric"},
        "question_hint": "vehicles whose mileage exceeds the maximum mileage among electric vehicles",
    },
]

PROVENANCE_EXAMPLES = [
    {
        "left_table": "households",
        "right_table": "community",
        "key": "household_id",
        "collision": "region",
        "left_value": "income",
        "right_value": "safety_score",
    },
    {
        "left_table": "students",
        "right_table": "attendance",
        "key": "student_id",
        "collision": "year",
        "left_value": "test_score",
        "right_value": "days_absent",
    },
    {
        "left_table": "customers",
        "right_table": "orders",
        "key": "customer_id",
        "collision": "status",
        "left_value": "age",
        "right_value": "amount",
    },
    {
        "left_table": "vehicles",
        "right_table": "inspections",
        "key": "vehicle_id",
        "collision": "region_code",
        "left_value": "mileage",
        "right_value": "inspection_score",
    },
]

FANOUT_EXAMPLES = [
    {
        "unit": "household",
        "key": "household_id",
        "anchor": "households",
        "branch_a": "people",
        "branch_a_rows": "multiple people per household",
        "branch_a_metric": "person_count",
        "branch_b": "expenses",
        "branch_b_rows": "multiple expense records per household",
        "branch_b_metric": "total_expense",
        "final_metric": "average household expense by person-count band",
    },
    {
        "unit": "school",
        "key": "school_id",
        "anchor": "schools",
        "branch_a": "students",
        "branch_a_rows": "multiple students per school",
        "branch_a_metric": "student_count",
        "branch_b": "exams",
        "branch_b_rows": "multiple exam records per school",
        "branch_b_metric": "avg_exam_score",
        "final_metric": "school-level exam performance by enrollment size",
    },
    {
        "unit": "customer",
        "key": "customer_id",
        "anchor": "customers",
        "branch_a": "orders",
        "branch_a_rows": "multiple orders per customer",
        "branch_a_metric": "order_count",
        "branch_b": "payments",
        "branch_b_rows": "multiple payments per customer",
        "branch_b_metric": "total_paid",
        "final_metric": "customer-level payment totals by order frequency",
    },
    {
        "unit": "vehicle",
        "key": "vehicle_id",
        "anchor": "vehicles",
        "branch_a": "repairs",
        "branch_a_rows": "multiple repair records per vehicle",
        "branch_a_metric": "repair_count",
        "branch_b": "fuel_logs",
        "branch_b_rows": "multiple fuel logs per vehicle",
        "branch_b_metric": "total_fuel_cost",
        "final_metric": "vehicle-level fuel cost by repair frequency",
    },
]

MULTI_JOIN_EXAMPLES = [
    {
        "table_a": "people",
        "table_b": "households",
        "table_c": "community",
        "key_ab": "household_id",
        "key_bc": "community_id",
        "condition_a": "a person-level condition",
        "condition_b": "a household attribute",
        "value_c": "a community-level value",
    },
    {
        "table_a": "students",
        "table_b": "schools",
        "table_c": "districts",
        "key_ab": "school_id",
        "key_bc": "district_id",
        "condition_a": "a student-level condition",
        "condition_b": "a school characteristic",
        "value_c": "a district-level value",
    },
    {
        "table_a": "orders",
        "table_b": "customers",
        "table_c": "regions",
        "key_ab": "customer_id",
        "key_bc": "region_id",
        "condition_a": "an order-level condition",
        "condition_b": "a customer attribute",
        "value_c": "a regional value",
    },
]


REQUIREMENT_OPENERS = [
    "The query plan MUST include",
    "Construct the plan so that it contains",
    "The resulting plan is required to contain",
]

QUESTION_OPENERS = [
    "The generated question MUST genuinely require",
    "Phrase the analytical question so that answering it requires",
    "The question should be impossible to answer correctly without",
]

CHECK_OPENERS = [
    "Before returning the plan, internally verify",
    "As a final internal consistency check, verify",
    "Before emitting JSON, reason through",
]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _pick(rng: random.Random, values: Sequence[Any]) -> Any:
    return values[rng.randrange(len(values))]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _dependency_ids(rng: random.Random, n_inputs: int) -> tuple[str, list[str]]:
    """Return one output id and n input ids with every input id < output id."""
    values = sorted(rng.sample(range(1, 13), n_inputs + 1))
    output_id = f"n{values[-1]}"
    input_ids = [f"n{i}" for i in values[:-1]]
    rng.shuffle(input_ids)
    return output_id, input_ids


def _scan_id(rng: random.Random) -> str:
    return f"n{rng.randint(1, 9)}"


def _render_aggregations(aggregations: list[dict[str, Any]], indent: int = 4) -> str:
    return json.dumps(aggregations, indent=indent, ensure_ascii=False)


def _render_conditions(conditions: list[dict[str, Any]], indent: int = 4) -> str:
    return json.dumps(conditions, indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Per-node documentation, independently flavored
# ---------------------------------------------------------------------------

def _scan_node_doc(rng: random.Random) -> str:
    node_id = _scan_id(rng)
    table = _pick(rng, SCAN_TABLE_EXAMPLES)

    return f"""SCAN NODE
=========

A scan node loads one dataframe.

Required format:

{{
  "id": "{node_id}",
  "operation": "scan",
  "table": "{table}"
}}"""


def _filter_node_doc(rng: random.Random) -> str:
    node_id, (input_id,) = _dependency_ids(rng, 1)
    example = _pick(rng, FILTER_EXAMPLES)
    value = _json(example["value"])

    return f"""FILTER NODE
===========

A filter node corresponds to SQL WHERE.

Required format:

{{
  "id": "{node_id}",
  "operation": "filter",
  "input": "{input_id}",
  "conditions": [
    {{
      "column": "{example['column']}",
      "operator": "{example['operator']}",
      "value": {value}
    }}
  ]
}}

Allowed operators:

"=", "!=", ">", ">=", "<", "<=", "in", "not_in", "contains"

A filter may contain more than one condition when the question requires it.
Each condition must still be a structured object inside "conditions".

Incorrect:

{{
  "id": "{node_id}",
  "operation": "filter",
  "input": "{input_id}",
  "condition": "{example['column']} {example['operator']} {example['value']}"
}}

Reason: never use "condition" as a string. Use "conditions" as a list of structured objects."""


def _select_node_doc(rng: random.Random) -> str:
    node_id, (input_id,) = _dependency_ids(rng, 1)
    columns = _pick(rng, SELECT_EXAMPLES)

    return f"""SELECT NODE
===========

A select node keeps only selected columns.

Required format:

{{
  "id": "{node_id}",
  "operation": "select",
  "input": "{input_id}",
  "columns": {_json(columns)}
}}"""


def _join_node_doc(rng: random.Random) -> str:
    node_id, input_ids = _dependency_ids(rng, 2)
    left_id, right_id = input_ids
    example = _pick(rng, JOIN_EXAMPLES)

    return f"""JOIN NODE
=========

A join node corresponds to SQL JOIN.

It keeps columns from both the left and right inputs.

Required format:

{{
  "id": "{node_id}",
  "operation": "join",
  "left_input": "{left_id}",
  "right_input": "{right_id}",
  "left_on": "{example['left_on']}",
  "right_on": "{example['right_on']}",
  "join_type": "{example['join_type']}"
}}

Allowed join types:

"inner", "left", "right", "outer"

The left and right key names may differ if the two dataframes use different
names for the same logical key.

Incorrect:

{{
  "id": "{node_id}",
  "operation": "join",
  "left": "{left_id}",
  "right": "{right_id}",
  "on": ["{example['left_on']}"]
}}

Reason: use "left_input", "right_input", "left_on", "right_on", and "join_type"."""


def _semi_join_node_doc(rng: random.Random) -> str:
    node_id, input_ids = _dependency_ids(rng, 2)
    left_id, right_id = input_ids
    example = _pick(rng, EXISTENCE_JOIN_EXAMPLES)

    return f"""SEMI_JOIN NODE
==============

A semi_join corresponds to SQL WHERE key IN (subquery).

It keeps rows from the left input that have a matching key in the right input.
It only keeps columns from the left input.

Required format:

{{
  "id": "{node_id}",
  "operation": "semi_join",
  "left_input": "{left_id}",
  "right_input": "{right_id}",
  "left_on": "{example['left_on']}",
  "right_on": "{example['right_on']}"
}}"""


def _anti_join_node_doc(rng: random.Random) -> str:
    node_id, input_ids = _dependency_ids(rng, 2)
    left_id, right_id = input_ids
    example = _pick(rng, EXISTENCE_JOIN_EXAMPLES)

    return f"""ANTI_JOIN NODE
==============

An anti_join corresponds to SQL WHERE key NOT IN (subquery).

It keeps rows from the left input that do not have a matching key in the right input.
It only keeps columns from the left input.

Required format:

{{
  "id": "{node_id}",
  "operation": "anti_join",
  "left_input": "{left_id}",
  "right_input": "{right_id}",
  "left_on": "{example['left_on']}",
  "right_on": "{example['right_on']}"
}}"""


def _groupby_node_doc(rng: random.Random) -> str:
    node_id, (input_id,) = _dependency_ids(rng, 1)
    example = _pick(rng, GROUPBY_EXAMPLES)
    by = _json(example["by"])
    aggregations = _render_aggregations(example["aggregations"], indent=4)

    return f"""GROUPBY NODE
============

A groupby node corresponds to SQL GROUP BY with aggregations.

The "by" list may contain one column, several columns, or be empty. Use
"by": [] only when aggregating the entire input into exactly one scalar row.

Required format:

{{
  "id": "{node_id}",
  "operation": "groupby",
  "input": "{input_id}",
  "by": {by},
  "aggregations": {aggregations}
}}

Allowed aggregation functions:

"sum", "mean", "count", "min", "max"

Incorrect aggregation object:

{{
  "column": "{example['aggregations'][0]['column']}",
  "agg": "{example['aggregations'][0]['function']}",
  "as": "{example['aggregations'][0]['alias']}"
}}

Reason: use "function" and "alias", not "agg" and "as"."""


def _sort_node_doc(rng: random.Random) -> str:
    node_id, (input_id,) = _dependency_ids(rng, 1)
    example = _pick(rng, SORT_EXAMPLES)
    ascending = str(example["ascending"]).lower()

    return f"""SORT NODE
=========

A sort node corresponds to SQL ORDER BY.

Required format:

{{
  "id": "{node_id}",
  "operation": "sort",
  "input": "{input_id}",
  "by": "{example['by']}",
  "ascending": {ascending}
}}"""


def _limit_node_doc(rng: random.Random) -> str:
    node_id, (input_id,) = _dependency_ids(rng, 1)
    n = _pick(rng, LIMIT_EXAMPLES)

    return f"""LIMIT NODE
==========

A limit node corresponds to SQL LIMIT.

Required format:

{{
  "id": "{node_id}",
  "operation": "limit",
  "input": "{input_id}",
  "n": {n}
}}"""


def _scalar_filter_node_doc(rng: random.Random) -> str:
    node_id, input_ids = _dependency_ids(rng, 2)
    input_id, scalar_input_id = input_ids
    example = _pick(rng, SCALAR_NODE_EXAMPLES)

    return f"""SCALAR_FILTER NODE
==================

A scalar_filter corresponds to a comparison with a scalar subquery.

Example SQL idea:

WHERE {example['column']} {example['operator']} (SELECT {example['sql_agg']}({example['column']}) FROM table)

Required format:

{{
  "id": "{node_id}",
  "operation": "scalar_filter",
  "input": "{input_id}",
  "column": "{example['column']}",
  "operator": "{example['operator']}",
  "scalar_input": "{scalar_input_id}",
  "scalar_column": "{example['scalar_column']}"
}}

The scalar_input must be a previous node that returns exactly one row and
contains scalar_column."""


_SHUFFLABLE_NODE_DOCS: dict[str, Callable[[random.Random], str]] = {
    "filter": _filter_node_doc,
    "select": _select_node_doc,
    "join": _join_node_doc,
    "semi_join": _semi_join_node_doc,
    "anti_join": _anti_join_node_doc,
    "groupby": _groupby_node_doc,
    "sort": _sort_node_doc,
    "limit": _limit_node_doc,
    "scalar_filter": _scalar_filter_node_doc,
}


def build_json_rules(rng: random.Random | None = None) -> str:
    """Build independently flavored node documentation.

    Passing an RNG makes prompt generation reproducible. If omitted, a fresh
    RNG is created so callers of the old zero-argument API continue to work.
    """
    rng = rng or random.Random()

    shuffled_ops = list(_SHUFFLABLE_NODE_DOCS)
    rng.shuffle(shuffled_ops)

    sections = [_scan_node_doc(rng)] + [
        _SHUFFLABLE_NODE_DOCS[op](rng) for op in shuffled_ops
    ]

    return JSON_RULES_PREAMBLE.strip() + "\n\n\n" + "\n\n\n".join(sections)


# ---------------------------------------------------------------------------
# Flavored bias blocks
# ---------------------------------------------------------------------------

def _having_bias_block(rng: random.Random) -> str:
    example = _pick(rng, HAVING_EXAMPLES)
    group_id, (input_id,) = _dependency_ids(rng, 1)
    having_id, _ = _dependency_ids_above(rng, [group_id])

    aggregations = _render_aggregations(example["aggregations"], indent=2)
    condition = _render_conditions([example["condition"]], indent=2)
    req = _pick(rng, REQUIREMENT_OPENERS)
    qreq = _pick(rng, QUESTION_OPENERS)

    return f"""REQUIRED PATTERN: POST-AGGREGATION FILTER (SQL HAVING-STYLE)
============================================================

{req} a HAVING-style pattern: first aggregate rows with a "groupby" node,
then apply a "filter" to the aggregated result.

The required structure is:

1. A "groupby" node that groups by one or more columns and produces one or
   more aggregation outputs with aliases.
2. A later "filter" whose input is the groupby output, not the raw rows.
3. The filter references an aggregation alias or another column present in
   the groupby output.

Illustrative shape:

{{
  "id": "{group_id}",
  "operation": "groupby",
  "input": "{input_id}",
  "by": {_json(example['group_by'])},
  "aggregations": {aggregations}
}}

{{
  "id": "{having_id}",
  "operation": "filter",
  "input": "{group_id}",
  "conditions": {condition}
}}

The essential property is evaluation order: aggregate first, filter groups
second. Filtering raw rows before grouping is SQL WHERE, not HAVING.

{qreq} the post-aggregation restriction. A possible semantic pattern is:
"{example['question_hint']}"."""


def _dependency_ids_above(
    rng: random.Random,
    existing_ids: Sequence[str],
    count: int = 1,
) -> tuple[str, list[str]]:
    """Create an id numerically above all ids in existing_ids.

    This is used by multi-node examples that must visibly preserve dependency
    order across separately constructed snippets.
    """
    max_existing = max(int(node_id[1:]) for node_id in existing_ids)
    available = list(range(max_existing + 1, max_existing + 1 + max(4, count + 2)))
    chosen = sorted(rng.sample(available, count))
    ids = [f"n{i}" for i in chosen]
    return ids[-1], ids[:-1]


def _scalar_filter_bias_block(rng: random.Random) -> str:
    example = _pick(rng, SCALAR_BIAS_EXAMPLES)
    req = _pick(rng, REQUIREMENT_OPENERS)
    qreq = _pick(rng, QUESTION_OPENERS)

    # Build a coherent dependency-ordered miniature branch.
    main_scan = "n1"
    scalar_scan = "n2"
    next_num = 3

    subset_text = ""
    scalar_input = scalar_scan
    if example["subset_filter"] is not None:
        subset = example["subset_filter"]
        scalar_filter_id = f"n{next_num}"
        next_num += 1
        subset_text = f'''\n{{
  "id": "{scalar_filter_id}",
  "operation": "filter",
  "input": "{scalar_scan}",
  "conditions": [
    {{
      "column": "{subset['column']}",
      "operator": "{subset['operator']}",
      "value": {_json(subset['value'])}
    }}
  ]
}}\n'''
        scalar_input = scalar_filter_id

    group_id = f"n{next_num}"
    scalar_filter_id = f"n{next_num + 1}"

    return f"""REQUIRED PATTERN: SCALAR_FILTER NODE
=====================================

{req} at least one "scalar_filter" node. The plan is invalid for this bias
without one.

A scalar_filter compares a row-level value against a scalar computed by a
separate branch. The scalar branch may use the whole comparison population
or a filtered reference subset.

Illustrative topology:

{{
  "id": "{main_scan}",
  "operation": "scan",
  "table": "{example['main_table']}"
}}

{{
  "id": "{scalar_scan}",
  "operation": "scan",
  "table": "{example['scalar_table']}"
}}
{subset_text}
{{
  "id": "{group_id}",
  "operation": "groupby",
  "input": "{scalar_input}",
  "by": [],
  "aggregations": [
    {{
      "column": "{example['column']}",
      "function": "{example['function']}",
      "alias": "{example['scalar_alias']}"
    }}
  ]
}}

{{
  "id": "{scalar_filter_id}",
  "operation": "scalar_filter",
  "input": "{main_scan}",
  "column": "{example['column']}",
  "operator": "{example['operator']}",
  "scalar_input": "{group_id}",
  "scalar_column": "{example['scalar_alias']}"
}}

For a whole-branch scalar, use "by": [] so the groupby returns exactly one
row. Do not compare the main branch against a grouped multi-row result.

{qreq} the scalar comparison. One possible semantic formulation is:
"{example['question_hint']}"."""


def _column_provenance_bias_block(rng: random.Random) -> str:
    example = _pick(rng, PROVENANCE_EXAMPLES)
    req = _pick(rng, REQUIREMENT_OPENERS)
    qreq = _pick(rng, QUESTION_OPENERS)
    check = _pick(rng, CHECK_OPENERS)

    collision = example["collision"]

    return f"""REQUIRED PATTERN: COLUMN PROVENANCE AFTER JOIN
===============================================

{req} a real "join" between two tables with at least one overlapping non-key
column name. This is intended to force reasoning about post-join column
provenance, not merely key existence.

Illustrative schema:

{example['left_table']}:
{example['key']} | {collision} | {example['left_value']}

{example['right_table']}:
{example['key']} | {collision} | {example['right_value']}

After a pandas-style join on "{example['key']}", the overlapping non-key
column may become:

{example['key']} | {collision}_x | {example['left_value']} | {collision}_y | {example['right_value']}

Every later filter, groupby, select, sort, or second join must reference the
actual post-join names. Do not refer to bare "{collision}" if pandas would
have replaced it with suffixed columns.

{qreq} at least one value from the left table and one value from the right
table. Do not satisfy this requirement with semi_join or anti_join.

{check}:
1. which input each required column originates from;
2. which name it has after every join;
3. whether a second join creates a new collision or suffix;
4. whether all downstream nodes use the resulting names."""


def _fanout_topology_text(rng: random.Random, example: dict[str, str]) -> str:
    topology = rng.choice(["branches_first", "anchor_then_a", "anchor_then_b"])
    anchor = example["anchor"]
    a = example["branch_a"]
    b = example["branch_b"]
    a_metric = example["branch_a_metric"]
    b_metric = example["branch_b_metric"]
    key = example["key"]

    if topology == "branches_first":
        return f"""One safe illustrative topology is:

{a} -> groupby {key} -> {a_metric}
{b} -> groupby {key} -> {b_metric}
join the two one-row-per-{example['unit']} summaries on {key}
optionally join {anchor} afterward if anchor attributes are needed

Both many-row branches are reduced to the intended grain before they meet."""

    if topology == "anchor_then_a":
        return f"""Another safe topology is:

{a} -> groupby {key} -> {a_metric}
join {anchor} with the aggregated {a} branch on {key}
{b} -> groupby {key} -> {b_metric}
join the aggregated {b} branch to that combined one-row-per-{example['unit']} result

The join order changes, but the two many-row branches still cannot multiply
each other because each is reduced to one row per {example['unit']} first."""

    return f"""Another safe topology is:

{b} -> groupby {key} -> {b_metric}
join {anchor} with the aggregated {b} branch on {key}
{a} -> groupby {key} -> {a_metric}
join the aggregated {a} branch to that combined one-row-per-{example['unit']} result

The important invariant is the grain, not a memorized left-to-right join order."""


def _join_fanout_bias_block(rng: random.Random) -> str:
    example = _pick(rng, FANOUT_EXAMPLES)
    qreq = _pick(rng, QUESTION_OPENERS)
    check = _pick(rng, CHECK_OPENERS)
    topology = _fanout_topology_text(rng, example)

    return f"""REQUIRED PATTERN: JOIN CARDINALITY / FAN-OUT REASONING
=======================================================

This query must require reasoning about row multiplication caused by joins.
The intended unit of observation is the {example['unit']}.

Illustrative grains:

{example['anchor']}: typically one row per {example['unit']}
{example['branch_a']}: {example['branch_a_rows']}
{example['branch_b']}: {example['branch_b_rows']}

A naïve raw join of two many-per-{example['unit']} branches on
"{example['key']}" can multiply rows within each {example['unit']} and corrupt
counts, sums, or averages.

{topology}

The generated plan must avoid accidental double counting and preserve the
intended analytical grain. It should not mechanically pre-aggregate every
branch: first reason about which keys are unique and where fan-out can occur.

{qreq} information from multiple tables in a way where a naïve raw-row join
could change the answer. A representative target statistic is
"{example['final_metric']}".

{check}:
- what one row represents in each input table;
- whether the join key is unique on either side;
- which join can multiply rows;
- which branch, if any, must be aggregated before joining;
- whether the final aggregation is performed at the intended grain."""


def _multi_join_bias_block(rng: random.Random) -> str:
    example = _pick(rng, MULTI_JOIN_EXAMPLES)
    qreq = _pick(rng, QUESTION_OPENERS)
    join_type_1 = rng.choice(["inner", "left"])
    join_type_2 = rng.choice(["inner", "left"])

    # Two valid topological variants: chain A-B-C or chain C-B-A.
    reverse = rng.choice([False, True])

    if not reverse:
        steps = f"""1. scan {example['table_a']} -> n1
2. scan {example['table_b']} -> n2
3. join n1 and n2 on {example['key_ab']} -> n3
4. scan {example['table_c']} -> n4
5. join n3 and n4 using the key connecting {example['table_b']} to {example['table_c']} -> n5"""
        first_left, first_right = "n1", "n2"
        first_key_left = example["key_ab"]
        first_key_right = example["key_ab"]
        second_left, second_right = "n3", "n4"
        second_key_left = example["key_bc"]
        second_key_right = example["key_bc"]
    else:
        steps = f"""1. scan {example['table_c']} -> n1
2. scan {example['table_b']} -> n2
3. join n1 and n2 on {example['key_bc']} -> n3
4. scan {example['table_a']} -> n4
5. join n3 and n4 using the key connecting {example['table_b']} to {example['table_a']} -> n5"""
        first_left, first_right = "n1", "n2"
        first_key_left = example["key_bc"]
        first_key_right = example["key_bc"]
        second_left, second_right = "n3", "n4"
        second_key_left = example["key_ab"]
        second_key_right = example["key_ab"]

    return f"""REQUIRED PATTERN: CHAINED JOINS ACROSS 3 TABLES
==================================================

The query plan MUST contain at least TWO real "join" nodes chaining THREE
different scanned tables into one combined branch. semi_join and anti_join do
not count because they discard right-side columns.

One valid illustrative topology for this prompt instance is:

{steps}

Example join nodes:

{{
  "id": "n3",
  "operation": "join",
  "left_input": "{first_left}",
  "right_input": "{first_right}",
  "left_on": "{first_key_left}",
  "right_on": "{first_key_right}",
  "join_type": "{join_type_1}"
}}

{{
  "id": "n5",
  "operation": "join",
  "left_input": "{second_left}",
  "right_input": "{second_right}",
  "left_on": "{second_key_left}",
  "right_on": "{second_key_right}",
  "join_type": "{join_type_2}"
}}

The second join must consume the first join's output rather than starting a
separate unrelated branch.

Watch for overlapping non-key names after the first and second joins. If
pandas would suffix a column, downstream nodes must use the suffixed name.
A select immediately after a join is acceptable when it deliberately removes
unneeded colliding columns without dropping information required later.

{qreq} all three sources: {example['condition_a']} from {example['table_a']},
{example['condition_b']} from {example['table_b']}, and {example['value_c']}
from {example['table_c']}."""


BiasBuilder = Callable[[random.Random], str]

BIAS_BLOCKS: dict[str, BiasBuilder] = {
    "having": _having_bias_block,
    "scalar_filter": _scalar_filter_bias_block,
    "multi_join": _multi_join_bias_block,
    "column_provenance": _column_provenance_bias_block,
    "join_fanout": _join_fanout_bias_block,
}


# ---------------------------------------------------------------------------
# Dataframe summaries
# ---------------------------------------------------------------------------

def summarize_dataframe(
    name: str,
    df: pd.DataFrame,
    n_sample_rows: int = 3,
) -> str:
    if n_sample_rows < 0:
        raise ValueError("n_sample_rows must be >= 0")

    sample = df.head(n_sample_rows).to_dict(orient="records")

    summary = {
        "name": name,
        "n_rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample_rows": sample,
    }

    return json.dumps(summary, indent=2, ensure_ascii=False, default=str)


def summarize_dataframes(
    dataframes: dict[str, pd.DataFrame],
    n_sample_rows: int = 3,
) -> str:
    parts = []

    for name, df in dataframes.items():
        parts.append(summarize_dataframe(name, df, n_sample_rows))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Main prompt builder
# ---------------------------------------------------------------------------

def build_query_plan_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    number_of_nested_queries: int = 1,
    n_sample_rows: int = 3,
    bias: str | None = None,
    random_seed: int | None = None,
) -> str:
    """Build the query-plan generation prompt.

    This is backwards compatible with the previous API. The only new public
    argument is ``random_seed``. Leave it as None for fresh flavor on each
    call, or set it during experiments/tests for a reproducible prompt.
    """
    if number_of_nested_queries < 0:
        raise ValueError("number_of_nested_queries must be >= 0")

    rng = random.Random(random_seed)

    dataframe_summary = summarize_dataframes(
        dataframes=dataframes,
        n_sample_rows=n_sample_rows,
    )

    json_template = json.dumps(
        QUERY_PLAN_TEMPLATE,
        indent=2,
        ensure_ascii=False,
    )

    allowed_operations = ", ".join(ALLOWED_OPERATIONS)
    json_rules = build_json_rules(rng)

    realism_wording = rng.choice(
        [
            "Generate one realistic analytical question over the DataFrames.",
            "Formulate one plausible analytical question that can be answered from the DataFrames.",
            "Create one natural data-analysis question grounded in the supplied DataFrames.",
        ]
    )

    dependency_wording = rng.choice(
        [
            "define nodes in dependency order",
            "order nodes so every dependency has already been defined",
            "emit nodes in a valid topological/dependency order",
        ]
    )

    prompt = f"""
You are a query-planning assistant.

Your task is to generate a SQL-like query plan in JSON format.

The query plan will later be validated by a strict Pydantic schema and compiled into pandas code.

You are given:
1. A set of pandas DataFrames with their names, columns, dtypes, and sample rows.
2. A textual description explaining the semantic meaning of the DataFrames and their columns.
3. A required minimum number of nested query operations.

DATAFRAMES
==========

{dataframe_summary}

DATAFRAME DESCRIPTION
=====================

{dataframe_description}

ALLOWED OPERATIONS
==================

You may only use these operations:

{allowed_operations}

REQUIREMENTS
============


{ADVERSARIAL_REQUIREMENT_BLOCK}

{realism_wording}

Then generate a JSON query plan that answers this question.

The query plan must:
- use only the given DataFrame names;
- use only existing column names;
- use only the JSON field names defined below;
- contain at least {number_of_nested_queries} nested query operation(s);
- use node ids such as "n1", "n2", "n3", etc.;
- {dependency_wording};
- make every non-scan node depend only on previous nodes;
- define the final output node in the "output" field;
- return valid JSON only;
- not include markdown;
- not include explanations outside the JSON.

Nested query operations include:
- semi_join
- anti_join
- scalar_filter
- a node consuming the output of a previous aggregate/groupby node


Before returning the JSON, internally check that:
- no node uses "condition";
- no node uses "left", "right", "on", or "how";
- no aggregation uses "agg" or "as";
- aggregations is always a list, never a dictionary;
- filters always use "conditions" as a list;
- joins always use left_input, right_input, left_on, right_on, join_type;
- groupby "by" is always a list, including [] for a scalar aggregation;
- every referenced input node has already been defined;
- every referenced table and raw column exists in the supplied schema;
- the output JSON can be parsed by the provided Pydantic schema.

If your JSON contains any forbidden field, rewrite it before answering.

{json_rules}

OUTPUT TEMPLATE
===============

Your output must follow this general structure:

{json_template}

FINAL INSTRUCTION
=================

Return only the JSON object.
""".strip()

    if bias is not None:
        if bias not in BIAS_BLOCKS:
            raise ValueError(
                f"Unsupported bias: {bias!r}. Expected one of {sorted(BIAS_BLOCKS)}."
            )

        bias_block = BIAS_BLOCKS[bias](rng).strip()

        marker = "Before returning the JSON, internally check that:"
        if marker not in prompt:
            raise RuntimeError("Internal prompt marker not found")

        prompt = prompt.replace(
            marker,
            f"{bias_block}\n\n{marker}",
            1,
        )

    return prompt


__all__ = [
    "ALLOWED_OPERATIONS",
    "QUERY_PLAN_TEMPLATE",
    "EXAMPLE_FLAVORS",
    "BIAS_BLOCKS",
    "build_json_rules",
    "summarize_dataframe",
    "summarize_dataframes",
    "build_query_plan_prompt",
]
