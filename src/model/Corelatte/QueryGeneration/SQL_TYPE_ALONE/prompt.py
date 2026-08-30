# prompt.py

import json
import random
import pandas as pd


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
"""


# Illustrative-only flavors for the per-node-type example snippets below.
# These are NOT the real tables/columns for a given query -- the real dataframe
# schema is injected separately in the DATAFRAMES section. A random flavor and
# random node ids are picked fresh on every prompt build (and the doc section
# order is shuffled too, scan always first) so the model sees a worked example
# every time, but never always the exact same one -- otherwise every generated
# query plan tends to structurally mimic whichever single example it always saw.
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


def _random_ids(count: int) -> list[str]:
    return [f"n{i}" for i in random.sample(range(1, 9), count)]


def _scan_node_doc(flavor: dict) -> str:
    (node_id,) = _random_ids(1)

    return f"""SCAN NODE
=========

A scan node loads one dataframe.

Required format:

{{
  "id": "{node_id}",
  "operation": "scan",
  "table": "table_name"
}}"""


def _filter_node_doc(flavor: dict) -> str:
    node_id, input_id = _random_ids(2)
    value = json.dumps(flavor["filter_value"])

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
      "column": "{flavor['filter_column']}",
      "operator": "{flavor['filter_operator']}",
      "value": {value}
    }}
  ]
}}

Allowed operators:

"=", "!=", ">", ">=", "<", "<=", "in", "not_in", "contains"

Incorrect:

{{
  "id": "{node_id}",
  "operation": "filter",
  "input": "{input_id}",
  "condition": "{flavor['filter_column']} {flavor['filter_operator']} {flavor['filter_value']}"
}}

Reason: never use "condition" as a string. Use "conditions" as a list of structured objects."""


def _select_node_doc(flavor: dict) -> str:
    node_id, input_id = _random_ids(2)
    columns = json.dumps(flavor["select_columns"])

    return f"""SELECT NODE
===========

A select node keeps only selected columns.

Required format:

{{
  "id": "{node_id}",
  "operation": "select",
  "input": "{input_id}",
  "columns": {columns}
}}"""


def _join_node_doc(flavor: dict) -> str:
    node_id, left_id, right_id = _random_ids(3)

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
  "left_on": "{flavor['join_key']}",
  "right_on": "{flavor['join_key']}",
  "join_type": "inner"
}}

Allowed join types:

"inner", "left", "right", "outer"

Incorrect:

{{
  "id": "{node_id}",
  "operation": "join",
  "left": "{left_id}",
  "right": "{right_id}",
  "on": ["{flavor['join_key']}"]
}}

Reason: use "left_input", "right_input", "left_on", and "right_on"."""


def _semi_join_node_doc(flavor: dict) -> str:
    node_id, left_id, right_id = _random_ids(3)

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
  "left_on": "{flavor['join_key']}",
  "right_on": "{flavor['join_key']}"
}}"""


def _anti_join_node_doc(flavor: dict) -> str:
    node_id, left_id, right_id = _random_ids(3)

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
  "left_on": "{flavor['join_key']}",
  "right_on": "{flavor['join_key']}"
}}"""


def _groupby_node_doc(flavor: dict) -> str:
    node_id, input_id = _random_ids(2)

    return f"""GROUPBY NODE
============

A groupby node corresponds to SQL GROUP BY with aggregations.

Required format:

{{
  "id": "{node_id}",
  "operation": "groupby",
  "input": "{input_id}",
  "by": ["{flavor['group_column']}"],
  "aggregations": [
    {{
      "column": "{flavor['agg_column']}",
      "function": "{flavor['agg_function']}",
      "alias": "{flavor['agg_alias']}"
    }}
  ]
}}

Allowed aggregation functions:

"sum", "mean", "count", "min", "max"

Incorrect:

{{
  "column": "{flavor['agg_column']}",
  "agg": "{flavor['agg_function']}",
  "as": "{flavor['agg_alias']}"
}}

Reason: use "function" and "alias", not "agg" and "as"."""


def _sort_node_doc(flavor: dict) -> str:
    node_id, input_id = _random_ids(2)

    return f"""SORT NODE
=========

A sort node corresponds to SQL ORDER BY.

Required format:

{{
  "id": "{node_id}",
  "operation": "sort",
  "input": "{input_id}",
  "by": "{flavor['agg_alias']}",
  "ascending": false
}}"""


def _limit_node_doc(flavor: dict) -> str:
    node_id, input_id = _random_ids(2)

    return f"""LIMIT NODE
==========

A limit node corresponds to SQL LIMIT.

Required format:

{{
  "id": "{node_id}",
  "operation": "limit",
  "input": "{input_id}",
  "n": {flavor['limit_n']}
}}"""


def _scalar_filter_node_doc(flavor: dict) -> str:
    node_id, input_id, scalar_input_id = _random_ids(3)

    return f"""SCALAR_FILTER NODE
==================

A scalar_filter corresponds to a comparison with a scalar subquery.

Example SQL idea:

