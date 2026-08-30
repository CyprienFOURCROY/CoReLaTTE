import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import os
import re
import json
import random
import argparse
import logging
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from src.model.Corelatte.QueryGeneration.SQL_TYPE_ALONE import (
    build_query_plan_prompt,
    parse_llm_json_response,
    extract_question_and_query_plan,
    validate_or_repair_query_plan,
    compile_query_plan,
    query_plan_to_question,
    
)


# =====================
# CONFIG
# =====================

SOURCE_DATASET = "hh09dta_b2"

RAW_DATA_ROOT = ROOT / "raw_data"
PROCESSED_ROOT = ROOT / "processed"

DATA_DIR = RAW_DATA_ROOT / SOURCE_DATASET
JSON_DIR = DATA_DIR / "codebook_json"

CSV_COLUMNS = [
    "question_from_llm",
    "natural_question_arisen_from_code",
    "python_script_path",
    "tables",
    "text",
    "source_dataset",
    "check_if_code_works",
    "bias",
    "number_of_nested_queries",
]

# v1 has no structural bias. v2 rotates deterministically through forcing a
# HAVING-style post-aggregation filter, a scalar_filter node, a chained
# multi-join across 3 tables, a join with overlapping (non-key) column names
# that requires tracking post-join column provenance, and a join where a
# fan-out (row multiplication) has to be avoided/handled correctly.
BIAS_ROTATION = [
    "having",
    "scalar_filter",
    "multi_join",
    "column_provenance",
    "join_fanout",
]


def get_csv_path(version: int) -> Path:
    return PROCESSED_ROOT / f"dataset_query_v{version}.csv"


def get_generated_script_dir(version: int) -> Path:
    return (
        PROCESSED_ROOT
        / "python_script_for_queries"
        / "SQL_TYPE_ALONE"
        / f"v{version}"
        / SOURCE_DATASET
    )


def get_bias_for_query_index(version: int, query_index: int) -> str | None:
    if version == 1:
        return None

    # Rotates on the persistent script index (not the in-run offset), so the
    # bias rotation holds across separate CLI invocations too -- the normal
    # usage pattern is one query per run (n_queries=1).
    return BIAS_ROTATION[(query_index - 1) % len(BIAS_ROTATION)]


LOGS_ROOT = PROCESSED_ROOT / "logs" / "SQL_TYPE_ALONE"


def get_log_dir(version: int) -> Path:
    return LOGS_ROOT / f"v{version}"


def setup_logging(version: int) -> logging.Logger:
    log_dir = get_log_dir(version)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"generation_{timestamp}.log"

    logger = logging.getLogger(f"sql_type_generation_v{version}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logging to: {log_path}")

    return logger


NATURAL_SAMPLING_DICT = {
    1: "ii_portad",
    2: {"non_detailed": "ii_su"},
    3: "ii_inr",
    4: {"non_detailed": "ii_nna"},
    5: "ii_ah",
    6: "ii_crh",
    7: "ii_in",
    8: "ii_se",
    9: "ii_vlh",
}


# =====================
# ENVIRONMENT CHECKS
# =====================

def check_environment(version: int) -> None:
    csv_path = get_csv_path(version)
    generated_script_dir = get_generated_script_dir(version)

    if not RAW_DATA_ROOT.exists():
        raise FileNotFoundError(f"Raw data root not found: {RAW_DATA_ROOT}")

    if not PROCESSED_ROOT.exists():
        raise FileNotFoundError(f"Processed data root not found: {PROCESSED_ROOT}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATA_DIR}")

    if not JSON_DIR.exists():
        raise FileNotFoundError(f"Metadata folder not found: {JSON_DIR}")

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}\n"
            f"Expected header:\n{','.join(CSV_COLUMNS)}"
        )

    existing_columns = list(pd.read_csv(csv_path, nrows=0).columns)

    if existing_columns != CSV_COLUMNS:
        raise ValueError(
            "CSV columns are incorrect.\n"
            f"Expected: {CSV_COLUMNS}\n"
            f"Found:    {existing_columns}"
        )

    if not generated_script_dir.exists():
        raise FileNotFoundError(
            f"Generated script folder not found: {generated_script_dir}"
        )


