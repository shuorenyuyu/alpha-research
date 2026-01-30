import math
from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import pytest

from market.fetchers.yfinance_fetcher import MarketDataFetcher
from market.fetchers import futu_fetcher
from strategies.buffett_munger import BuffettMungerStrategy
from strategies.warren_buffett import WarrenBuffettStrategy
from strategies.li_lu import LiLuStrategy
from strategies.duan_yongping import DuanYongpingStrategy


def test_buffett_munger_strategy_selection(monkeypatch):
    strategy = BuffettMungerStrategy()
    strategy.UNIVERSE = ["GOOD", "BAD"]

    good_metrics = {
        "symbol": "GOOD",
        "market_cap": 20_000_000_000,
        "pe_ratio": 15,
        "debt_to_equity": 10,
        "roe": 0.2,
        "profit_margin": 0.2,
        "current_price": 120,
        "price_to_book": 2,
    }

    def fake_metrics(symbol: str):
        return good_metrics if symbol == "GOOD" else {"symbol": symbol, "market_cap": 1}

    monkeypatch.setattr(strategy, "_get_financial_metrics", fake_metrics)

    picks = strategy.get_top_picks(count=1)
    assert len(picks) == 1
    summary = strategy.get_portfolio_summary()
    assert summary["total_stocks"] == 1
    assert summary["allocation_per_stock"] == 100.0


def test_buffett_munger_strategy_no_qualified(monkeypatch):
    strategy = BuffettMungerStrategy()
    strategy.UNIVERSE = ["NONE"]
    monkeypatch.setattr(strategy, "_get_financial_metrics", lambda symbol: {"symbol": symbol, "market_cap": 0})
    monkeypatch.setattr(strategy, "_meets_quality_criteria", lambda metrics: False)

    picks = strategy.get_top_picks(count=5)
    assert picks == []
    summary = strategy.get_portfolio_summary()
    assert summary["total_stocks"] == 0
    assert summary["allocation_per_stock"] == 0


def _positive_price_for(symbol: str, holdings):
    for h in holdings:
        if h["symbol"] == symbol:
            return h["buy_price"] * 2
    return 0


def test_warren_buffett_strategy_summary(monkeypatch):
    strategy = WarrenBuffettStrategy()
    monkeypatch.setattr(strategy, "_get_current_price", lambda symbol: _positive_price_for(symbol, strategy.KNOWN_HOLDINGS))

    summary = strategy.get_portfolio_summary()
    assert summary["total_stocks"] == len(strategy.KNOWN_HOLDINGS)
    assert summary["best_performer"] is not None
    assert summary["weighted_avg_return"] >= 0


def test_li_lu_strategy_summary(monkeypatch):
    strategy = LiLuStrategy()
    monkeypatch.setattr(strategy, "_get_current_price", lambda symbol: _positive_price_for(symbol, strategy.KNOWN_HOLDINGS))

    summary = strategy.get_portfolio_summary()
    assert summary["total_stocks"] == len(strategy.KNOWN_HOLDINGS)
    assert summary["weighted_avg_return"] >= 0
    assert summary["winners"] == len(strategy.KNOWN_HOLDINGS)


def test_duan_yongping_strategy_summary(monkeypatch):
    strategy = DuanYongpingStrategy()
    monkeypatch.setattr(strategy, "_get_current_price", lambda symbol: _positive_price_for(symbol, strategy.KNOWN_HOLDINGS))

    summary = strategy.get_portfolio_summary()
    assert summary["total_stocks"] == len(strategy.KNOWN_HOLDINGS)
    assert summary["weighted_avg_return"] >= 0
    assert summary["best_performer"] is not None


def test_compute_cagr_edge_cases(monkeypatch):
    fetcher = MarketDataFetcher()
    assert fetcher._compute_cagr([1]) is None
    assert fetcher._compute_cagr([0, 2]) is None

    monkeypatch.setattr(math, "pow", lambda a, b: (_ for _ in ()).throw(RuntimeError("boom")))
    assert fetcher._compute_cagr([1, 2]) is None


class _StubTicker:
    def __init__(self, info=None, income=None, history_df=None):
        self.info = info or {}
        self._income = income
        self._history_df = history_df

    def get_income_stmt(self, freq="annual"):
        if isinstance(self._income, Exception):
            raise self._income
        return self._income

    @property
    def income_stmt(self):
        return self._income

    def history(self, period="1d", interval=None):
        return self._history_df if self._history_df is not None else pd.DataFrame()


