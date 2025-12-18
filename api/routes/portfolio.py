"""
Portfolio strategy API routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from strategies.warren_buffett import warren_buffett_strategy
from strategies.buffett_munger import buffett_munger_strategy
from strategies.li_lu import li_lu_strategy
from strategies.duan_yongping import duan_yongping_strategy
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

class PortfolioStock(BaseModel):
    symbol: str
    name: str
    market_cap: float
    pe_ratio: float
    debt_to_equity: float
    roe: float
    current_price: float
    allocation: float
    weight: str

class PortfolioSummary(BaseModel):
    stocks: List[PortfolioStock]
    total_stocks: int
    last_rebalance: str
    next_rebalance: str
    days_until_rebalance: int
    strategy: str
    avg_pe: float
    avg_roe: float
    allocation_per_stock: float

@router.get("/warren-buffett")
async def get_warren_buffett_portfolio() -> Dict[str, Any]:
    """
    Get Warren Buffett's actual Berkshire Hathaway portfolio
    
    Based on latest 13F filings showing real holdings.
    Includes buy-in dates, prices, and current performance.
    
    Investment philosophy:
    - Buy wonderful companies at fair prices
    - Hold forever (30+ year positions in KO, AXP, MCO)
    - Circle of competence
    - Concentrated positions (AAPL ~48% of portfolio)
    """
    try:
        logger.info("Fetching Warren Buffett portfolio...")
        portfolio = warren_buffett_strategy.get_portfolio_summary()
        return portfolio
    except Exception as e:
        logger.error(f"Error fetching Warren Buffett portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")


@router.get("/market-cap-screener", response_model=PortfolioSummary)
async def get_market_cap_screener():
    """
    Market Cap Top 25 - Quality Screener
    
    Selection criteria:
    - Understandable business (within circle of competence)
    - Consistent revenue/earnings (ROE > 15%, profit margin > 10%)
    - Low debt (Debt-to-Equity < 50%)
    - Reasonable valuation (PE < 30, P/B < 5)
    
    Returns top 25 stocks by market cap with equal weighting (4% each)
    Rebalanced annually on January 1st
    """
    try:
        logger.info("Fetching market cap screener portfolio...")
        portfolio = buffett_munger_strategy.get_portfolio_summary()
        return portfolio
    except Exception as e:
        logger.error(f"Error fetching market cap screener: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")

@router.get("/buffett-munger")
async def get_buffett_munger_redirect():
    """
    Backward compatibility: Redirect to market-cap-screener
    Old name kept for compatibility with existing clients
    """
    try:
        logger.info("Fetching market cap screener (via old buffett-munger endpoint)...")
        portfolio = buffett_munger_strategy.get_portfolio_summary()
        return portfolio
    except Exception as e:
        logger.error(f"Error fetching market cap screener: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")


@router.get("/buffett-munger/picks", response_model=List[PortfolioStock])
async def get_top_picks(count: int = 25):
    """
    Get top stock picks only (without summary)
    
    - **count**: Number of stocks to return (default: 25)
    """
    try:
        picks = buffett_munger_strategy.get_top_picks(count)
        return picks
    except Exception as e:
        logger.error(f"Error fetching stock picks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch picks: {str(e)}")


@router.get("/li-lu")
async def get_li_lu_portfolio() -> Dict[str, Any]:
    """
    Get Li Lu (李录) - Himalaya Capital portfolio
    
    Based on public 13F filings and disclosed positions.
    Shows buy-in dates, prices, current values, and returns.
    
    Investment philosophy:
    - Concentrated positions in high-quality businesses
    - Long holding periods (10+ years)
    - Charlie Munger's protégé and family fund manager
    """
    try:
        logger.info("Fetching Li Lu portfolio...")
        portfolio = li_lu_strategy.get_portfolio_summary()
        return portfolio
    except Exception as e:
        logger.error(f"Error fetching Li Lu portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")


@router.get("/duan-yongping")
async def get_duan_yongping_portfolio() -> Dict[str, Any]:
    """
    Get Duan Yongping (段永平) portfolio
    
    Based on public disclosures and interviews.
    Shows buy-in dates, prices, current values, and returns.
    
    Investment philosophy:
    - 极度集中 (Extreme concentration)
    - 长期持有 (Long-term holding)
    - 只投资理解的公司 (Only invest in businesses you understand)
    - Famous for heavy Apple position since ~$10/share
    """
    try:
        logger.info("Fetching Duan Yongping portfolio...")
        portfolio = duan_yongping_strategy.get_portfolio_summary()
        return portfolio
    except Exception as e:
        logger.error(f"Error fetching Duan Yongping portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")