# =====================
# TABLE SAMPLING
# =====================

def make_table_subsets(
    n_queries: int,
    n_extra_tables: int,
) -> list[list[str]]:
    subsets = []
    available_numbers = list(range(2, 10))

    for _ in range(n_queries):
        subset_numbers = [1]

        sampled = random.sample(
            available_numbers,
            k=n_extra_tables,
        )

        subset_numbers.extend(sampled)

        table_names = []

        for table_number in subset_numbers:
            value = NATURAL_SAMPLING_DICT[table_number]

            if isinstance(value, dict):
                table_names.append(value["non_detailed"])
            else:
                table_names.append(value)

        subsets.append(table_names)

    return subsets


# =====================
# DATA / METADATA
# =====================

def load_tables(table_names: list[str]) -> dict[str, pd.DataFrame]:
    tables = {}

    for table_name in table_names:
        path = DATA_DIR / f"{table_name}.dta"

        if not path.exists():
            raise FileNotFoundError(f"Missing Stata file: {path}")

        tables[table_name] = pd.read_stata(path)

    return tables


def metadata_text_name(table_name: str) -> str:
    return f"{table_name}_enriched.txt"


def load_metadata_text(table_name: str) -> str:
    path = JSON_DIR / metadata_text_name(table_name)

    if not path.exists():
        raise FileNotFoundError(f"Missing metadata text file: {path}")

    return path.read_text(encoding="utf-8")


def build_description(table_names: list[str]) -> str:
    parts = []

    for table_name in table_names:
        text_name = metadata_text_name(table_name)
        text = load_metadata_text(table_name)

        parts.append(
            f"TABLE: {table_name}\n"
            f"TEXT FILE: {text_name}\n"
            f"{text}"
        )

    return "\n\n".join(parts)


# =====================
# SCRIPT NAMING / SAVING
# =====================

def get_next_query_index(version: int) -> int:
    pattern = re.compile(r"query_(\d{6})\.py$")

    max_index = 0

    for path in get_generated_script_dir(version).glob("query_*.py"):
        match = pattern.match(path.name)

        if match:
            index = int(match.group(1))
            max_index = max(max_index, index)

    return max_index + 1


def script_path_from_index(index: int, version: int) -> Path:
    return get_generated_script_dir(version) / f"query_{index:06d}.py"


def save_python_code(code: str, query_index: int, version: int) -> Path:
    script_path = script_path_from_index(query_index, version=version)

    if script_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing script: {script_path}"
        )

    script_path.write_text(code, encoding="utf-8")

    return script_path


# =====================
# CSV APPEND
# =====================

def append_row(row: dict, version: int) -> None:
    csv_path = get_csv_path(version)

    df = pd.read_csv(csv_path)

    row_df = pd.DataFrame([row], columns=CSV_COLUMNS)

    df = pd.concat(
        [df, row_df],
        ignore_index=True,
    )

    df.to_csv(csv_path, index=False)


# =====================
# ONE QUERY GENERATION
# =====================

