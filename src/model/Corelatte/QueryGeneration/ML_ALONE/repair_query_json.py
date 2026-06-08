import json
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from src.model.Corelatte.QueryGeneration.ML_ALONE.query_plan_schema import (
    ClusteringPlan,
    RelationshipPlan,
)


def validate_ml_plan_object(query_plan: dict) -> RelationshipPlan | ClusteringPlan:
    task_type = query_plan.get("task_type")

    if task_type == "relationship":
        return RelationshipPlan.model_validate(query_plan)

    if task_type == "clustering":
        return ClusteringPlan.model_validate(query_plan)

    raise ValueError(
        f"Unknown task_type: {task_type}. "
        "Expected 'relationship' or 'clustering'."
    )


def build_repair_prompt(
    query_plan: dict,
    validation_error: Exception,
) -> str:
    return f"""
The following ML_ALONE query plan is invalid.

Your task is to repair it so that it satisfies the required schema and constraints.

Return valid JSON only.
Return only the repaired query_plan object.
Do not return the outer question object.

Invalid query_plan:

{json.dumps(query_plan, indent=2, ensure_ascii=False)}

Validation error:

{str(validation_error)}

Allowed task types:

1. relationship

Schema:
{{
  "task_type": "relationship",
  "table_name": "...",
  "x_column": "...",
  "y_column": "...",
  "method": "simple_linear_regression",
  "metrics": [
    "coefficient",
    "intercept",
    "r2",
    "correlation"
  ],
  "drop_missing_rows": true,
  "scale_x": false
}}

Rules for relationship:
- x_column and y_column must be different.
- x_column must be numeric.
- y_column must be numeric.
- method must be "simple_linear_regression".
- metrics can only contain: coefficient, intercept, r2, correlation.
- Do not invent table names.
- Do not invent column names.

2. clustering

Schema:
{{
  "task_type": "clustering",
  "table_name": "...",
  "feature_columns": [
    "...",
    "..."
  ],
  "model_type": "kmeans",
  "n_clusters": 3,
  "random_state": 42,
  "metrics": [
    "cluster_summary",
    "silhouette_score",
    "inertia"
  ],
  "drop_missing_rows": true,
  "scale_features": true
}}

Rules for clustering:
- feature_columns must contain exactly two numeric columns.
- feature_columns must not contain duplicates.
- model_type must be "kmeans".
- n_clusters should usually be 3.
- random_state must be 42.
- metrics can only contain: cluster_summary, silhouette_score, inertia.
- Do not invent table names.
- Do not invent column names.

General rules:
- Keep the original task_type if possible.
- Keep the task simple.
- Return valid JSON only.
""".strip()


def validate_or_repair_ml_plan(
    ml_plan: dict,
    client: OpenAI,
    model: str = "gpt-5",
    max_repair_attempts: int = 2,
) -> dict[str, Any]:
    current_plan = ml_plan

    for attempt in range(max_repair_attempts + 1):
        try:
            validated_plan = validate_ml_plan_object(current_plan)

            return {
                "validated_plan": validated_plan,
                "repaired_ml_plan": validated_plan.model_dump(),
                "n_repair_attempts": attempt,
            }

        except (ValidationError, ValueError) as e:
            if attempt >= max_repair_attempts:
                raise

            prompt = build_repair_prompt(
                query_plan=current_plan,
                validation_error=e,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You repair invalid ML_ALONE query plans. "
                            "Return valid JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if content is None:
                raise ValueError("Repair response content is empty.")

            current_plan = json.loads(content)

    raise RuntimeError("Unreachable repair loop state.")