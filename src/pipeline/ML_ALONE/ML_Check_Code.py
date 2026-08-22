import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import subprocess

import pandas as pd


SOURCE_DATASET = "hh09dta_b2"

PROCESSED_ROOT = ROOT / "processed"
QUESTION_TYPE = "ML_ALONE"

SOURCE_DATASET = "hh09dta_b2"

CSV_PATH = PROCESSED_ROOT / "dataset_query_ML.csv"

SCRIPT_ROOT = (
    PROCESSED_ROOT
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


def check_environment() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    if not SCRIPT_ROOT.exists():
        raise FileNotFoundError(f"Script folder not found: {SCRIPT_ROOT}")

    existing_columns = list(pd.read_csv(CSV_PATH, nrows=0).columns)

    if existing_columns != CSV_COLUMNS:
        raise ValueError(
            "CSV columns are incorrect.\n"
            f"Expected: {CSV_COLUMNS}\n"
            f"Found:    {existing_columns}"
        )


def resolve_script_path(relative_path: str) -> Path:
    path = PROCESSED_ROOT / relative_path

    if not path.exists():
        raise FileNotFoundError(f"Script not found: {path}")

    return path


def run_script(
    script_path: Path,
    timeout_seconds: int = 120,
) -> tuple[bool, str, str]:
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    success = result.returncode == 0

    return success, result.stdout, result.stderr

def is_ml_script_path(path_value: str) -> bool:
    return (
        isinstance(path_value, str)
        and path_value.startswith(
            f"python_script_for_queries/{QUESTION_TYPE}/{SOURCE_DATASET}/"
        )
        and path_value.endswith(".py")
    )


def check_ml_scripts(
    timeout_seconds: int = 120,
    only_unchecked: bool = True,
) -> None:
    check_environment()

    df = pd.read_csv(CSV_PATH)

    candidate_mask = df["python_script_path"].apply(is_ml_script_path)

    if only_unchecked:
        candidate_mask &= df["check_if_code_works"].astype(str).str.lower().eq("no")

    candidate_indices = df.index[candidate_mask].tolist()

    print(f"Found {len(candidate_indices)} ML scripts to check.")

    for position, index in enumerate(candidate_indices, start=1):
        relative_path = df.loc[index, "python_script_path"]

        print("=" * 80)
        print(f"Checking {position}/{len(candidate_indices)}")
        print(f"Row index: {index}")
        print(f"Script: {relative_path}")

        try:
            script_path = resolve_script_path(relative_path)

            success, stdout, stderr = run_script(
                script_path=script_path,
                timeout_seconds=timeout_seconds,
            )

            if success:
                df.loc[index, "check_if_code_works"] = "yes"
                print("SUCCESS")
                print(stdout)

            else:
                df.loc[index, "check_if_code_works"] = "no"
                print("FAILED")
                print("STDOUT:")
                print(stdout)
                print("STDERR:")
                print(stderr)

        except Exception as e:
            df.loc[index, "check_if_code_works"] = "no"
            print("FAILED WITH EXCEPTION")
            print(type(e).__name__, ":", e)

        df.to_csv(CSV_PATH, index=False)

    print("=" * 80)
    print("Done.")


if __name__ == "__main__":
    check_ml_scripts(
        timeout_seconds=120,
        only_unchecked=True,
    )