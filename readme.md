# CoReLaTTe

**CoReLaTTe (Complex Request over Large Tabular and Textual Data)** is a benchmark generation framework for evaluating Large Language Model (LLM) agents on tabular data reasoning tasks.

Developed as part of a Master's thesis, CoReLaTTe automatically generates benchmark questions, executable solutions, and ground-truth answers from real-world datasets. The framework aims to provide a systematic way of evaluating how effectively LLM agents can reason over structured data using relational operations, statistical methods, and multi-step analytical workflows.

Unlike traditional benchmark construction approaches that rely heavily on manual annotation, CoReLaTTe generates benchmark instances automatically through structured query plans that can be validated, executed, and reproduced.

---

# Overview

Tabular reasoning encompasses a broad range of analytical tasks. Some questions require classical database operations such as filtering, joining, grouping, and aggregation. Others require statistical analysis, machine learning techniques, or a combination of both.

For now, CoReLaTTe organizes benchmark questions into one category :

* **SQL-Type Queries**



---


## SQL-Type Queries

SQL-Type Queries evaluate an agent's ability to perform reasoning based on relational operations.

Supported operations include:

* Filtering
* Projection
* Aggregation
* Sorting
* Grouping
* Inner Joins
* Left Joins
* Right Joins
* Outer Joins
* Semi-Joins
* Anti-Joins

Example:

> Which states contain the largest number of households reporting robberies since 2005?

These questions assess whether an agent can correctly interpret and execute structured data manipulation tasks.


# Benchmark Generation Framework

The benchmark generation process is based on executable query plans.

Each generated benchmark instance follows the same workflow:

```text
Dataset
   │
   ▼
Query Plan Generation
   │
   ▼
Schema Validation
   │
   ▼
Query Repair
   │
   ▼
Python/Pandas Generation
   │
   ▼
Execution
   │
   ▼
Ground Truth Generation
   │
   ▼
Benchmark Instance
```

This approach ensures that every generated question is accompanied by:

* A structured analytical specification.
* Executable Python code.
* A reproducible ground-truth answer.

---

# Architecture

The repository is organized around independent query-generation modules.

```text
src/
├── model/
│   └── Corelatte/
│       └── QueryGeneration/
│           ├── SQL_TYPE_ALONE/
│           ├── ML_ALONE/
│           └── SQL_TYPE_ML/
│
├── pipeline/
│   ├── SQL_TYPE_ALONE/
│   └── ML_ALONE/
│   └── ML_ALONE/
│
└── evaluation/
```

Each query-generation module contains:

```text
prompt.py
query_plan_schema.py
extract_llm_output.py
repair_query_json.py
json_to_pandas.py
execute_code.py
query_plan_to_question.py
```

This modular architecture makes it straightforward to extend the framework with new analytical operations or benchmark categories.

---

# Dataset

The current benchmark uses the **Mexican Family Life Survey (MxFLS)**.

Experiments are conducted on the household survey component of the 2009–2012 wave.

The dataset contains information related to:

* Demographics
* Household income
* Assets
* Agricultural activities
* Land ownership
* Credit
* Economic shocks

Repository location:

```text
raw_data/hh09dta_b2/
```



# Example for running a pipeline : the SQL-Type Pipeline

Every SQL-Type pipeline script accepts a `--version {1,2}` flag (default `1`). Each version reads and writes its own CSV (`processed/dataset_query_v{version}.csv`) and its own output directories, so v1 and v2 queries never mix.

