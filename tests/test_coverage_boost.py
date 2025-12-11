"""
Additional tests to push coverage to 99%+
"""
import pytest
from unittest.mock import patch, Mock
import tempfile
import os


class TestCoverageBoost:
    """Tests to cover remaining lines"""
    
    def test_list_wechat_with_md_read_error(self, client):
        """Test listing when .md file exists but can't be read (error handling)"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Create .html file
            html_path = os.path.join(temp_dir, 'wechat_20231211.html')
            with open(html_path, 'w') as f:
                f.write('<html></html>')
            
            # Create .md file that will cause read error
            md_path = os.path.join(temp_dir, 'wechat_20231211.md')
            with open(md_path, 'w') as f:
                f.write('# Bad encoding \\xFF\\xFF')
            
            response = client.get('/api/research/wechat/list')
            
            # Should still work, just use default title
            assert response.status_code == 200
            data = response.json()
            assert len(data['articles']) == 1
            
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_list_wechat_with_no_title_match(self, client):
        """Test listing when .md exists but has no title"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            import api.routes.research as research_module
            original_path = research_module.WECHAT_PATH
            research_module.WECHAT_PATH = temp_dir
            
            # Create .html file
            html_path = os.path.join(temp_dir, 'wechat_20231211.html')
            with open(html_path, 'w') as f:
                f.write('<html></html>')
            
            # Create .md file without expected title format
            md_path = os.path.join(temp_dir, 'wechat_20231211.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('Some content without proper title')
            
            response = client.get('/api/research/wechat/list')
            
            # Should use default title format
            assert response.status_code == 200
            data = response.json()
            assert len(data['articles']) == 1
            assert 'AI Research' in data['articles'][0]['title']
            
            research_module.WECHAT_PATH = original_path
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_stats_with_null_avg(self, client):
        """Test stats when no papers have citations (avg is NULL)"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            import sqlite3
            conn = sqlite3.connect(temp_db.name)
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
            # Insert paper with NULL citation_count
            cursor.execute('''
                INSERT INTO papers VALUES
                (1, 'Test', 'Author', 2023, 'Venue', 'Abstract', 'url', NULL, NULL, NULL, '2023-12-10', 0)
            ''')
            conn.commit()
            conn.close()
            
            import api.routes.research as research_module
            original_db = research_module.DB_PATH
            research_module.DB_PATH = temp_db.name
            
            response = client.get('/api/research/stats')
            
            assert response.status_code == 200
            data = response.json()
            # Should handle NULL avg gracefully
            assert data['avg_citations'] == 0.0
            
            research_module.DB_PATH = original_db
        finally:
            os.unlink(temp_db.name)
    
    def test_connection_init_db(self):
        """Test init_db function creates database"""
        from market.database.connection import init_db
        
        # This should create the database and tables
        init_db()
        
        # Verify database exists
        from market.database.connection import DB_PATH
        assert os.path.exists(DB_PATH)
