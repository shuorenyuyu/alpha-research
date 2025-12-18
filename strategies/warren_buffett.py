"""
Warren Buffett - Berkshire Hathaway Portfolio
Based on latest 13F filings (Q3 2025)
"""

import logging
from datetime import datetime
from typing import List, Dict
import yfinance as yf

logger = logging.getLogger(__name__)


class WarrenBuffettStrategy:
    """
    Warren Buffett's actual Berkshire Hathaway portfolio
    Based on public 13F filings
    """
    
    # Top holdings from Berkshire Hathaway 13F (Q3 2025)
    # Source: https://www.dataroma.com/m/holdings.php?m=BRK
    KNOWN_HOLDINGS = [
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'buy_date': '2016-05-01',
            'buy_price': 23.50,  # Split-adjusted average cost basis
            'weight': 47.8,  # ~47.8% of portfolio
            'notes': 'Largest position, started Q2 2016'
        },
        {
            'symbol': 'BAC',
            'name': 'Bank of America',
            'buy_date': '2017-07-01',
            'buy_price': 24.00,
            'weight': 10.2,
            'notes': 'Second largest, accumulated 2017-2019'
        },
        {
            'symbol': 'AXP',
            'name': 'American Express',
            'buy_date': '1991-01-01',
            'buy_price': 8.50,  # Split-adjusted
            'weight': 7.9,
            'notes': 'Held since 1991, over 30 years'
        },
        {
            'symbol': 'KO',
            'name': 'Coca-Cola',
            'buy_date': '1988-01-01',
            'buy_price': 2.50,  # Split-adjusted
            'weight': 6.8,
            'notes': 'Iconic position since 1988, 36+ years'
        },
        {
            'symbol': 'CVX',
            'name': 'Chevron Corporation',
            'buy_date': '2020-10-01',
            'buy_price': 75.00,
            'weight': 5.4,
            'notes': 'Major energy position, started Q4 2020'
        },
        {
            'symbol': 'OXY',
            'name': 'Occidental Petroleum',
            'buy_date': '2022-03-01',
            'buy_price': 56.00,
            'weight': 4.9,
            'notes': 'Aggressive accumulation 2022-2023'
        },
        {
            'symbol': 'KHC',
            'name': 'Kraft Heinz',
            'buy_date': '2015-06-01',
            'buy_price': 72.50,
            'weight': 3.2,
            'notes': 'Helped merge Kraft & Heinz in 2015'
        },
        {
            'symbol': 'MCO',
            'name': "Moody's Corporation",
            'buy_date': '2000-01-01',
            'buy_price': 24.00,  # Split-adjusted
            'weight': 2.4,
            'notes': 'Held since 2000, 25+ years'
        },
        {
            'symbol': 'DVA',
            'name': 'DaVita Inc.',
            'buy_date': '2011-01-01',
            'buy_price': 75.00,
            'weight': 1.8,
            'notes': 'Healthcare services position'
        },
        {
            'symbol': 'V',
            'name': 'Visa Inc.',
            'buy_date': '2011-01-01',
            'buy_price': 85.00,  # Split-adjusted
            'weight': 1.5,
            'notes': 'Payment processing leader'
        },
        {
            'symbol': 'MA',
            'name': 'Mastercard Inc.',
            'buy_date': '2011-01-01',
            'buy_price': 280.00,  # Split-adjusted
            'weight': 1.2,
            'notes': 'Duopoly with Visa'
        },
        {
            'symbol': 'LSXMA',
            'name': 'Liberty Media Corp-Liberty SiriusXM',
            'buy_date': '2016-01-01',
            'buy_price': 35.00,
            'weight': 1.1,
            'notes': 'Media investment'
        },
        {
            'symbol': 'LSXMK',
            'name': 'Liberty Media Corp-Liberty SiriusXM',
            'buy_date': '2016-01-01',
            'buy_price': 35.00,
            'weight': 0.9,
            'notes': 'Media investment (Class K)'
        },
        {
            'symbol': 'HPQ',
            'name': 'HP Inc.',
            'buy_date': '2022-04-01',
            'buy_price': 37.00,
            'weight': 0.8,
            'notes': 'Recent tech hardware position'
        },
        {
            'symbol': 'C',
            'name': 'Citigroup Inc.',
            'buy_date': '2022-01-01',
            'buy_price': 60.00,
            'weight': 0.7,
            'notes': 'Banking sector play'
        }
    ]
    
    def __init__(self):
        self.strategy_name = "Warren Buffett - Berkshire Hathaway"
        self.description = "The Oracle of Omaha's actual portfolio. Focus on quality, moat, and long-term value."
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
            return {'gain_loss': 0.0, 'return_pct': 0.0, 'multiple': 0.0}
        
        gain_loss = current_price - buy_price
        return_pct = (gain_loss / buy_price) * 100
        multiple = current_price / buy_price
        
        return {
            'gain_loss': round(gain_loss, 2),
            'return_pct': round(return_pct, 2),
            'multiple': round(multiple, 2)
        }
    
    def get_portfolio(self) -> List[Dict]:
        """Get Warren Buffett's portfolio with current prices and returns"""
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
                'multiple': returns['multiple'],
                'holding_period_years': holding_years,
                'notes': holding['notes']
            })
        
        logger.info(f"Retrieved Warren Buffett portfolio: {len(portfolio)} holdings")
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
        
        # Find best performer
        best_stock = max(portfolio, key=lambda x: x['return_pct']) if portfolio else None
        
        return {
            'stocks': portfolio,
            'total_stocks': len(portfolio),
            'strategy': self.strategy_name,
            'description': self.description,
            'weighted_avg_return': round(weighted_return, 2),
            'avg_holding_years': round(avg_holding_years, 1),
            'winners': winners,
            'losers': len(portfolio) - winners,
            'best_performer': {
                'symbol': best_stock['symbol'],
                'return': best_stock['return_pct'],
                'multiple': best_stock['multiple']
            } if best_stock else None,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M'),
            'philosophy': 'Buy wonderful companies at fair prices and hold forever. Circle of competence.'
        }


# Global instance
warren_buffett_strategy = WarrenBuffettStrategy()
