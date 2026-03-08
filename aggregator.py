import argparse
from email import parser
import os

import polars as pl

INPUT_FILE = "ad_data.csv"


SCHEMA = {
    "campaign_id": pl.Utf8,
    "date": pl.Utf8,
    "impressions": pl.Int64,
    "clicks": pl.Int64,
    "spend": pl.Float64,
    "conversions": pl.Int64,
}


def load_data(input_file: str) -> pl.LazyFrame:
    """
    Load advertising dataset as a Polars LazyFrame.

    Lazy execution allows query optimization and reduces memory usage,
    which is useful for large datasets.

    Args:
        input_file (str): Path to input CSV file.

    Returns:
        pl.LazyFrame: Lazy representation of dataset.
    """
    return pl.scan_csv(
        input_file,
        schema=SCHEMA,
        low_memory=True
    )

def aggregate_campaigns(lf: pl.LazyFrame) -> pl.LazyFrame:
    """
    Aggregate campaign-level metrics.
    For each campaign_id we compute:
    - total impressions
    - total clicks
    - total spend
    - total conversions
    - CTR (Click-Through Rate)
    - CPA (Cost Per Acquisition)
    Args:
        lf (pl.LazyFrame): Raw campaign dataset.
    Returns:
        pl.LazyFrame: Aggregated campaign metrics.
    """
    return (
        lf.group_by("campaign_id")
        .agg(
            [
                pl.sum("impressions").alias("total_impressions"),
                pl.sum("clicks").alias("total_clicks"),
                pl.sum("spend").alias("total_spend"),
                pl.sum("conversions").alias("total_conversions"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("total_impressions") > 0)
                .then(pl.col("total_clicks") / pl.col("total_impressions"))
                .otherwise(None)
                .alias("CTR"),

                pl.when(pl.col("total_conversions") > 0)
                .then(pl.col("total_spend") / pl.col("total_conversions"))
                .otherwise(None)
                .alias("CPA"),
            ]
        )
    )


def compute_top_ctr(agg: pl.LazyFrame,k: int) -> pl.DataFrame:
    """
    Compute top campaigns ranked by highest CTR.
    Args:
        agg (pl.LazyFrame): Aggregated campaign metrics.
        k (int): Number of top campaigns to return.
    Returns:
        pl.DataFrame: Top campaigns by CTR.
    """
    return (
        agg
        .top_k(k, by="CTR")
        .with_columns(
            [
                pl.col("CTR").round(4),
                pl.col("CPA").round(2)
            ]
        )
        .collect(streaming=True)
    )


def compute_top_cpa(agg: pl.LazyFrame, k: int) -> pl.DataFrame:
    """
    Compute campaigns with the lowest CPA.
    Only campaigns with conversions are considered.
    Args:
        agg (pl.LazyFrame): Aggregated campaign metrics.
        k (int): Number of top campaigns to return.
    Returns:
        pl.DataFrame: Campaigns ranked by lowest CPA.
    """
    return (
        agg
        .filter(pl.col("total_conversions") > 0)
        .top_k(k, by="CPA", descending=False)
        .with_columns(
            [
                pl.col("CTR").round(4),
                pl.col("CPA").round(2)
            ]
        )
        .collect(streaming=True)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    TOP_K = 10
    lf = load_data(args.input)
    agg = aggregate_campaigns(lf)

    top_ctr = compute_top_ctr(agg, TOP_K)
    top_ctr.write_csv(f"{args.output}/top10_ctr.csv")

    top_cpa = compute_top_cpa(agg, TOP_K)
    top_cpa.write_csv(f"{args.output}/top10_cpa.csv")


if __name__ == "__main__":
    main()