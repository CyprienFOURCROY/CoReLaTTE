from typing import Literal

from pydantic import BaseModel, Field, model_validator


MLTaskType = Literal[
    "relationship",
    "clustering",
]

RelationshipMethod = Literal[
    "simple_linear_regression",
]

ClusteringModelType = Literal[
    "kmeans",
]

RelationshipMetric = Literal[
    "coefficient",
    "intercept",
    "r2",
    "correlation",
]

ClusteringMetric = Literal[
    "cluster_summary",
    "silhouette_score",
    "inertia",
]


class RelationshipPlan(BaseModel):
    task_type: Literal["relationship"] = "relationship"
    table_name: str

    x_column: str
    y_column: str

    method: RelationshipMethod = "simple_linear_regression"
    metrics: list[RelationshipMetric] = Field(
        default_factory=lambda: [
            "coefficient",
            "intercept",
            "r2",
            "correlation",
        ]
    )

    drop_missing_rows: bool = True
    scale_x: bool = False

    @model_validator(mode="after")
    def validate_relationship_plan(self):
        if self.x_column == self.y_column:
            raise ValueError(
                "x_column and y_column must be different."
            )

        if len(self.metrics) == 0:
            raise ValueError("metrics must contain at least one metric.")

        if len(set(self.metrics)) != len(self.metrics):
            raise ValueError("metrics must not contain duplicates.")

        return self


class ClusteringPlan(BaseModel):
    task_type: Literal["clustering"] = "clustering"
    table_name: str

    feature_columns: list[str]
    model_type: ClusteringModelType = "kmeans"
    n_clusters: int = Field(default=3, ge=2, le=10)
    random_state: int = 42

    metrics: list[ClusteringMetric] = Field(
        default_factory=lambda: [
            "cluster_summary",
            "silhouette_score",
            "inertia",
        ]
    )

    drop_missing_rows: bool = True
    scale_features: bool = True

    @model_validator(mode="after")
    def validate_clustering_plan(self):
        if len(self.feature_columns) != 2:
            raise ValueError(
                "Clustering must use exactly two numeric feature columns."
            )

        if len(set(self.feature_columns)) != len(self.feature_columns):
            raise ValueError("feature_columns must not contain duplicates.")

        if len(self.metrics) == 0:
            raise ValueError("metrics must contain at least one metric.")

        if len(set(self.metrics)) != len(self.metrics):
            raise ValueError("metrics must not contain duplicates.")

        return self


class MLGenerationOutput(BaseModel):
    question: str
    query_plan: RelationshipPlan | ClusteringPlan