# query_plan_to_question.py

import json
from typing import Any

from openai import OpenAI

from .query_plan_schema import validate_query_plan


SYSTEM_PROMPT = """
You are a data-question generation assistant.

You receive a validated JSON query plan over pandas DataFrames.

Your task is to write one clear natural-language analytical question that the query plan answers.

Rules:
- Do not mention node ids such as n1, n2, n3.
- Do not mention pandas.
- Do not mention JSON.
- Use the table and column semantics if provided.
- Be concise but specific.
- Return valid JSON only.
"""


def build_question_prompt(
    query_plan: dict[str, Any],
    dataframe_description: str | None = None,
) -> str:
    validated_plan = validate_query_plan(query_plan)

    payload = {
        "query_plan": validated_plan.model_dump(),
        "dataframe_description": dataframe_description or "",
    }

    return f"""
Generate a natural-language question answered by this query plan.

INPUT
=====

{json.dumps(payload, indent=2, ensure_ascii=False)}

OUTPUT FORMAT
=============

Return only:

{{
  "question": "..."
}}
""".strip()


def query_plan_to_question(
    query_plan: dict[str, Any],
    client: OpenAI,
    model: str = "gpt-5",
    dataframe_description: str | None = None,
) -> str:
    prompt = build_question_prompt(
        query_plan=query_plan,
        dataframe_description=dataframe_description,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
    )

    output = json.loads(response.choices[0].message.content)

    return output["question"]