def test_extract_ebitda_series_paths(monkeypatch):
    fetcher = MarketDataFetcher()

    empty_ticker = _StubTicker(income=pd.DataFrame())
    assert fetcher._extract_ebitda_series(empty_ticker) == []

    income = pd.DataFrame({"2020": {"EBITDA": 100.0}, "2021": {"EBITDA": 120.0}})
    ticker_with_income = _StubTicker(income=income)
    series = fetcher._extract_ebitda_series(ticker_with_income)
    assert series == [100.0, 120.0]

    class _ErrorTicker(_StubTicker):
        def get_income_stmt(self, freq="annual"):
            raise RuntimeError("fail")

    error_ticker = _ErrorTicker(income=None)
    assert fetcher._extract_ebitda_series(error_ticker) == []


def test_get_metrics_missing_price(monkeypatch):
    fetcher = MarketDataFetcher()
    monkeypatch.setattr("market.fetchers.yfinance_fetcher.yf.Ticker", lambda symbol: _StubTicker(info={}))
    assert fetcher.get_metrics("TEST") is None


def test_get_metrics_success(monkeypatch):
    fetcher = MarketDataFetcher()
    info = {
        "currentPrice": 10.0,
        "overallRisk": 1,
        "marketCap": 100,
        "trailingPE": 5,
        "pegRatio": 1.5,
        "priceToBook": 2.0,
        "dividendYield": 0.01,
        "longName": "Sample Co",
    }
    income = pd.DataFrame({
        "2020": {"EBITDA": 100.0},
        "2021": {"EBITDA": 150.0},
        "2022": {"EBITDA": 200.0},
    })
    history_df = pd.DataFrame({"Close": [10]}, index=[datetime.now()])
    ticker = _StubTicker(info=info, income=income, history_df=history_df)
    monkeypatch.setattr("market.fetchers.yfinance_fetcher.yf.Ticker", lambda symbol: ticker)

    metrics = fetcher.get_metrics("GOOD")
    assert metrics is not None
    assert metrics["ebitdaGrowth1Y"] is not None


def test_buffett_munger_financial_metrics(monkeypatch):
    strategy = BuffettMungerStrategy()

    class DummyTicker:
        def __init__(self):
            self.info = {
                "longName": "Sample",
                "marketCap": 20_000_000_000,
                "trailingPE": 20,
                "debtToEquity": 10,
                "returnOnEquity": 0.2,
                "revenueGrowth": 0.2,
                "profitMargins": 0.15,
                "currentPrice": 150,
                "priceToBook": 2,
                "dividendYield": 0.01,
                "beta": 1.0,
            }

        def history(self, period="5y"):
            return pd.DataFrame({"Close": [1, 2]}, index=[0, 1])

    monkeypatch.setattr("strategies.buffett_munger.yf.Ticker", lambda symbol: DummyTicker())
    metrics = strategy._get_financial_metrics("AAPL")
    assert metrics is not None
    assert strategy._meets_quality_criteria(metrics) is True

    # Empty history triggers None
    class EmptyTicker(DummyTicker):
        def history(self, period="5y"):
            return pd.DataFrame()

    monkeypatch.setattr("strategies.buffett_munger.yf.Ticker", lambda symbol: EmptyTicker())
    assert strategy._get_financial_metrics("AAPL") is None


def test_duan_and_li_lu_return_edges(monkeypatch):
    duan = DuanYongpingStrategy()
    assert duan._calculate_returns(0, 10) == {"gain_loss": 0.0, "return_pct": 0.0, "multiple": 0.0}

    li_lu = LiLuStrategy()
    # Li Lu doesn't include 'multiple' field in returns
    assert li_lu._calculate_returns(0, 10) == {"gain_loss": 0.0, "return_pct": 0.0}


def test_get_current_price_error_paths(monkeypatch):
    monkeypatch.setattr("strategies.duan_yongping.yf.Ticker", lambda symbol: (_ for _ in ()).throw(RuntimeError("fail")))
    duan = DuanYongpingStrategy()
    assert duan._get_current_price("AAPL") == 0.0

    class FailingHistory:
        def __init__(self):
            self.info = {}

        def history(self, period="1d"):
            return pd.DataFrame()

    monkeypatch.setattr("strategies.li_lu.yf.Ticker", lambda symbol: FailingHistory())
    li_lu = LiLuStrategy()
    assert li_lu._get_current_price("META") == 0.0

    monkeypatch.setattr("strategies.warren_buffett.yf.Ticker", lambda symbol: FailingHistory())
    wb = WarrenBuffettStrategy()
    assert wb._get_current_price("AAPL") == 0.0


