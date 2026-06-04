# prompt.py

import json
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


JSON_RULES = """
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


SCAN NODE
=========

A scan node loads one dataframe.

Required format:

{
  "id": "n1",
  "operation": "scan",
  "table": "table_name"
}


FILTER NODE
===========

A filter node corresponds to SQL WHERE.

Required format:

{
  "id": "n2",
  "operation": "filter",
  "input": "n1",
  "conditions": [
    {
      "column": "column_name",
      "operator": "=",
      "value": 123
    }
  ]
}

Allowed operators:

"=", "!=", ">", ">=", "<", "<=", "in", "not_in", "contains"

Incorrect:

{
  "id": "n2",
  "operation": "filter",
  "input": "n1",
  "condition": "age > 30"
}

Reason: never use "condition" as a string. Use "conditions" as a list of structured objects.


SELECT NODE
===========

A select node keeps only selected columns.

Required format:

{
  "id": "n3",
  "operation": "select",
  "input": "n2",
  "columns": ["column_1", "column_2"]
}


JOIN NODE
=========

A join node corresponds to SQL JOIN.

It keeps columns from both the left and right inputs.

Required format:

{
  "id": "n4",
  "operation": "join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "key_column_left",
  "right_on": "key_column_right",
  "join_type": "inner"
}

Allowed join types:

"inner", "left", "right", "outer"

Incorrect:

{
  "id": "n4",
  "operation": "join",
  "left": "n1",
  "right": "n2",
  "on": ["folio"]
}

Reason: use "left_input", "right_input", "left_on", and "right_on".


SEMI_JOIN NODE
==============

A semi_join corresponds to SQL WHERE key IN (subquery).

It keeps rows from the left input that have a matching key in the right input.

It only keeps columns from the left input.

Required format:

{
  "id": "n5",
  "operation": "semi_join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "folio",
  "right_on": "folio"
}

Use semi_join for questions like:
- households that appear in another table
- individuals that have at least one matching record
- rows where a key is present in a filtered subquery


ANTI_JOIN NODE
==============

An anti_join corresponds to SQL WHERE key NOT IN (subquery).

It keeps rows from the left input that do not have a matching key in the right input.

It only keeps columns from the left input.

Required format:

{
  "id": "n5",
  "operation": "anti_join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "folio",
  "right_on": "folio"
}


GROUPBY NODE
============

A groupby node corresponds to SQL GROUP BY with aggregations.

Required format:

{
  "id": "n6",
  "operation": "groupby",
  "input": "n5",
  "by": ["group_column"],
  "aggregations": [
    {
      "column": "numeric_column",
      "function": "mean",
      "alias": "avg_value"
    }
  ]
}

Allowed aggregation functions:

"sum", "mean", "count", "min", "max"

Incorrect:

{
  "column": "age",
  "agg": "mean",
  "as": "avg_age"
}

Reason: use "function" and "alias", not "agg" and "as".


SORT NODE
=========

A sort node corresponds to SQL ORDER BY.

Required format:

{
  "id": "n7",
  "operation": "sort",
  "input": "n6",
  "by": "avg_value",
  "ascending": false
}


LIMIT NODE
==========

A limit node corresponds to SQL LIMIT.

Required format:

{
  "id": "n8",
  "operation": "limit",
  "input": "n7",
  "n": 10
}


SCALAR_FILTER NODE
==================

A scalar_filter corresponds to a comparison with a scalar subquery.

Example SQL idea:

WHERE age > (SELECT AVG(age) FROM table)

Required format:

{
  "id": "n5",
  "operation": "scalar_filter",
  "input": "n1",
  "column": "age",
  "operator": ">",
  "scalar_input": "n4",
  "scalar_column": "avg_age"
}

The scalar_input must be a previous node that returns one row and contains scalar_column.
"""


def summarize_dataframe(
    name: str,
    df: pd.DataFrame,
    n_sample_rows: int = 3,
) -> str:
    sample = df.head(n_sample_rows).to_dict(orient="records")

    summary = {
        "name": name,
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


def build_query_plan_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    number_of_nested_queries: int = 1,
    n_sample_rows: int = 3,
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

{JSON_RULES}

OUTPUT TEMPLATE
===============

Your output must follow this general structure:

{json_template}

FINAL INSTRUCTION
=================

Return only the JSON object.
""".strip()

    return prompt