# CoReLaTTe

**CoReLaTTe (Complex Requests over Large Tabular and Textual Data)** is a benchmark generation framework designed to evaluate the analytical reasoning capabilities of Large Language Model (LLM) agents on real-world tabular datasets.

Developed as part of a Master's thesis, CoReLaTTe addresses a limitation of existing tabular benchmarks: most evaluate SQL generation or table question answering, while many real-world analytical tasks require statistical reasoning, machine learning methods, and multi-step analytical workflows.

The framework automatically generates:

* Natural language questions
* Structured query plans
* Executable Python/Pandas solutions
* Ground-truth answers
* Evaluation artifacts

allowing researchers to systematically assess the ability of LLM agents to perform end-to-end analytical reasoning over structured data.

---

# Motivation

Most existing benchmarks focus on questions answerable through SQL-style operations such as filtering, joining, aggregation, and sorting.

However, real-world data analysis frequently requires additional reasoning capabilities:

* Discovering relationships between variables
* Identifying clusters
* Detecting anomalies
* Evaluating statistical hypotheses
* Combining data preparation and analytical modeling

CoReLaTTe was designed to generate benchmark questions that explicitly target these capabilities.

---

# Query Categories

The framework distinguishes three categories of analytical questions.

## SQL-Type Queries

Questions answerable using relational operations only.

Examples of supported operations:

* Filtering
* Selection
* Projection
* Aggregation
* Sorting
* Group By
* Joins
* Semi-Joins
* Anti-Joins

Example:

> Which states have the highest number of households reporting robberies since 2005?

---

## ML-Type Queries

Questions requiring statistical or machine learning methods.

Supported analytical families include:

* Correlation analysis
* Regression-based explanatory analysis
* Clustering
* Feature importance estimation
* Dimensionality reduction
* Statistical hypothesis testing
* Anomaly detection

Current implementation focuses on:

* Linear Regression
* K-Means Clustering

Example:

> Is there a relationship between household income and household assets?

---

## SQL+ML Queries

Questions requiring both relational preprocessing and analytical modeling.

Example:

> Among households located in Oaxaca, what relationship exists between agricultural income and land ownership?

---

# Architecture

The repository is organized around a modular query-generation framework.

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
│
└── evaluation/
```

Each query type contains its own generation pipeline:

```text
QueryGeneration/
├── prompt.py
├── query_plan_schema.py
├── extract_llm_output.py
├── repair_query_json.py
├── json_to_pandas.py
├── execute_code.py
└── query_plan_to_question.py
```

This modular design makes it possible to independently extend:

* the prompt generation process,
* the analytical operators,
* the validation schemas,
* the code generation backend.

---

# Benchmark Generation Pipeline

The benchmark generation process follows the workflow below:

```text
Dataset
   │
   ▼
LLM Query Plan Generation
   │
   ▼
JSON Validation
   │
   ▼
Query Plan Repair
   │
   ▼
Pandas Code Generation
   │
   ▼
Code Execution
   │
   ▼
Gold Answer Generation
   │
   ▼
Benchmark Dataset
   │
   ▼
LLM Agent Evaluation
```

The generated Python code serves as an executable specification of the reasoning process and produces verifiable ground-truth answers.

---

# Dataset

The current benchmark uses the **Mexican Family Life Survey (MxFLS)**.

More specifically, experiments were conducted on:

* Book II (Household Survey)
* Wave 2009–2012

The dataset contains information regarding:

* Household demographics
* Income
* Assets
* Agricultural activities
* Credit
* Land ownership
* Economic shocks

Repository location:

```text
data/hh09dta_b2/
```

---

# Repository Structure

```text
CoReLaTTe/
├── data/
│   ├── hh09dta_b2/
│   ├── dataset_query.csv
│   ├── dataset_query_ML.csv
│   ├── gold_answer/
│   └── python_script_for_queries/
│
├── evaluation/
│   ├── compute_metrics.py
│   ├── compare_answers.py
│   ├── generate_and_execute_semeval.py
│   ├── predicted_answers/
│   ├── saved_python_script/
│   └── results/
│
├── src/
│   ├── model/
│   └── pipeline/
│
├── main.ipynb
└── DistributionNumberColumns.png
```

---

# Running the SQL-Type Pipeline

Generate SQL-style benchmark questions:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py
```

Validate and repair generated code:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Check_Code.py
```

Generate gold answers:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_creating_gold_answer.py
```

---

# Running the ML-Type Pipeline

Generate ML-style benchmark questions:

```bash
python3 src/pipeline/ML_ALONE/ML_Generation.py
```

Validate generated code:

```bash
python3 src/pipeline/ML_ALONE/ML_Check_Code.py
```

---

# Evaluation

CoReLaTTe includes an evaluation framework for comparing model predictions against generated ground-truth answers.

Example:

```bash
python3 evaluation/compute_metrics.py \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_ITUNLP \
    --dataset hh09dta_b2
```

Evaluation artifacts are stored under:

```text
evaluation/results/
evaluation/predicted_answers/
evaluation/saved_python_script/
```

---

# Research Objective

The goal of CoReLaTTe is to study whether LLM agents can reliably perform analytical reasoning over tabular data beyond traditional SQL generation.

The framework enables controlled evaluation of:

* data preparation capabilities,
* analytical planning,
* statistical reasoning,
* machine learning reasoning,
* end-to-end workflow execution.

---

# Citation

If you use this repository in academic work, please cite the associated Master's thesis.

```bibtex
@mastersthesis{fourcroy2026corelatte,
  author = {Cyprien Fourcroy},
  title  = {CoReLaTTe: Benchmark Generation for LLM Agents Specialized in Tabular Data Reasoning},
  school = {Politechnika Warszawska},
  year   = {2026}
}
```
