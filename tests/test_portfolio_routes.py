import pytest
from fastapi.testclient import TestClient

from api.main import app
from strategies import warren_buffett, buffett_munger, li_lu, duan_yongping


client = TestClient(app)
def test_warren_buffett_portfolio_success(monkeypatch):
    sample = {"strategy": "wb", "total_stocks": 2}
    monkeypatch.setattr(warren_buffett.warren_buffett_strategy, "get_portfolio_summary", lambda: sample)

    resp = client.get("/api/portfolio/warren-buffett")
    assert resp.status_code == 200
    assert resp.json() == sample


def test_warren_buffett_portfolio_failure(monkeypatch):
    def _boom():
        raise RuntimeError("fail")

    monkeypatch.setattr(warren_buffett.warren_buffett_strategy, "get_portfolio_summary", _boom)

    resp = client.get("/api/portfolio/warren-buffett")
    assert resp.status_code == 500
    assert "Failed to fetch portfolio" in resp.text


def test_market_cap_screener_success(monkeypatch):
    stock = {
        "symbol": "AAPL",
        "name": "Apple",
        "market_cap": 1_000,
        "pe_ratio": 20.0,
        "debt_to_equity": 10.0,
        "roe": 0.25,
        "current_price": 150.0,
        "allocation": 4.0,
        "weight": "4.0%",
    }
    sample = {
        "stocks": [stock],
        "total_stocks": 1,
        "last_rebalance": "2024-01-01",
        "next_rebalance": "2025-01-01",
        "days_until_rebalance": 10,
        "strategy": "screener",
        "avg_pe": 20.0,
        "avg_roe": 25.0,
        "allocation_per_stock": 100.0,
    }
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_portfolio_summary", lambda: sample)

    resp = client.get("/api/portfolio/market-cap-screener")
    assert resp.status_code == 200
    assert resp.json() == sample


def test_market_cap_screener_failure(monkeypatch):
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_portfolio_summary", lambda: (_ for _ in ()).throw(RuntimeError("nope")))

    resp = client.get("/api/portfolio/market-cap-screener")
    assert resp.status_code == 500


def test_buffett_munger_redirect(monkeypatch):
    sample = {"strategy": "legacy", "total_stocks": 1}
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_portfolio_summary", lambda: sample)

    resp = client.get("/api/portfolio/buffett-munger")
    assert resp.status_code == 200
    assert resp.json() == sample


def test_buffett_munger_top_picks(monkeypatch):
    picks = [
        {
            "symbol": "AAPL",
            "name": "Apple",
            "market_cap": 1_000,
            "pe_ratio": 20.0,
            "debt_to_equity": 10.0,
            "roe": 0.25,
            "current_price": 150.0,
            "allocation": 4.0,
            "weight": "4.0%",
        }
    ]
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_top_picks", lambda count: picks)

    resp = client.get("/api/portfolio/buffett-munger/picks?count=1")
    assert resp.status_code == 200
    assert resp.json() == picks


def test_buffett_munger_top_picks_failure(monkeypatch):
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_top_picks", lambda count: (_ for _ in ()).throw(RuntimeError("oops")))

    resp = client.get("/api/portfolio/buffett-munger/picks?count=2")
    assert resp.status_code == 500


def test_buffett_munger_redirect_failure(monkeypatch):
    monkeypatch.setattr(buffett_munger.buffett_munger_strategy, "get_portfolio_summary", lambda: (_ for _ in ()).throw(RuntimeError("nope")))

    resp = client.get("/api/portfolio/buffett-munger")
    assert resp.status_code == 500


def test_li_lu_portfolio_failure(monkeypatch):
    monkeypatch.setattr(li_lu.li_lu_strategy, "get_portfolio_summary", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    resp = client.get("/api/portfolio/li-lu")
    assert resp.status_code == 500


def test_duan_yongping_portfolio_failure(monkeypatch):
    monkeypatch.setattr(duan_yongping.duan_yongping_strategy, "get_portfolio_summary", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    resp = client.get("/api/portfolio/duan-yongping")
    assert resp.status_code == 500


def test_li_lu_portfolio_success(monkeypatch):
    sample = {"strategy": "li lu", "total_stocks": 2}
    monkeypatch.setattr(li_lu.li_lu_strategy, "get_portfolio_summary", lambda: sample)

    resp = client.get("/api/portfolio/li-lu")
    assert resp.status_code == 200
    assert resp.json() == sample


def test_duan_yongping_portfolio_success(monkeypatch):
    sample = {"strategy": "duan", "total_stocks": 3}
    monkeypatch.setattr(duan_yongping.duan_yongping_strategy, "get_portfolio_summary", lambda: sample)

    resp = client.get("/api/portfolio/duan-yongping")
    assert resp.status_code == 200
    assert resp.json() == sample
