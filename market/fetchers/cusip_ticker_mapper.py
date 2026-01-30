"""
CUSIP to Ticker Symbol Mapper
Maps CUSIP numbers to stock ticker symbols
"""

import logging
from typing import Optional, Dict
import requests

logger = logging.getLogger(__name__)

class CUSIPTickerMapper:
    """Map CUSIP numbers to ticker symbols"""
    
    # Common CUSIP to ticker mappings for major stocks
    KNOWN_MAPPINGS = {
        '037833100': 'AAPL',   # Apple Inc
        '060505104': 'BAC',    # Bank of America
        '084670702': 'BRK.B',  # Berkshire Hathaway B
        '025816109': 'AXP',    # American Express
        '191216100': 'KO',     # Coca-Cola
        '166764100': 'CVX',    # Chevron
        '674599105': 'OXY',    # Occidental Petroleum
        '500754106': 'KHC',    # Kraft Heinz
        '615369105': 'MCO',    # Moody's
        '92826C839': 'V',      # Visa
        '57636Q104': 'MA',     # Mastercard
        '26614N102': 'DVA',    # DaVita
        '02079K305': 'GOOGL',  # Alphabet Inc
        '30303M102': 'META',   # Meta Platforms
        '01609W102': 'BABA',   # Alibaba
        '82968B103': 'C',      # Citigroup
        '40412C101': 'HPQ',    # HP Inc
        '69608A108': 'PDD',    # Pinduoduo
        '64110W102': 'NTES',   # NetEase
    }
    
    def get_ticker(self, cusip: str) -> Optional[str]:
        """
        Get ticker symbol for a CUSIP
        
        Args:
            cusip: 9-character CUSIP identifier
        
        Returns:
            Ticker symbol or None
        """
        if not cusip or len(cusip) != 9:
            return None
        
        # Check known mappings first
        if cusip in self.KNOWN_MAPPINGS:
            return self.KNOWN_MAPPINGS[cusip]
        
        # Could add API lookup here for unknown CUSIPs
        # For now, return None for unknowns
        logger.debug(f"Unknown CUSIP: {cusip}")
        return None
    
    def add_tickers_to_holdings(self, holdings: list) -> list:
        """
        Add ticker symbols to holdings list
        
        Args:
            holdings: List of holding dicts with 'cusip' field
        
        Returns:
            Updated holdings list with 'ticker' field
        """
        for holding in holdings:
            cusip = holding.get('cusip')
            if cusip:
                ticker = self.get_ticker(cusip)
                holding['ticker'] = ticker
            else:
                holding['ticker'] = None
        
        return holdings


# Global instance
cusip_mapper = CUSIPTickerMapper()
