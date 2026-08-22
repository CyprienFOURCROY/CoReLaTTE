import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_ROOT = ROOT / "raw_data"
PROCESSED_ROOT = ROOT / "processed"
CSV_PATH = PROCESSED_ROOT / "dataset_query.csv"

CSV_COLUMNS = [
    "question_from_llm",
    "natural_question_arisen_from_code",
    "python_script_path",
    "tables",
    "text",
    "source_dataset",
    "check_if_code_works",
]


def load_dataset_csv() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    missing = [col for col in CSV_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing CSV columns: {missing}")

    return df


def save_dataset_csv(df: pd.DataFrame) -> None:
    df = df[CSV_COLUMNS]
    df.to_csv(CSV_PATH, index=False)


def parse_json_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    return json.loads(value)


def get_dataset_dir(source_dataset: str) -> Path:
    return RAW_DATA_ROOT / source_dataset


def load_tables_for_row(row: pd.Series) -> dict[str, pd.DataFrame]:
    source_dataset = row["source_dataset"]
    table_names = parse_json_list(row["tables"])

    dataset_dir = get_dataset_dir(source_dataset)

    tables = {}

    for table_name in table_names:
        path = dataset_dir / f"{table_name}.dta"

        if not path.exists():
            raise FileNotFoundError(f"Missing table file: {path}")

        tables[table_name] = pd.read_stata(path)

    return tables


def load_python_script(row: pd.Series) -> str:
    script_path = PROCESSED_ROOT / row["python_script_path"]

    if not script_path.exists():
        raise FileNotFoundError(f"Missing Python script: {script_path}")

    return script_path.read_text(encoding="utf-8")


def execute_python_script_code(
    code: str,
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    namespace = {}

    exec(code, namespace)

    if "run_query" not in namespace:
        raise NameError("Generated script does not define run_query(tables).")

    result = namespace["run_query"](tables)

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            f"run_query(tables) must return a pandas DataFrame, got {type(result)}"
        )

    return result


def check_generated_code_for_row(row: pd.Series) -> str:
    try:
        code = load_python_script(row)
        tables = load_tables_for_row(row)

        result = execute_python_script_code(
            code=code,
            tables=tables,
        )

        if not isinstance(result, pd.DataFrame):
            return "no"

        return "yes"

    except Exception as e:
        print("\n" + "=" * 80)
        print("FAILED SCRIPT")
        print(row["python_script_path"])
        print("-" * 80)
        print(type(e).__name__)
        print(str(e))
        print("=" * 80 + "\n")

        return "no"