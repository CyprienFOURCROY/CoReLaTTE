# extract_llm_output.py

import json
from typing import Any


def parse_llm_json_response(response) -> dict[str, Any]:
    content = response.choices[0].message.content
    return json.loads(content)


def extract_generated_question(output: dict[str, Any]) -> str:
    if "question" not in output:
        raise KeyError("The LLM output does not contain a 'question' field.")

    return output["question"]


def extract_query_plan(output: dict[str, Any]) -> dict[str, Any]:
    if "query_plan" not in output:
        raise KeyError("The LLM output does not contain a 'query_plan' field.")

    return output["query_plan"]


def extract_question_and_query_plan(output: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    question = extract_generated_question(output)
    query_plan = extract_query_plan(output)

    return question, query_plan