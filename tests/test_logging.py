"""
Tests for logging configuration and functionality
"""
import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from api.logging_config import (
    setup_logger,
    setup_error_logger,
    setup_research_logger,
    get_logger,
    ColoredFormatter,
    LOGS_DIR,
    API_LOG_FILE,
    ERROR_LOG_FILE,
    RESEARCH_LOG_FILE
)


class TestLoggingConfiguration:
    """Test logging configuration and setup"""
    
    def test_logs_directory_created(self):
        """Test that logs directory is created"""
        assert LOGS_DIR.exists()
        assert LOGS_DIR.is_dir()
    
    def test_log_file_paths(self):
        """Test log file paths are correct"""
        assert API_LOG_FILE.name == "api.log"
        assert ERROR_LOG_FILE.name == "errors.log"
        assert RESEARCH_LOG_FILE.name == "research.log"
        assert str(LOGS_DIR) in str(API_LOG_FILE)
    
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a properly configured logger"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            logger = setup_logger("test_logger", log_file=tmp_path, level=logging.INFO)
            
            assert logger.name == "test_logger"
            assert logger.level == logging.INFO
            assert len(logger.handlers) >= 1  # At least file handler
            
            # Test logging works
            logger.info("Test message")
            
            # Check log file was created and written
            assert tmp_path.exists()
            with open(tmp_path, 'r') as f:
                content = f.read()
                assert "Test message" in content
                assert "INFO" in content
        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_setup_logger_no_duplicates(self):
        """Test that calling setup_logger twice doesn't create duplicate handlers"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            logger1 = setup_logger("test_dup", log_file=tmp_path)
            handler_count_1 = len(logger1.handlers)
            
            # Call again with same name
            logger2 = setup_logger("test_dup", log_file=tmp_path)
            handler_count_2 = len(logger2.handlers)
            
            # Should be same logger instance with same handlers
            assert logger1 is logger2
            assert handler_count_1 == handler_count_2
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_colored_formatter(self):
        """Test ColoredFormatter adds colors to log records"""
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        
        # Create log record
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should contain ANSI color codes for ERROR (red)
        assert '\033[' in formatted  # ANSI escape sequence
        assert 'Test error' in formatted
    
    def test_setup_error_logger(self):
        """Test error logger configuration"""
        error_logger = setup_error_logger()
        
        assert error_logger.name == "alpha_research.errors"
        assert error_logger.level == logging.ERROR
        
        # Should only log ERROR and above
        # (We can't easily test this without checking handlers)
        assert len(error_logger.handlers) >= 1
    
    def test_setup_research_logger(self):
        """Test research logger configuration"""
        research_logger = setup_research_logger()
        
        assert research_logger.name == "alpha_research.research"
        assert research_logger.level == logging.DEBUG  # More verbose
        assert len(research_logger.handlers) >= 1
    
    def test_get_logger(self):
        """Test get_logger convenience function"""
        logger = get_logger("test_module")
        
        assert logger.name == "test_module"
        assert len(logger.handlers) >= 1
    
    def test_log_rotation_config(self):
        """Test that rotating file handler is configured"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            logger = setup_logger("test_rotation", log_file=tmp_path)
            
            # Find rotating file handler
            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            
            assert len(rotating_handlers) >= 1
            
            handler = rotating_handlers[0]
            assert handler.maxBytes == 10 * 1024 * 1024  # 10 MB
            assert handler.backupCount == 5
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_console_output_optional(self):
        """Test that console output can be disabled"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            logger = setup_logger(
                "test_no_console",
                log_file=tmp_path,
                console_output=False
            )
            
            # Should only have file handler, no console handler
            stream_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)
            ]
            
            assert len(stream_handlers) == 0
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestLogViewer:
    """Test log viewer endpoint functionality"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        from fastapi.testclient import TestClient
        from api.main import app
        return TestClient(app)
    
    def test_get_logs_api(self, client):
        """Test fetching API logs"""
        response = client.get("/api/research/logs/api?lines=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "log_type" in data
        assert data["log_type"] == "api"
        assert "entries" in data
        assert "lines_requested" in data
    
    def test_get_logs_research(self, client):
        """Test fetching research logs"""
        response = client.get("/api/research/logs/research?lines=50")
        assert response.status_code == 200
        
        data = response.json()
        assert data["log_type"] == "research"
        assert data["lines_requested"] == 50
    
    def test_get_logs_errors(self, client):
        """Test fetching error logs"""
        response = client.get("/api/research/logs/errors")
        assert response.status_code == 200
        
        data = response.json()
        assert data["log_type"] == "errors"
    
    def test_get_logs_invalid_type(self, client):
        """Test invalid log type returns 400"""
        response = client.get("/api/research/logs/invalid")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data["detail"]
        assert "valid_types" in data["detail"]
    
    def test_get_logs_limit_enforcement(self, client):
        """Test that lines parameter is limited to 1000"""
        response = client.get("/api/research/logs/api?lines=5000")
        assert response.status_code == 200
        
        data = response.json()
        # Should be capped at 1000
        assert data["lines_requested"] == 1000
    
    def test_get_logs_nonexistent_file(self, client):
        """Test handling of nonexistent log file"""
        # Use a temporary log type that won't exist
        with patch('api.routes.research.os.path.exists', return_value=False):
            response = client.get("/api/research/logs/api")
            assert response.status_code == 200
            
            data = response.json()
            assert data["lines_available"] == 0
            assert "not yet created" in data["message"]
    
    def test_get_logs_default_lines_parameter(self, client):
        """Test default lines parameter when not specified"""
        response = client.get("/api/research/logs/api")
        assert response.status_code == 200
        
        data = response.json()
        # Default should be 100 lines
        assert data["lines_requested"] == 100
    
    def test_get_logs_read_error(self, client):
        """Test handling of log file read errors"""
        with patch('api.routes.research.os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                response = client.get("/api/research/logs/api")
                assert response.status_code == 500
                
                data = response.json()
                assert "error" in data["detail"]


class TestErrorLogging:
    """Test error logging in research paper generation"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        from fastapi.testclient import TestClient
        from api.main import app
        return TestClient(app)
    
    def test_generate_paper_logs_trace_id(self, client):
        """Test that paper generation includes trace ID"""
        with patch('api.routes.research.os.path.exists', return_value=False):
            response = client.post("/api/research/wechat/generate")
            
            # Should fail with 404 (script not found)
            assert response.status_code == 404
            
            data = response.json()
            assert "trace_id" in data["detail"]
            assert len(data["detail"]["trace_id"]) == 8  # Short UUID
    
    def test_generate_paper_logs_subprocess_error(self, client):
        """Test that subprocess errors are logged with details"""
        with patch('api.routes.research.os.path.exists', return_value=True):
            with patch('api.routes.research.subprocess.run') as mock_run:
                # Simulate subprocess failure
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_result.stdout = "Some output"
                mock_result.stderr = "Error message"
                mock_run.return_value = mock_result
                
                response = client.post("/api/research/wechat/generate")
                
                assert response.status_code == 500
                data = response.json()
                assert "trace_id" in data["detail"]
                assert "stderr" in data["detail"]
                assert "suggestion" in data["detail"]
    
    def test_generate_paper_timeout_logged(self, client):
        """Test that timeouts are properly logged"""
        import subprocess
        
        with patch('api.routes.research.os.path.exists', return_value=True):
            with patch('api.routes.research.subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", 300)):
                response = client.post("/api/research/wechat/generate")
                
                assert response.status_code == 500
                data = response.json()
                assert "timeout" in data["detail"]["error"].lower()
                assert "trace_id" in data["detail"]


class TestRequestLogging:
    """Test request logging middleware"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        from fastapi.testclient import TestClient
        from api.main import app
        return TestClient(app)
    
    def test_request_logged(self, client, caplog):
        """Test that HTTP requests are logged"""
        with caplog.at_level(logging.INFO):
            response = client.get("/")
            assert response.status_code == 200
            
            # Check logs contain request info
            log_messages = [record.message for record in caplog.records]
            assert any("GET" in msg and "/" in msg for msg in log_messages)
    
    def test_response_logged_with_status(self, client, caplog):
        """Test that responses are logged with status code"""
        with caplog.at_level(logging.INFO):
            response = client.get("/api/market/quotes?symbols=AAPL")
            
            log_messages = [record.message for record in caplog.records]
            # Should log status code
            assert any("Status:" in msg or str(response.status_code) in msg for msg in log_messages)
    
    def test_timing_logged(self, client, caplog):
        """Test that request duration is logged"""
        with caplog.at_level(logging.INFO):
            client.get("/")
            
            log_messages = [record.message for record in caplog.records]
            # Should log duration in ms
            assert any("ms" in msg.lower() or "duration" in msg.lower() for msg in log_messages)
