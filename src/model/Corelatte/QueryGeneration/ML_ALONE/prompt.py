import random

import pandas as pd

from src.model.Corelatte.QueryGeneration.ML_ALONE.prompt_cluster import (
    build_cluster_prompt,
)
from src.model.Corelatte.QueryGeneration.ML_ALONE.prompt_relationship import (
    build_relationship_prompt,
)


PROMPT_BUILDERS = {
    "relationship": build_relationship_prompt,
    "clustering": build_cluster_prompt,
}


def build_ml_plan_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    n_sample_rows: int = 3,
    prompt_type: str | None = None,
) -> tuple[str, str]:
    if prompt_type is None:
        prompt_type = random.choice(list(PROMPT_BUILDERS.keys()))

    if prompt_type not in PROMPT_BUILDERS:
        raise ValueError(
            f"Unknown prompt_type: {prompt_type}. "
            f"Expected one of: {list(PROMPT_BUILDERS.keys())}"
        )

    prompt = PROMPT_BUILDERS[prompt_type](
        dataframes=dataframes,
        dataframe_description=dataframe_description,
        n_sample_rows=n_sample_rows,
    )

    return prompt, prompt_type