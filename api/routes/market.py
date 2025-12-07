"""
Stock market API routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from market.fetchers import market_fetcher

router = APIRouter()

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


class StockQuote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int]
    updated_at: str

class HistoricalData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_quote(symbol: str):
    """
    Get real-time quote for a stock
    
    - **symbol**: Stock ticker symbol (e.g., AAPL, MSFT)
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', current_price)
        
        # Calculate change
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        return StockQuote(
            symbol=symbol.upper(),
            name=info.get('longName', symbol.upper()),
            price=round(current_price, 2),
            change=round(change, 2),
            change_percent=round(change_percent, 2),
            volume=info.get('volume', 0),
            market_cap=info.get('marketCap'),
            updated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch data for {symbol}: {str(e)}")

@router.get("/quotes", response_model=List[StockQuote])
async def get_quotes(symbols: str):
    """
    Get quotes for multiple stocks
    
    - **symbols**: Comma-separated ticker symbols (e.g., AAPL,MSFT,GOOGL)
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    quotes = []
    
    for symbol in symbol_list:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            quotes.append(StockQuote(
                symbol=symbol,
                name=info.get('longName', symbol),
                price=round(current_price, 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=info.get('volume', 0),
                market_cap=info.get('marketCap'),
                updated_at=datetime.now().isoformat()
            ))
        except Exception as e:
            # Skip failed symbols
            continue
    
    if not quotes:
        raise HTTPException(status_code=404, detail="No valid quotes found")
    
    return quotes

@router.get("/history/{symbol}", response_model=List[HistoricalData])
async def get_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
):
    """
    Get historical price data
    
    - **symbol**: Stock ticker symbol
    - **period**: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - **interval**: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        data = []
        for index, row in hist.iterrows():
            data.append(HistoricalData(
                date=index.strftime('%Y-%m-%d'),
                open=round(row['Open'], 2),
                high=round(row['High'], 2),
                low=round(row['Low'], 2),
                close=round(row['Close'], 2),
                volume=int(row['Volume'])
            ))
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.get("/trending")
async def get_trending():
    """Get trending stocks (mock data for now - yfinance doesn't have trending API)"""
    # Default watchlist
    default_symbols = ['NVDA', 'MSFT', 'GOOGL', 'TSLA', 'AAPL', 'AMZN', 'META']
    
    try:
        quotes = await get_quotes(','.join(default_symbols))
        # Sort by absolute change percent
        sorted_quotes = sorted(quotes, key=lambda x: abs(x.change_percent), reverse=True)
        return sorted_quotes[:10]
    except:
        return []
