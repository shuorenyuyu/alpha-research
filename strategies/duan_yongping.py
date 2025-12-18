"""
Duan Yongping (段永平) Portfolio Strategy
Based on public disclosures and interviews
"""

import logging
from datetime import datetime
from typing import List, Dict
import yfinance as yf

logger = logging.getLogger(__name__)


class DuanYongpingStrategy:
    """
    Duan Yongping's investment strategy
    Known for: Lunch with Buffett, heavy Apple position, focus on business quality
    Famous for: "Don't do things you don't understand"
    """
    
    # Known holdings based on public disclosures and interviews
    KNOWN_HOLDINGS = [
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'buy_date': '2011-01-01',  # Started accumulating around $10-12 (split-adjusted)
            'buy_price': 11.50,  # Split-adjusted average cost
            'weight': 50.0,  # Largest position, possibly 50%+ of portfolio
            'notes': 'Largest and most famous position, held since ~$10'
        },
        {
            'symbol': 'BRK-B',
            'name': 'Berkshire Hathaway',
            'buy_date': '2006-01-01',  # After lunch with Buffett
            'buy_price': 85.00,
            'weight': 15.0,
            'notes': 'Inspired by 2006 lunch with Buffett'
        },
        {
            'symbol': 'PDD',
            'name': 'Pinduoduo',
            'buy_date': '2018-08-01',  # Around IPO time
            'buy_price': 22.00,
            'weight': 12.0,
            'notes': 'Colin Huang (founder) connection, significant stake'
        },
        {
            'symbol': 'BABA',
            'name': 'Alibaba Group',
            'buy_date': '2014-10-01',  # Around IPO
            'buy_price': 90.00,
            'weight': 8.0,
            'notes': 'China tech exposure'
        },
        {
            'symbol': 'NTES',
            'name': 'NetEase',
            'buy_date': '2016-06-01',
            'buy_price': 220.00,
            'weight': 5.0,
            'notes': 'China gaming and internet'
        },
        {
            'symbol': 'GOOGL',
            'name': 'Alphabet Inc.',
            'buy_date': '2015-01-01',
            'buy_price': 520.00,  # Pre-split
            'weight': 5.0,
            'notes': 'Quality tech business'
        },
        {
            'symbol': 'TCEHY',
            'name': 'Tencent (ADR)',
            'buy_date': '2012-01-01',
            'buy_price': 40.00,
            'weight': 5.0,
            'notes': 'China tech giant, WeChat ecosystem'
        }
    ]
    
    def __init__(self):
        self.strategy_name = "Duan Yongping (段永平)"
        self.description = "极度集中投资，重仓苹果。'不做不懂的事情'"
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
        """Get Duan Yongping's portfolio with current prices and returns"""
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
        
        logger.info(f"Retrieved Duan Yongping portfolio: {len(portfolio)} holdings")
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
        
        # Find best performer
        best_stock = max(portfolio, key=lambda x: x['return_pct']) if portfolio else None
        
        return {
            'stocks': portfolio,
            'total_stocks': len(portfolio),
            'strategy': self.strategy_name,
            'description': self.description,
            'weighted_avg_return': round(weighted_return, 2),
            'avg_holding_years': round(avg_holding_years, 1),
            'best_performer': {
                'symbol': best_stock['symbol'],
                'return': best_stock['return_pct'],
                'multiple': best_stock['multiple']
            } if best_stock else None,
            'last_update': self.last_update.strftime('%Y-%m-%d %H:%M'),
            'philosophy': '极度集中，长期持有，只投资理解的公司'
        }


# Global instance
duan_yongping_strategy = DuanYongpingStrategy()
