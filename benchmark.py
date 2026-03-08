import polars as pl
import time
import psutil
import os

from aggregator import aggregate_campaigns


DATA_FILE = "ad_data.csv"
LOG_FILE = "benchmark.log"


def run_benchmark():

    process = psutil.Process(os.getpid())

    # memory trước khi chạy
    mem_before = process.memory_info().rss / 1024 / 1024

    start = time.perf_counter()

    # đọc dữ liệu lazy
    lf = pl.scan_csv(DATA_FILE)

    # chạy aggregation
    result = aggregate_campaigns(lf).collect()

    end = time.perf_counter()

    # memory sau khi chạy
    mem_after = process.memory_info().rss / 1024 / 1024

    elapsed = end - start

    # đếm rows
    rows = pl.scan_csv(DATA_FILE).select(pl.len()).collect().item()

    throughput = rows / elapsed

    log = f"""
===== BENCHMARK RESULT =====
Dataset file: {DATA_FILE}
Rows processed: {rows}
Execution time: {elapsed:.3f} seconds
Throughput: {throughput:,.0f} rows/sec
Memory usage: {mem_after - mem_before:.2f} MB
============================
"""

    print(log)

    # ghi log ra file
    with open(LOG_FILE, "a") as f:
        f.write(log)

    return result


if __name__ == "__main__":
    run_benchmark()