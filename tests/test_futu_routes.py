"""
Comprehensive tests for Futu API routes

Testing strategy:
- Mock all Futu API connections to avoid real trading
- Test both successful and error scenarios
- Achieve 99%+ coverage for futu.py and futu_fetcher.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from api.main import app


class TestFutuRoutes:
    """Test Futu API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_fetcher(self):
        """Mock Futu fetcher with common responses"""
        with patch('api.routes.futu.futu_fetcher') as mock:
            yield mock
    
    def test_get_positions_success(self, client, mock_fetcher):
        """Test successful position retrieval"""
        mock_fetcher.get_account_positions.return_value = [
            {
                'symbol': '00700',
                'name': '腾讯控股',
                'quantity': 100,
                'canSellQty': 100,
                'costPrice': 350.0,
                'currentPrice': 360.0,
                'marketValue': 36000.0,
                'profitLoss': 1000.0,
                'profitLossPercent': 2.857,
                'currency': 'HKD',
                'updateTime': '2023-12-11 10:30:00'
            }
        ]
        
        response = client.get('/api/futu/positions')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['symbol'] == '00700'
    
    def test_get_positions_simulate_env(self, client, mock_fetcher):
        """Test positions with simulated environment"""
        mock_fetcher.get_account_positions.return_value = []
        
        response = client.get('/api/futu/positions?env=simulate')
        
        assert response.status_code == 200
        mock_fetcher.get_account_positions.assert_called_once()
    
    def test_get_positions_real_env(self, client, mock_fetcher):
        """Test positions with real trading environment"""
        mock_fetcher.get_account_positions.return_value = []
        
        response = client.get('/api/futu/positions?env=real')
        
        assert response.status_code == 200
    
    def test_get_positions_error(self, client, mock_fetcher):
        """Test position retrieval error handling"""
        mock_fetcher.get_account_positions.side_effect = Exception("Connection failed")
        
        response = client.get('/api/futu/positions')
        
        assert response.status_code == 500
        assert 'detail' in response.json()
    
    def test_get_account_info_success(self, client, mock_fetcher):
        """Test successful account info retrieval"""
        mock_fetcher.get_account_info.return_value = {
            'totalAssets': 100000.0,
            'cash': 50000.0,
            'marketValue': 50000.0,
            'profitLoss': 5000.0,
            'profitLossPercent': 5.26,
            'currency': 'HKD',
            'updateTime': '2023-12-11 10:30:00'
        }
        
        response = client.get('/api/futu/account')
        
        assert response.status_code == 200
        data = response.json()
        assert data['totalAssets'] == 100000.0
        assert data['currency'] == 'HKD'
    
    def test_get_account_info_error(self, client, mock_fetcher):
        """Test account info error handling"""
        mock_fetcher.get_account_info.side_effect = RuntimeError("API error")
        
        response = client.get('/api/futu/account')
        
        assert response.status_code == 500
    
    def test_get_market_quote_success(self, client, mock_fetcher):
        """Test market quote retrieval"""
        mock_fetcher.get_quote.return_value = {
            'symbol': 'HK.00700',
            'name': '腾讯控股',
            'price': 360.0,
            'change': 5.0,
            'changePercent': 1.41,
            'volume': 15000000,
            'updateTime': '2023-12-11 16:00:00'
        }
        
        response = client.get('/api/futu/quote/HK.00700')
        
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'HK.00700'
        assert data['price'] == 360.0
    
    def test_get_market_quote_not_found(self, client, mock_fetcher):
        """Test quote retrieval for invalid symbol"""
        mock_fetcher.get_quote.return_value = None
        
        response = client.get('/api/futu/quote/INVALID')
        
        assert response.status_code == 404
    
    def test_get_market_quote_error(self, client, mock_fetcher):
        """Test quote retrieval error"""
        mock_fetcher.get_quote.side_effect = Exception("Quote fetch failed")
        
        response = client.get('/api/futu/quote/HK.00700')
        
        assert response.status_code == 500


