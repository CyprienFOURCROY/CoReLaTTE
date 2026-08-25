"""
Local browser UI for exploring CoReLaTTe benchmark queries and model runs.

Run with:
    python3 viewer/app.py

Then open http://127.0.0.1:5057
"""

import functools

import json
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_ROOT = ROOT / "raw_data"
PROCESSED_ROOT = ROOT / "processed"
EVAL_ROOT = ROOT / "evaluation"
STATIC_DIR = Path(__file__).resolve().parent / "static"

QUESTION_TYPE_CSV = {
    "SQL_TYPE_ALONE": "dataset_query.csv",
    "ML_ALONE": "dataset_query_ML.csv",
}

MAX_ANSWER_ROWS = 500
MAX_TABLE_PAGE_SIZE = 1000

app = Flask(__name__, static_folder=None)


# ==================================================
# HELPERS
# ==================================================

def safe_value(value, default=""):
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    return value


def parse_json_list(value):
    if isinstance(value, list):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return json.loads(value)


def query_name_from_script_path(path_value: str) -> str:
    return Path(path_value).stem


def read_text_or_none(path: Path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def read_csv_preview(path: Path, max_rows: int = MAX_ANSWER_ROWS):
    if not path.exists():
        return None

    df = pd.read_csv(path)
    truncated = len(df) > max_rows

    return {
        "columns": list(df.columns),
        "rows": json.loads(df.head(max_rows).to_json(orient="records")),
        "total_rows": int(len(df)),
        "truncated": truncated,
    }


@functools.lru_cache(maxsize=8)
def load_dataset_csv(question_type: str) -> pd.DataFrame:
    csv_name = QUESTION_TYPE_CSV.get(question_type)
    if csv_name is None:
        raise ValueError(f"Unknown question type: {question_type}")

    df = pd.read_csv(PROCESSED_ROOT / csv_name)
    df["query_name"] = df["python_script_path"].apply(query_name_from_script_path)
    return df


@functools.lru_cache(maxsize=32)
def load_eval_csv(question_type: str, model: str, dataset: str):
    path = EVAL_ROOT / "results" / f"{question_type}_{model}_{dataset}_eval.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


@functools.lru_cache(maxsize=32)
def load_raw_table(dataset: str, table: str) -> pd.DataFrame:
    path = RAW_DATA_ROOT / dataset / f"{table}.dta"
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")
    return pd.read_stata(path)


def eval_row_for_query(question_type: str, model: str, dataset: str, query_name: str):
    eval_df = load_eval_csv(question_type, model, dataset)
    if eval_df is None:
        return None

    matches = eval_df[eval_df["query_name"] == query_name]
    if matches.empty:
        return None

    r = matches.iloc[0]
    return {
        "comparison_status": safe_value(r.get("comparison_status")),
        "answer": safe_value(r.get("answer")),
        "error_type": safe_value(r.get("error_type")),
    }


# ==================================================
# API — selection
# ==================================================

@app.get("/api/config")
def api_config():
    source_datasets = sorted(
        p.name for p in RAW_DATA_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ) if RAW_DATA_ROOT.exists() else []

    question_types = [
        qt for qt, csv_name in QUESTION_TYPE_CSV.items()
        if (PROCESSED_ROOT / csv_name).exists()
    ]

    return jsonify({
        "question_types": question_types,
        "source_datasets": source_datasets,
    })


@app.get("/api/models")
def api_models():
    question_type = request.args["question_type"]
    dataset = request.args["dataset"]

    script_root = EVAL_ROOT / "saved_python_script" / question_type
    if not script_root.exists():
        return jsonify([])

    models = sorted(
        p.name for p in script_root.iterdir()
        if p.is_dir() and (p / dataset).exists()
    )
    return jsonify(models)


# ==================================================
# API — queries
# ==================================================

@app.get("/api/queries")
def api_queries():
    question_type = request.args["question_type"]
    dataset = request.args["dataset"]
    model = request.args.get("model") or None

    df = load_dataset_csv(question_type)
    subset = df[df["source_dataset"] == dataset]

    rows = []
    for _, row in subset.iterrows():
        query_name = row["query_name"]

        entry = {
            "query_name": query_name,
            "question": safe_value(row.get("natural_question_arisen_from_code")),
            "tables": parse_json_list(row["tables"]),
            "check_if_code_works": safe_value(row.get("check_if_code_works")),
            "eval": None,
        }

        if model:
            entry["eval"] = eval_row_for_query(question_type, model, dataset, query_name)

        rows.append(entry)

    rows.sort(key=lambda r: r["query_name"])
    return jsonify(rows)


@app.get("/api/query_detail")
def api_query_detail():
    question_type = request.args["question_type"]
    dataset = request.args["dataset"]
    query_name = request.args["query_name"]
    model = request.args.get("model") or None

    df = load_dataset_csv(question_type)
    matches = df[(df["source_dataset"] == dataset) & (df["query_name"] == query_name)]
    if matches.empty:
        return jsonify({"error": "query not found"}), 404

    row = matches.iloc[0]

    gold_script_path = PROCESSED_ROOT / row["python_script_path"]
    gold_answer_path = (
        PROCESSED_ROOT / "gold_answer" / question_type / dataset / f"df_{query_name}.csv"
    )

    benchmark = {
        "question_from_llm": safe_value(row.get("question_from_llm")),
        "natural_question": safe_value(row.get("natural_question_arisen_from_code")),
        "tables": parse_json_list(row["tables"]),
        "text_files": parse_json_list(row["text"]),
        "check_if_code_works": safe_value(row.get("check_if_code_works")),
        "gold_script_path": str(gold_script_path.relative_to(ROOT)),
        "gold_script": read_text_or_none(gold_script_path),
        "gold_answer": read_csv_preview(gold_answer_path),
    }

    model_data = None
    if model:
        script_path = (
            EVAL_ROOT / "saved_python_script" / question_type / model / dataset
            / f"{query_name}.py"
        )
        pred_path = (
            EVAL_ROOT / "predicted_answers" / question_type / model / dataset
            / f"df_{query_name}.csv"
        )
        explanation_dir = EVAL_ROOT / "results" / "explanation" / question_type / model / dataset

        model_data = {
            "model": model,
            "predicted_script": read_text_or_none(script_path),
            "predicted_answer": read_csv_preview(pred_path),
            "explanation": read_text_or_none(explanation_dir / f"{query_name}_explanation.txt"),
            "raw_response": read_text_or_none(explanation_dir / f"{query_name}_raw_response.txt"),
            "debug": read_text_or_none(explanation_dir / f"{query_name}_debug.txt"),
            "eval": eval_row_for_query(question_type, model, dataset, query_name),
        }

    return jsonify({"benchmark": benchmark, "model": model_data})


# ==================================================
# API — raw tables
# ==================================================

@app.get("/api/table")
def api_table():
    dataset = request.args["dataset"]
    table = request.args["table"]
    offset = max(int(request.args.get("offset", 0)), 0)
    limit = min(int(request.args.get("limit", 200)), MAX_TABLE_PAGE_SIZE)

    try:
        df = load_raw_table(dataset, table)
    except FileNotFoundError:
        return jsonify({"error": "table not found"}), 404

    chunk = df.iloc[offset: offset + limit]

    return jsonify({
        "columns": list(df.columns),
        "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
        "rows": json.loads(chunk.to_json(orient="records")),
        "total_rows": int(len(df)),
        "offset": offset,
        "limit": limit,
    })


@app.get("/api/codebook")
def api_codebook():
    dataset = request.args["dataset"]
    table = request.args["table"]
    path = RAW_DATA_ROOT / dataset / "codebook_json" / f"{table}_enriched.txt"
    return jsonify({"text": read_text_or_none(path)})


# ==================================================
# STATIC FRONTEND
# ==================================================

@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=True, use_reloader=False)
