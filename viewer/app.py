"""
Local browser UI for exploring CoReLaTTe benchmark queries and model runs.

Run with:
    python3 viewer/app.py

Then open http://127.0.0.1:5057
"""

import functools
import json
import re
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_ROOT = ROOT / "raw_data"
PROCESSED_ROOT = ROOT / "processed"
EVAL_ROOT = ROOT / "evaluation"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Only SQL_TYPE_ALONE has been split into versioned runs (v1 = the original
# unbiased generation, v2 = rotates structural biases into the generated
# query plans). ML_ALONE still reads/writes a single unversioned CSV and
# output tree, so every path helper below branches on is_versioned().
VERSIONED_QUESTION_TYPES = {"SQL_TYPE_ALONE"}

UNVERSIONED_QUESTION_TYPE_CSV = {
    "ML_ALONE": "dataset_query_ML.csv",
}

KNOWN_QUESTION_TYPES = ["SQL_TYPE_ALONE", "ML_ALONE"]

MAX_ANSWER_ROWS = 500
MAX_TABLE_PAGE_SIZE = 1000

app = Flask(__name__, static_folder=None)


# ==================================================
# HELPERS
# ==================================================

def is_versioned(question_type: str) -> bool:
    return question_type in VERSIONED_QUESTION_TYPES


def get_version_arg():
    raw = request.args.get("version")
    return int(raw) if raw not in (None, "") else None


def safe_value(value, default=""):
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    return value


def safe_int_value(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return int(value)


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


# ---------- version-aware path resolution ----------
# saved_python_script / predicted_answers : {root}/{question_type}/v{n}/{model}/{dataset}
# explanation                             : results/explanation/{question_type}/{model}/v{n}/{dataset}
# gold_answer                             : processed/gold_answer/{question_type}/v{n}/{dataset}
# eval csv                                : results/{question_type}_{model}_{dataset}_v{n}_eval.csv
# These orderings come straight from the pipeline scripts (generate_and_execute_semeval.py,
# compare_answers.py, SQL_TYPE_creating_gold_answer.py) — they are NOT uniform, so each
# helper below mirrors its producing script rather than assuming one shared convention.

def dataset_csv_path(question_type: str, version) -> Path:
    if is_versioned(question_type):
        return PROCESSED_ROOT / f"dataset_query_v{version}.csv"
    return PROCESSED_ROOT / UNVERSIONED_QUESTION_TYPE_CSV[question_type]


def available_versions(question_type: str) -> list[int]:
    if not is_versioned(question_type):
        return []

    pattern = re.compile(r"dataset_query_v(\d+)\.csv$")
    versions = []
    for p in PROCESSED_ROOT.glob("dataset_query_v*.csv"):
        m = pattern.match(p.name)
        if m:
            versions.append(int(m.group(1)))
    return sorted(versions)


def gold_answer_path(question_type: str, dataset: str, query_name: str, version) -> Path:
    base = PROCESSED_ROOT / "gold_answer" / question_type
    if is_versioned(question_type):
        base = base / f"v{version}"
    return base / dataset / f"df_{query_name}.csv"


def saved_script_dir(question_type: str, model: str, dataset: str, version) -> Path:
    base = EVAL_ROOT / "saved_python_script" / question_type
    if is_versioned(question_type):
        base = base / f"v{version}"
    return base / model / dataset


def predicted_answer_dir(question_type: str, model: str, dataset: str, version) -> Path:
    base = EVAL_ROOT / "predicted_answers" / question_type
    if is_versioned(question_type):
        base = base / f"v{version}"
    return base / model / dataset


def explanation_dir_path(question_type: str, model: str, dataset: str, version) -> Path:
    base = EVAL_ROOT / "results" / "explanation" / question_type / model
    if is_versioned(question_type):
        base = base / f"v{version}"
    return base / dataset


def eval_csv_path(question_type: str, model: str, dataset: str, version) -> Path:
    suffix = f"_v{version}" if is_versioned(question_type) else ""
    return EVAL_ROOT / "results" / f"{question_type}_{model}_{dataset}{suffix}_eval.csv"


# Cached readers are keyed on (path, mtime), not just path: this is a live
# view over files the pipeline scripts keep rewriting while the server stays
# up (re-running compare_answers.py, adding queries, re-checking code), so a
# plain lru_cache-by-path would keep serving a pre-edit snapshot forever.
# Stat-ing the file on every request is effectively free next to parsing it.

@functools.lru_cache(maxsize=64)
def _read_csv_cached(path: Path, mtime_ns: int) -> pd.DataFrame:
    return pd.read_csv(path)


@functools.lru_cache(maxsize=64)
def _read_stata_cached(path: Path, mtime_ns: int) -> pd.DataFrame:
    return pd.read_stata(path)


def load_dataset_csv(question_type: str, version) -> pd.DataFrame:
    csv_path = dataset_csv_path(question_type, version)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = _read_csv_cached(csv_path, csv_path.stat().st_mtime_ns).copy()
    df["query_name"] = df["python_script_path"].apply(query_name_from_script_path)
    return df


def load_eval_csv(question_type: str, model: str, dataset: str, version):
    path = eval_csv_path(question_type, model, dataset, version)
    if not path.exists():
        return None
    return _read_csv_cached(path, path.stat().st_mtime_ns)


def load_raw_table(dataset: str, table: str) -> pd.DataFrame:
    path = RAW_DATA_ROOT / dataset / f"{table}.dta"
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")
    return _read_stata_cached(path, path.stat().st_mtime_ns)


def eval_row_for_query(question_type: str, model: str, dataset: str, query_name: str, version):
    eval_df = load_eval_csv(question_type, model, dataset, version)
    if eval_df is None:
        return None

    matches = eval_df[eval_df["query_name"] == query_name]
    if matches.empty:
        return None

    # compare_answers.py appends a new row on every re-run rather than
    # replacing a prior "failed" attempt for the same query_name, so a
    # query retried after a transient judge failure ends up with more than
    # one row here. Always take the most recently appended one.
    r = matches.iloc[-1]
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

    question_types = []
    for qt in KNOWN_QUESTION_TYPES:
        if is_versioned(qt):
            versions = available_versions(qt)
            if versions:
                question_types.append({"name": qt, "versioned": True, "versions": versions})
        else:
            csv_path = PROCESSED_ROOT / UNVERSIONED_QUESTION_TYPE_CSV[qt]
            if csv_path.exists():
                question_types.append({"name": qt, "versioned": False, "versions": []})

    return jsonify({
        "question_types": question_types,
        "source_datasets": source_datasets,
    })


@app.get("/api/models")
def api_models():
    question_type = request.args["question_type"]
    dataset = request.args["dataset"]
    version = get_version_arg()

    root = EVAL_ROOT / "saved_python_script" / question_type
    if is_versioned(question_type):
        root = root / f"v{version}"

    if not root.exists():
        return jsonify([])

    models = sorted(
        p.name for p in root.iterdir()
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
    version = get_version_arg()
    model = request.args.get("model") or None

    df = load_dataset_csv(question_type, version)
    subset = df[df["source_dataset"] == dataset]

    rows = []
    for _, row in subset.iterrows():
        query_name = row["query_name"]

        entry = {
            "query_name": query_name,
            "question": safe_value(row.get("natural_question_arisen_from_code")),
            "tables": parse_json_list(row["tables"]),
            "check_if_code_works": safe_value(row.get("check_if_code_works")),
            "bias": safe_value(row.get("bias")),
            "number_of_nested_queries": safe_int_value(row.get("number_of_nested_queries")),
            "eval": None,
        }

        if model:
            entry["eval"] = eval_row_for_query(question_type, model, dataset, query_name, version)

        rows.append(entry)

    rows.sort(key=lambda r: r["query_name"])
    return jsonify(rows)


@app.get("/api/query_detail")
def api_query_detail():
    question_type = request.args["question_type"]
    dataset = request.args["dataset"]
    query_name = request.args["query_name"]
    version = get_version_arg()
    model = request.args.get("model") or None

    df = load_dataset_csv(question_type, version)
    matches = df[(df["source_dataset"] == dataset) & (df["query_name"] == query_name)]
    if matches.empty:
        return jsonify({"error": "query not found"}), 404

    row = matches.iloc[0]

    gold_script_path = PROCESSED_ROOT / row["python_script_path"]
    gold_path = gold_answer_path(question_type, dataset, query_name, version)

    benchmark = {
        "question_from_llm": safe_value(row.get("question_from_llm")),
        "natural_question": safe_value(row.get("natural_question_arisen_from_code")),
        "tables": parse_json_list(row["tables"]),
        "text_files": parse_json_list(row["text"]),
        "check_if_code_works": safe_value(row.get("check_if_code_works")),
        "bias": safe_value(row.get("bias")),
        "number_of_nested_queries": safe_int_value(row.get("number_of_nested_queries")),
        "gold_script_path": str(gold_script_path.relative_to(ROOT)),
        "gold_script": read_text_or_none(gold_script_path),
        "gold_answer": read_csv_preview(gold_path),
    }

    model_data = None
    if model:
        script_path = saved_script_dir(question_type, model, dataset, version) / f"{query_name}.py"
        pred_path = predicted_answer_dir(question_type, model, dataset, version) / f"df_{query_name}.csv"
        expl_dir = explanation_dir_path(question_type, model, dataset, version)

        model_data = {
            "model": model,
            "predicted_script": read_text_or_none(script_path),
            "predicted_answer": read_csv_preview(pred_path),
            "explanation": read_text_or_none(expl_dir / f"{query_name}_explanation.txt"),
            "raw_response": read_text_or_none(expl_dir / f"{query_name}_raw_response.txt"),
            "debug": read_text_or_none(expl_dir / f"{query_name}_debug.txt"),
            "eval": eval_row_for_query(question_type, model, dataset, query_name, version),
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
