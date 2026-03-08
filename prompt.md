# PROMPTS.md

## AI Assistant Notes

During the development of this project, I used AI assistants (primarily ChatGPT and occasionally GitHub Copilot) as a supporting tool for brainstorming ideas, validating approaches, and improving documentation.

AI was **not used as a direct code generator**, but rather as a way to:

- explore different algorithmic approaches
- verify complexity analysis
- discuss performance trade-offs
- generate small utility scripts (benchmarking, documentation structure)

All final architectural decisions, optimizations, and code implementations were reviewed and written manually.

Below are some representative prompts used during the development process.

---

# 1. Choosing a Data Processing Approach

### Prompt

```
I have a CSV dataset with advertising campaign metrics:

campaign_id
date
impressions
clicks
spend
conversions

The dataset can be around 1GB or larger.

I need to aggregate by campaign_id and compute:
- total impressions
- total clicks
- total spend
- total conversions
- CTR (clicks / impressions)
- CPA (spend / conversions)

What would be the most efficient approach in Python for processing this?
```

### Discussion

I explored several approaches:

#### Option 1 — Pandas

Typical implementation:

```
df.groupby("campaign_id").agg(...)
```

Advantages:

- Simple API
- Very common ecosystem

Disadvantages:

- Eager execution
- Entire dataset loaded into memory
- Limited multi-threading

For large CSV datasets (~1GB), this can lead to high memory usage.

---

#### Option 2 — Polars (LazyFrame)

Using:

```
pl.scan_csv()
```

instead of:

```
pl.read_csv()
```

Advantages:

- Lazy query planning
- Streaming execution
- Parallel execution
- Arrow columnar memory format

Polars can optimize the query plan before executing it.

After evaluating these options, I decided to implement the pipeline using **Polars LazyFrame**.

---

# 2. Aggregation Algorithm

### Prompt

```
What is the most efficient way to perform group-by aggregation on a large dataset?

I need to compute sums for multiple columns grouped by campaign_id.
```

### Discussion

The aggregation step uses **hash aggregation**.

Conceptually:

```
hash_map[campaign_id] += metrics
```

Time Complexity:

```
O(n)
```

Where:

```
n = number of rows
```

Space Complexity:

```
O(m)
```

Where:

```
m = number of unique campaigns
```

Polars internally performs parallel aggregation using multiple CPU threads.

This makes the aggregation step highly scalable.

---

# 3. Computing CTR and CPA

### Prompt

```
After aggregation, I need to compute CTR and CPA.

Should I compute them row-by-row or use vectorized operations?
```

### Discussion

Vectorized operations are significantly faster because they operate on entire columns.

Instead of:

```
for row in rows:
    ctr = clicks / impressions
```

The implementation uses:

```
pl.col("clicks") / pl.col("impressions")
```

Time Complexity:

```
O(m)
```

Where:

```
m = number of campaigns
```

This step is very fast because it runs on a columnar data structure.

---

# 4. Selecting Top Campaigns

### Prompt

```
I need the top 10 campaigns by CTR and the lowest CPA.

Is it better to sort the dataset or use a top-k algorithm?
```

### Discussion

Two approaches were considered.

### Full Sorting

```
sort("CTR").head(10)
```

Complexity:

```
O(n log n)
```

This sorts the entire dataset.

---

### Top-K Selection

Polars provides:

```
top_k()
```

Complexity:

```
O(n log k)
```

Where:

```
k = 10
```

Since `k` is very small compared to `n`, this approach is significantly faster.

Therefore the final implementation uses:

```
top_k()
```

instead of full sorting.

---

# 5. Benchmarking Strategy

### Prompt

```
How can I benchmark a data processing pipeline in Python?

I want to measure:
- execution time
- rows processed
- throughput
- memory usage
```

### Discussion

To evaluate the performance of the solution, I implemented a small benchmark script.

Metrics measured:

- execution time
- rows processed
- throughput (rows/sec)
- memory usage

Example result:

```
Rows processed: 26,843,544
Execution time: 5.002 seconds
Throughput: 5,366,799 rows/sec
Memory usage: 1400 MB
```

This benchmark confirms that the implementation scales well for datasets with tens of millions of rows.

---

# 6. Memory Considerations

### Prompt

```
What techniques help reduce memory usage when processing large CSV files?
```

### Discussion

Key techniques used:

**Lazy Execution**

The dataset is not immediately loaded into memory.

Instead, Polars builds a query plan.

---

**Streaming CSV Scan**

```
scan_csv()
```

This allows chunked processing instead of loading the entire dataset.

---

**Column Projection**

Only required columns are processed.

---

# 7. Documentation Assistance

### Prompt

```
Help me structure a README for a data processing project.

Sections should include:
- overview
- setup
- benchmark
- complexity analysis
- explanation of design choices
```

### Discussion

AI suggestions helped organize the documentation structure.

However:

- benchmark results were generated manually
- complexity analysis was written manually
- architectural decisions were made during development

---

# Development Philosophy

AI assistants were used primarily as a **discussion partner** for exploring ideas.

The development workflow was:

1. Understand the problem requirements
2. Evaluate possible tools (Pandas vs Polars)
3. Design a scalable aggregation pipeline
4. Implement the solution
5. Benchmark the system
6. Document the architecture and complexity

AI helped accelerate exploration, but the final implementation and decisions were made manually.

---

# Summary

This project demonstrates:

- scalable data processing using Polars
- efficient aggregation algorithms
- optimized top-k selection
- benchmarking and performance analysis

AI assistants were used as a **productivity tool**, while the engineering decisions and implementation were handled manually.