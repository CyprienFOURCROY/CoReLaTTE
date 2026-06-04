from .query_plan_schema import validate_query_plan, QueryPlan
from .json_to_pandas import compile_query_plan


def get_required_tables(plan_json: dict) -> set[str]:
    plan = validate_query_plan(plan_json)

    required_tables = set()

    for node in plan.nodes:
        if node.operation == "scan":
            required_tables.add(node.table)

    return required_tables


def execute_query_plan(plan_json: dict, tables: dict):
    required_tables = get_required_tables(plan_json)

    missing_tables = required_tables - set(tables.keys())

    if missing_tables:
        raise ValueError(
            f"Missing required table(s): {sorted(missing_tables)}. "
            f"Available tables: {sorted(tables.keys())}"
        )

    code = compile_query_plan(plan_json)

    namespace = {}

    exec(code, namespace)

    run_query = namespace["run_query"]

    return run_query(tables)