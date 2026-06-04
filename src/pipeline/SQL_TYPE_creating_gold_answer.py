import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.pipeline.code_checking_utils import (
    load_dataset_csv,
    save_dataset_csv,
    load_tables_for_row,
    load_python_script,
    execute_python_script_code,
)


DATA_ROOT = ROOT / "data"
GOLD_ROOT = DATA_ROOT / "gold_answer" / "SQL_TYPE_ALONE" / "hh09dta_b2"


def extract_query_name(python_script_path: str) -> str:
    """
    Example:
    python_script_for_queries/hh09dta_b2/SQL_TYPE_ALONE/query_000001.py
    -> query_000001
    """
    return Path(python_script_path).stem


def gold_answer_path(query_name: str) -> Path:
    """
    query_000001 -> data/gold_answer/hh09dta_b2/df_query_000001.csv
    """
    return GOLD_ROOT / f"df_{query_name}.csv"


def create_gold_answer_for_row(row: pd.Series) -> Path:
    query_name = extract_query_name(row["python_script_path"])
    output_path = gold_answer_path(query_name)

    if output_path.exists():
        return output_path

    code = load_python_script(row)
    tables = load_tables_for_row(row)

    result = execute_python_script_code(
        code=code,
        tables=tables,
    )

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            f"Gold answer must be a DataFrame, got {type(result)}"
        )

    result.to_csv(output_path, index=False)

    return output_path


def main() -> None:
    if not GOLD_ROOT.exists():
        raise FileNotFoundError(
            f"Gold answer folder not found: {GOLD_ROOT}"
        )

    df = load_dataset_csv()

    mask = df["check_if_code_works"].fillna("no").eq("yes")
    indices = df[mask].index.tolist()

    print(f"Rows eligible for gold answer creation: {len(indices)}")

    for i, idx in enumerate(indices, start=1):
        row = df.loc[idx]

        query_name = extract_query_name(row["python_script_path"])
        output_path = gold_answer_path(query_name)

        print("=" * 80)
        print(f"Row {idx} ({i}/{len(indices)})")
        print(f"Query: {query_name}")
        print(f"Gold answer: {output_path}")

        if output_path.exists():
            print("Already exists. Skipping.")
            continue

        try:
            created_path = create_gold_answer_for_row(row)
            print(f"Created: {created_path}")

        except Exception as e:
            print("FAILED")
            print(type(e).__name__, ":", e)


if __name__ == "__main__":
    main()