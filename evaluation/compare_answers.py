import argparse
import json
import os
import traceback
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


MAX_CHARS_PER_TABLE = 60_000

RESULT_COLUMNS = [
    "question_type",
    "model",
    "dataset",
    "query_name",
    "question",
    "gold_answer_path",
    "pred_answer_path",
    "gold_chars",
    "pred_chars",
    "prompt_chars",
    "comparison_status",
    "answer",
    "explanation_path",
    "raw_response_path",
    "error_type",
]


def dataframe_to_text(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def safe_linearize_csv(path: Path):
    df = pd.read_csv(path)
    text = dataframe_to_text(df)
    n_chars = len(text)

    if n_chars > MAX_CHARS_PER_TABLE:
        return None, f"CSV too large: {n_chars} chars > {MAX_CHARS_PER_TABLE}", n_chars

    return text, None, n_chars


def get_query_name(path: Path) -> str:
    stem = path.stem
    return stem[3:] if stem.startswith("df_") else stem


def load_question_map(dataset_csv: Path) -> dict[str, str]:
    df = pd.read_csv(dataset_csv)
    question_map = {}

    for _, row in df.iterrows():
        query_name = Path(row["python_script_path"]).stem
        question_map[query_name] = row["natural_question_arisen_from_code"]

    return question_map


def build_output_path(results_dir: Path, question_type: str, model_name: str, dataset: str) -> Path:
    return results_dir / f"{question_type}_{model_name}_{dataset}_eval.csv"


def build_explanation_dir(results_dir: Path, question_type: str, model_name: str, dataset: str) -> Path:
    return results_dir / "explanation" / question_type / model_name / dataset


def load_existing_results(output_path: Path) -> pd.DataFrame:
    if output_path.exists():
        df = pd.read_csv(output_path)

        for col in RESULT_COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[RESULT_COLUMNS]

    return pd.DataFrame(columns=RESULT_COLUMNS)


def build_prompt(question: str, gold_text: str, pred_text: str) -> str:
    return f"""
You are comparing two dataframe answers to the same data question.

Question:
{question}

Gold answer CSV:
{gold_text}

Predicted answer CSV:
{pred_text}

Decide whether the predicted answer is equivalent to the gold answer.

Return "yes" if it sufficiently answers the question, even if:
- columns are in a different order;
- rows are in a different order, unless ranking/order is essential;
- column names differ but the meaning is clearly equivalent;
- numeric formatting differs slightly;
- integer/float formatting differs, e.g. 3 vs 3.0.
- both CSVs are empty answers;
- both CSVs contain only column headers and no rows;
- both CSVs contain no meaningful result rows;
- one CSV represents an empty dataframe and the other represents the same empty result with different formatting.

Return "no" if:
- values are wrong;
- required rows are missing;
- extra rows change the answer;
- the aggregation is wrong;
- the grouping is wrong;
- the filters are wrong;
- top-k/ranking is wrong when the question asks for ranking.

If answer is "yes", explanation must be an empty string.
If answer is "no", explanation must briefly explain why.

Return JSON only:

{{
  "answer": "yes" or "no",
  "explanation": ""
}}
""".strip()


def call_judge(
    client: OpenAI,
    prompt: str,
    model: str,
    max_retries: int = 3,
):
    last_error = None
    last_raw = ""

    strict_prompt = (
        prompt
        + "\n\nIMPORTANT:\n"
        + "Return exactly one valid JSON object.\n"
        + "Do not return markdown.\n"
        + "Do not return an empty response.\n"
        + "The JSON must have exactly these keys: answer, explanation.\n"
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Judge attempt {attempt}/{max_retries}")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": strict_prompt,
                    }
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=800,
            )

            raw = response.choices[0].message.content or ""
            last_raw = raw

            if not raw.strip():
                raise ValueError("Empty LLM response.")

            parsed = json.loads(raw)

            if "answer" not in parsed:
                raise ValueError(f"Missing key 'answer'. Raw={raw!r}")

            if "explanation" not in parsed:
                parsed["explanation"] = ""

            return parsed, raw

        except Exception as e:
            last_error = e
            print(f"Judge attempt {attempt} failed: {type(e).__name__}: {e}")

    raise ValueError(
        f"Judge failed after {max_retries} attempts. "
        f"Last error: {type(last_error).__name__}: {last_error}. "
        f"Last raw response: {last_raw!r}"
    )