WHERE {flavor['scalar_column']} {flavor['scalar_operator']} (SELECT AVG({flavor['scalar_column']}) FROM table)

Required format:

{{
  "id": "{node_id}",
  "operation": "scalar_filter",
  "input": "{input_id}",
  "column": "{flavor['scalar_column']}",
  "operator": "{flavor['scalar_operator']}",
  "scalar_input": "{scalar_input_id}",
  "scalar_column": "{flavor['scalar_alias']}"
}}

The scalar_input must be a previous node that returns one row and contains scalar_column."""


# scan always comes first (every other node type builds on the idea of a
# scanned dataframe); the rest have no real reading-order dependency on each
# other, so their order is shuffled on every call.
_SHUFFLABLE_NODE_DOCS = {
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


def build_json_rules() -> str:
    flavor = random.choice(EXAMPLE_FLAVORS)

    shuffled_ops = list(_SHUFFLABLE_NODE_DOCS)
    random.shuffle(shuffled_ops)

    sections = [_scan_node_doc(flavor)] + [
        _SHUFFLABLE_NODE_DOCS[op](flavor) for op in shuffled_ops
    ]

    return JSON_RULES_PREAMBLE.strip() + "\n\n\n" + "\n\n\n".join(sections)


def _having_bias_block(flavor: dict) -> str:
    input_id, group_id, having_id = _random_ids(3)

    return f"""REQUIRED PATTERN: POST-AGGREGATION FILTER (SQL HAVING-STYLE)
============================================================

The query plan MUST include a HAVING-style pattern: first aggregate rows
with a "groupby" node, then apply a "filter" to the aggregated result.

The required structure is:

1. A "groupby" node that groups by one or more columns and produces one
   or more aggregation outputs with aliases.

2. A later "filter" node whose "input" is the id of that groupby node,
   rather than the pre-aggregation input.

3. The filter condition must reference a column available in the
   groupby output, such as:

   * an aggregation alias produced by the groupby, or
   * one of the grouping ("by") columns.

Generic example:

{{
"id": "{group_id}",
"operation": "groupby",
"input": "{input_id}",
"by": ["{flavor['group_column']}"],
"aggregations": [
{{
"column": "{flavor['agg_column']}",
"function": "{flavor['agg_function']}",
"alias": "{flavor['agg_alias']}"
}},
{{
"column": "{flavor['agg_column']}",
"function": "count",
"alias": "{flavor['count_alias']}"
}}
]
}}

{{
"id": "{having_id}",
"operation": "filter",
"input": "{group_id}",
"conditions": [
{{
"column": "{flavor['count_alias']}",
"operator": ">=",
"value": "<threshold>"
}}
]
}}

The essential requirement is that the filter is evaluated AFTER
aggregation and operates on the groupby output.

Incorrect pattern:

* filtering the pre-aggregation input on a raw row-level column;
* applying a condition before the groupby when that condition is meant
  to constrain groups based on an aggregate statistic.

Such a filter is equivalent to SQL WHERE, not SQL HAVING, and does not
satisfy this requirement.

The natural-language question MUST explicitly reflect the
post-aggregation restriction. For example, it may ask for results
"among groups with at least <threshold> observations",
"for categories whose average exceeds <threshold>",
or any equivalent condition defined on aggregated groups."""



SCALAR_FILTER_BIAS_BLOCK = """
REQUIRED PATTERN: SCALAR_FILTER NODE
=====================================

This query plan MUST include at least one "scalar_filter" node (see the
SCALAR_FILTER NODE section below for its exact format). It is not optional
here: the plan is invalid without it.

The scalar_filter node compares a row-level column against a scalar value
computed by a separate branch of the plan (e.g. an overall average, or the
average within some other filtered subset), similar to:

WHERE age > (SELECT AVG(age) FROM table)

Build a small separate branch of the plan (scan -> optional filter ->
groupby) that produces that scalar, then reference it from a scalar_filter
node applied to the main branch.

