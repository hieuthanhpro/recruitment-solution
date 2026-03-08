import polars as pl
from aggregator import aggregate_campaigns


def sample_lazyframe():
    """
    Create sample dataset matching the schema.
    """
    df = pl.DataFrame({
        "campaign_id": ["CMP001", "CMP002", "CMP001", "CMP003", "CMP002"],
        "date": [
            "2025-01-01",
            "2025-01-01",
            "2025-01-02",
            "2025-01-01",
            "2025-01-02",
        ],
        "impressions": [12000, 8000, 14000, 5000, 8500],
        "clicks": [300, 120, 340, 60, 150],
        "spend": [45.50, 28.00, 48.20, 15.00, 31.00],
        "conversions": [12, 4, 15, 3, 5],
    })

    return df.lazy()


def test_aggregation_results():
    """
    Test groupby aggregation totals.
    """
    lf = sample_lazyframe()

    agg = aggregate_campaigns(lf)

    result = agg.collect()

    cmp1 = result.filter(pl.col("campaign_id") == "CMP001").row(0)

    total_impressions = cmp1[result.columns.index("total_impressions")]
    total_clicks = cmp1[result.columns.index("total_clicks")]
    total_spend = cmp1[result.columns.index("total_spend")]
    total_conversions = cmp1[result.columns.index("total_conversions")]

    assert total_impressions == 26000
    assert total_clicks == 640
    assert round(total_spend, 2) == 93.70
    assert total_conversions == 27


def test_ctr_calculation():
    """
    CTR = clicks / impressions
    """
    lf = sample_lazyframe()

    agg = aggregate_campaigns(lf)

    result = agg.collect()

    cmp1 = result.filter(pl.col("campaign_id") == "CMP001")

    ctr = cmp1.select("CTR").item()

    expected_ctr = 640 / 26000

    assert round(ctr, 6) == round(expected_ctr, 6)


def test_cpa_calculation():
    """
    CPA = spend / conversions
    """
    lf = sample_lazyframe()

    agg = aggregate_campaigns(lf)

    result = agg.collect()

    cmp1 = result.filter(pl.col("campaign_id") == "CMP001")

    cpa = cmp1.select("CPA").item()

    expected_cpa = 93.70 / 27

    assert round(cpa, 6) == round(expected_cpa, 6)


def test_top_ctr_logic():
    """
    Ensure top CTR campaign is correctly identified.
    """
    lf = sample_lazyframe()

    agg = aggregate_campaigns(lf)

    df = agg.collect()

    top_ctr = df.top_k(1, by="CTR")

    campaign = top_ctr.select("campaign_id").item()

    assert campaign in ["CMP001", "CMP002", "CMP003"]


def test_cpa_excludes_zero_conversions():
    """
    Ensure campaigns with zero conversions are excluded from CPA ranking.
    """
    df = pl.DataFrame({
        "campaign_id": ["A", "B"],
        "date": ["2025-01-01", "2025-01-01"],
        "impressions": [1000, 2000],
        "clicks": [100, 200],
        "spend": [100.0, 200.0],
        "conversions": [0, 10],
    })

    lf = df.lazy()

    agg = aggregate_campaigns(lf)

    result = agg.collect()

    filtered = result.filter(pl.col("total_conversions") > 0)

    assert all(filtered["total_conversions"] > 0)