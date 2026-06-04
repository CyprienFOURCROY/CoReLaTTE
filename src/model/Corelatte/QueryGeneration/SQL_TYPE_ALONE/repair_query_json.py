# repair_json_query.py

import json
from typing import Any

from pydantic import ValidationError
from openai import OpenAI

from .query_plan_schema import validate_query_plan


REPAIR_SYSTEM_PROMPT = """
You are a JSON repair assistant.

Your task is to repair an invalid JSON query plan so that it matches a strict Pydantic schema.

Return valid JSON only.
Do not return markdown.
Do not explain anything.

Forbidden fields:
- condition
- left
- right
- on
- how
- agg
- as
- expressions inside select

Required replacements:
- use conditions, not condition
- use left_input and right_input, not left and right
- use left_on and right_on, not on
- use join_type, not how
- use function and alias, not agg and as
- aggregations must be a list, not a dictionary

Filter nodes must look like:

{
  "id": "n2",
  "operation": "filter",
  "input": "n1",
  "conditions": [
    {
      "column": "ent",
      "operator": "=",
      "value": 20
    }
  ]
}

Join nodes must look like:

{
  "id": "n4",
  "operation": "join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "folio",
  "right_on": "folio",
  "join_type": "inner"
}

Semi-join nodes must look like:

{
  "id": "n5",
  "operation": "semi_join",
  "left_input": "n1",
  "right_input": "n2",
  "left_on": "folio",
  "right_on": "folio"
}

Groupby nodes must look like:

{
  "id": "n6",
  "operation": "groupby",
  "input": "n5",
  "by": ["folio"],
  "aggregations": [
    {
      "column": "edad",
      "function": "mean",
      "alias": "avg_age"
    }
  ]
}

If a select node contains expressions, replace it with:
1. a valid select node without expressions;
2. a compute node if the schema supports compute.

If compute is not supported by the schema, remove unsupported expressions.
"""


def build_repair_prompt(
    invalid_query_plan: dict[str, Any],
    validation_error: str,
) -> str:
    return f"""
The following query plan is invalid.

INVALID QUERY PLAN
==================

{json.dumps(invalid_query_plan, indent=2, ensure_ascii=False)}

VALIDATION ERROR
================

{validation_error}

Repair the query plan so that it matches the schema.

Return only the repaired query_plan JSON object.
Do not wrap it inside "query_plan".
Do not include the question.
""".strip()


def repair_query_plan_once(
    invalid_query_plan: dict[str, Any],
    validation_error: str,
    client: OpenAI,
    model: str = "gpt-5",
) -> dict[str, Any]:
    repair_prompt = build_repair_prompt(
        invalid_query_plan=invalid_query_plan,
        validation_error=validation_error,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": REPAIR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": repair_prompt,
            },
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    return json.loads(content)


def validate_or_repair_query_plan(
    query_plan: dict[str, Any],
    client: OpenAI,
    model: str = "gpt-5",
    max_repair_attempts: int = 2,
):
    current_plan = query_plan

    for attempt in range(max_repair_attempts + 1):
        try:
            validated_plan = validate_query_plan(current_plan)

            return {
                "validated_plan": validated_plan,
                "repaired_query_plan": current_plan,
                "was_repaired": attempt > 0,
                "repair_attempts": attempt,
            }

        except ValidationError as e:
            if attempt == max_repair_attempts:
                raise

            current_plan = repair_query_plan_once(
                invalid_query_plan=current_plan,
                validation_error=str(e),
                client=client,
                model=model,
            )