To aggregate an entire branch down to ONE scalar row (no grouping column,
equivalent to SQL's plain "SELECT AVG(x) FROM table" with no GROUP BY), use
a groupby node with "by": [] (an empty list):

{
  "id": "n3",
  "operation": "groupby",
  "input": "n1",
  "by": [],
  "aggregations": [
    {"column": "edad", "function": "mean", "alias": "avg_age"}
  ]
}

This produces a single-row result containing "avg_age", which a
scalar_filter node can then reference as its scalar_column. Do not try to
compute a whole-table scalar any other way.

The final question must reflect this comparison against the computed
scalar (e.g. "... above the overall average ...").
"""

COLUMN_PROVENANCE_BIAS_BLOCK = """
REQUIRED PATTERN: COLUMN PROVENANCE AFTER JOIN
===============================================

This query plan MUST include at least one real "join" between two tables
that contain one or more overlapping non-key column names.

The purpose is to require reasoning about which table a column originates
from after the join.

After a pandas-style join, overlapping non-key columns may be renamed with
suffixes such as "_x" and "_y".

Example:

Table A:
folio | ent | income

Table B:
folio | ent | safety

After joining on "folio":

folio | ent_x | income | ent_y | safety

Any later filter, groupby, sort, or select MUST reference the actual
post-join column name.

The generated question MUST genuinely require:
- at least one value originating from the left table; and
- at least one value originating from the right table.

Do not use semi_join or anti_join to satisfy this requirement.

Do not create a join if all required information can be obtained from
only one of the participating tables.

Internally verify column provenance after every join:
1. determine which input each required column came from;
2. determine its resulting column name after the join;
3. use that resulting name in all subsequent nodes.
"""

JOIN_FANOUT_BIAS_BLOCK = """
REQUIRED PATTERN: JOIN CARDINALITY / FAN-OUT REASONING
=======================================================

This query MUST require reasoning about row multiplication caused by joins.

Use tables for which the join key is not necessarily unique on both sides,
so that directly joining raw rows could duplicate observations and produce
an incorrect aggregation.

The query plan must avoid incorrect double counting.

When necessary, aggregate a one-to-many branch BEFORE joining it with
another one-to-many branch.

Example conceptual structure:

Table A:
one row per household

Table B:
multiple persons per household

Table C:
multiple expenses per household

Incorrect pattern:

A -> join B -> join C -> sum(expense)

because joining B and C on household may create a Cartesian multiplication
within each household.

Correct pattern when the question requires household-level statistics:

B -> groupby household -> person_count
C -> groupby household -> total_expense
join aggregated B and aggregated C on household

The generated question MUST require information from multiple tables in a
way where naïve raw-row joining could alter counts, sums, or averages.

The plan must preserve the intended unit of observation.

Before returning the plan, internally verify:
- what one row represents in each input table;
- whether the join key is unique in either input;
- whether the join can multiply rows;
- whether an aggregation must occur before the join to avoid duplication.
"""

MULTI_JOIN_BIAS_BLOCK = """
REQUIRED PATTERN: CHAINED JOINS ACROSS 3 TABLES
==================================================

This query plan MUST include at least TWO "join" nodes (see the JOIN NODE
section below), chaining together THREE different scanned tables into one
wide table. It is not optional here: the plan is invalid without it.

Do not substitute semi_join or anti_join for this requirement -- those only
filter rows by key existence and do not count. A real "join" node keeps
columns from both sides.

Build the chain like this:
1. scan table A -> n1
2. scan table B -> n2
3. join n1 and n2 on their shared key -> n3
4. scan table C -> n4
5. join n3 and n4 on their shared key -> n5 (n3's "left_input"/"right_input"
   is the PREVIOUS join's output, not a fresh scan)

Example:

{
  "id": "n3",
  "operation": "join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "folio",
  "right_on": "folio",
  "join_type": "inner"
}

{
  "id": "n5",
  "operation": "join",
  "left_input": "n3",
  "right_input": "n4",
  "left_on": "folio",
  "right_on": "folio",
  "join_type": "inner"
}

Warning about column name collisions: if two joined tables share a
non-key column name (e.g. both have "ent"), pandas will suffix them
("ent_x", "ent_y") in the merged output. After a join, either reference
the suffixed names correctly in later nodes, or add a "select" node right
after the join to keep only the specific columns you actually need
(unambiguous names, no suffixes to worry about).

The final question must genuinely require information from all three
tables (e.g. a condition from table A, a condition from table B, and a
value to aggregate from table C), not just from one of them.
"""


def summarize_dataframe(
    name: str,
    df: pd.DataFrame,
    n_sample_rows: int = 3,
) -> str:
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


# "having" is flavored/randomized like the JSON_RULES node docs (a callable
# taking a flavor dict); the others are still static strings for now.
BIAS_BLOCKS: dict[str, str] = {
    "having": _having_bias_block,
    "scalar_filter": SCALAR_FILTER_BIAS_BLOCK,
    "multi_join": MULTI_JOIN_BIAS_BLOCK,
    "column_provenance": COLUMN_PROVENANCE_BIAS_BLOCK,
    "join_fanout": JOIN_FANOUT_BIAS_BLOCK,
}


def build_query_plan_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    number_of_nested_queries: int = 1,
    n_sample_rows: int = 3,
    bias: str | None = None,
) -> str:
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

    json_rules = build_json_rules()

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

Generate one realistic analytical question over the DataFrames.

Then generate a JSON query plan that answers this question.

The query plan must:
- use only the given DataFrame names;
- use only existing column names;
- use only the JSON field names defined below;
- contain at least {number_of_nested_queries} nested query operation(s);
- use node ids such as "n1", "n2", "n3", etc.;
- define nodes in dependency order;
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

        bias_block = BIAS_BLOCKS[bias]

        if callable(bias_block):
            bias_block = bias_block(random.choice(EXAMPLE_FLAVORS))

        bias_block = bias_block.strip()

        prompt = prompt.replace(
            "Before returning the JSON, internally check that:",
            f"{bias_block}\n\nBefore returning the JSON, internally check that:",
        )

    return prompt