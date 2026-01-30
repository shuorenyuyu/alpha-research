"""
Live 13F Portfolio Data Mock
Shows how automated portfolio fetching would work
This is a proof-of-concept - production version would use real-time API
"""

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Live13FPortfolioMock:
    """Mock portfolio data showing latest Q3 2024 holdings"""
    
    # Latest data from Q3 2024 13F filings
    PORTFOLIOS = {
        'warren_buffett': {
            'investor': 'Warren Buffett - Berkshire Hathaway',
            'report_date': '09/30/2024',
            'total_value_usd': 370_000_000_000,  # $370B approximate
            'holdings': [
                {'ticker': 'AAPL', 'name': 'Apple Inc', 'shares': 300000000, 'value_millions': 67500, 'weight_pct': 42.2},
                {'ticker': 'BAC', 'name': 'Bank of America Corp', 'shares': 1032852006, 'value_millions': 41300, 'weight_pct': 12.9},
                {'ticker': 'AXP', 'name': 'American Express Co', 'shares': 151610700, 'value_millions': 40300, 'weight_pct': 12.6},
                {'ticker': 'KO', 'name': 'Coca-Cola Co', 'shares': 400000000, 'value_millions': 28100, 'weight_pct': 8.8},
                {'ticker': 'CVX', 'name': 'Chevron Corp', 'shares': 123117156, 'value_millions': 18700, 'weight_pct': 5.9},
                {'ticker': 'OXY', 'name': 'Occidental Petroleum Corp', 'shares': 255281624, 'value_millions': 15400, 'weight_pct': 4.8},
                {'ticker': 'KHC', 'name': 'Kraft Heinz Co', 'shares': 325634818, 'value_millions': 10700, 'weight_pct': 3.3},
                {'ticker': 'MCO', 'name': "Moody's Corp", 'shares': 24669778, 'value_millions': 10300, 'weight_pct': 3.2},
                {'ticker': 'DVA', 'name': 'DaVita Inc', 'shares': 36095570, 'value_millions': 4900, 'weight_pct': 1.5},
                {'ticker': 'C', 'name': 'Citigroup Inc', 'shares': 55155797, 'value_millions': 3400, 'weight_pct': 1.1},
                {'ticker': 'V', 'name': 'Visa Inc', 'shares': 8297383, 'value_millions': 2200, 'weight_pct': 0.7},
                {'ticker': 'MA', 'name': 'Mastercard Inc', 'shares': 3986648, 'value_millions': 1900, 'weight_pct': 0.6},
                {'ticker': 'HPQ', 'name': 'HP Inc', 'shares': 104476301, 'value_millions': 3800, 'weight_pct': 1.2},
            ]
        },
        'li_lu': {
            'investor': 'Li Lu - Himalaya Capital',
            'report_date': '09/30/2024',
            'total_value_usd': 1_200_000_000,  # $1.2B approximate
            'holdings': [
                {'ticker': 'BAC', 'name': 'Bank of America Corp', 'shares': 7500000, 'value_millions': 300.0, 'weight_pct': 25.0},
                {'ticker': 'AAPL', 'name': 'Apple Inc', 'shares': 1000000, 'value_millions': 225.0, 'weight_pct': 18.8},
                {'ticker': 'GOOGL', 'name': 'Alphabet Inc', 'shares': 1200000, 'value_millions': 168.0, 'weight_pct': 14.0},
                {'ticker': 'BABA', 'name': 'Alibaba Group', 'shares': 1500000, 'value_millions': 135.0, 'weight_pct': 11.3},
                {'ticker': 'BRK.B', 'name': 'Berkshire Hathaway B', 'shares': 300000, 'value_millions': 120.0, 'weight_pct': 10.0},
                {'ticker': 'META', 'name': 'Meta Platforms', 'shares': 200000, 'value_millions': 96.0, 'weight_pct': 8.0},
                {'ticker': 'PDD', 'name': 'Pinduoduo Inc', 'shares': 500000, 'value_millions': 72.0, 'weight_pct': 6.0},
                {'ticker': 'NTES', 'name': 'NetEase Inc ADR', 'shares': 400000, 'value_millions': 48.0, 'weight_pct': 4.0},
            ]
        }
    }
    
    def get_portfolio_summary(self, investor_key: str) -> Dict:
        """
        Get portfolio summary for an investor
        
        Args:
            investor_key: 'warren_buffett' or 'li_lu'
        
        Returns:
            Dict with holdings and metadata
        """
        if investor_key not in self.PORTFOLIOS:
            return {
                'status': 'error',
                'message': f'Unknown investor: {investor_key}'
            }
        
        portfolio = self.PORTFOLIOS[investor_key]
        
        # Calculate value_usd for each holding
        holdings = []
        for h in portfolio['holdings']:
            holding = h.copy()
            holding['value_usd'] = int(h['value_millions'] * 1_000_000)
            holdings.append(holding)
        
        return {
            'status': 'success',
            'investor': portfolio['investor'],
            'report_date': portfolio['report_date'],
            'data_source': 'Q3 2024 13F Filing (Mock Data - Production will use real-time API)',
            'total_holdings': len(holdings),
            'total_value_usd': portfolio['total_value_usd'],
            'holdings': holdings
        }


# Global instance
live_13f_mock = Live13FPortfolioMock()
