import argparse
from pathlib import Path

import pandas as pd


def build_eval_path(
    results_dir: Path,
    question_type: str,
    model_name: str,
    dataset: str,
    version: int,
) -> Path:
    return results_dir / f"{question_type}_{model_name}_{dataset}_v{version}_eval.csv"


def print_section(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_query_list(df: pd.DataFrame, title: str) -> None:
    print_section(title)

    if df.empty:
        print("None")
        return

    for _, row in df.iterrows():
        print(f"- {row['query_name']}")
        if "question" in row and pd.notna(row["question"]):
            print(f"  Question: {row['question']}")
        if "answer" in row and pd.notna(row["answer"]):
            print(f"  Answer: {row['answer']}")
        if "error_type" in row and pd.notna(row["error_type"]) and row["error_type"] != "":
            print(f"  Error type: {row['error_type']}")
        if "explanation_path" in row and pd.notna(row["explanation_path"]) and row["explanation_path"] != "":
            print(f"  Explanation/debug: {row['explanation_path']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    parser.add_argument(
        "--pred-folder",
        type=Path,
        default=None,
        help=(
            "Folder containing predicted answer CSV files. Defaults to "
            "evaluation/predicted_answers/SQL_TYPE_ALONE/v{version}/{model-name}/{dataset}"
        ),
    )
    parser.add_argument(
        "--results-dir",
        default=Path("evaluation/results"),
        type=Path,
    )
    parser.add_argument("--question-type", required=True, type=str)
    parser.add_argument("--model-name", required=True, type=str)
    parser.add_argument("--dataset", required=True, type=str)

    args = parser.parse_args()

    if args.pred_folder is None:
        args.pred_folder = Path(
            f"evaluation/predicted_answers/SQL_TYPE_ALONE/v{args.version}/"
            f"{args.model_name}/{args.dataset}"
        )

    eval_path = build_eval_path(
        results_dir=args.results_dir,
        question_type=args.question_type,
        model_name=args.model_name,
        dataset=args.dataset,
        version=args.version,
    )

    if not eval_path.exists():
        raise FileNotFoundError(f"Evaluation CSV not found: {eval_path}")

    df = pd.read_csv(eval_path)

    pred_files = sorted(args.pred_folder.glob("df_query_*.csv"))
    predicted_query_names = {
        path.stem.replace("df_", "", 1)
        for path in pred_files
    }

    evaluated_query_names = set(df["query_name"].astype(str))

    missing_from_eval = sorted(
        predicted_query_names - evaluated_query_names
    )

    total_predictions = len(predicted_query_names)
    total_evaluated_rows = len(df)

    successful_comparisons = int(df["comparison_status"].eq("success").sum())
    failed_comparisons = int(df["comparison_status"].eq("failed").sum())

    correct_df = df[
        df["comparison_status"].eq("success")
        & df["answer"].eq("yes")
    ]

    incorrect_df = df[
        df["comparison_status"].eq("success")
        & df["answer"].eq("no")
    ]

    failed_comparison_df = df[
        df["comparison_status"].eq("failed")
    ]

    correct = len(correct_df)
    incorrect = len(incorrect_df)

    overall_accuracy_over_predictions = (
        correct / total_predictions
        if total_predictions
        else 0
    )

    overall_accuracy_over_evaluated_rows = (
        correct / total_evaluated_rows
        if total_evaluated_rows
        else 0
    )

    conditional_accuracy = (
        correct / successful_comparisons
        if successful_comparisons
        else 0
    )

    comparison_success_rate_over_predictions = (
        successful_comparisons / total_predictions
        if total_predictions
        else 0
    )

    comparison_success_rate_over_evaluated_rows = (
        successful_comparisons / total_evaluated_rows
        if total_evaluated_rows
        else 0
    )

    print_section("METRICS")
    print("Evaluation file:", eval_path)
    print("Prediction folder:", args.pred_folder)
    print("Version:", args.version)
    print("Question type:", args.question_type)
    print("Model:", args.model_name)
    print("Dataset:", args.dataset)
    print("-" * 80)
    print("Predicted answer files:", total_predictions)
    print("Rows in evaluation CSV:", total_evaluated_rows)
    print("Missing from evaluation CSV:", len(missing_from_eval))
    print("-" * 80)
    print("Successful comparisons:", successful_comparisons)
    print("Failed comparisons:", failed_comparisons)
    print("Correct:", correct)
    print("Incorrect:", incorrect)
    print("-" * 80)
    print(f"Overall accuracy over predictions: {overall_accuracy_over_predictions:.4f}")
    print(f"Overall accuracy over evaluated rows: {overall_accuracy_over_evaluated_rows:.4f}")
    print(f"Conditional accuracy: {conditional_accuracy:.4f}")
    print(f"Comparison success rate over predictions: {comparison_success_rate_over_predictions:.4f}")
    print(f"Comparison success rate over evaluated rows: {comparison_success_rate_over_evaluated_rows:.4f}")

    print_query_list(
        failed_comparison_df,
        "FAILED COMPARISONS",
    )

    print_query_list(
        incorrect_df,
        "QUERIES ANSWERED INCORRECTLY",
    )

    if missing_from_eval:
        print_section("PREDICTIONS NOT YET EVALUATED")
        for query_name in missing_from_eval:
            print(f"- {query_name}")


if __name__ == "__main__":
    main()