import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.pipeline.code_checking_utils import (
    load_dataset_csv,
    save_dataset_csv,
    check_generated_code_for_row,
)


def main(version: int = 1) -> None:
    df = load_dataset_csv(version=version)

    mask = df["check_if_code_works"].fillna("no").eq("no")
    indices = df[mask].index.tolist()

    print(f"Rows to check: {len(indices)}")

    for i, idx in enumerate(indices, start=1):
        row = df.loc[idx]

        print("=" * 80)
        print(f"Checking row {idx} ({i}/{len(indices)})")
        print(row["python_script_path"])

        status = check_generated_code_for_row(row)



        if status == "yes":
            df.loc[idx, "check_if_code_works"] = "yes"

        save_dataset_csv(df, version=version)

        print("Status:", status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    args = parser.parse_args()

    main(version=args.version)