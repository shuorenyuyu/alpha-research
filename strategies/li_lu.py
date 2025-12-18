"""
Li Lu (李录) Portfolio Strategy - Himalaya Capital
Based on public 13F filings and disclosed positions
"""

import logging
from datetime import datetime
from typing import List, Dict
import yfinance as yf

logger = logging.getLogger(__name__)


class LiLuStrategy:
    """
    Li Lu's investment strategy through Himalaya Capital
    Known for concentrated positions in high-quality businesses
    Charlie Munger's protégé and family fund manager
    """
    
    # Known holdings based on 13F filings and public disclosures
    # Format: (symbol, buy_date, buy_price_estimate, notes)
    KNOWN_HOLDINGS = [
        {
            'symbol': 'BAC',
            'name': 'Bank of America',
            'buy_date': '2009-03-01',  # Post-crisis accumulation
            'buy_price': 5.00,  # Estimated average cost basis
            'weight': 25.0,  # Percentage of portfolio
            'notes': 'Largest position, accumulated post-2008 crisis'
        },
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'buy_date': '2016-06-01',
            'buy_price': 95.00,  # Split-adjusted
            'weight': 20.0,
            'notes': 'Added following Buffett\'s lead'
        },
        {
            'symbol': 'BABA',
            'name': 'Alibaba Group',
            'buy_date': '2015-09-01',
            'buy_price': 70.00,
            'weight': 15.0,
            'notes': 'China tech exposure, held through volatility'
        },
        {
            'symbol': 'GOOGL',
            'name': 'Alphabet Inc.',
            'buy_date': '2017-01-01',
            'buy_price': 800.00,  # Pre-split
            'weight': 12.0,
            'notes': 'Quality tech business with moat'
        },
        {
            'symbol': 'BRK-B',
            'name': 'Berkshire Hathaway',
            'buy_date': '2010-01-01',
            'buy_price': 80.00,
            'weight': 10.0,
            'notes': 'Munger connection'
        },
        {
            'symbol': 'BYDDY',
            'name': 'BYD Company (ADR)',
            'buy_date': '2020-03-01',
            'buy_price': 35.00,
            'weight': 8.0,
            'notes': 'EV exposure, Munger favorite'
        },
        {
            'symbol': 'META',
            'name': 'Meta Platforms',
            'buy_date': '2022-11-01',  # Bottom fishing
            'buy_price': 95.00,
            'weight': 5.0,
            'notes': 'Added during 2022 selloff'
        },
        {
            'symbol': 'JD',
            'name': 'JD.com',
            'buy_date': '2018-06-01',
            'buy_price': 40.00,
            'weight': 5.0,
            'notes': 'China e-commerce'
        }
    ]
    
    def __init__(self):
        self.strategy_name = "Li Lu (李录) - Himalaya Capital"
        self.description = "Concentrated value investing in quality businesses. Charlie Munger's protégé."
        self.last_update = datetime.now()
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.warning(f"Failed to get price for {symbol}: {e}")
        return 0.0
    
    def _calculate_returns(self, buy_price: float, current_price: float) -> Dict:
        """Calculate returns and gain/loss"""
        if buy_price <= 0:
            return {'gain_loss': 0.0, 'return_pct': 0.0}
        
        gain_loss = current_price - buy_price
        return_pct = (gain_loss / buy_price) * 100
        
        return {
            'gain_loss': round(gain_loss, 2),
            'return_pct': round(return_pct, 2)
        }
    
    def get_portfolio(self) -> List[Dict]:
        """Get Li Lu's portfolio with current prices and returns"""
        portfolio = []
        
        for holding in self.KNOWN_HOLDINGS:
            current_price = self._get_current_price(holding['symbol'])
            returns = self._calculate_returns(holding['buy_price'], current_price)
            
            # Calculate holding period
            buy_date = datetime.strptime(holding['buy_date'], '%Y-%m-%d')
            holding_days = (datetime.now() - buy_date).days
            holding_years = round(holding_days / 365.25, 1)
            
            portfolio.append({
                'symbol': holding['symbol'],
                'name': holding['name'],
                'buy_date': holding['buy_date'],
                'buy_price': holding['buy_price'],
                'current_price': current_price,
                'weight': holding['weight'],
                'gain_loss': returns['gain_loss'],
                'return_pct': returns['return_pct'],
                'holding_period_years': holding_years,
                'notes': holding['notes']
            })
        
        logger.info(f"Retrieved Li Lu portfolio: {len(portfolio)} holdings")
        return portfolio
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary with performance metrics"""
        portfolio = self.get_portfolio()
        
        if not portfolio:
            return {
                'stocks': [],
                'total_stocks': 0,
                'strategy': self.strategy_name,
                'description': self.description
            }
        
        # Calculate weighted average return
        total_weight = sum(p['weight'] for p in portfolio)
        weighted_return = sum(p['return_pct'] * p['weight'] for p in portfolio) / total_weight if total_weight > 0 else 0
        
        # Average holding period
        avg_holding_years = sum(p['holding_period_years'] for p in portfolio) / len(portfolio)
        
        # Count winners vs losers
        winners = sum(1 for p in portfolio if p['return_pct'] > 0)
        
        return {
            'stocks': portfolio,
            'total_stocks': len(portfolio),
            'strategy': self.strategy_name,
            'description': self.description,
            'weighted_avg_return': round(weighted_return, 2),
            'avg_holding_years': round(avg_holding_years, 1),
            'winners': winners,
            'losers': len(portfolio) - winners,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M'),
            'philosophy': 'Concentrated positions, long holding periods, quality over quantity'
        }


# Global instance
li_lu_strategy = LiLuStrategy()
