import json
from pathlib import Path

import pandas as pd

from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_ROOT = ROOT / "raw_data"

QUERY_PLAN = {
    "task_type": "relationship",
    "table_name": "ii_vlh",
    "x_column": "vlh09a",
    "y_column": "vlh18a",
    "method": "simple_linear_regression",
    "metrics": [
        "coefficient",
        "intercept",
        "r2",
        "correlation"
    ],
    "drop_missing_rows": true,
    "scale_x": false
}


def load_dataframe() -> pd.DataFrame:
    source_dataset = QUERY_PLAN.get("source_dataset", "hh09dta_b2")
    table_name = QUERY_PLAN["table_name"]

    path = RAW_DATA_ROOT / source_dataset / f"{table_name}.dta"

    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")

    return pd.read_stata(path)


def validate_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    missing_columns = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    non_numeric_columns = [
        column
        for column in columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]

    if non_numeric_columns:
        raise ValueError(
            "Expected numeric columns only. "
            f"Non-numeric columns: {non_numeric_columns}"
        )


def run_relationship_query(df: pd.DataFrame) -> pd.DataFrame:
    x_column = QUERY_PLAN["x_column"]
    y_column = QUERY_PLAN["y_column"]

    validate_numeric_columns(
        df=df,
        columns=[x_column, y_column],
    )

    working_df = df[[x_column, y_column]].copy()

    if QUERY_PLAN["drop_missing_rows"]:
        working_df = working_df.dropna(subset=[x_column, y_column])

    if len(working_df) < 3:
        raise ValueError(
            "Not enough rows after preprocessing for linear regression."
        )

    X = working_df[[x_column]]
    y = working_df[y_column]

    if QUERY_PLAN.get("scale_x", False):
        scaler = StandardScaler()
        X_model = scaler.fit_transform(X)
    else:
        X_model = X

    model = LinearRegression()
    model.fit(X_model, y)

    y_pred = model.predict(X_model)

    coefficient = float(model.coef_[0])
    intercept = float(model.intercept_)
    r2 = float(r2_score(y, y_pred))
    correlation = float(working_df[x_column].corr(working_df[y_column]))

    row = {
        "task_type": "relationship",
        "table_name": QUERY_PLAN["table_name"],
        "x_column": x_column,
        "y_column": y_column,
    }

    if "coefficient" in QUERY_PLAN["metrics"]:
        row["coefficient"] = coefficient

    if "intercept" in QUERY_PLAN["metrics"]:
        row["intercept"] = intercept

    if "r2" in QUERY_PLAN["metrics"]:
        row["r2"] = r2

    if "correlation" in QUERY_PLAN["metrics"]:
        row["correlation"] = correlation

    return pd.DataFrame([row])


def run_clustering_query(df: pd.DataFrame) -> pd.DataFrame:
    feature_columns = QUERY_PLAN["feature_columns"]

    validate_numeric_columns(
        df=df,
        columns=feature_columns,
    )

    working_df = df[feature_columns].copy()

    if QUERY_PLAN["drop_missing_rows"]:
        working_df = working_df.dropna(subset=feature_columns)

    if len(working_df) < QUERY_PLAN["n_clusters"]:
        raise ValueError(
            "Not enough rows after preprocessing for clustering."
        )

    X = working_df[feature_columns]

    if QUERY_PLAN["scale_features"]:
        scaler = StandardScaler()
        X_model = scaler.fit_transform(X)
    else:
        X_model = X.to_numpy()

    model = KMeans(
        n_clusters=QUERY_PLAN["n_clusters"],
        random_state=QUERY_PLAN["random_state"],
        n_init=10,
    )

    labels = model.fit_predict(X_model)

    working_df = working_df.copy()
    working_df["cluster"] = labels

    cluster_summary = (
        working_df
        .groupby("cluster", as_index=False)
        .agg(
            count=("cluster", "size"),
            x_mean=(feature_columns[0], "mean"),
            y_mean=(feature_columns[1], "mean"),
        )
        .sort_values("cluster")
        .reset_index(drop=True)
    )

    n_unique_clusters = len(set(labels))

    if n_unique_clusters < 2 or n_unique_clusters >= len(labels):
        score = None
    else:
        score = float(silhouette_score(X_model, labels))

    inertia = float(model.inertia_)

    if "silhouette_score" in QUERY_PLAN["metrics"]:
        cluster_summary["silhouette_score"] = score

    if "inertia" in QUERY_PLAN["metrics"]:
        cluster_summary["inertia"] = inertia

    cluster_summary.insert(0, "task_type", "clustering")
    cluster_summary.insert(1, "table_name", QUERY_PLAN["table_name"])
    cluster_summary.insert(2, "x_column", feature_columns[0])
    cluster_summary.insert(3, "y_column", feature_columns[1])

    return cluster_summary


def run_query() -> pd.DataFrame:
    df = load_dataframe()

    if QUERY_PLAN["task_type"] == "relationship":
        return run_relationship_query(df)

    if QUERY_PLAN["task_type"] == "clustering":
        return run_clustering_query(df)

    raise ValueError(f"Unknown task_type: {QUERY_PLAN['task_type']}")


if __name__ == "__main__":
    result = run_query()
    print(result.to_string(index=False))