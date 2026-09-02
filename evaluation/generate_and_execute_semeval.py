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

# Folder label for this script's output -- distinct from the underlying LLM
# model string (DEFAULT_MODEL / --model), which is what actually gets sent
# to the API. Keeps runs from different models from overwriting each other.
MODEL_LABEL = "SEMEVAL8_GPT_5"
DEFAULT_MODEL = "gpt-5"

# Written as the prediction file's entire content when code generation or
# execution fails, instead of leaving no prediction file at all -- a missing
# file makes compare_answers.py silently skip the query (never counted
# either way), which hides real failures from accuracy. compare_answers.py
# recognizes this exact sentinel and auto-classifies it "no" / "code failed"
# without spending a judge call on it.
CODE_FAILED_MARKER = "thecodefailed"


def get_csv_path(version: int) -> Path:
    return PROCESSED_ROOT / f"dataset_query_v{version}.csv"


def get_semeval_script_root(version: int) -> Path:
    return (
        EVAL_ROOT
        / "saved_python_script"
        / "SQL_TYPE_ALONE"
        / f"v{version}"
        / MODEL_LABEL
        / SOURCE_DATASET
    )


def get_semeval_pred_root(version: int) -> Path:
    return (
        EVAL_ROOT
        / "predicted_answers"
        / "SQL_TYPE_ALONE"
        / f"v{version}"
        / MODEL_LABEL
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

    # Weaker models (e.g. gpt-4.1-nano) frequently write
    # def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # as the signature but put "import pandas as pd" *inside* the function
    # body. Annotations are evaluated at def-time, before the body runs, so
    # that always raises NameError: name 'pd' is not defined -- even though
    # the function body itself would work fine once called. Deferring
    # annotation evaluation (PEP 563) sidesteps this generically, without
    # needing to know the model's exact mistake.
    exec("from __future__ import annotations\n" + code, namespace)

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

def main(
    model: str = DEFAULT_MODEL,
    version: int = 1,
    queries: list[str] | None = None,
    force: bool = False,
) -> None:
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

    query_filter = set(queries) if queries else None

    print(f"Version: {version}")
    print(f"Model: {model}  (label: {MODEL_LABEL})")
    print(f"Rows in CSV: {len(df)}")
    if query_filter:
        print(f"Restricted to: {sorted(query_filter)} (always (re)run, ignoring existing predictions)")
    elif force:
        print("Force mode: reprocessing every row, ignoring existing predictions")
    else:
        print("Default mode: only rows without an existing prediction file are processed")
    print(f"Saving scripts to: {script_root}")
    print(f"Saving predictions to: {pred_root}")

    n_skipped = 0

    for idx, row in df.iterrows():
        query_name = query_name_from_script(row["python_script_path"])

        if query_filter is not None:
            if query_name not in query_filter:
                continue
        elif not force and prediction_path(query_name, version=version).exists():
            n_skipped += 1
            continue

        print("=" * 80)
        print(f"ROW {idx}")

        try:
            question = row["natural_question_arisen_from_code"]
            source_dataset = row["source_dataset"]
            table_names = parse_json_list(row["tables"])
            text_files = parse_json_list(row["text"])

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
                model=model,
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

            fail_pred_path = prediction_path(query_name, version=version)
            fail_pred_path.write_text(
                f"{CODE_FAILED_MARKER}\nexplanation_text: {type(e).__name__}: {e}\n",
                encoding="utf-8",
            )
            print(f"Saved failure marker: {fail_pred_path.relative_to(ROOT)}")

    print("=" * 80)
    if n_skipped:
        print(f"Skipped (already had a prediction): {n_skipped}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument(
        "--queries",
        type=str,
        nargs="+",
        default=None,
        help=(
            "Only (re)run these specific query names (e.g. query_000013 query_000014). "
            "Always processed even if a prediction already exists."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess every row, ignoring existing predictions (old default behavior).",
    )
    args = parser.parse_args()

    main(
        model=args.model,
        version=args.version,
        queries=args.queries,
        force=args.force,
    )