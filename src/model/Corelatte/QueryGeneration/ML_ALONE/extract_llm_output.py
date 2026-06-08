import json
from typing import Any

from src.model.Corelatte.QueryGeneration.ML_ALONE.query_plan_schema import (
    ClusteringPlan,
    MLGenerationOutput,
    RelationshipPlan,
)


def parse_llm_json_response(response: Any) -> dict:
    content = response.choices[0].message.content

    if content is None:
        raise ValueError("LLM response content is empty.")

    try:
        return json.loads(content)

    except json.JSONDecodeError as e:
        raise ValueError(
            "Could not parse LLM response as JSON.\n"
            f"Raw content:\n{content}"
        ) from e


def extract_question_and_ml_plan(
    output: dict,
) -> tuple[str, dict]:
    parsed = MLGenerationOutput.model_validate(output)

    question = parsed.question
    query_plan = parsed.query_plan.model_dump()

    return question, query_plan


def validate_ml_plan(
    query_plan: dict,
) -> RelationshipPlan | ClusteringPlan:
    task_type = query_plan.get("task_type")

    if task_type == "relationship":
        return RelationshipPlan.model_validate(query_plan)

    if task_type == "clustering":
        return ClusteringPlan.model_validate(query_plan)

    raise ValueError(
        f"Unknown task_type: {task_type}. "
        "Expected 'relationship' or 'clustering'."
    )