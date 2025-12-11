"""
Test suite for API routes - research.py
"""
import pytest
from unittest.mock import patch, Mock, mock_open
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
        with patch('subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 300)
            
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 500
            assert 'timeout' in response.json()['detail'].lower()
    
    def test_generate_research_paper_failure(self, client):
        """Test workflow execution failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = 'Error message'
            
            response = client.post('/api/research/wechat/generate')
            
            assert response.status_code == 500
            assert 'Workflow failed' in response.json()['detail']
