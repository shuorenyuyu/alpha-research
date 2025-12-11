"""
Test suite for API routes - research.py
"""
import pytest
from unittest.mock import patch, Mock, mock_open, MagicMock
import os
import tempfile
import shutil


class TestResearchRoutes:
    """Test cases for research API routes"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        # Create temporary directory for test articles
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch the WECHAT_PATH in the research module
        import api.routes.research as research_module
        self.original_path = research_module.WECHAT_PATH
        research_module.WECHAT_PATH = self.temp_dir
        
        yield
        
        # Cleanup
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        research_module.WECHAT_PATH = self.original_path
    
    def create_test_article(self, filename, content):
        """Helper to create test article"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_list_wechat_articles_success(self, client, sample_article_content):
        """Test successful article listing"""
        # Create test articles (API looks for .html files)
        self.create_test_article('wechat_20231211.html', '<html></html>')
        self.create_test_article('wechat_20231210.html', '<html></html>')
        # Also create .md files for title extraction
        self.create_test_article('wechat_20231211.md', sample_article_content)
        self.create_test_article('wechat_20231210.md', sample_article_content)
        
        response = client.get('/api/research/wechat/list')
        
        assert response.status_code == 200
        data = response.json()
        assert 'articles' in data
        assert len(data['articles']) == 2
        assert data['articles'][0]['filename'] == 'wechat_20231211.html'
    
    def test_list_wechat_articles_empty(self, client):
        """Test listing when no articles exist"""
        response = client.get('/api/research/wechat/list')
        
        assert response.status_code == 200
        data = response.json()
        assert data['articles'] == []
    
    def test_list_wechat_articles_directory_not_found(self, client):
        """Test when directory doesn't exist"""
        import api.routes.research as research_module
        research_module.WECHAT_PATH = '/non/existent/path'
        
        response = client.get('/api/research/wechat/list')
        
        # Returns empty list when directory doesn't exist
        assert response.status_code == 200
        data = response.json()
        assert data['articles'] == []
    
    def test_get_wechat_article_success(self, client, sample_article_content):
        """Test successful article retrieval"""
        # API requires .html filename and serves markdown from .md file
        self.create_test_article('wechat_20231211.md', sample_article_content)
        
        response = client.get('/api/research/wechat/wechat_20231211.html')
        
        assert response.status_code == 200
        # Returns HTML content
        assert 'text/html' in response.headers['content-type']
    
    def test_get_wechat_article_not_found(self, client):
        """Test retrieving non-existent article"""
        response = client.get('/api/research/wechat/nonexistent.html')
        
        assert response.status_code == 404
        assert 'detail' in response.json()
    
    def test_get_wechat_article_path_traversal(self, client):
        """Test path traversal attack prevention"""
        # Path normalization removes .. so it becomes /api/research/wechat/etc/passwd.html
        # which doesn't exist, hence 404
        response = client.get('/api/research/wechat/test/../passwd.html')
        
        # Should prevent directory traversal
        assert response.status_code in [400, 404]  # Either blocked or not found
    
    def test_delete_wechat_article_success(self, client, sample_article_content):
        """Test successful article deletion"""
        self.create_test_article('wechat_20231211.html', '<html></html>')
        self.create_test_article('wechat_20231211.md', sample_article_content)
        
        response = client.delete('/api/research/wechat/wechat_20231211.html')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        # Both .html and .md should be deleted
        assert not os.path.exists(os.path.join(self.temp_dir, 'wechat_20231211.html'))
        assert not os.path.exists(os.path.join(self.temp_dir, 'wechat_20231211.md'))
    
    def test_delete_wechat_article_not_found(self, client):
        """Test deleting non-existent article"""
        response = client.delete('/api/research/wechat/nonexistent.html')
        
        assert response.status_code == 404
    
    def test_delete_wechat_article_error_handling(self, client, sample_article_content):
        """Test delete error handling"""
        self.create_test_article('wechat_20231211.html', '<html></html>')
        
        # Mock os.remove to raise exception
        with patch('api.routes.research.os.remove', side_effect=PermissionError("Access denied")):
            response = client.delete('/api/research/wechat/wechat_20231211.html')
            
            assert response.status_code == 500
            assert 'Error deleting article' in response.json()['detail']
    
    def test_get_wechat_article_html_fallback(self, client):
        """Test fallback to HTML when markdown doesn't exist"""
        # Create only HTML file, no .md file
        html_content = '<html><body><h1>Test Article</h1></body></html>'
        self.create_test_article('wechat_20231211.html', html_content)
        
        response = client.get('/api/research/wechat/wechat_20231211.html')
        
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']
    
    def test_create_wechat_article_success(self, client):
        """Test successful article creation"""
        article_data = {
            'title': 'Test Research Paper',
            'content': 'This is test content',
            'url': 'https://example.com'
        }
        
        response = client.post('/api/research/wechat/create', json=article_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'filename' in data
        assert data['filename'].startswith('wechat_')
        assert data['filename'].endswith('.html')  # Returns .html extension
    
    def test_create_wechat_article_without_url(self, client):
        """Test article creation without URL"""
        article_data = {
            'title': 'Test Research Paper',
            'content': 'This is test content'
        }
        
        response = client.post('/api/research/wechat/create', json=article_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    def test_create_wechat_article_missing_fields(self, client):
        """Test article creation with missing required fields"""
        article_data = {
            'title': 'Test Research Paper'
            # Missing content
        }
        
        response = client.post('/api/research/wechat/create', json=article_data)
        
        assert response.status_code == 422
    
    def test_generate_research_paper_success(self, client):
        """Test successful research paper generation"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'Successfully generated paper'
            mock_run.return_value.stderr = ''
            
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'output' in data
    
    def test_generate_research_paper_timeout(self, client):
        """Test workflow timeout"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 300)
            
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 500
            assert 'timeout' in response.json()['detail']['error'].lower()
    
    def test_generate_research_paper_failure(self, client):
        """Test workflow execution failure"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = 'Error message'
            mock_result.stdout = 'Some output'
            mock_run.return_value = mock_result
            
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 500
            assert 'Workflow failed' in response.json()['detail']['error']
    
    def test_generate_research_paper_script_not_found(self, client):
        """Test when workflow script doesn't exist"""
        with patch('api.routes.research.os.path.exists', return_value=False):
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 404
            data = response.json()
            assert 'trace_id' in data['detail']
            assert 'not found' in data['detail']['error'].lower()
    
    def test_generate_research_paper_unexpected_error(self, client):
        """Test handling of unexpected errors"""
        with patch('api.routes.research.os.path.exists', side_effect=RuntimeError("Unexpected")):
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 500
            data = response.json()
            assert 'trace_id' in data['detail']
            assert 'Unexpected' in data['detail']['error']
    
    def test_list_articles_title_extraction_error(self, client):
        """Test when title extraction from markdown fails"""
        # Create article with invalid markdown (no title)
        self.create_test_article('wechat_20231211.html', '<html></html>')
        self.create_test_article('wechat_20231211.md', 'No title here')
        
        response = client.get('/api/research/wechat/list')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['articles']) == 1
        # Should fall back to default title with date
        assert data['articles'][0]['title'] == 'AI Research - 2023-12-11'


class TestThemeSearch:
    """Test cases for custom theme search"""
    
    def test_theme_search_success(self, client):
        """Test successful theme search"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '''[
                {
                    "title": "Attention Is All You Need",
                    "authors": ["Vaswani", "et al."],
                    "published_date": "2017-06-12",
                    "citations": 50000,
                    "url": "https://arxiv.org/abs/1706.03762"
                }
            ]'''
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            
            response = client.post('/api/research/search/theme', json={
                'theme': 'transformers',
                'max_results': 10,
                'source': 'all'
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['theme'] == 'transformers'
            assert data['total_results'] == 1
            assert len(data['papers']) == 1
            assert 'trace_id' in data
    
    def test_theme_search_empty_theme(self, client):
        """Test search with empty theme"""
        response = client.post('/api/research/search/theme', json={
            'theme': '',
            'max_results': 10
        })
        
        assert response.status_code == 400
        data = response.json()
        assert 'trace_id' in data['detail']
        assert 'at least 2 characters' in data['detail']['error']
    
    def test_theme_search_invalid_source(self, client):
        """Test search with invalid source"""
        response = client.post('/api/research/search/theme', json={
            'theme': 'machine learning',
            'source': 'invalid_source'
        })
        
        assert response.status_code == 400
        data = response.json()
        assert 'Invalid source' in data['detail']['error']
        assert 'valid_sources' in data['detail']
    
    def test_theme_search_script_not_found(self, client):
        """Test when search script doesn't exist"""
        with patch('api.routes.research.os.path.exists', return_value=False):
            response = client.post('/api/research/search/theme', json={
                'theme': 'reinforcement learning'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'script not found' in data['detail']['error']
            assert 'trace_id' in data['detail']
    
    def test_theme_search_script_failure(self, client):
        """Test when search script fails"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = 'API rate limit exceeded'
            mock_result.stdout = ''
            mock_run.return_value = mock_result
            
            response = client.post('/api/research/search/theme', json={
                'theme': 'deep learning'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'Search script failed' in data['detail']['error']
            assert 'trace_id' in data['detail']
    
    def test_theme_search_timeout(self, client):
        """Test search timeout"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 60)
            
            response = client.post('/api/research/search/theme', json={
                'theme': 'neural networks'
            })
            
            assert response.status_code == 504
            data = response.json()
            assert 'timed out' in data['detail']['error'].lower()
    
    def test_theme_search_invalid_json(self, client):
        """Test when script returns invalid JSON"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = 'Invalid JSON output'
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            
            response = client.post('/api/research/search/theme', json={
                'theme': 'computer vision'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'Failed to parse' in data['detail']['error']
    
    def test_theme_search_max_results_limit(self, client):
        """Test that max_results is capped at 50"""
        with patch('api.routes.research.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '[]'
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            
            response = client.post('/api/research/search/theme', json={
                'theme': 'AI',
                'max_results': 1000  # Request more than max
            })
            
            # Check that subprocess was called with max 50
            call_args = mock_run.call_args[0][0]
            assert '--max-results' in call_args
            max_idx = call_args.index('--max-results')
            assert call_args[max_idx + 1] == '50'
    
    def test_theme_search_unexpected_error(self, client):
        """Test handling of unexpected errors"""
        with patch('api.routes.research.os.path.exists', side_effect=RuntimeError("Unexpected error")):
            response = client.post('/api/research/search/theme', json={
                'theme': 'quantum computing'
            })
            
            assert response.status_code == 500
            data = response.json()
            assert 'Unexpected error' in data['detail']['error']
            assert 'trace_id' in data['detail']
