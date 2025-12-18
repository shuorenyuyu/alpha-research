"""
Buffett-Munger Investment Strategy Implementation

"It's far better to buy a wonderful company at a fair price 
than a fair company at a wonderful price"
"""
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BuffettMungerStrategy:
    """
    Implementation of the Buffett-Munger "Wonderful Company at a Fair Price" strategy
    
    Four Key Pillars:
    1. Understandable Business (circle of competence)
    2. Consistent Revenue and Earnings
    3. No Significant Long-Term Debt
    4. Attractive Stock Price
    """
    
    # S&P 500 top holdings and quality blue chips
    UNIVERSE = [
        # Tech (understandable businesses)
        'AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'INTC',
        # Consumer
        'AMZN', 'TSLA', 'HD', 'NKE', 'SBUX', 'MCD', 'TGT', 'COST', 'WMT', 'PG',
        # Healthcare
        'JNJ', 'UNH', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN',
        # Financial
        'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'AXP', 'SCHW',
        # Industrial
        'BA', 'CAT', 'GE', 'UPS', 'HON', 'RTX', 'LMT', 'DE', 'MMM', 'UNP',
        # Energy
        'XOM', 'CVX', 'COP', 'SLB', 'EOG',
        # Telecom
        'T', 'VZ', 'TMUS',
        # Consumer Staples
        'KO', 'PEP', 'PM', 'MDLZ', 'CL'
    ]
    
    def __init__(self):
        self.last_rebalance_date = self._get_last_rebalance_date()
        self.next_rebalance_date = self._get_next_rebalance_date()
    
    def _get_last_rebalance_date(self) -> datetime:
        """Get the most recent January 1st (start of year)"""
        now = datetime.now()
        return datetime(now.year, 1, 1)
    
    def _get_next_rebalance_date(self) -> datetime:
        """Get next January 1st for rebalancing"""
        now = datetime.now()
        if now.month == 1 and now.day == 1:
            return now
        return datetime(now.year + 1, 1, 1)
    
    def _get_financial_metrics(self, symbol: str) -> Optional[Dict]:
        """Fetch financial metrics for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get historical data for consistency check
            hist = ticker.history(period="5y")
            if hist.empty:
                return None
            
            # Key metrics
            metrics = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'profit_margin': info.get('profitMargins', 0),
                'current_price': info.get('currentPrice', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0)
            }
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Could not fetch metrics for {symbol}: {e}")
            return None
    
    def _meets_quality_criteria(self, metrics: Dict) -> bool:
        """
        Check if stock meets Buffett-Munger quality criteria
        
        Criteria:
        1. Understandable business (in our universe)
        2. Consistent revenue/earnings (ROE > 15%, profit margin > 10%)
        3. Low debt (Debt/Equity < 50%)
        4. Reasonable valuation (PE < 30, P/B < 5)
        """
        if not metrics or metrics['market_cap'] < 10_000_000_000:  # Min $10B market cap
            return False
        
        # Quality checks
        checks = [
            metrics.get('roe', 0) > 0.15,  # ROE > 15%
            metrics.get('profit_margin', 0) > 0.10,  # Profit margin > 10%
            metrics.get('debt_to_equity', 100) < 50,  # D/E < 50%
            0 < metrics.get('pe_ratio', 0) < 30,  # Reasonable PE
            metrics.get('price_to_book', 10) < 5,  # P/B < 5
        ]
        
        return sum(checks) >= 4  # Must pass at least 4 out of 5 criteria
    
    def get_top_picks(self, count: int = 25) -> List[Dict]:
        """
        Get top stock picks using Buffett-Munger strategy
        
        Args:
            count: Number of stocks to select (default 25)
            
        Returns:
            List of stock dictionaries with metrics and allocation
        """
        logger.info("Running Buffett-Munger strategy stock selection...")
        
        qualified_stocks = []
        
        # Screen all stocks in universe
        for symbol in self.UNIVERSE:
            metrics = self._get_financial_metrics(symbol)
            
            if metrics and self._meets_quality_criteria(metrics):
                qualified_stocks.append(metrics)
        
        # Sort by market cap (larger = more stable)
        qualified_stocks.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # Select top N stocks
        top_picks = qualified_stocks[:count]
        
        # Equal weighting
        allocation = 100.0 / len(top_picks) if top_picks else 0
        
        for stock in top_picks:
            stock['allocation'] = round(allocation, 2)
            stock['weight'] = f"{allocation:.1f}%"
        
        logger.info(f"Selected {len(top_picks)} stocks meeting Buffett-Munger criteria")
        
        return top_picks
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary with rebalancing info"""
        picks = self.get_top_picks()
        
        total_value = sum(p.get('market_cap', 0) for p in picks)
        avg_pe = sum(p.get('pe_ratio', 0) for p in picks) / len(picks) if picks else 0
        avg_roe = sum(p.get('roe', 0) for p in picks) / len(picks) if picks else 0
        
        return {
            'stocks': picks,
            'total_stocks': len(picks),
            'last_rebalance': self.last_rebalance_date.strftime('%Y-%m-%d'),
            'next_rebalance': self.next_rebalance_date.strftime('%Y-%m-%d'),
            'days_until_rebalance': (self.next_rebalance_date - datetime.now()).days,
            'strategy': 'Market Cap Top 25 - Quality Screener',
            'description': 'Top 25 companies by market cap meeting Buffett-Munger quality criteria',
            'avg_pe': round(avg_pe, 2),
            'avg_roe': round(avg_roe * 100, 2),
            'allocation_per_stock': round(100.0 / len(picks), 2) if picks else 0,
            'philosophy': 'Systematic screening: ROE >15%, Low debt, Reasonable valuation, Equal weighting'
        }

# Global instance
buffett_munger_strategy = BuffettMungerStrategy()
