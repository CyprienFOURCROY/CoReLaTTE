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


def build_cluster_prompt(
    dataframes: dict[str, pd.DataFrame],
    dataframe_description: str,
    n_sample_rows: int = 3,
) -> str:
    previews = "\n\n".join(
        dataframe_preview_text(name, df, n_sample_rows)
        for name, df in dataframes.items()
    )

    return f"""
You are generating one clustering benchmark task.

Create a simple KMeans clustering task.

The task must:
- use exactly one table
- use task_type = "clustering"
- use model_type = "kmeans"
- choose exactly two numeric columns as feature_columns
- use n_clusters = 3
- use random_state = 42
- avoid identifier columns
- avoid categorical or textual columns
- avoid columns with too many missing values
- choose meaningful numeric variables
- return a cluster summary

Expected answer produced later:
- one row per cluster
- cluster id
- count of observations in the cluster
- mean of the first selected variable inside the cluster
- mean of the second selected variable inside the cluster
- silhouette_score
- inertia

Return valid JSON only.

Expected JSON structure:

{{
  "question": "Cluster the observations using variables X and Y, and summarize the resulting groups.",
  "query_plan": {{
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
}}

DATAFRAME METADATA:

{dataframe_description}

DATAFRAME PREVIEWS:

{previews}
""".strip()