# query_plan_schema.py

from typing import Any, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator


Operator = Literal["=", "!=", ">", ">=", "<", "<=", "in", "not_in", "contains"]
JoinType = Literal["inner", "left", "right", "outer"]


class Condition(BaseModel):
    column: str
    operator: Operator
    value: Any


class Aggregation(BaseModel):
    column: str
    function: Literal["sum", "mean", "count", "min", "max"]
    alias: str


class ScanNode(BaseModel):
    id: str
    operation: Literal["scan"]
    table: str


class FilterNode(BaseModel):
    id: str
    operation: Literal["filter"]
    input: str
    conditions: list[Condition]


class SelectNode(BaseModel):
    id: str
    operation: Literal["select"]
    input: str
    columns: list[str]


class JoinNode(BaseModel):
    id: str
    operation: Literal["join"]
    left_input: str
    right_input: str
    left_on: str
    right_on: str
    join_type: JoinType = "inner"


class GroupByNode(BaseModel):
    id: str
    operation: Literal["groupby"]
    input: str
    by: list[str]
    aggregations: list[Aggregation]


class SortNode(BaseModel):
    id: str
    operation: Literal["sort"]
    input: str
    by: str
    ascending: bool = True


class LimitNode(BaseModel):
    id: str
    operation: Literal["limit"]
    input: str
    n: int = Field(gt=0)


class SemiJoinNode(BaseModel):
    id: str
    operation: Literal["semi_join"]
    left_input: str
    right_input: str
    left_on: str
    right_on: str


class AntiJoinNode(BaseModel):
    id: str
    operation: Literal["anti_join"]
    left_input: str
    right_input: str
    left_on: str
    right_on: str


class ScalarFilterNode(BaseModel):
    id: str
    operation: Literal["scalar_filter"]
    input: str
    column: str
    operator: Operator
    scalar_input: str
    scalar_column: str

QueryNode = Union[
    ScanNode,
    FilterNode,
    SelectNode,
    JoinNode,
    GroupByNode,
    SortNode,
    LimitNode,
    SemiJoinNode,
    AntiJoinNode,
    ScalarFilterNode,
]


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[QueryNode]
    output: str

    @model_validator(mode="after")
    def validate_graph(self):
        ids = [node.id for node in self.nodes]

        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node ids found.")

        id_set = set(ids)

        for node in self.nodes:
            if hasattr(node, "input") and node.input not in id_set:
                raise ValueError(f"Unknown input node: {node.input}")

            if hasattr(node, "left_input") and node.left_input not in id_set:
                raise ValueError(f"Unknown left_input node: {node.left_input}")

            if hasattr(node, "right_input") and node.right_input not in id_set:
                raise ValueError(f"Unknown right_input node: {node.right_input}")

            if hasattr(node, "scalar_input") and node.scalar_input not in id_set:
                raise ValueError(f"Unknown scalar_input node: {node.scalar_input}")

        if self.output not in id_set:
            raise ValueError(f"Unknown output node: {self.output}")

        return self


def validate_query_plan(data: dict) -> QueryPlan:
    return QueryPlan.model_validate(data)