import sys
import json
import argparse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


# ==================================================
# PATHS
# ==================================================

ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_ROOT = ROOT / "raw_data"
PROCESSED_ROOT = ROOT / "processed"
EVAL_ROOT = ROOT / "evaluation"

SOURCE_DATASET = "hh09dta_b2"


def get_csv_path(version: int) -> Path:
    return PROCESSED_ROOT / f"dataset_query_v{version}.csv"


def get_semeval_script_root(version: int) -> Path:
    return (
        EVAL_ROOT
        / "saved_python_script"
        / "SQL_TYPE_ALONE"
        / f"v{version}"
        / "SEMEVAL8_ITUNLP"
        / SOURCE_DATASET
    )


def get_semeval_pred_root(version: int) -> Path:
    return (
        EVAL_ROOT
        / "predicted_answers"
        / "SQL_TYPE_ALONE"
        / f"v{version}"
        / "SEMEVAL8_ITUNLP"
        / SOURCE_DATASET
    )


# ==================================================
# IMPORT SEMEVAL AGENT
# ==================================================

SEMEVAL_ROOT = (
    ROOT
    / "src"
    / "model"
    / "semeval8-itunlp"
)

sys.path.insert(0, str(SEMEVAL_ROOT))

from utilities.agents_modified_for_CoReLaTTe import get_pandas_code


# ==================================================
# HELPERS
# ==================================================

def parse_json_list(value):
    if isinstance(value, list):
        return value

    return json.loads(value)


def query_name_from_script(script_path: str) -> str:
    return Path(script_path).stem


def semeval_script_path(query_name: str, version: int) -> Path:
    return get_semeval_script_root(version) / f"{query_name}.py"


def prediction_path(query_name: str, version: int) -> Path:
    return get_semeval_pred_root(version) / f"df_{query_name}.csv"


def load_tables(
    source_dataset: str,
    table_names: list[str],
) -> dict[str, pd.DataFrame]:
    dataset_dir = RAW_DATA_ROOT / source_dataset

    tables = {}

    for table in table_names:
        path = dataset_dir / f"{table}.dta"

        if not path.exists():
            raise FileNotFoundError(f"Missing table file: {path}")

        tables[table] = pd.read_stata(path)

    return tables


def load_metadata_text(
    source_dataset: str,
    text_files: list[str],
) -> str:
    json_dir = RAW_DATA_ROOT / source_dataset / "codebook_json"

    parts = []

    for file in text_files:
        path = json_dir / file

        if not path.exists():
            raise FileNotFoundError(f"Missing metadata text file: {path}")

        parts.append(
            f"TEXT FILE: {file}\n"
            f"{path.read_text(encoding='utf-8')}"
        )

    return "\n\n".join(parts)


def build_schema_text(
    source_dataset: str,
    table_names: list[str],
    text_files: list[str],
) -> str:
    dataset_dir = RAW_DATA_ROOT / source_dataset

    sections = []

    for table in table_names:
        path = dataset_dir / f"{table}.dta"

        if not path.exists():
            raise FileNotFoundError(f"Missing table file: {path}")

        df = pd.read_stata(path)

        sections.append(
            f"""
TABLE: {table}

N_ROWS: {len(df)}

COLUMNS:
{list(df.columns)}

DTYPES:
{df.dtypes.astype(str).to_dict()}

SAMPLE:
{df.head(3).to_dict(orient="records")}
""".strip()
        )

    metadata = load_metadata_text(
        source_dataset=source_dataset,
        text_files=text_files,
    )

    return (
        "\n\n".join(sections)
        + "\n\nCOLUMN METADATA\n===============\n\n"
        + metadata
    )


def execute_generated_code(
    code: str,
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    namespace = {}

    exec(code, namespace)

    if "run_query" not in namespace:
        raise RuntimeError("Generated code does not define run_query(tables).")

    result = namespace["run_query"](tables)

    if not isinstance(result, pd.DataFrame):
        raise RuntimeError(
            f"run_query(tables) must return a pandas DataFrame, got {type(result)}"
        )

    return result


# ==================================================
# MAIN
# ==================================================

def main(model: str = "gpt-5", version: int = 1) -> None:
    load_dotenv()

    csv_path = get_csv_path(version)
    script_root = get_semeval_script_root(version)
    pred_root = get_semeval_pred_root(version)

    script_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    pred_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    df = pd.read_csv(csv_path)

    print(f"Version: {version}")
    print(f"Rows to process: {len(df)}")
    print(f"Saving scripts to: {script_root}")
    print(f"Saving predictions to: {pred_root}")

    for idx, row in df.iterrows():
        print("=" * 80)
        print(f"ROW {idx}")

        try:
            question = row["natural_question_arisen_from_code"]
            source_dataset = row["source_dataset"]
            table_names = parse_json_list(row["tables"])
            text_files = parse_json_list(row["text"])

            query_name = query_name_from_script(
                row["python_script_path"]
            )

            script_path = semeval_script_path(query_name, version=version)
            pred_path = prediction_path(query_name, version=version)

            print(f"Query: {query_name}")
            print(f"Tables: {table_names}")

            schema = build_schema_text(
                source_dataset=source_dataset,
                table_names=table_names,
                text_files=text_files,
            )

            code = get_pandas_code(
                dataset_name=source_dataset,
                question=question,
                schema=schema,
                temperature=0,
            )

            script_path.write_text(
                code,
                encoding="utf-8",
            )

            tables = load_tables(
                source_dataset=source_dataset,
                table_names=table_names,
            )

            pred_df = execute_generated_code(
                code=code,
                tables=tables,
            )

            pred_df.to_csv(
                pred_path,
                index=False,
            )

            print("Saved script:", script_path.relative_to(ROOT))
            print("Saved prediction:", pred_path.relative_to(ROOT))
            print("Status: success")

        except Exception as e:
            print("Status: failed")
            print(type(e).__name__, ":", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    parser.add_argument("--model", type=str, default="gpt-5")
    args = parser.parse_args()

    main(model=args.model, version=args.version)