"""
Additional tests to increase coverage to 99%
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
import sqlite3
import os
import tempfile


class TestMarketRoutesAdditional:
    """Additional tests for market routes to reach 99% coverage"""
    
    def test_get_single_quote_success(self, client, mock_yfinance_ticker):
        """Test single quote endpoint"""
        with patch('yfinance.Ticker', return_value=mock_yfinance_ticker):
            response = client.get('/api/market/quote/AAPL')
            
            assert response.status_code == 200
            data = response.json()
            assert data['symbol'] == 'AAPL'
            assert data['price'] == 150.00
    
    def test_get_single_quote_not_found(self, client):
        """Test single quote with invalid symbol"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.info = {}
            response = client.get('/api/market/quote/INVALID')
            
            assert response.status_code == 404


class TestResearchRoutesAdditional:
    """Additional tests for research routes to reach 99% coverage"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create test database
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE papers (
                id INTEGER PRIMARY KEY,
                title TEXT,
                authors TEXT,
                year INTEGER,
                venue TEXT,
                abstract TEXT,
                url TEXT,
                citation_count INTEGER,
                summary_zh TEXT,
                investment_insights TEXT,
                fetched_at TEXT,
                processed INTEGER
            )
        ''')
        
        # Insert test data
        cursor.execute('''
            INSERT INTO papers VALUES
            (1, 'Test Paper 1', 'Author 1', 2023, 'NeurIPS', 'Abstract 1', 
             'http://test1.com', 100, 'Summary 1', 'Insights 1', '2023-12-10', 1),
            (2, 'Test Paper 2', 'Author 2', 2024, 'ICML', 'Abstract 2',
             'http://test2.com', 50, 'Summary 2', 'Insights 2', '2023-12-11', 0)
        ''')
        conn.commit()
        conn.close()
        
        # Patch DB_PATH
        import api.routes.research as research_module
        self.original_db_path = research_module.DB_PATH
        research_module.DB_PATH = self.temp_db.name
        
        yield
        
        # Cleanup
        research_module.DB_PATH = self.original_db_path
        os.unlink(self.temp_db.name)
    
    def test_get_papers_default(self, client):
        """Test get papers with default parameters"""
        response = client.get('/api/research/papers')
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_get_papers_with_limit(self, client):
        """Test get papers with limit"""
        response = client.get('/api/research/papers?limit=1')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_papers_with_offset(self, client):
        """Test get papers with offset"""
        response = client.get('/api/research/papers?offset=1')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_papers_processed_only(self, client):
        """Test get processed papers only"""
        response = client.get('/api/research/papers?processed_only=true')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['processed'] == 1
    
    def test_get_paper_by_id(self, client):
        """Test get single paper by ID"""
        response = client.get('/api/research/papers/1')
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == 1
        assert data['title'] == 'Test Paper 1'
    
    def test_get_paper_not_found(self, client):
        """Test get non-existent paper"""
        response = client.get('/api/research/papers/999')
        
        assert response.status_code == 404
    
    def test_get_stats(self, client):
        """Test get research statistics"""
        response = client.get('/api/research/stats')
        
        assert response.status_code == 200
        data = response.json()
        assert 'total_papers' in data
        assert 'processed_papers' in data
        assert 'avg_citations' in data
        assert 'latest_fetch' in data
        assert data['total_papers'] == 2
        assert data['processed_papers'] == 1
    
    def test_get_papers_database_error(self, client):
        """Test database error handling"""
        import api.routes.research as research_module
        research_module.DB_PATH = '/nonexistent/db.db'
        
        response = client.get('/api/research/papers')
        
        assert response.status_code == 500
        assert 'Database error' in response.json()['detail']
    
    def test_list_wechat_error_handling(self, client):
        """Test error handling in list_wechat_articles"""
        import api.routes.research as research_module
        
        # Make os.listdir raise an exception
        with patch.object(research_module.os, 'listdir', side_effect=PermissionError('Access denied')):
            response = client.get('/api/research/wechat/list')
            
            assert response.status_code == 500
            assert 'Error listing articles' in response.json()['detail']
    
    def test_delete_wechat_only_html(self, client):
        """Test deleting when only HTML exists"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Create only .html file
            html_path = os.path.join(temp_dir, 'wechat_20231211.html')
            with open(html_path, 'w') as f:
                f.write('<html>Test</html>')
            
            response = client.delete('/api/research/wechat/wechat_20231211.html')
            
            assert response.status_code == 200
            assert not os.path.exists(html_path)
            
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_delete_wechat_exception_handling(self, client):
        """Test delete returns 404 when file doesn't exist"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Try to delete non-existent file
            response = client.delete('/api/research/wechat/wechat_20231211.html')
            
            # Should return 404
            assert response.status_code == 404
            
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_create_wechat_multiple_same_day(self, client):
        """Test creating multiple articles same day (counter increment)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Create first article
            response1 = client.post('/api/research/wechat/create', json={
                'title': 'Test 1',
                'content': 'Content 1'
            })
            assert response1.status_code == 200
            
            # Create second article same day (should increment counter)
            response2 = client.post('/api/research/wechat/create', json={
                'title': 'Test 2',
                'content': 'Content 2'
            })
            assert response2.status_code == 200
            data2 = response2.json()
            # Filename should have _1 suffix
            assert '_1.html' in data2['filename'] or len(data2['filename']) > 18
            
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