def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--pred-folder", required=True, type=Path)
    parser.add_argument("--gold-folder", required=True, type=Path)
    parser.add_argument("--dataset-csv", default=Path("processed/dataset_query_v1.csv"), type=Path)
    parser.add_argument("--results-dir", default=Path("evaluation/results"), type=Path)
    parser.add_argument("--question-type", required=True, type=str)
    parser.add_argument("--model-name", required=True, type=str)
    parser.add_argument("--dataset", required=True, type=str)
    parser.add_argument("--judge-model", default="gpt-5", type=str)

    args = parser.parse_args()

    load_dotenv()
    client = OpenAI(api_key=os.getenv("API_KEY"))

    args.results_dir.mkdir(parents=True, exist_ok=True)

    output_path = build_output_path(
        args.results_dir,
        args.question_type,
        args.model_name,
        args.dataset,
    )

    explanation_dir = build_explanation_dir(
        args.results_dir,
        args.question_type,
        args.model_name,
        args.dataset,
    )

    question_map = load_question_map(args.dataset_csv)
    results_df = load_existing_results(output_path)

    already_done = set(
        results_df.loc[
            results_df["comparison_status"].eq("success"),
            "query_name",
        ].astype(str)
    )

    pred_files = sorted(args.pred_folder.glob("df_query_*.csv"))

    print(f"Pred files found: {len(pred_files)}")
    print(f"Already completed: {len(already_done)}")
    print(f"Output CSV: {output_path}")
    print(f"Explanation folder: {explanation_dir}")

    rows_to_append = []

    for pred_path in pred_files:
        query_name = get_query_name(pred_path)

        if query_name in already_done:
            print(f"Skipping already compared: {query_name}")
            continue

        gold_path = args.gold_folder / f"df_{query_name}.csv"

        print("=" * 80)
        print(f"Comparing {query_name}")
        print(f"Gold: {gold_path}")
        print(f"Pred: {pred_path}")

        explanation_path = explanation_dir / f"{query_name}_explanation.txt"
        raw_response_path = explanation_dir / f"{query_name}_raw_response.txt"
        debug_path = explanation_dir / f"{query_name}_debug.txt"

        row = {
            "question_type": args.question_type,
            "model": args.model_name,
            "dataset": args.dataset,
            "query_name": query_name,
            "question": question_map.get(query_name, ""),
            "gold_answer_path": str(gold_path),
            "pred_answer_path": str(pred_path),
            "gold_chars": "",
            "pred_chars": "",
            "prompt_chars": "",
            "comparison_status": "not_run",
            "answer": "no",
            "explanation_path": "",
            "raw_response_path": "",
            "error_type": "",
        }

        try:
            if query_name not in question_map:
                raise ValueError(f"No question found for {query_name}")

            if not gold_path.exists():
                raise FileNotFoundError(f"Missing gold answer: {gold_path}")

            gold_text, gold_error, gold_chars = safe_linearize_csv(gold_path)
            pred_text, pred_error, pred_chars = safe_linearize_csv(pred_path)

            row["gold_chars"] = gold_chars
            row["pred_chars"] = pred_chars

            print(f"Gold chars: {gold_chars}")
            print(f"Pred chars: {pred_chars}")

            if gold_error:
                raise ValueError(gold_error)

            if pred_error:
                raise ValueError(pred_error)

            prompt = build_prompt(
                question=question_map[query_name],
                gold_text=gold_text,
                pred_text=pred_text,
            )

            row["prompt_chars"] = len(prompt)

            judgment, raw_response = call_judge(
                client=client,
                prompt=prompt,
                model=args.judge_model,
            )

            answer = judgment.get("answer", "no")
            explanation = judgment.get("explanation", "")

            if answer not in {"yes", "no"}:
                answer = "no"
                explanation = f"Invalid judge answer: {answer!r}"

            if answer == "yes":
                explanation = ""

            write_text(raw_response_path, raw_response)
            write_text(explanation_path, explanation)

            row["comparison_status"] = "success"
            row["answer"] = answer
            row["explanation_path"] = str(explanation_path)
            row["raw_response_path"] = str(raw_response_path)

            print("Answer:", answer)
            if explanation:
                print("Explanation file:", explanation_path)

        except KeyboardInterrupt:
            print("\nInterrupted. Saving progress before exit...")

            rows_to_append.append(row)
            combined = pd.concat(
                [results_df, pd.DataFrame(rows_to_append)],
                ignore_index=True,
            )[RESULT_COLUMNS]
            combined.to_csv(output_path, index=False)

            raise

        except Exception as e:
            error_text = (
                f"QUERY: {query_name}\n"
                f"ERROR TYPE: {type(e).__name__}\n"
                f"ERROR MESSAGE: {str(e)}\n\n"
                f"TRACEBACK:\n{traceback.format_exc()}\n"
            )

            write_text(debug_path, error_text)

            row["comparison_status"] = "failed"
            row["answer"] = "no"
            row["explanation_path"] = str(debug_path)
            row["raw_response_path"] = ""
            row["error_type"] = type(e).__name__

            print("FAILED")
            print(type(e).__name__, ":", e)
            print("Debug file:", debug_path)

        rows_to_append.append(row)

        combined = pd.concat(
            [results_df, pd.DataFrame(rows_to_append)],
            ignore_index=True,
        )[RESULT_COLUMNS]

        combined.to_csv(output_path, index=False)

    print("=" * 80)
    print(f"Saved evaluation to: {output_path}")


if __name__ == "__main__":
    main()