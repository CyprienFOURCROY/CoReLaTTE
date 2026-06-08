import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import os
import re
import json
import random

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from src.model.Corelatte.QueryGeneration.ML_ALONE import (
    build_ml_plan_prompt,
    parse_llm_json_response,
    extract_question_and_ml_plan,
    validate_or_repair_ml_plan,
    compile_ml_plan,
    ml_plan_to_question,
)


SOURCE_DATASET = "hh09dta_b2"

DATA_ROOT = ROOT / "data"
DATA_DIR = DATA_ROOT / SOURCE_DATASET
JSON_DIR = DATA_DIR / "codebook_json"

CSV_PATH = DATA_ROOT / "dataset_query.csv"

QUESTION_TYPE = "ML_ALONE"

SOURCE_DATASET = "hh09dta_b2"

CSV_PATH = DATA_ROOT / "dataset_query_ML.csv"

GENERATED_SCRIPT_DIR = (
    DATA_ROOT
    / "python_script_for_queries"
    / QUESTION_TYPE
    / SOURCE_DATASET
)

CSV_COLUMNS = [
    "question_from_llm",
    "natural_question_arisen_from_code",
    "python_script_path",
    "tables",
    "text",
    "source_dataset",
    "check_if_code_works",
]

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


def check_environment() -> None:
    if not DATA_ROOT.exists():
        raise FileNotFoundError(f"Data root not found: {DATA_ROOT}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATA_DIR}")

    if not JSON_DIR.exists():
        raise FileNotFoundError(f"Metadata folder not found: {JSON_DIR}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    existing_columns = list(pd.read_csv(CSV_PATH, nrows=0).columns)

    if existing_columns != CSV_COLUMNS:
        raise ValueError(
            "CSV columns are incorrect.\n"
            f"Expected: {CSV_COLUMNS}\n"
            f"Found:    {existing_columns}"
        )

    GENERATED_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)


def make_table_subsets(
    n_queries: int,
    n_extra_tables: int = 0,
) -> list[list[str]]:
    subsets = []
    available_numbers = list(range(2, 10))

    for _ in range(n_queries):
        subset_numbers = [1]

        if n_extra_tables > 0:
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


def get_next_query_index() -> int:
    pattern = re.compile(r"query_(\d{6})\.py$")

    max_index = 0

    for path in GENERATED_SCRIPT_DIR.glob("query_*.py"):
        match = pattern.match(path.name)

        if match:
            index = int(match.group(1))
            max_index = max(max_index, index)

    return max_index + 1


def script_path_from_index(index: int) -> Path:
    return GENERATED_SCRIPT_DIR / f"query_{index:06d}.py"


def save_python_code(code: str, query_index: int) -> Path:
    script_path = script_path_from_index(query_index)

    if script_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing script: {script_path}"
        )

    script_path.write_text(code, encoding="utf-8")

    return script_path


def append_row(row: dict) -> None:
    df = pd.read_csv(CSV_PATH)

    row_df = pd.DataFrame([row], columns=CSV_COLUMNS)

    df = pd.concat(
        [df, row_df],
        ignore_index=True,
    )

    df.to_csv(CSV_PATH, index=False)


def generate_one_query(
    table_names: list[str],
    client: OpenAI,
    query_index: int,
    model: str = "gpt-5",
    prompt_type: str | None = None,
) -> dict:
    tables = load_tables(table_names)
    dataframe_description = build_description(table_names)

    prompt, selected_prompt_type = build_ml_plan_prompt(
        dataframes=tables,
        dataframe_description=dataframe_description,
        n_sample_rows=3,
        prompt_type=prompt_type,
    )

    print(f"Selected ML prompt type: {selected_prompt_type}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an ML benchmark generation assistant. "
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

    question_from_llm, ml_plan = extract_question_and_ml_plan(output)

    repair_result = validate_or_repair_ml_plan(
        ml_plan=ml_plan,
        client=client,
        model=model,
        max_repair_attempts=2,
    )

    validated_plan = repair_result["validated_plan"]
    repaired_ml_plan = repair_result["repaired_ml_plan"]

    python_code = compile_ml_plan(repaired_ml_plan)

    script_path = save_python_code(
        code=python_code,
        query_index=query_index,
    )

    relative_script_path = script_path.relative_to(DATA_ROOT)

    natural_question_arisen_from_code = ml_plan_to_question(
        ml_plan=validated_plan.model_dump(),
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
    }

    append_row(row)

    return row


def main(
    n_queries: int = 10,
    n_extra_tables: int = 0,
    model: str = "gpt-5",
    prompt_type: str | None = None,
) -> None:
    check_environment()

    load_dotenv()

    api_key = os.getenv("API_KEY")

    if api_key is None:
        raise ValueError("API_KEY not found in .env")

    client = OpenAI(api_key=api_key)

    subsets = make_table_subsets(
        n_queries=n_queries,
        n_extra_tables=n_extra_tables,
    )

    next_index = get_next_query_index()

    print(f"Starting script index: {next_index}")

    for offset, table_names in enumerate(subsets):
        query_index = next_index + offset

        print("=" * 80)
        print(f"Generating ML query {offset + 1}/{n_queries}")
        print(f"Script index: {query_index:06d}")
        print(f"Candidate tables: {table_names}")

        try:
            row = generate_one_query(
                table_names=table_names,
                client=client,
                query_index=query_index,
                model=model,
                prompt_type=prompt_type,
            )

            print("Saved ML query:")
            print(row["question_from_llm"])
            print("Natural question from code:")
            print(row["natural_question_arisen_from_code"])
            print("Script:")
            print(row["python_script_path"])

        except Exception as e:
            print(f"FAILED for tables {table_names}")
            print(type(e).__name__, ":", e)


if __name__ == "__main__":
    main(
        n_queries=1,
        n_extra_tables=2,
        model="gpt-5",
        prompt_type=None,
    )