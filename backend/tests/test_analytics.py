import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.database.models import Statement

client = TestClient(app)

def test_analytics_running_balance():
    res = client.get("/api/v1/analytics/running-balance")
    assert res.status_code == 200
    data = res.json()
    assert "points" in data
    assert "currency" in data
    assert isinstance(data["points"], list)
    if len(data["points"]) > 0:
        p = data["points"][0]
        assert "sequence" in p
        assert "balance" in p
        assert "debit" in p
        assert "credit" in p

def test_analytics_activity_heatmap():
    res = client.get("/api/v1/analytics/activity-heatmap")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        d = data[0]
        assert "date" in d
        assert "count" in d
        assert "total_volume" in d

def test_analytics_merchant_concentration():
    res = client.get("/api/v1/analytics/merchants?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "total_tracked_spending" in data
    assert "top_merchants" in data
    assert isinstance(data["top_merchants"], list)
    if len(data["top_merchants"]) > 0:
        m = data["top_merchants"][0]
        assert "merchant" in m
        assert "amount" in m
        assert "percentage" in m
        assert "cumulative_percentage" in m

def test_analytics_payment_channels():
    res = client.get("/api/v1/analytics/channels")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        c = data[0]
        assert "channel" in c
        assert "count" in c
        assert "total_amount" in c

def test_analytics_classification_deep():
    res = client.get("/api/v1/analytics/classification-deep")
    assert res.status_code == 200
    data = res.json()
    assert "total_transactions" in data
    assert "rule_based_count" in data
    assert "ml_based_count" in data
    assert "score_distribution" in data
    assert isinstance(data["score_distribution"], list)

def test_analytics_extraction_completeness():
    res = client.get("/api/v1/analytics/completeness")
    assert res.status_code == 200
    data = res.json()
    assert "total_records" in data
    assert "date_completeness_pct" in data
    assert "overall_completeness_pct" in data
    assert 0 <= data["overall_completeness_pct"] <= 100

def test_analytics_multi_statement():
    res = client.get("/api/v1/analytics/multi-statement")
    assert res.status_code == 200
    data = res.json()
    assert "by_currency" in data
    assert isinstance(data["by_currency"], dict)
    for curr, stmts in data["by_currency"].items():
        assert isinstance(curr, str)
        assert isinstance(stmts, list)

def test_analytics_category_trends():
    res = client.get("/api/v1/analytics/category-trends")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
