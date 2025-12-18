"""
Test suite for API routes - market.py
"""
import pytest
from unittest.mock import patch, Mock
import json


class TestMarketRoutes:
    """Test cases for market data API routes"""
    
    def test_get_quotes_success(self, client, mock_yfinance_ticker):
        """Test successful quote retrieval"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            response = client.get('/api/market/quotes?symbols=AAPL,MSFT')
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['symbol'] == 'AAPL'
            assert data[0]['price'] == 150.00
            assert data[0]['change'] == 2.00
    
    def test_get_quotes_empty_symbols(self, client):
        """Test quotes endpoint with no symbols"""
        response = client.get('/api/market/quotes')
        
        assert response.status_code == 422  # FastAPI validation error
        assert 'detail' in response.json()
    
    def test_get_quotes_invalid_symbol(self, client):
        """Test quotes with invalid symbol"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {}
            response = client.get('/api/market/quotes?symbols=INVALID')
            
            assert response.status_code == 404  # No valid symbols
            assert 'detail' in response.json()
    
    def test_get_historical_data_success(self, client, mock_yfinance_ticker):
        """Test successful historical data retrieval"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            response = client.get('/api/market/history/AAPL?period=1mo&interval=1d')
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 30
            assert data[0]['open'] == 150.0
    
    def test_get_historical_data_default_params(self, client, mock_yfinance_ticker):
        """Test historical data with default parameters"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            response = client.get('/api/market/history/AAPL')
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    def test_get_historical_data_not_found(self, client):
        """Test historical data for non-existent symbol"""
        with patch('yfinance.Ticker') as mock_ticker:
            import pandas as pd
            mock_ticker.return_value.history.return_value = pd.DataFrame()
            
            response = client.get('/api/market/history/INVALID')
            
            assert response.status_code == 404
            assert 'detail' in response.json()
    
    def test_get_trending_stocks(self, client, mock_yfinance_ticker):
        """Test trending stocks endpoint"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            response = client.get('/api/market/trending')
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

    def test_get_metrics_success(self, client):
        """Test metrics endpoint success"""
        sample_metrics = {
            'symbol': 'AAPL',
            'company': 'Apple Inc.',
            'currentPrice': 190.5,
            'predictabilityRank': 4,
            'marketCap': 2_000_000_000,
            'ebitdaGrowth10Y': 12.3,
            'ebitdaGrowth5Y': 11.1,
            'ebitdaGrowth1Y': 8.9,
            'peRatio': 30.1,
            'pegRatio': 2.0,
            'pbRatio': 8.5,
            'dividendYield': 0.6
        }
        with patch('api.routes.market.market_fetcher.get_metrics', return_value=sample_metrics):
            response = client.get('/api/market/metrics/AAPL')

        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'AAPL'
        assert data['currentPrice'] == 190.5
        assert data['peRatio'] == 30.1
        assert data['dividendYield'] == 0.6

    def test_get_metrics_not_found(self, client):
        """Test metrics endpoint when data missing"""
        with patch('api.routes.market.market_fetcher.get_metrics', return_value=None):
            response = client.get('/api/market/metrics/INVALID')

        assert response.status_code == 404
        body = response.json()
        assert 'detail' in body
