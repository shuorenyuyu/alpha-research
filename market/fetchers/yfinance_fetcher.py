"""
Market data fetcher service
Fetches stock data from Yahoo Finance using yfinance
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random

class MarketDataFetcher:
    """
    Fetches stock market data
    TODO: Replace mock data with real yfinance once Python 3.11+ is available
    """
    
    def __init__(self):
        """Initialize the fetcher"""
        self.cache = {}
        self.cache_duration = 60  # Cache for 60 seconds
        
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get current quote for a stock symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dictionary with stock data or None if not found
        """
        # Mock data for now - replace with yfinance later
        mock_prices = {
            'AAPL': 195.20,
            'MSFT': 425.80,
            'GOOGL': 175.30,
            'NVDA': 135.50,
            'TSLA': 248.90,
            'AMZN': 178.50,
            'META': 485.30,
            'NFLX': 612.20,
        }
        
        if symbol.upper() not in mock_prices:
            return None
            
        base_price = mock_prices[symbol.upper()]
        # Add some random variation
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        previous_close = base_price
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        return {
            'symbol': symbol.upper(),
            'name': self._get_company_name(symbol.upper()),
            'price': round(current_price, 2),
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'volume': random.randint(10000000, 100000000),
            'marketCap': random.randint(100000000000, 3000000000000),
            'high': round(current_price * 1.02, 2),
            'low': round(current_price * 0.98, 2),
            'open': round(base_price * 1.001, 2),
            'previousClose': round(previous_close, 2),
            'timestamp': datetime.now().isoformat()
        }
    
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
        Get historical price data
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            List of OHLCV data dictionaries
        """
        quote = self.get_quote(symbol)
        if not quote:
            return None
        
        # Generate mock historical data
        days = self._period_to_days(period)
        base_price = quote['price']
        
        history = []
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            price = base_price * (1 + random.uniform(-0.05, 0.05))
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(price * 0.99, 2),
                'high': round(price * 1.02, 2),
                'low': round(price * 0.98, 2),
                'close': round(price, 2),
                'volume': random.randint(10000000, 100000000),
                'adjClose': round(price, 2)
            })
        
        return history
    
    def get_trending_stocks(self) -> List[Dict]:
        """
        Get trending/popular stocks
        
        Returns:
            List of trending stock quotes
        """
        trending_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
        return self.get_quotes(trending_symbols)
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for symbol"""
        names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'NVDA': 'NVIDIA Corporation',
            'TSLA': 'Tesla, Inc.',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.',
        }
        return names.get(symbol, symbol)
    
    def _period_to_days(self, period: str) -> int:
        """Convert period string to number of days"""
        period_map = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
        }
        return period_map.get(period, 30)


# Global instance
market_fetcher = MarketDataFetcher()