def test_get_metrics_exception(monkeypatch):
    fetcher = MarketDataFetcher()

    class Boom:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("fail")

    monkeypatch.setattr("market.fetchers.yfinance_fetcher.yf.Ticker", Boom)
    assert fetcher.get_metrics("ERR") is None


def test_futu_fetcher_close_connections(monkeypatch):
    fetcher = futu_fetcher.FutuFetcher()

    class DummyCtx:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fetcher.quote_ctx = DummyCtx()
    fetcher.trade_ctx = DummyCtx()
    fetcher.close()

    assert fetcher.quote_ctx is None
    assert fetcher.trade_ctx is None


def test_futu_fetcher_quote_error(monkeypatch):
    fetcher = futu_fetcher.FutuFetcher()

    class DummyQuote:
        def get_market_snapshot(self, symbols):
            return 1, pd.DataFrame()

    monkeypatch.setattr(fetcher, "_ensure_quote_connection", lambda: DummyQuote())
    assert fetcher.get_quote("HK.00001") is None


def test_futu_fetcher_account_info_errors(monkeypatch):
    fetcher = futu_fetcher.FutuFetcher()

    class DummyTrade:
        def accinfo_query(self, trd_env=None):
            return 1, pd.DataFrame()

        def position_list_query(self, trd_env=None):
            return 1, pd.DataFrame()

    monkeypatch.setattr(fetcher, "_ensure_trade_connection", lambda: DummyTrade())
    assert fetcher.get_account_info() is None
    assert fetcher.get_account_positions() == []


def test_buffett_munger_quality_filters(monkeypatch):
    strategy = BuffettMungerStrategy()
    strategy.UNIVERSE = ['GOOD', 'TINY', 'NONE']

    def fake_metrics(symbol):
        if symbol == 'GOOD':
            return {
                'symbol': 'GOOD',
                'name': 'Good Co',
                'market_cap': 20_000_000_000,
                'pe_ratio': 10,
                'debt_to_equity': 20,
                'roe': 0.2,
                'revenue_growth': 0.15,
                'profit_margin': 0.2,
                'current_price': 50,
                'price_to_book': 3,
                'dividend_yield': 0.01,
                'beta': 1.0,
            }
        if symbol == 'TINY':
            return {'symbol': 'TINY', 'market_cap': 500_000_000}
        return None

    monkeypatch.setattr(strategy, "_get_financial_metrics", fake_metrics)
    picks = strategy.get_top_picks(count=2)

    assert len(picks) == 1
    assert picks[0]['symbol'] == 'GOOD'
    assert strategy._meets_quality_criteria(None) is False
    assert strategy._meets_quality_criteria({'market_cap': 1_000_000_000}) is False


def test_duan_li_lu_and_wb_portfolios(monkeypatch):
    class StubTicker:
        def __init__(self, close):
            self.info = {}
            self._close = close

        def history(self, period='1d'):
            return pd.DataFrame({'Close': [self._close]})

    monkeypatch.setattr('strategies.duan_yongping.yf.Ticker', lambda symbol: StubTicker(200))
    duan = DuanYongpingStrategy()
    duan_summary = duan.get_portfolio_summary()
    assert duan_summary['total_stocks'] == len(duan.KNOWN_HOLDINGS)

    monkeypatch.setattr('strategies.li_lu.yf.Ticker', lambda symbol: StubTicker(120))
    li_lu = LiLuStrategy()
    li_lu_returns = li_lu._calculate_returns(50, 60)
    assert li_lu_returns['gain_loss'] == 10.0
    li_lu_summary = li_lu.get_portfolio_summary()
    assert li_lu_summary['total_stocks'] == len(li_lu.KNOWN_HOLDINGS)

    monkeypatch.setattr('strategies.warren_buffett.yf.Ticker', lambda symbol: StubTicker(150))
    wb = WarrenBuffettStrategy()
    wb_summary = wb.get_portfolio_summary()
    assert wb_summary['total_stocks'] == len(wb.KNOWN_HOLDINGS)
