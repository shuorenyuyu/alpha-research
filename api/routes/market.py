"""
Stock market API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from market.fetchers import market_fetcher
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

class StockQuote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: int
    marketCap: int
    high: float
    low: float
    open: float
    previousClose: float
    timestamp: str

class HistoricalData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjClose: float

class StockMetrics(BaseModel):
    symbol: str
    company: str
    currentPrice: float
    predictabilityRank: Optional[float] = None
    marketCap: Optional[int] = None
    ebitdaGrowth10Y: Optional[float] = None
    ebitdaGrowth5Y: Optional[float] = None
    ebitdaGrowth1Y: Optional[float] = None
    peRatio: Optional[float] = None
    pegRatio: Optional[float] = None
    pbRatio: Optional[float] = None
    dividendYield: Optional[float] = None

@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(symbol: str):
    """
    Get real-time quote for a single stock
    
    - **symbol**: Stock ticker symbol (e.g., AAPL, MSFT)
    """
    quote = market_fetcher.get_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not found")
    return quote

@router.get("/quotes", response_model=List[StockQuote])
async def get_multiple_quotes(
    symbols: str = Query(..., description="Comma-separated stock symbols (e.g., AAPL,MSFT,GOOGL)")
):
    """
    Get quotes for multiple stocks
    
    - **symbols**: Comma-separated list of stock symbols
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    quotes = market_fetcher.get_quotes(symbol_list)
    
    if not quotes:
        raise HTTPException(status_code=404, detail="No valid symbols found")
    
    return quotes

@router.get("/history/{symbol}", response_model=List[HistoricalData])
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y)"),
    interval: str = Query("1d", description="Data interval (1d, 1wk, 1mo)")
):
    """
    Get historical price data for a stock
    
    - **symbol**: Stock ticker symbol
    - **period**: Time period for historical data
    - **interval**: Data interval (granularity)
    """
    history = market_fetcher.get_historical_data(symbol, period, interval)
    
    if not history:
        raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not found")
    
    return history

@router.get("/trending", response_model=List[StockQuote])
async def get_trending_stocks():
    """
    Get trending/popular stocks
    """
    return market_fetcher.get_trending_stocks()

@router.get("/metrics/{symbol}", response_model=StockMetrics)
async def get_stock_metrics(symbol: str):
    """
    Get fundamental metrics for a stock symbol to support value screens.
    """
    metrics = market_fetcher.get_metrics(symbol)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Metrics unavailable for symbol '{symbol}'")
    return metrics
