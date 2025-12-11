"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker object"""
    mock_ticker = Mock()
    mock_ticker.info = {
        'currentPrice': 150.00,
        'previousClose': 148.00,
        'longName': 'Test Company Inc.',
        'volume': 1000000,
        'marketCap': 1000000000,
        'dayHigh': 152.00,
        'dayLow': 147.00,
        'open': 149.00,
    }
    
    # Mock history DataFrame
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    mock_ticker.history.return_value = pd.DataFrame({
        'Open': [150.0] * 30,
        'High': [152.0] * 30,
        'Low': [148.0] * 30,
        'Close': [150.0] * 30,
        'Volume': [1000000] * 30,
    }, index=dates)
    
    return mock_ticker


@pytest.fixture
def mock_research_articles():
    """Mock research articles data"""
    return {
        'articles': [
            {
                'filename': 'wechat_20231211.md',
                'date': '2023-12-11',
                'title': 'Test Research Paper 1'
            },
            {
                'filename': 'wechat_20231210.md',
                'date': '2023-12-10',
                'title': 'Test Research Paper 2'
            }
        ]
    }


@pytest.fixture
def sample_article_content():
    """Sample markdown article content"""
    return """# Test Research Paper

**Date:** 2023-12-11  
**Source:** https://example.com/paper

## Summary
This is a test research paper summary.

## Key Findings
- Finding 1
- Finding 2

## Investment Insights
Investment insights here.
"""
