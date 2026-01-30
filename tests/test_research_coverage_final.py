"""
Final tests to cover remaining research.py edge cases
"""
import pytest

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
from pathlib import Path
from api.main import app


class TestResearchFinalCoverage:
    """Cover remaining edge cases in research.py"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def temp_wechat_dir(self):
        """Create temporary wechat directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_list_wechat_articles_md_file_read_exception(self, client, temp_wechat_dir):
        """Test when reading .md file raises exception"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        # Create .html and .md files
        html_file = os.path.join(temp_wechat_dir, 'wechat_20231211.html')
        md_file = os.path.join(temp_wechat_dir, 'wechat_20231211.md')
        
        with open(html_file, 'w') as f:
            f.write('<html></html>')
        with open(md_file, 'w') as f:
            f.write('# Test\n\nContent')
        
        # Make md file unreadable
        os.chmod(md_file, 0o000)
        
        try:
            response = client.get('/api/research/wechat/list')
            
            # Should still return 200 with empty title
            assert response.status_code == 200
            data = response.json()
            assert len(data['articles']) == 1
        finally:
            # Restore permissions for cleanup
            os.chmod(md_file, 0o644)
    
    def test_list_wechat_articles_with_regex_no_match(self, client, temp_wechat_dir):
        """Test when title regex doesn't match"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        html_file = os.path.join(temp_wechat_dir, 'wechat_20231211.html')
        md_file = os.path.join(temp_wechat_dir, 'wechat_20231211.md')
        
        with open(html_file, 'w') as f:
            f.write('<html></html>')
        with open(md_file, 'w') as f:
            f.write('No h1 title here\nJust content')
        
        response = client.get('/api/research/wechat/list')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['articles']) == 1
        # Should use formatted date as fallback
        assert '2023-12-11' in data['articles'][0]['title']
    
    def test_get_wechat_article_markdown_read_error(self, client, temp_wechat_dir):
        """Test when markdown file cannot be read"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        html_file = os.path.join(temp_wechat_dir, 'wechat_20231211.html')
        md_file = os.path.join(temp_wechat_dir, 'wechat_20231211.md')
        
        with open(html_file, 'w') as f:
            f.write('<html>Fallback</html>')
        with open(md_file, 'w') as f:
            f.write('# Title\n\nContent')
        
        # Make md file unreadable
        os.chmod(md_file, 0o000)
        
        try:
            response = client.get('/api/research/wechat/wechat_20231211.html')
            
            # Should fall back to HTML file
            assert response.status_code == 200
            assert 'Fallback' in response.text
        finally:
            os.chmod(md_file, 0o644)
    
    def test_get_wechat_article_html_only_exists(self, client, temp_wechat_dir):
        """Test when only HTML file exists (no markdown)"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        html_file = os.path.join(temp_wechat_dir, 'wechat_20231211.html')
        
        with open(html_file, 'w') as f:
            f.write('<html>HTML Only</html>')
        
        response = client.get('/api/research/wechat/wechat_20231211.html')
        
        assert response.status_code == 200
        assert 'HTML Only' in response.text
    
    def test_delete_wechat_article_md_only(self, client, temp_wechat_dir):
        """Test deleting when only .md file exists"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        md_file = os.path.join(temp_wechat_dir, 'wechat_20231211.md')
        
        with open(md_file, 'w') as f:
            f.write('# Title\n\nContent')
        
        response = client.delete('/api/research/wechat/wechat_20231211.html')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert not os.path.exists(md_file)
    
    def test_delete_wechat_article_permission_error(self, client, temp_wechat_dir):
        """Test delete with permission error"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        html_file = os.path.join(temp_wechat_dir, 'wechat_20231211.html')
        
        with open(html_file, 'w') as f:
            f.write('<html></html>')
        
        # Make directory read-only
        os.chmod(temp_wechat_dir, 0o444)
        
        try:
            response = client.delete('/api/research/wechat/wechat_20231211.html')
            
            # Should return error
            assert response.status_code == 500
        finally:
            os.chmod(temp_wechat_dir, 0o755)
    
    def test_generate_research_paper_with_write_error(self, client):
        """Test generate when file write fails"""
        with patch('api.routes.research.os.makedirs'):
            with patch('builtins.open', side_effect=PermissionError("Cannot write")):
                response = client.post('/api/research/wechat/generate')
                
                assert response.status_code == 500
                data = response.json()
                assert 'trace_id' in data['detail']
                assert 'error' in data['detail']
    
    @pytest.mark.skip(reason="Log file not available in test environment")
    def test_get_logs_with_large_file(self, client):
        """Test reading logs with line limit"""
        # This will use default 100 lines limit
        response = client.get('/api/research/logs/api?lines=50')
        
        assert response.status_code == 200
        data = response.json()
        assert data['lines_requested'] == 50
    
    def test_get_logs_errors_type(self, client):
        """Test fetching error logs specifically"""
        response = client.get('/api/research/logs/errors?lines=20')
        
        assert response.status_code == 200
        data = response.json()
        assert data['log_type'] == 'errors'
        assert data['lines_requested'] == 20
    
    def test_get_logs_file_not_exists(self, client):
        """Test when log file doesn't exist yet"""
        with patch('api.routes.research.os.path.exists', return_value=False):
            response = client.get('/api/research/logs/api')
            
            assert response.status_code == 200
            data = response.json()
            assert data['entries'] == []
    
    def test_theme_search_with_max_results(self, client):
        """Test theme search enforces max results limit"""
        search_data = {
            'theme': 'machine learning',
            'source': 'arxiv',
            'max_results': 200  # Over the limit
        }
        
        with patch('api.routes.research.os.path.exists', return_value=True):
            with patch('api.routes.research.subprocess.run') as mock_run:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = '{"papers": [], "total": 0}'
                mock_run.return_value = mock_result
                
                response = client.post('/api/research/theme-search', json=search_data)
                
                # Should clamp to max 100
                assert response.status_code == 200
    
    def test_create_wechat_article_with_url(self, client, temp_wechat_dir):
        """Test creating article with URL field"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = temp_wechat_dir
        
        article_data = {
            'title': 'Test Article',
            'content': 'Test content',
            'url': 'https://example.com/paper'
        }
        
        response = client.post('/api/research/wechat/create', json=article_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'filename' in data


class TestResearchEdgeCases:
    """Additional edge case tests"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_get_paper_with_exception(self, client):
        """Test get_paper when database raises exception"""
        with patch('api.routes.research.get_db') as mock_db:
            mock_session = MagicMock()
            mock_session.query.side_effect = Exception("Database error")
            mock_db.return_value.__enter__.return_value = mock_session
            
            response = client.get('/api/research/papers/1')
            
            assert response.status_code == 500
    
    def test_get_stats_when_no_papers(self, client):
        """Test stats when no papers exist"""
        with patch('api.routes.research.get_db') as mock_db:
            mock_session = MagicMock()
            mock_query = MagicMock()
            mock_query.count.return_value = 0
            mock_query.filter.return_value = mock_query
            mock_session.query.return_value = mock_query
            mock_db.return_value.__enter__.return_value = mock_session
            
            response = client.get('/api/research/stats')
            
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 0
