# Ad Campaign Aggregation

## Overview

This project processes a large advertising dataset and computes:

- **Top 10 campaigns by CTR (Click-Through Rate)**
- **Top 10 campaigns by lowest CPA (Cost Per Acquisition)**

The implementation uses **Polars LazyFrame** to efficiently process large CSV datasets (~26M rows).

Key optimizations:

- Lazy execution
- Streaming CSV scan
- Parallel aggregation
- Optimized `top_k` selection

---

# Dataset

The dataset is provided as a compressed file:

```
ad_data.csv.zip
```

Extract it first:

```bash
unzip ad_data.csv.zip
```

Result:

```
ad_data.csv
```

Dataset schema:

| Column | Type | Description |
|------|------|------|
| campaign_id | string | Campaign identifier |
| date | string | Event date |
| impressions | integer | Number of impressions |
| clicks | integer | Number of clicks |
| spend | float | Advertising cost |
| conversions | integer | Number of conversions |

---

# Setup Instructions

## 1. Python Version

Python **3.10+** recommended.

Check version:

```bash
python --version
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
polars
psutil
pytest
```

---

# Project Structure

```
project/
├── Dockerfile
├── README.md
├── __pycache__
│   └── aggregator.cpython-310.pyc
├── ad_data.csv
├── ad_data.csv.zip
├── aggregator.py
├── benchmark.log
├── benchmark.py
├── requirements.txt
├── results
├── test.ipynb
├── tests
│   └── test_aggregator.py
├── top10_cpa.csv
└── top10_ctr.csv

3 directories, 13 files
```

---

# Running the Aggregation

After extracting the dataset:

```bash
python aggregator.py --input ad_data.csv --output results/
```

Example:

```bash
python aggregator.py --input ad_data.csv --output results/
```

Output files:

```
results/
 ├── top10_ctr.csv
 └── top10_cpa.csv
```

---

# Output Description

## top10_ctr.csv

Top 10 campaigns ranked by **highest CTR**.

| Column | Description |
|------|------|
| campaign_id | Campaign ID |
| total_impressions | Total impressions |
| total_clicks | Total clicks |
| total_spend | Total spend |
| total_conversions | Total conversions |
| CTR | Click-through rate |
| CPA | Cost per acquisition |

---

## top10_cpa.csv

Top 10 campaigns ranked by **lowest CPA**.

Only campaigns with **at least one conversion** are included.

---

# Running Tests

Run unit tests using `pytest`:

```bash
pytest
```

---

# Benchmark

Benchmark executed on the full dataset.

Dataset size:

```
26,843,544 rows
```

Benchmark result:

```
===== BENCHMARK RESULT =====
Dataset file: ad_data.csv
Rows processed: 26843544
Execution time: 12.617 seconds
Throughput: 2,127,588 rows/sec
Memory usage: 1396.94 MB
============================
```

Environment:

| Component | Value |
|------|------|
| CPU | 8-core |
| RAM | 16GB |
| Dataset | ~1GB CSV |
| Engine | Polars LazyFrame |

---

# Running Benchmark

To reproduce the benchmark:

```bash
python benchmark.py
```

The benchmark script measures:

- Execution time
- Rows processed
- Throughput (rows/sec)
- Memory usage

Benchmark logs are written to:

```
benchmark.log
```

---

# Docker Support

The project can also be executed using Docker.

## Build Docker Image

```bash
docker build -t campaign-aggregator .
```

## Run Aggregation

```bash
docker run --rm -v $(pwd):/app campaign-aggregator
```

## Run Benchmark

```bash
docker run --rm -v $(pwd):/app \
--entrypoint python \
campaign-aggregator benchmark.py
```

---

# Processing Pipeline

```
CSV Scan
   ↓
Group By campaign_id
   ↓
Aggregate metrics
   ↓
Compute CTR / CPA
   ↓
Top-K Selection
   ↓
Write Results
```

---

# Complexity Analysis

## CSV Scan

```
O(n)
```

Where:

- `n` = number of rows.

---

## Aggregation

Hash aggregation by `campaign_id`.

```
Time:  O(n)
Space: O(m)
```

Where:

- `m` = number of unique campaigns.

---

## CTR / CPA Computation

Vectorized column operations.

```
O(m)
```

---

## Top-K Selection

Using `top_k` instead of full sorting.

```
O(m log k)
```

Where:

- `k = 10`

---

## Overall Complexity

```
O(n) + O(m log k)
```

Since typically:

```
n >> m
```

The pipeline scales **linearly with dataset size**.

---

# Why Polars Instead of Pandas

## Lazy Execution

Polars builds an optimized execution plan before running queries.

This allows:

- predicate pushdown
- projection pushdown
- query optimization

---

## Streaming Processing

Large CSV files can be processed **without loading the entire dataset into memory**.

---

## Parallel Execution

Polars is written in **Rust** and automatically uses multiple CPU cores.

Operations like:

- group by
- aggregation
- sorting

run in parallel.

---

## Memory Efficiency

Polars uses **Apache Arrow columnar memory format**, enabling:

- zero-copy operations
- columnar processing
- efficient memory layout

---

# Author

Implementation using **Polars LazyFrame for scalable data processing**.