* `--version 1` — the original, unbiased query-plan generation.
* `--version 2` — rotates the query-plan prompt between five structural biases, one per generated query in turn:
  1. a HAVING-style post-aggregation filter (filter on a groupby's aggregated output);
  2. a `scalar_filter` comparison (row value vs. a scalar computed by a separate branch, e.g. an overall average);
  3. a chained multi-join (2+ real `join` nodes across 3 tables, instead of the semi/anti-join shortcut);
  4. a column-provenance join (two joined tables share a non-key column name, so pandas' `_x`/`_y` suffixes kick in — later nodes must reference the correct post-join column);
  5. a join-fan-out join (the join key isn't unique on both sides, so a naive join before aggregating would double-count — the plan must aggregate the one-to-many branch first).

`SQL_TYPE_Generation.py` also accepts `--n-queries` (default `1`, generates that many queries in one run), `--min-extra-tables`/`--max-extra-tables` (default `2`/`4`, tables beyond the always-included base table `ii_portad`), and `--model` (default `gpt-5`):

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py --version 1
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py --version 2
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py --version 2 --n-queries 20
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py --version 2 --min-extra-tables 3 --max-extra-tables 4
```

Two things are randomized independently per query, not fixed once for the whole batch:

* **Number of extra tables** — a fresh integer in `[min-extra-tables, max-extra-tables]` is drawn for every query, so a single run mixes 3-table, 4-table, and 5-table (incl. `ii_portad`) plans. The floor defaults to `2` (not lower) because `multi_join` needs at least 3 tables total to chain; the ceiling defaults to `4` since only 8 non-`ii_portad` tables exist in the sampling pool (`--max-extra-tables` can't exceed `8`).
* **Number of nested query operations** — a fresh integer in `[1, 3]` is drawn per query (the "contain at least N nested query operation(s)" requirement in the prompt).

Progress (per-query status, timing, running success/fail tally, and a final summary) is logged to both the console and a timestamped file under `processed/logs/SQL_TYPE_ALONE/v{version}/generation_<timestamp>.log`, so a long batch run's history isn't lost if the terminal scrolls or the run is backgrounded.

Each query takes roughly 30–70s (one `gpt-5` call to plan the query, up to 2 repair-retry calls if the plan fails schema validation, and one call to phrase the natural-language question), so budget run time accordingly for large `--n-queries` batches.

There is no hard cap on `--n-queries` itself, but table-subset diversity is bounded: the base table is always `ii_portad`, and the extra tables are sampled from the remaining 8 tables, giving C(8, k) distinct table-subset combinations for each extra-table count k in range (28 for k=2, 56 for k=3, 70 for k=4 — summing to 154 across the default `[2, 4]` range). Beyond that many queries, table subsets start repeating within a run — the model still generates a different question/plan each time, so this isn't a hard limit, just a point where topical variety plateaus.

Validate generated code:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Check_Code.py --version 1
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Check_Code.py --version 2
```

Generate gold answers:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_creating_gold_answer.py --version 1
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_creating_gold_answer.py --version 2
```

This only processes rows where `check_if_code_works` is `yes` in that version's CSV — a query that hasn't been through `SQL_TYPE_Check_Code.py` yet (still `no`) is silently skipped, not an error. If a newly added query isn't getting a gold answer, run `SQL_TYPE_Check_Code.py --version {n}` for it first.

Repair scripts that failed validation:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Repair_Code.py --version 1
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Repair_Code.py --version 2
```


# Evaluation

The repository includes an evaluation framework for comparing model predictions against generated ground-truth answers.

**Prerequisite:** every query you want to evaluate must already have passed `SQL_TYPE_Check_Code.py` and have a gold answer from `SQL_TYPE_creating_gold_answer.py` for that same `--version` (see the SQL-Type Pipeline section above). A query without a gold answer isn't a hard failure — `compare_answers.py` just marks it `failed: Missing gold answer` and moves on — but its result won't count toward accuracy.

Every evaluation script also accepts `--version {1,2}` (default `1`), keeping v1 and v2 predictions, gold answers, and results completely separate — v1 and v2 both restart query numbering at `query_000001`, so without a version tag "the same" query name would silently mean two different queries.

1. Run the baseline agent (SEMEVAL8-ITUNLP, code in `src/model/semeval8-itunlp/`) and save its predictions. Each entrypoint runs the *same* agent code against a different underlying LLM, with its own output tree so they never collide:

```bash
python3 evaluation/generate_and_execute_semeval.py --version 1        # gpt-5        -> SEMEVAL8_GPT_5
python3 evaluation/generate_and_execute_semeval.py --version 2        # gpt-5        -> SEMEVAL8_GPT_5
python3 evaluation/generate_and_execute_semeval_nano.py --version 2   # gpt-4.1-nano -> SEMEVAL8_NANO
python3 evaluation/generate_and_execute_semeval_gpt41.py --version 2  # gpt-4.1      -> SEMEVAL8_GPT_4.1
```

`--model` picks the actual LLM sent to the API (default `gpt-5` / `gpt-4.1-nano` / `gpt-4.1` respectively) and can be overridden on any of the three, e.g. `--model gpt-5-mini`; the resulting predictions still land under that script's fixed folder label (`SEMEVAL8_GPT_5` / `SEMEVAL8_NANO` / `SEMEVAL8_GPT_4.1`), so use `--model-name` in the next two steps to match whichever one you actually ran. Adding another model is a ~5-line change: copy one of these three scripts and change its `MODEL_LABEL`/`DEFAULT_MODEL` constants.

If code generation or execution fails for a query, the prediction file is written with the literal content `thecodefailed` instead of being skipped — `compare_answers.py` recognizes that sentinel and auto-classifies it `no` / `"code failed"` without spending a judge call, so failures still count against accuracy instead of silently vanishing from the results.

By default this only (re)runs queries that don't already have a saved prediction — safe to re-run after adding new queries, it won't re-spend API calls on ones already done. Two options change that:

```bash
# Force-(re)run only specific queries, even if they already have a prediction
python3 evaluation/generate_and_execute_semeval.py --version 2 --queries query_000013 query_000014

# Reprocess every row regardless of existing predictions
python3 evaluation/generate_and_execute_semeval.py --version 2 --force
```

2. Judge each prediction against its gold answer with an LLM judge:

```bash
python3 evaluation/compare_answers.py \
    --version 1 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_5 \
    --dataset hh09dta_b2

python3 evaluation/compare_answers.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_5 \
    --dataset hh09dta_b2

python3 evaluation/compare_answers.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_NANO \
    --dataset hh09dta_b2

python3 evaluation/compare_answers.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_4.1 \
    --dataset hh09dta_b2
```

3. Summarize accuracy:

```bash
python3 evaluation/compute_metrics.py \
    --version 1 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_5 \
    --dataset hh09dta_b2

python3 evaluation/compute_metrics.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_5 \
    --dataset hh09dta_b2

python3 evaluation/compute_metrics.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_NANO \
    --dataset hh09dta_b2

python3 evaluation/compute_metrics.py \
    --version 2 \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_GPT_4.1 \
    --dataset hh09dta_b2
```

`--pred-folder`, `--gold-folder`, and `--dataset-csv` all default to the right `v{version}` path and can still be overridden explicitly if needed.

Evaluation outputs are stored under:

```text
evaluation/results/{question_type}_{model_name}_{dataset}_v{version}_eval.csv
evaluation/results/explanation/{question_type}/{model_name}/v{version}/{dataset}/
evaluation/predicted_answers/{question_type}/v{version}/{model_name}/{dataset}/
evaluation/saved_python_script/{question_type}/v{version}/{model_name}/{dataset}/
```

---

# Research Objective

The objective of CoReLaTTe is to provide a reproducible framework for generating and evaluating tabular reasoning benchmarks for LLM agents.

By supporting SQL reasoning, machine learning reasoning, and hybrid analytical workflows within the same framework, CoReLaTTe enables a more comprehensive evaluation of agent capabilities on structured data.

---

# Citation

If you use this repository in academic work, please cite the associated Master's thesis.
