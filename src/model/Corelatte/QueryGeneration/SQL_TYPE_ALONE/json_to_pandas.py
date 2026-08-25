# json_to_pandas.py

from .query_plan_schema import QueryPlan, validate_query_plan


def compile_condition(df_name: str, condition) -> str:
    col = f'{df_name}[{condition.column!r}]'
    value = repr(condition.value)

    if condition.operator == "=":
        return f"{col} == {value}"
    if condition.operator == "!=":
        return f"{col} != {value}"
    if condition.operator in {">", ">=", "<", "<="}:
        return f"{col} {condition.operator} {value}"
    if condition.operator == "in":
        return f"{col}.isin({value})"
    if condition.operator == "not_in":
        return f"~{col}.isin({value})"
    if condition.operator == "contains":
        return f"{col}.astype(str).str.contains({value}, na=False)"

    raise ValueError(f"Unsupported operator: {condition.operator}")


def compile_query_plan(plan_json: dict) -> str:
    plan: QueryPlan = validate_query_plan(plan_json)

    lines = [
        "import pandas as pd",
        "",
        "def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:",
    ]

    for node in plan.nodes:
        out = node.id

        if node.operation == "scan":
            lines.append(f"    {out} = tables[{node.table!r}].copy()")

        elif node.operation == "filter":
            conditions = [
                compile_condition(node.input, cond)
                for cond in node.conditions
            ]
            mask = " & ".join(f"({c})" for c in conditions)
            lines.append(f"    {out} = {node.input}[{mask}].copy()")

        elif node.operation == "select":
            lines.append(f"    {out} = {node.input}[{node.columns!r}].copy()")

        elif node.operation == "join":
            lines.append(
                f"    {out} = {node.left_input}.merge("
                f"{node.right_input}, "
                f"left_on={node.left_on!r}, "
                f"right_on={node.right_on!r}, "
                f"how={node.join_type!r}"
                f")"
            )

        elif node.operation == "semi_join":
            lines.append(
                f"    {out} = {node.left_input}["
                f"{node.left_input}[{node.left_on!r}].isin("
                f"{node.right_input}[{node.right_on!r}]"
                f")"
                f"].copy()"
            )

        elif node.operation == "anti_join":
            lines.append(
                f"    {out} = {node.left_input}["
                f"~{node.left_input}[{node.left_on!r}].isin("
                f"{node.right_input}[{node.right_on!r}]"
                f")"
                f"].copy()"
            )

        elif node.operation == "groupby":
            if node.by:
                agg_parts = [
                    f"{agg.alias}=({agg.column!r}, {agg.function!r})"
                    for agg in node.aggregations
                ]
                agg_code = ", ".join(agg_parts)
                lines.append(
                    f"    {out} = {node.input}.groupby("
                    f"{node.by!r}, as_index=False"
                    f").agg({agg_code})"
                )
            else:
                # by=[] aggregates the whole input to a single-row DataFrame
                # (pandas raises on groupby([]), so this is compiled directly).
                scalar_parts = [
                    f"{agg.alias!r}: [{node.input}[{agg.column!r}].{agg.function}()]"
                    for agg in node.aggregations
                ]
                scalar_code = ", ".join(scalar_parts)
                lines.append(
                    f"    {out} = pd.DataFrame({{{scalar_code}}})"
                )

        elif node.operation == "sort":
            lines.append(
                f"    {out} = {node.input}.sort_values("
                f"{node.by!r}, ascending={node.ascending!r}"
                f")"
            )

        elif node.operation == "limit":
            lines.append(f"    {out} = {node.input}.head({node.n})")

        elif node.operation == "scalar_filter":
            scalar_value_name = f"{node.scalar_input}_{node.scalar_column}_value"

            lines.append(
                f"    {scalar_value_name} = "
                f"{node.scalar_input}[{node.scalar_column!r}].iloc[0]"
            )

            condition = type(
                "ConditionLike",
                (),
                {
                    "column": node.column,
                    "operator": node.operator,
                    "value": scalar_value_name,
                },
            )

            col = f"{node.input}[{node.column!r}]"
            scalar = scalar_value_name

            if node.operator == "=":
                expr = f"{col} == {scalar}"
            elif node.operator == "!=":
                expr = f"{col} != {scalar}"
            elif node.operator in {">", ">=", "<", "<="}:
                expr = f"{col} {node.operator} {scalar}"
            else:
                raise ValueError(
                    f"Unsupported scalar_filter operator: {node.operator}"
                )

            lines.append(f"    {out} = {node.input}[{expr}].copy()")

        else:
            raise ValueError(f"Unsupported operation: {node.operation}")

    lines.append("")
    lines.append(f"    return {plan.output}")

    return "\n".join(lines)