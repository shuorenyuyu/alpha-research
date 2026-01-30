"""
Dataroma Portfolio Scraper
Scrapes portfolio holdings from dataroma.com which aggregates 13F filings
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class DataromaPortfolioScraper:
    """Scrape portfolio holdings from Dataroma"""
    
    BASE_URL = "https://www.dataroma.com"
    
    # Investor IDs on Dataroma
    INVESTORS = {
        'warren_buffett': {
            'id': 'BRK',
            'name': 'Warren Buffett - Berkshire Hathaway'
        },
        'li_lu': {
            'id': 'HimalayaCapital',
            'name': 'Li Lu - Himalaya Capital'
        }
    }
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def get_portfolio(self, investor_key: str) -> List[Dict]:
        """
        Get portfolio holdings for an investor
        
        Args:
            investor_key: Key from INVESTORS dict
        
        Returns:
            List of holdings with ticker, name, value, weight
        """
        if investor_key not in self.INVESTORS:
            logger.error(f"Unknown investor: {investor_key}")
            return []
        
        investor_id = self.INVESTORS[investor_key]['id']
        url = f"{self.BASE_URL}/m/holdings.php?m={investor_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the holdings table
            table = soup.find('table', {'id': 'grid'})
            if not table:
                logger.warning(f"Holdings table not found for {investor_key}")
                return []
            
            holdings = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 6:
                    continue
                
                try:
                    # Extract ticker from link
                    ticker_link = cols[1].find('a')
                    ticker = ticker_link.text.strip() if ticker_link else None
                    
                    # Extract company name
                    name_link = cols[0].find('a')
                    name = name_link.text.strip() if name_link else None
                    
                    # Extract portfolio weight
                    weight_text = cols[3].text.strip().replace('%', '')
                    weight_pct = float(weight_text) if weight_text else 0.0
                    
                    # Extract value
                    value_text = cols[4].text.strip().replace('$', '').replace(',', '')
                    value_millions = float(value_text) if value_text else 0.0
                    value_usd = int(value_millions * 1_000_000)
                    
                    # Extract shares
                    shares_text = cols[2].text.strip().replace(',', '')
                    shares = int(shares_text) if shares_text else None
                    
                    if ticker and name:
                        holding = {
                            'ticker': ticker,
                            'name': name,
                            'shares': shares,
                            'value_usd': value_usd,
                            'value_millions': value_millions,
                            'weight_pct': weight_pct
                        }
                        holdings.append(holding)
                        
                except Exception as e:
                    logger.warning(f"Error parsing row: {e}")
                    continue
            
            logger.info(f"Scraped {len(holdings)} holdings for {investor_key} from Dataroma")
            return holdings
            
        except Exception as e:
            logger.error(f"Error scraping Dataroma for {investor_key}: {e}")
            return []
    
    def get_portfolio_metadata(self, investor_key: str) -> Dict:
        """
        Get portfolio metadata (filing date, total value, etc.)
        
        Args:
            investor_key: Investor identifier
        
        Returns:
            Dict with metadata
        """
        if investor_key not in self.INVESTORS:
            return {}
        
        investor_id = self.INVESTORS[investor_key]['id']
        url = f"{self.BASE_URL}/m/holdings.php?m={investor_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            metadata = {
                'investor': self.INVESTORS[investor_key]['name'],
                'data_source': 'Dataroma (SEC 13F aggregator)'
            }
            
            # Extract filing date from page
            date_div = soup.find('div', string=re.compile(r'Portfolio as of'))
            if date_div:
                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', date_div.text)
                if date_match:
                    metadata['report_date'] = date_match.group(1)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            return {}
    
    def get_portfolio_summary(self, investor_key: str) -> Dict:
        """
        Get complete portfolio summary
        
        Args:
            investor_key: Investor identifier
        
        Returns:
            Dict with holdings and metadata
        """
        holdings = self.get_portfolio(investor_key)
        metadata = self.get_portfolio_metadata(investor_key)
        
        if not holdings:
            return {
                'status': 'error',
                'message': 'No holdings found',
                'investor': metadata.get('investor', 'Unknown')
            }
        
        total_value = sum(h['value_usd'] for h in holdings)
        
        return {
            'status': 'success',
            'investor': metadata.get('investor'),
            'report_date': metadata.get('report_date'),
            'data_source': metadata.get('data_source'),
            'total_holdings': len(holdings),
            'total_value_usd': total_value,
            'holdings': holdings
        }


# Global instance
dataroma_scraper = DataromaPortfolioScraper()