class TestFutuFetcher:
    """Test Futu fetcher implementation"""
    
    @pytest.fixture
    def mock_quote_ctx(self):
        """Mock OpenQuoteContext"""
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock:
            yield mock
    
    @pytest.fixture
    def mock_trade_ctx(self):
        """Mock OpenSecTradeContext"""
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock:
            yield mock
    
    def test_fetcher_init(self):
        """Test FutuFetcher initialization"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        fetcher = FutuFetcher(host='localhost', port=11111)
        
        assert fetcher.host == 'localhost'
        assert fetcher.port == 11111
        assert fetcher.quote_ctx is None
        assert fetcher.trade_ctx is None
    
    def test_ensure_quote_connection(self, mock_quote_ctx):
        """Test quote context connection"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_ctx = MagicMock()
        mock_quote_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        result = fetcher._ensure_quote_connection()
        
        assert result == mock_ctx
        assert fetcher.quote_ctx == mock_ctx
    
    def test_ensure_trade_connection(self, mock_trade_ctx):
        """Test trade context connection"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_ctx = MagicMock()
        mock_trade_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        result = fetcher._ensure_trade_connection()
        
        assert result == mock_ctx
        assert fetcher.trade_ctx == mock_ctx
    
    def test_get_account_positions_success(self, mock_trade_ctx):
        """Test getting account positions"""
        from market.fetchers.futu_fetcher import FutuFetcher
        from futu import TrdEnv
        import pandas as pd
        
        # Mock trade context response with DataFrame
        mock_ctx = MagicMock()
        mock_ret = 0  # success
        mock_data = pd.DataFrame([{
            'code': '00700',
            'stock_name': '腾讯控股',
            'qty': 100.0,
            'can_sell_qty': 100.0,
            'cost_price': 350.0,
            'price': 360.0,
            'market_val': 36000.0,
            'pl_val': 1000.0,
            'pl_ratio': 0.02857,
            'currency': 'HKD'
        }])
        mock_ctx.position_list_query.return_value = (mock_ret, mock_data)
        mock_trade_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        positions = fetcher.get_account_positions(TrdEnv.SIMULATE)
        
        assert len(positions) == 1
        assert positions[0]['symbol'] == '00700'
        assert positions[0]['quantity'] == 100
    
    def test_get_account_positions_error(self, mock_trade_ctx):
        """Test position retrieval error"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_ctx = MagicMock()
        mock_ctx.position_list_query.return_value = (1, "Error message")  # 1 = error
        mock_trade_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        positions = fetcher.get_account_positions()
        
        # Returns empty list on error, not exception
        assert positions == []
    
    def test_get_account_info_success(self, mock_trade_ctx):
        """Test getting account info"""
        import pandas as pd
        
        mock_ctx = MagicMock()
        mock_ret = 0
        mock_data = pd.DataFrame([{
            'total_assets': 100000.0,
            'cash': 50000.0,
            'market_val': 50000.0,
            'frozen_cash': 0.0,
            'available_funds': 50000.0,
            'currency': 'HKD'
        }])
        mock_ctx.accinfo_query.return_value = (mock_ret, mock_data)
        mock_trade_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        info = fetcher.get_account_info()
        
        assert info is not None
        assert info['totalAssets'] == 100000.0
        assert info['cash'] == 50000.0
    
    def test_get_quote_success(self, mock_quote_ctx):
        """Test getting market quote"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_ctx = MagicMock()
        import pandas as pd
        
        mock_ctx = MagicMock()
        mock_ret = 0
        mock_data = pd.DataFrame([{
            'stock_name': '腾讯控股',
            'last_price': 360.0,
            'change_val': 5.0,
            'change_rate': 1.41,
            'volume': 15000000,
            'turnover': 5400000000.0,
            'high': 365.0,
            'low': 355.0,
            'open_price': 358.0,
            'prev_close_price': 355.0
        }])
        mock_ctx.get_market_snapshot.return_value = (mock_ret, mock_data)
        mock_quote_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        quote = fetcher.get_quote('HK.00700')
        
        assert quote is not None
        assert quote['symbol'] == 'HK.00700'
        assert quote['price'] == 360.0
    
    def test_get_quote_error(self, mock_quote_ctx):
        """Test quote retrieval error"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_ctx = MagicMock()
        mock_ctx.get_market_snapshot.return_value = (1, "Error")
        mock_quote_ctx.return_value = mock_ctx
        
        fetcher = FutuFetcher()
        quote = fetcher.get_quote('HK.00700')
        
        assert quote is None
    
    def test_close_connections(self, mock_quote_ctx, mock_trade_ctx):
        """Test closing connections"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        mock_q_ctx = MagicMock()
        mock_t_ctx = MagicMock()
        mock_quote_ctx.return_value = mock_q_ctx
        mock_trade_ctx.return_value = mock_t_ctx
        
        fetcher = FutuFetcher()
        fetcher._ensure_quote_connection()
        fetcher._ensure_trade_connection()
        fetcher.close()
        
        mock_q_ctx.close.assert_called_once()
        mock_t_ctx.close.assert_called_once()


class TestFutuIntegration:
    """Integration tests for Futu module"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_futu_module_imports(self):
        """Test that all Futu modules can be imported"""
        from market.fetchers.futu_fetcher import FutuFetcher
        from api.routes import futu
        from futu import TrdEnv, TrdMarket, OpenQuoteContext, OpenSecTradeContext
        
        assert FutuFetcher is not None
        assert futu is not None
        assert TrdEnv is not None
    
    def test_futu_fetcher_singleton(self):
        """Test that futu_fetcher is properly initialized"""
        from market.fetchers.futu_fetcher import futu_fetcher
        
        assert futu_fetcher is not None
        assert futu_fetcher.host == '127.0.0.1'
        assert futu_fetcher.port == 11111
