import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI

from src.pipeline.code_checking_utils import (
    load_dataset_csv,
    save_dataset_csv,
    load_python_script,
    check_generated_code_for_row,
)


REPAIR_SYSTEM_PROMPT = """
You are a Python code repair assistant.

You receive:
1. A broken generated pandas script.
2. The runtime error.
3. The original analytical question.
4. The table names used by the script.
5. The metadata text file names.

Your task:
Repair the Python script.

Rules:
- Return valid JSON only.
- The JSON must contain exactly one key: "python_code".
- The repaired code must define a function run_query(tables).
- run_query(tables) must return a pandas DataFrame.
- Do not include markdown.
- Do not include explanations.
- Do not use files directly inside the generated script.
- Use only the DataFrames passed through the tables dictionary.
"""


def build_repair_prompt(row, broken_code: str) -> str:
    payload = {
        "question_from_llm": row["question_from_llm"],
        "natural_question_arisen_from_code": row["natural_question_arisen_from_code"],
        "python_script_path": row["python_script_path"],
        "tables": row["tables"],
        "text": row["text"],
        "source_dataset": row["source_dataset"],
        "error_message": row["error_message"],
        "broken_python_code": broken_code,
    }

    return f"""
Repair this generated pandas script.

INPUT
=====

{json.dumps(payload, indent=2, ensure_ascii=False)}

OUTPUT FORMAT
=============

Return only:

{{
  "python_code": "..."
}}
""".strip()


def repair_code_with_llm(
    row,
    client: OpenAI,
    model: str = "gpt-5",
) -> str:
    broken_code = load_python_script(row)

    prompt = build_repair_prompt(
        row=row,
        broken_code=broken_code,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": REPAIR_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
    )

    output = json.loads(response.choices[0].message.content)

    return output["python_code"]


def repaired_script_path(original_script_path: str) -> Path:
    path = ROOT / original_script_path

    stem = path.stem

    pattern = re.compile(r"(.+)_repaired_v(\d+)$")
    match = pattern.match(stem)

    if match:
        base = match.group(1)
    else:
        base = stem

    existing = sorted(path.parent.glob(f"{base}_repaired_v*.py"))

    version = len(existing) + 1

    return path.parent / f"{base}_repaired_v{version}.py"


def main(
    model: str = "gpt-5",
) -> None:
    load_dotenv()

    api_key = os.getenv("API_KEY")

    if api_key is None:
        raise ValueError("API_KEY not found in .env")

    client = OpenAI(api_key=api_key)

    df = load_dataset_csv()

    mask = df["check_if_code_works"].fillna("").eq("runtime_error")

    indices = df[mask].index.tolist()

    print(f"Rows to repair: {len(indices)}")

    for i, idx in enumerate(indices, start=1):
        row = df.loc[idx]

        print("=" * 80)
        print(f"Repairing row {idx} ({i}/{len(indices)})")
        print(row["python_script_path"])

        try:
            repaired_code = repair_code_with_llm(
                row=row,
                client=client,
                model=model,
            )

            new_path = repaired_script_path(row["python_script_path"])
            new_path.write_text(repaired_code, encoding="utf-8")

            relative_path = new_path.relative_to(ROOT)

            df.loc[idx, "python_script_path"] = str(relative_path)
            df.loc[idx, "check_if_code_works"] = "no"
            df.loc[idx, "error_message"] = ""

            save_dataset_csv(df)

            print("Saved repaired script:")
            print(relative_path)

        except Exception as e:
            df.loc[idx, "check_if_code_works"] = "repair_failed"
            df.loc[idx, "error_message"] = str(e)

            save_dataset_csv(df)

            print("Repair failed:", type(e).__name__, e)


if __name__ == "__main__":
    main()