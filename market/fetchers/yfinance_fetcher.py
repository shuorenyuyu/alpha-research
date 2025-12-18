"""
Market data fetcher service
Fetches stock data from Yahoo Finance using yfinance
"""
from typing import List, Dict, Optional
from datetime import datetime
import yfinance as yf
import math
import logging

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """
    Fetches stock market data from Yahoo Finance
    Uses yfinance library for real-time data with hourly refresh capability
    """
    
    def __init__(self):
        """Initialize the fetcher"""
        self.cache = {}
        self.cache_duration = 3600  # Cache for 1 hour (3600 seconds)
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get current quote for a stock symbol from Yahoo Finance
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with stock data or None if not found
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price data
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
            
            if current_price == 0:
                return None
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', symbol),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'volume': info.get('volume', 0),
                'marketCap': info.get('marketCap', 0),
                'high': round(info.get('dayHigh', current_price), 2),
                'low': round(info.get('dayLow', current_price), 2),
                'open': round(info.get('open', current_price), 2),
                'previousClose': round(previous_close, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_quotes(self, symbols: List[str]) -> List[Dict]:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            List of stock data dictionaries
        """
        quotes = []
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Get historical price data from Yahoo Finance
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            List of OHLCV data dictionaries
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            history = []
            for date, row in hist.iterrows():
                history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume']),
                    'adjClose': round(row['Close'], 2)
                })
            
            return history
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_trending_stocks(self) -> List[Dict]:
        """
        Get trending/popular stocks
        
        Returns:
            List of trending stock quotes
        """
        # Popular tech stocks to track
        trending_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META', 'NFLX']
        return self.get_quotes(trending_symbols)

    def _compute_cagr(self, values: List[float]) -> Optional[float]:
        """Compute CAGR for a list of yearly values (oldest -> newest)"""
        if len(values) < 2:
            return None
        start, end = values[0], values[-1]
        years = len(values) - 1
        if start <= 0 or end <= 0 or years <= 0:
            return None
        try:
            return (math.pow(end / start, 1 / years) - 1) * 100
        except Exception:
            return None

    def _extract_ebitda_series(self, ticker: yf.Ticker) -> List[float]:
        """Extract EBITDA series ordered from oldest to newest"""
        df = None
        # Attempt modern API first
        if hasattr(ticker, "get_income_stmt"):
            try:
                df = ticker.get_income_stmt(freq="annual")
            except Exception:
                df = None
        # Fallback to legacy attributes
        if df is None and hasattr(ticker, "income_stmt"):
            df = ticker.income_stmt
        if df is None or df.empty or 'EBITDA' not in df.index:
            return []
        series = df.loc['EBITDA']
        # Columns are periods; sort by column name to approximate chronology
        values = []
        for col in sorted(series.index, key=str):
            try:
                val = float(series[col])
                if not math.isnan(val):
                    values.append(val)
            except Exception:
                continue
        return values

    def get_metrics(self, symbol: str) -> Optional[Dict]:
        """
        Get fundamental metrics for stock selection.
        Returns None when data is insufficient.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Price & market data
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                return None

            ebitda_values = self._extract_ebitda_series(ticker)
            ebitda_growth_10y = self._compute_cagr(ebitda_values[-11:]) if len(ebitda_values) >= 2 else None
            ebitda_growth_5y = self._compute_cagr(ebitda_values[-6:]) if len(ebitda_values) >= 2 else None
            ebitda_growth_1y = self._compute_cagr(ebitda_values[-2:]) if len(ebitda_values) >= 2 else None

            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            peg_ratio = info.get('pegRatio')
            pb_ratio = info.get('priceToBook')
            dividend_yield = info.get('dividendYield')

            return {
                'symbol': symbol.upper(),
                'company': info.get('longName', symbol),
                'currentPrice': round(float(current_price), 2),
                'predictabilityRank': info.get('overallRisk'),  # Placeholder if available
                'marketCap': info.get('marketCap'),
                'ebitdaGrowth10Y': round(ebitda_growth_10y, 2) if ebitda_growth_10y is not None else None,
                'ebitdaGrowth5Y': round(ebitda_growth_5y, 2) if ebitda_growth_5y is not None else None,
                'ebitdaGrowth1Y': round(ebitda_growth_1y, 2) if ebitda_growth_1y is not None else None,
                'peRatio': round(float(pe_ratio), 2) if pe_ratio else None,
                'pegRatio': round(float(peg_ratio), 2) if peg_ratio else None,
                'pbRatio': round(float(pb_ratio), 2) if pb_ratio else None,
                'dividendYield': round(float(dividend_yield) * 100, 2) if dividend_yield else None
            }
        except Exception as e:
            logger.exception(f"Error fetching metrics for %s", symbol)
            return None


# Global instance
market_fetcher = MarketDataFetcher()
