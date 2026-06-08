import json

from openai import OpenAI

from src.model.Corelatte.QueryGeneration.ML_ALONE.query_plan_schema import (
    ClusteringPlan,
    RelationshipPlan,
)


def validate_plan(
    ml_plan: dict | RelationshipPlan | ClusteringPlan,
) -> RelationshipPlan | ClusteringPlan:
    if isinstance(ml_plan, (RelationshipPlan, ClusteringPlan)):
        return ml_plan

    task_type = ml_plan.get("task_type")

    if task_type == "relationship":
        return RelationshipPlan.model_validate(ml_plan)

    if task_type == "clustering":
        return ClusteringPlan.model_validate(ml_plan)

    raise ValueError(f"Unknown task_type: {task_type}")


def build_ml_plan_to_question_prompt(
    ml_plan: dict,
    dataframe_description: str,
) -> str:
    return f"""
You are given a validated ML_ALONE analytical query plan.

Rewrite it as a clear natural-language benchmark question.

The question must:
- be answerable by executing the plan
- mention the table
- for relationship tasks, mention the x variable and y variable
- for relationship tasks, ask whether X can explain Y or what relationship exists between X and Y
- for clustering tasks, mention the two variables used for clustering
- for clustering tasks, ask to group observations and summarize the clusters
- not mention JSON, pandas, Python code, or implementation details
- not invent extra requirements

Validated ML_ALONE query plan:

{json.dumps(ml_plan, indent=2, ensure_ascii=False)}

Available dataframe metadata:

{dataframe_description}

Return only the natural-language question.
""".strip()


def ml_plan_to_question(
    ml_plan: dict | RelationshipPlan | ClusteringPlan,
    client: OpenAI,
    model: str = "gpt-5",
    dataframe_description: str = "",
) -> str:
    plan = validate_plan(ml_plan)
    plan_dict = plan.model_dump()

    prompt = build_ml_plan_to_question_prompt(
        ml_plan=plan_dict,
        dataframe_description=dataframe_description,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert validated ML_ALONE plans into natural "
                    "benchmark questions. Return plain text only."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("Question rewriting response is empty.")

    return content.strip()