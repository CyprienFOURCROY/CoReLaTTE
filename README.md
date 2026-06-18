# CoReLaTTe

**CoReLaTTe (Complex Request over Large Tabular and Textual Data)** is a benchmark generation framework for evaluating Large Language Model (LLM) agents on tabular data reasoning tasks.

Developed as part of a Master's thesis, CoReLaTTe automatically generates benchmark questions, executable solutions, and ground-truth answers from real-world datasets. The framework aims to provide a systematic way of evaluating how effectively LLM agents can reason over structured data using relational operations, statistical methods, and multi-step analytical workflows.

Unlike traditional benchmark construction approaches that rely heavily on manual annotation, CoReLaTTe generates benchmark instances automatically through structured query plans that can be validated, executed, and reproduced.

---

# Overview

Tabular reasoning encompasses a broad range of analytical tasks. Some questions require classical database operations such as filtering, joining, grouping, and aggregation. Others require statistical analysis, machine learning techniques, or a combination of both.

To capture this diversity, CoReLaTTe organizes benchmark questions into three categories:

* **SQL-Type Queries**
* **ML-Type Queries**
* **SQL+ML Queries**

Each category evaluates a different aspect of an LLM agent's reasoning capabilities while maintaining a common generation and evaluation framework.

---

# Query Categories

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

---

## ML-Type Queries

ML-Type Queries evaluate an agent's ability to perform statistical and machine learning analysis directly on tabular data.

Supported analytical families include:

* Correlation Analysis
* Regression-Based Analysis
* Clustering
* Feature Importance Estimation
* Statistical Hypothesis Testing
* Dimensionality Reduction
* Anomaly Detection

Current implementation focuses on:

* Linear Regression
* K-Means Clustering

Example:

> Is there a relationship between household income and household assets?

These questions assess whether an agent can identify patterns, relationships, and structures within data.

---

## SQL+ML Queries

SQL+ML Queries combine relational reasoning and analytical modeling.

They require:

1. Data preparation through SQL-style operations.
2. Statistical or machine learning analysis on the resulting dataset.

Example:

> Among households located in Oaxaca, what relationship exists between agricultural income and land ownership?

These questions evaluate an agent's ability to perform complete analytical workflows.

---

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
data/hh09dta_b2/
```



# Example for running a pipeline : the SQL-Type Pipeline

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Generation.py
```

Validate generated code:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_Check_Code.py
```

Generate gold answers:

```bash
python3 src/pipeline/SQL_TYPE_ALONE/SQL_TYPE_creating_gold_answer.py
```


# Evaluation

The repository includes an evaluation framework for comparing model predictions against generated ground-truth answers.

Example:

```bash
python3 evaluation/compute_metrics.py \
    --question-type SQL_TYPE_ALONE \
    --model-name SEMEVAL8_ITUNLP \
    --dataset hh09dta_b2
```

Evaluation outputs are stored under:

```text
evaluation/results/
evaluation/predicted_answers/
evaluation/saved_python_script/
```

---

# Research Objective

The objective of CoReLaTTe is to provide a reproducible framework for generating and evaluating tabular reasoning benchmarks for LLM agents.

By supporting SQL reasoning, machine learning reasoning, and hybrid analytical workflows within the same framework, CoReLaTTe enables a more comprehensive evaluation of agent capabilities on structured data.

---

# Citation

If you use this repository in academic work, please cite the associated Master's thesis.