def generate_one_query(
    table_names: list[str],
    client: OpenAI,
    query_index: int,
    version: int,
    model: str = "gpt-5",
    number_of_nested_queries: int = 2,
    bias: str | None = None,
) -> dict:
    tables = load_tables(table_names)
    dataframe_description = build_description(table_names)

    prompt = build_query_plan_prompt(
        dataframes=tables,
        dataframe_description=dataframe_description,
        number_of_nested_queries=number_of_nested_queries,
        n_sample_rows=3,
        bias=bias,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a query-planning assistant. "
                    "Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
    )

    output = parse_llm_json_response(response)

    question_from_llm, query_plan = extract_question_and_query_plan(output)

    repair_result = validate_or_repair_query_plan(
        query_plan=query_plan,
        client=client,
        model=model,
        max_repair_attempts=2,
    )

    validated_plan = repair_result["validated_plan"]
    repaired_query_plan = repair_result["repaired_query_plan"]

    python_code = compile_query_plan(repaired_query_plan)

    script_path = save_python_code(
        code=python_code,
        query_index=query_index,
        version=version,
    )

    relative_script_path = script_path.relative_to(PROCESSED_ROOT)

    natural_question_arisen_from_code = query_plan_to_question(
        query_plan=validated_plan.model_dump(),
        client=client,
        model=model,
        dataframe_description=dataframe_description,
    )

    row = {
        "question_from_llm": question_from_llm,
        "natural_question_arisen_from_code": natural_question_arisen_from_code,
        "python_script_path": str(relative_script_path),
        "tables": json.dumps(table_names, ensure_ascii=False),
        "text": json.dumps(
            [metadata_text_name(t) for t in table_names],
            ensure_ascii=False,
        ),
        "source_dataset": SOURCE_DATASET,
        "check_if_code_works": "no",
        "bias": bias or "",
        "number_of_nested_queries": number_of_nested_queries,
    }

    append_row(row, version=version)

    return row


# =====================
# MAIN
# =====================

def main(
    n_queries: int = 10,
    n_extra_tables: int = 2,
    model: str = "gpt-5",
    version: int = 1,
) -> None:
    check_environment(version=version)

    load_dotenv()

    api_key = os.getenv("API_KEY")

    if api_key is None:
        raise ValueError("API_KEY not found in .env")

    client = OpenAI(api_key=api_key)

    logger = setup_logging(version=version)

    subsets = make_table_subsets(
        n_queries=n_queries,
        n_extra_tables=n_extra_tables,
    )

    next_index = get_next_query_index(version=version)

    logger.info(f"Version: {version}  |  Model: {model}")
    logger.info(f"Queries requested: {n_queries}  |  Extra tables per query: {n_extra_tables}")
    logger.info(f"Starting script index: {next_index:06d}")

    n_succeeded = 0
    n_failed = 0
    run_start = time.perf_counter()

    for offset, table_names in enumerate(subsets):
        query_index = next_index + offset
        bias = get_bias_for_query_index(version=version, query_index=query_index)
        number_of_nested_queries = random.randint(1, 3)

        logger.info("=" * 80)
        logger.info(
            f"Query {offset + 1}/{n_queries}  |  script index {query_index:06d}  |  "
            f"bias={bias}  |  nested_queries={number_of_nested_queries}"
        )
        logger.info(f"Tables: {table_names}")
        logger.info(f"Number of nested queries planned: {number_of_nested_queries} ")

        query_start = time.perf_counter()

        try:
            row = generate_one_query(
                table_names=table_names,
                client=client,
                query_index=query_index,
                version=version,
                model=model,
                number_of_nested_queries=number_of_nested_queries,
                bias=bias,
            )

            elapsed = time.perf_counter() - query_start
            n_succeeded += 1

            logger.info(f"OK ({elapsed:.1f}s) -> {row['python_script_path']}")
            logger.info(f"Question: {row['question_from_llm']}")

        except Exception as e:
            elapsed = time.perf_counter() - query_start
            n_failed += 1

            logger.error(
                f"FAILED ({elapsed:.1f}s) for tables {table_names}: "
                f"{type(e).__name__}: {e}"
            )

        logger.info(
            f"Progress: {offset + 1}/{n_queries} done "
            f"({n_succeeded} succeeded, {n_failed} failed)"
        )

    total_elapsed = time.perf_counter() - run_start

    logger.info("=" * 80)
    logger.info(
        f"Run complete: {n_succeeded} succeeded, {n_failed} failed, "
        f"{total_elapsed:.1f}s total"
    )
    logger.info(
        f"Next script index for a future run: "
        f"{get_next_query_index(version=version):06d}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    parser.add_argument("--n-queries", type=int, default=1)
    parser.add_argument("--n-extra-tables", type=int, default=2)
    parser.add_argument("--model", type=str, default="gpt-5")
    args = parser.parse_args()

    main(
        n_queries=args.n_queries,
        n_extra_tables=args.n_extra_tables,
        model=args.model,
        version=args.version,
    )