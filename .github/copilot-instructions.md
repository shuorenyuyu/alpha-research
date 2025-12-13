# GitHub Copilot Instructions for Alpha Research

## Project Overview
**Alpha Research** is an AI-Powered Investment Research & Quantitative Analysis Platform that combines:
- 📄 AI Research Papers with daily curated summaries
- 📊 Stock Market Data from multiple sources (Yahoo Finance, Futu API, Akshare)
- 🧮 Quantitative Strategies with backtesting framework
- 💰 Value Investing with fundamental analysis
- 📈 Interactive Dashboard with real-time data visualization

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pandas, NumPy
- **Frontend**: Next.js 16, React 19, TypeScript 5, TailwindCSS 4
- **Database**: SQLite (development), PostgreSQL (production)
- **Market Data**: yfinance, futu-api, Akshare
- **Deployment**: Docker, Azure VM, PM2

## Critical Development Rules

### 1. Test Coverage - **99% MINIMUM** 🎯
**MANDATORY**: After ANY code modification, you MUST:
1. Write comprehensive tests covering all new/modified code
2. Run the test suite: `pytest --cov=. --cov-report=json --cov-report=html`
3. Verify coverage is **≥99%** in `coverage.json`
4. If coverage drops below 99%, add more tests until it reaches 99%+

**Test Requirements**:
- Unit tests for all functions and methods
- Integration tests for API endpoints
- Edge cases and error handling
- Mock external dependencies (Yahoo Finance, Futu API, databases)
- Test both success and failure scenarios

**Example Test Structure**:
```python
# tests/test_market_fetchers.py
import pytest
from unittest.mock import Mock, patch
from market.fetchers.yfinance_fetcher import YFinanceFetcher

class TestYFinanceFetcher:
    def test_get_quote_success(self):
        # Test successful quote fetch
        pass
    
    def test_get_quote_invalid_symbol(self):
        # Test error handling
        pass
    
    def test_get_quote_network_error(self):
        # Test network failure
        pass
```

### 2. Code Quality Standards
- **Type hints**: All functions must have type annotations
- **Docstrings**: Required for all public functions/classes (Google style)
- **Error handling**: Always handle exceptions gracefully
- **Logging**: Use proper logging instead of print statements
- **Code style**: Follow PEP 8, use `black` for formatting

### 3. API Development Guidelines
**Backend (FastAPI)**:
- Use Pydantic models for request/response validation
- Include proper HTTP status codes and error responses
- Add API documentation with examples in docstrings
- Implement rate limiting and caching where appropriate
- Always use `--no-pager` for git commands in responses

**Example API Endpoint**:
```python
@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(symbol: str) -> StockQuote:
    """
    Get real-time stock quote.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        StockQuote with current price, volume, market cap
    
    Raises:
        HTTPException: 404 if symbol not found
    """
    # Implementation with tests
```

### 4. Frontend Development Guidelines
**Dashboard (Next.js + React)**:
- Use TypeScript for type safety
- Implement loading states and error boundaries
- Follow dark theme design system
- Ensure responsive design (mobile-first)
- Use React hooks properly (avoid unnecessary re-renders)
- Implement proper data fetching with error handling

### 5. Database & Data Management
- **Migrations**: Use Alembic for database migrations
- **Models**: Define SQLAlchemy models with proper relationships
- **Queries**: Optimize queries, use indexes where needed
- **Caching**: Implement caching for expensive operations (1-hour TTL for market data)

### 6. Market Data Integration
**When integrating new data sources**:
- Create fetcher class in `market/fetchers/`
- Implement error handling and retry logic
- Add caching to avoid rate limits
- Write comprehensive tests with mocked API responses
- Document API limits and requirements

**Futu API Integration** (if adding):
```python
# market/fetchers/futu_fetcher.py
from futu import OpenQuoteContext, OpenSecTradeContext

class FutuFetcher:
    """Fetcher for Futu (Futubull) market data and account positions."""
    
    def get_quote(self, symbol: str) -> dict:
        """Get real-time quote from Futu API."""
        # Implementation with tests
    
    def get_positions(self) -> list:
        """Get user account positions from Futu."""
        # Implementation with tests
```

### 7. Git Workflow
**Commit Message Format**:
```
feat: add Futu API integration for portfolio tracking
fix: resolve cache timeout issue in yfinance fetcher
test: add 99% coverage for market data module
docs: update API documentation for new endpoints
```

**Before Committing**:
1. Run tests: `pytest --cov=. --cov-report=json`
2. Check coverage: Must be ≥99%
3. Run linter: `black . && flake8 .`
4. Update documentation if needed

### 8. Deployment & Production
- **Environment Variables**: Never commit secrets, use `.env` files
- **Docker**: Update Dockerfile if dependencies change
- **PM2**: Restart services after deployment
- **Monitoring**: Check logs after deployment (`pm2 logs`)

**Deployment Checklist**:
```bash
# 1. Update server
ssh research-azure
cd ~/alpha-research && git pull

# 2. Backend
source venv/bin/activate
pip install -r requirements.txt
pytest --cov=. --cov-report=json  # Verify 99% coverage

# 3. Frontend
cd dashboard && npm install && npm run build

# 4. Restart services
pm2 restart all && pm2 logs
```

### 9. Documentation
**Update these files when modifying code**:
- `README.md` - For major features
- `copilot.md` - For development progress
- API docstrings - For all endpoints
- `INTEGRATION_SUMMARY.md` - For integrations

### 10. Performance & Optimization
- Cache API responses (1-hour for market data)
- Use batch requests when possible
- Optimize database queries (use joins, avoid N+1)
- Implement pagination for large datasets
- Monitor API rate limits

## Common Tasks Reference

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=json --cov-report=html

# Run specific test file
pytest tests/test_market_fetchers.py -v

# Check coverage report
cat coverage.json | grep '"percent_covered"'
open htmlcov/index.html  # View HTML report
```

### Starting Development Servers
```bash
# Backend (port 8001)
cd /Users/Mac/code/alpha-research
source venv/bin/activate
python -m api.main

# Frontend (port 3000)
cd dashboard
npm run dev
```

### Database Operations
```bash
# Initialize database
python scripts/init_db.py

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Additional Context
- **Research Papers**: Synced from `research-tracker` project
- **Production Server**: 57.155.1.26 (wobbler)
- **SSH Access**: `ssh research-azure` (after setup)
- **Live URLs**: 
  - Frontend: http://alpha-research.southeastasia.cloudapp.azure.com
  - API: http://57.155.1.26:8001

## Questions or Issues?
Refer to:
- `README.md` - Project overview and setup
- `copilot.md` - Detailed development log and session history
- `INTEGRATION_SUMMARY.md` - Integration details

---

**REMEMBER**: 99% test coverage is NOT optional. Every code change MUST include tests!
