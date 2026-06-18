# CoReLaTTe

**CoReLaTTe (Complex Reasoning over Large Tabular and Textual Data)** is a benchmark generation framework designed to evaluate Large Language Model (LLM) agents on analytical reasoning tasks over real-world tabular datasets.

Developed as part of a Master's thesis, the project addresses a limitation of existing table question-answering benchmarks: most focus exclusively on SQL-style reasoning, while real-world data analysis frequently requires statistical and machine learning methods.

CoReLaTTe automatically generates benchmark questions, executable Python solutions, and ground-truth answers from structured datasets. The framework supports three complementary categories of analytical tasks:

* **SQL-Type Queries**: relational reasoning using filtering, aggregation, joins, and grouping operations.
* **ML-Type Queries**: statistical and machine learning analysis, including regression and clustering.
* **SQL+ML Queries**: hybrid tasks requiring both data preparation and analytical modeling.

The current implementation uses the Mexican Family Life Survey (MxFLS) and provides an end-to-end pipeline for benchmark generation, answer creation, and model evaluation.

---

## Key Features

* Automatic benchmark generation from tabular datasets.
* Structured query-plan generation using LLMs.
* Validation of generated analytical workflows.
* Automatic conversion of query plans into executable Python/Pandas code.
* Automatic generation of gold answers.
* Evaluation pipeline for LLM-generated answers.
* Support for SQL reasoning tasks.
* Support for machine learning and statistical reasoning tasks.
* Modular architecture for extending supported analytical operations.

---

## Repository Structure

```text
CoReLaTTe/
│
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
│   ├── pipeline/
│   │   ├── SQL_TYPE_ALONE/
│   │   └── ML_ALONE/
│   │
│   └── model/
│       ├── Corelatte/
│       └── semeval8-itunlp/
│
└── main.ipynb
```

## Supported Analytical Operations

### SQL-Type Queries

* Filtering
* Selection
* Projection
* Aggregation
* Sorting
* Group By
* Inner/Outer Joins
* Semi-Joins
* Anti-Joins

### ML-Type Queries

* Correlation Analysis
* Regression-Based Explanatory Analysis
* Clustering
* Feature Importance Estimation
* Statistical Hypothesis Testing
* Anomaly Detection
* Dimensionality Reduction

Current implementation focuses on:

* Linear Regression
* K-Means Clustering

---

## Running the SQL Pipeline

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py
```

---

## Running the ML Pipeline

```bash
python3 src/pipeline/ML_ALONE/ML_Generation.py
```

---

## Evaluation

The repository includes an evaluation framework for comparing model predictions against automatically generated ground-truth answers.

Example:

```bash
python3 evaluation/compute_metrics.py \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_ITUNLP \
    --dataset hh09dta_b2
```

Evaluation outputs are stored in:

```text
evaluation/results/
```

---

## Research Context

This repository accompanies a Master's thesis investigating how benchmark generation can be used to evaluate the analytical reasoning capabilities of LLM agents on tabular data.

The long-term objective is to move beyond SQL-only evaluation and assess whether agents can correctly perform end-to-end analytical workflows involving both data manipulation and machine learning.

```

