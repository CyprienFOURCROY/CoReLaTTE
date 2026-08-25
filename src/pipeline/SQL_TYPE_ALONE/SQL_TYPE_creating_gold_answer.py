import sys
import re
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.pipeline.code_checking_utils import (
    load_dataset_csv,
    save_dataset_csv,
    load_tables_for_row,
    load_python_script,
    execute_python_script_code,
)


PROCESSED_ROOT = ROOT / "processed"


def get_gold_root(version: int) -> Path:
    return PROCESSED_ROOT / "gold_answer" / "SQL_TYPE_ALONE" / f"v{version}" / "hh09dta_b2"


def extract_query_name(python_script_path: str) -> str:
    """
    Example:
    python_script_for_queries/hh09dta_b2/SQL_TYPE_ALONE/query_000001.py
    -> query_000001
    """
    return Path(python_script_path).stem


def gold_answer_path(query_name: str, version: int) -> Path:
    """
    query_000001 -> processed/gold_answer/SQL_TYPE_ALONE/v{version}/hh09dta_b2/df_query_000001.csv
    """
    return get_gold_root(version) / f"df_{query_name}.csv"


def create_gold_answer_for_row(row: pd.Series, version: int) -> Path:
    query_name = extract_query_name(row["python_script_path"])
    output_path = gold_answer_path(query_name, version=version)

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


def main(version: int = 1) -> None:
    gold_root = get_gold_root(version)

    if not gold_root.exists():
        raise FileNotFoundError(
            f"Gold answer folder not found: {gold_root}"
        )

    df = load_dataset_csv(version=version)

    mask = df["check_if_code_works"].fillna("no").eq("yes")
    indices = df[mask].index.tolist()

    print(f"Rows eligible for gold answer creation: {len(indices)}")

    for i, idx in enumerate(indices, start=1):
        row = df.loc[idx]

        query_name = extract_query_name(row["python_script_path"])
        output_path = gold_answer_path(query_name, version=version)

        print("=" * 80)
        print(f"Row {idx} ({i}/{len(indices)})")
        print(f"Query: {query_name}")
        print(f"Gold answer: {output_path}")

        if output_path.exists():
            print("Already exists. Skipping.")
            continue

        try:
            created_path = create_gold_answer_for_row(row, version=version)
            print(f"Created: {created_path}")

        except Exception as e:
            print("FAILED")
            print(type(e).__name__, ":", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    args = parser.parse_args()

    main(version=args.version)