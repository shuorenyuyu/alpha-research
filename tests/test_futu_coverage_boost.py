"""
Additional tests to reach 99% coverage for Futu module
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from api.main import app


class TestFutuCoverageBoost:
    """Tests to cover remaining Futu code paths"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_get_account_info_with_all_fields(self, client):
        """Test account info with complete data"""
        with patch('api.routes.futu.futu_fetcher') as mock_fetcher:
            mock_fetcher.get_account_info.return_value = {
                'totalAssets': 100000.0,
                'cash': 50000.0,
                'marketValue': 50000.0,
                'frozenCash': 1000.0,
                'availableFunds': 49000.0,
                'currency': 'HKD',
                'updateTime': '2023-12-11 10:30:00'
            }
            
            response = client.get('/api/futu/account')
            
            assert response.status_code == 200
            data = response.json()
            assert data['totalAssets'] == 100000.0
            assert data['frozenCash'] == 1000.0
            assert data['availableFunds'] == 49000.0
    
    def test_get_quote_with_all_fields(self, client):
        """Test quote with complete data"""
        with patch('api.routes.futu.futu_fetcher') as mock_fetcher:
            mock_fetcher.get_quote.return_value = {
                'symbol': 'HK.00700',
                'name': '腾讯控股',
                'price': 360.0,
                'change': 5.0,
                'changePercent': 1.41,
                'volume': 15000000,
                'turnover': 5400000000.0,
                'high': 365.0,
                'low': 355.0,
                'open': 358.0,
                'previousClose': 355.0,
                'timestamp': '2023-12-11 16:00:00'
            }
            
            response = client.get('/api/futu/quote/HK.00700')
            
            assert response.status_code == 200
            data = response.json()
            assert data['symbol'] == 'HK.00700'
            assert data['price'] == 360.0
            assert data['turnover'] == 5400000000.0
            assert data['high'] == 365.0
            assert data['low'] == 355.0
            assert data['open'] == 358.0
            assert data['previousClose'] == 355.0


class TestFutuFetcherDetailedCoverage:
    """Detailed tests for FutuFetcher internal methods"""
    
    def test_get_account_info_empty_dataframe(self):
        """Test when account info returns empty DataFrame"""
        from market.fetchers.futu_fetcher import FutuFetcher
        import pandas as pd
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            mock_ctx.accinfo_query.return_value = (0, pd.DataFrame())  # Empty DataFrame
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            result = fetcher.get_account_info()
            
            assert result is None
    
    def test_get_account_info_with_optional_fields(self):
        """Test account info with optional fields missing"""
        from market.fetchers.futu_fetcher import FutuFetcher
        import pandas as pd
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            # DataFrame without optional fields
            mock_data = pd.DataFrame([{
                'total_assets': 100000.0,
                'cash': 50000.0,
                'market_val': 50000.0
                # Missing: frozen_cash, available_funds, currency
            }])
            mock_ctx.accinfo_query.return_value = (0, mock_data)
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            info = fetcher.get_account_info()
            
            assert info is not None
            assert info['totalAssets'] == 100000.0
            # Should use defaults for missing fields
            assert 'currency' in info
            assert 'availableFunds' in info
    
    def test_get_account_positions_empty_dataframe(self):
        """Test when positions returns empty DataFrame"""
        from market.fetchers.futu_fetcher import FutuFetcher
        import pandas as pd
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            mock_ctx.position_list_query.return_value = (0, pd.DataFrame())
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            positions = fetcher.get_account_positions()
            
            assert positions == []
    
    def test_get_quote_empty_dataframe(self):
        """Test when quote returns empty DataFrame"""
        from market.fetchers.futu_fetcher import FutuFetcher
        import pandas as pd
        
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock_quote:
            mock_ctx = MagicMock()
            mock_ctx.get_market_snapshot.return_value = (0, pd.DataFrame())
            mock_quote.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            quote = fetcher.get_quote('HK.00700')
            
            assert quote is None
    
    def test_get_quote_with_stock_name(self):
        """Test quote retrieval with stock name field"""
        from market.fetchers.futu_fetcher import FutuFetcher
        import pandas as pd
        
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock_quote:
            mock_ctx = MagicMock()
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
            mock_ctx.get_market_snapshot.return_value = (0, mock_data)
            mock_quote.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            quote = fetcher.get_quote('HK.00700')
            
            assert quote is not None
            assert quote['name'] == '腾讯控股'
    
    def test_get_account_positions_exception_handling(self):
        """Test position retrieval with exception"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            mock_ctx.position_list_query.side_effect = Exception("Connection error")
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            positions = fetcher.get_account_positions()
            
            # Should return empty list on exception
            assert positions == []
    
    def test_get_account_info_exception_handling(self):
        """Test account info retrieval with exception"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            mock_ctx.accinfo_query.side_effect = RuntimeError("API Error")
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            info = fetcher.get_account_info()
            
            # Should return None on exception
            assert info is None
    
    def test_get_quote_exception_handling(self):
        """Test quote retrieval with exception"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock_quote:
            mock_ctx = MagicMock()
            mock_ctx.get_market_snapshot.side_effect = Exception("Network error")
            mock_quote.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            quote = fetcher.get_quote('HK.00700')
            
            # Should return None on exception
            assert quote is None
    
    def test_close_connections_both_contexts(self):
        """Test closing both quote and trade connections"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock_quote:
            with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
                mock_q_ctx = MagicMock()
                mock_t_ctx = MagicMock()
                mock_quote.return_value = mock_q_ctx
                mock_trade.return_value = mock_t_ctx
                
                fetcher = FutuFetcher()
                fetcher._ensure_quote_connection()
                fetcher._ensure_trade_connection()
                
                # Close both
                fetcher.close()
                
                mock_q_ctx.close.assert_called_once()
                mock_t_ctx.close.assert_called_once()
                assert fetcher.quote_ctx is None
                assert fetcher.trade_ctx is None
    
    def test_close_connections_already_none(self):
        """Test closing when connections are already None"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        fetcher = FutuFetcher()
        # Don't create connections
        fetcher.close()  # Should not raise error
        
        assert fetcher.quote_ctx is None
        assert fetcher.trade_ctx is None
    
    def test_ensure_quote_connection_reuses_existing(self):
        """Test that quote connection is reused if already exists"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenQuoteContext') as mock_quote:
            mock_ctx = MagicMock()
            mock_quote.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            ctx1 = fetcher._ensure_quote_connection()
            ctx2 = fetcher._ensure_quote_connection()
            
            # Should be same instance
            assert ctx1 is ctx2
            # Should only create once
            assert mock_quote.call_count == 1
    
    def test_ensure_trade_connection_reuses_existing(self):
        """Test that trade connection is reused if already exists"""
        from market.fetchers.futu_fetcher import FutuFetcher
        
        with patch('market.fetchers.futu_fetcher.OpenSecTradeContext') as mock_trade:
            mock_ctx = MagicMock()
            mock_trade.return_value = mock_ctx
            
            fetcher = FutuFetcher()
            ctx1 = fetcher._ensure_trade_connection()
            ctx2 = fetcher._ensure_trade_connection()
            
            # Should be same instance
            assert ctx1 is ctx2
            # Should only create once
            assert mock_trade.call_count == 1
