import pandas as pd


def dataframe_preview_text(
    table_name: str,
    dataframe: pd.DataFrame,
    n_sample_rows: int = 3,
) -> str:
    return (
        f"TABLE NAME: {table_name}\n"
        f"SHAPE: {dataframe.shape[0]} rows x {dataframe.shape[1]} columns\n"
        f"COLUMNS:\n{list(dataframe.columns)}\n\n"
        f"SAMPLE ROWS:\n{dataframe.head(n_sample_rows).to_string(index=False)}"
    )


def build_relationship_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    n_sample_rows: int = 3,
) -> str:
    previews = "\n\n".join(
        dataframe_preview_text(name, df, n_sample_rows)
        for name, df in dataframes.items()
    )

    return f"""
You are generating one analytical machine-learning benchmark task.

Create a relationship/explainability task of the form:
"Can variable X explain variable Y?"
or:
"What is the relationship between X and Y?"

The task must:
- use exactly one table
- choose exactly one numeric x_column
- choose exactly one numeric y_column
- x_column and y_column must be different
- use method = "simple_linear_regression"
- use task_type = "relationship"
- avoid identifier columns
- avoid textual or categorical columns
- avoid columns with too many missing values
- avoid using variables that are obvious duplicates of each other
- return statistics explaining the relationship between X and Y

Expected answer produced later:
- coefficient
- intercept
- r2
- correlation

Return valid JSON only.

Expected JSON structure:

{{
  "question": "Can X explain Y?",
  "query_plan": {{
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
}}

DATAFRAME METADATA:

{dataframe_description}

DATAFRAME PREVIEWS:

{previews}
""".strip()