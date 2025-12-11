"""
Final tests to achieve 99% coverage
"""
import pytest
from unittest.mock import patch, mock_open
import tempfile
import os


class TestFinalCoverage:
    """Tests for final coverage push"""
    
    def test_delete_wechat_general_exception(self, client):
        """Test delete with general exception (not HTTPException)"""
        import api.routes.research as research_module
        
        # Patch os.remove to raise a general exception
        with patch.object(research_module.os, 'remove', side_effect=IOError('Disk error')):
            # First need to make file appear to exist
            with patch.object(research_module.os.path, 'exists', return_value=True):
                response = client.delete('/api/research/wechat/test.html')
                
                # Should catch exception and return 500
                assert response.status_code == 500
                assert 'Error deleting article' in response.json()['detail']
    
    def test_create_wechat_write_error(self, client):
        """Test create with write error"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Make directory read-only
            os.chmod(temp_dir, 0o444)
            
            response = client.post('/api/research/wechat/create', json={
                'title': 'Test',
                'content': 'Content'
            })
            
            # Should handle write error
            assert response.status_code == 500
            assert 'Error creating article' in response.json()['detail']
            
            os.chmod(temp_dir, 0o755)
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            os.chmod(temp_dir, 0o755)
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_paper_database_error(self, client):
        """Test get_paper with database error"""
        import api.routes.research as research_module
        original_db = research_module.DB_PATH
        
        # Point to invalid database
        research_module.DB_PATH = '/dev/null/invalid.db'
        
        response = client.get('/api/research/papers/1')
        
        assert response.status_code == 500
        assert 'Database error' in response.json()['detail']
        
        research_module.DB_PATH = original_db
    
    def test_get_stats_database_error(self, client):
        """Test get_stats with database error"""
        import api.routes.research as research_module
        original_db = research_module.DB_PATH
        
        research_module.DB_PATH = '/dev/null/invalid.db'
        
        response = client.get('/api/research/stats')
        
        assert response.status_code == 500
        assert 'Database error' in response.json()['detail']
        
        research_module.DB_PATH = original_db
    
    def test_generate_workflow_script_exists_check(self, client):
        """Test generate when script exists"""
        import api.routes.research as research_module
        
        with patch('subprocess.run') as mock_run:
            # Mock script exists
            with patch('os.path.exists', return_value=True):
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = 'Success'
                
                response = client.post('/api/research/wechat/generate')
                
                assert response.status_code == 200
                assert response.json()['success'] is True
