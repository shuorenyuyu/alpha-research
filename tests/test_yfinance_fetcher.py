"""
Test suite for market fetchers - yfinance_fetcher.py
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime
import pandas as pd

from market.fetchers.yfinance_fetcher import MarketDataFetcher, market_fetcher


class TestMarketDataFetcher:
    """Test cases for MarketDataFetcher class"""
    
    def test_init(self):
        """Test fetcher initialization"""
        fetcher = MarketDataFetcher()
        
        assert fetcher.cache == {}
        assert fetcher.cache_duration == 3600
    
    def test_get_quote_success(self, mock_yfinance_ticker):
        """Test successful quote retrieval"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('AAPL')
            
            assert result is not None
            assert result['symbol'] == 'AAPL'
            assert result['name'] == 'Test Company Inc.'
            assert result['price'] == 150.00
            assert result['change'] == 2.00
            assert result['changePercent'] == 1.35
            assert result['volume'] == 1000000
            assert 'timestamp' in result
    
    def test_get_quote_with_only_regular_market_price(self):
        """Test quote when only regularMarketPrice is available"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'regularMarketPrice': 200.00,
            'previousClose': 198.00,
            'longName': 'Another Company',
            'volume': 500000,
            'marketCap': 500000000,
            'dayHigh': 202.00,
            'dayLow': 197.00,
            'open': 199.00,
        }
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('MSFT')
            
            assert result is not None
            assert result['price'] == 200.00
    
    def test_get_quote_zero_price(self):
        """Test quote with zero price returns None"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'currentPrice': 0,
            'previousClose': 100.00
        }
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('INVALID')
            
            assert result is None
    
    def test_get_quote_exception(self):
        """Test quote retrieval with exception"""
        with patch('yfinance.Ticker', side_effect=Exception('API Error')):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('ERROR')
            
            assert result is None
    
    def test_get_quote_missing_fields(self):
        """Test quote with missing optional fields"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'currentPrice': 100.00,
            'previousClose': 99.00
        }
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('TEST')
            
            assert result is not None
            assert result['volume'] == 0
            assert result['marketCap'] == 0
    
    def test_get_quotes_multiple_symbols(self, mock_yfinance_ticker):
        """Test retrieving multiple quotes"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            results = fetcher.get_quotes(['AAPL', 'MSFT', 'GOOGL'])
            
            assert len(results) == 3
            assert all('symbol' in quote for quote in results)
    
    def test_get_quotes_with_invalid_symbols(self):
        """Test quotes with some invalid symbols"""
        def mock_ticker_func(symbol):
            if symbol == 'INVALID':
                mock = Mock()
                mock.info = {}
                return mock
            return Mock(info={'currentPrice': 100.0, 'previousClose': 99.0, 'longName': symbol})
        
        with patch('yfinance.Ticker', side_effect=mock_ticker_func):
            fetcher = MarketDataFetcher()
            results = fetcher.get_quotes(['AAPL', 'INVALID', 'MSFT'])
            
            assert len(results) == 2
    
    def test_get_quotes_empty_list(self):
        """Test quotes with empty symbol list"""
        fetcher = MarketDataFetcher()
        results = fetcher.get_quotes([])
        
        assert results == []
    
    def test_get_historical_data_success(self, mock_yfinance_ticker):
        """Test successful historical data retrieval"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            results = fetcher.get_historical_data('AAPL', period='1mo', interval='1d')
            
            assert results is not None
            assert len(results) == 30
            assert all('date' in item for item in results)
            assert all('open' in item for item in results)
            assert all('close' in item for item in results)
            assert results[0]['open'] == 150.0
    
    def test_get_historical_data_default_params(self, mock_yfinance_ticker):
        """Test historical data with default parameters"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            results = fetcher.get_historical_data('AAPL')
            
            assert results is not None
            assert len(results) > 0
    
    def test_get_historical_data_empty(self):
        """Test historical data when DataFrame is empty"""
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            results = fetcher.get_historical_data('INVALID')
            
            assert results is None
    
    def test_get_historical_data_exception(self):
        """Test historical data with exception"""
        with patch('yfinance.Ticker', side_effect=Exception('API Error')):
            fetcher = MarketDataFetcher()
            results = fetcher.get_historical_data('ERROR')
            
            assert results is None
    
    def test_get_historical_data_different_intervals(self, mock_yfinance_ticker):
        """Test historical data with different intervals"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            
            for interval in ['1h', '1d', '1wk']:
                results = fetcher.get_historical_data('AAPL', period='1mo', interval=interval)
                assert results is not None
    
    def test_get_trending_stocks(self, mock_yfinance_ticker):
        """Test trending stocks retrieval"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            fetcher = MarketDataFetcher()
            results = fetcher.get_trending_stocks()
            
            assert len(results) == 8  # Default trending symbols
            assert all('symbol' in quote for quote in results)
    
    def test_global_instance_exists(self):
        """Test that global market_fetcher instance exists"""
        assert market_fetcher is not None
        assert isinstance(market_fetcher, MarketDataFetcher)
    
    def test_change_percent_calculation(self):
        """Test change percent calculation"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'currentPrice': 110.00,
            'previousClose': 100.00,
            'longName': 'Test'
        }
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('TEST')
            
            assert result['change'] == 10.00
            assert result['changePercent'] == 10.00
    
    def test_change_percent_with_zero_previous_close(self):
        """Test change percent when previous close is zero"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'currentPrice': 100.00,
            'previousClose': 0,
            'longName': 'Test'
        }
        
        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            result = fetcher.get_quote('TEST')
            
            assert result['changePercent'] == 0.00

    def test_get_metrics_success(self):
        """Test retrieving metrics with EBITDA growth and ratios"""
        income_df = pd.DataFrame({
            '2020': [1_000_000_000],
            '2021': [1_100_000_000],
            '2022': [1_320_000_000],
        }, index=['EBITDA'])
        mock_ticker = Mock()
        mock_ticker.info = {
            'currentPrice': 50.5,
            'longName': 'Example Corp',
            'marketCap': 1_500_000_000,
            'trailingPE': 10.1,
            'pegRatio': 1.2,
            'priceToBook': 2.5,
            'dividendYield': 0.015,
            'overallRisk': 3
        }
        mock_ticker.get_income_stmt = Mock(return_value=income_df)

        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            metrics = fetcher.get_metrics('exm')

        assert metrics['symbol'] == 'EXM'
        assert metrics['company'] == 'Example Corp'
        assert metrics['currentPrice'] == 50.5
        assert metrics['marketCap'] == 1_500_000_000
        assert metrics['peRatio'] == 10.1
        assert metrics['pegRatio'] == 1.2
        assert metrics['pbRatio'] == 2.5
        assert metrics['dividendYield'] == 1.5
        # CAGR using 2020->2022 values
        assert metrics['ebitdaGrowth1Y'] == 20.0
        assert metrics['ebitdaGrowth5Y'] is not None

    def test_get_metrics_insufficient_data(self):
        """Test metrics returns None when price missing"""
        mock_ticker = Mock()
        mock_ticker.info = {}
        mock_ticker.get_income_stmt = Mock(return_value=pd.DataFrame())

        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            metrics = fetcher.get_metrics('bad')

        assert metrics is None

    def test_extract_ebitda_skips_invalid_entries(self):
        """Ensure EBITDA parsing skips non-numeric and NaN values"""
        df = pd.DataFrame({
            '2020': ['oops'],
            '2021': [float('nan')],
            '2022': [500.0],
        }, index=['EBITDA'])

        mock_ticker = Mock()
        mock_ticker.get_income_stmt = Mock(return_value=df)

        with patch('yfinance.Ticker', return_value=mock_ticker):
            fetcher = MarketDataFetcher()
            values = fetcher._extract_ebitda_series(mock_ticker)

        assert values == [500.0]
