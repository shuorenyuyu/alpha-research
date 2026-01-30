"""
SEC 13F Filing Fetcher
Fetches institutional holdings from SEC EDGAR 13F filings
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class SEC13FFetcher:
    """Fetch 13F filings from SEC EDGAR"""
    
    BASE_URL = "https://data.sec.gov"
    
    # CIK numbers for major investors
    INVESTORS = {
        'warren_buffett': {
            'cik': '0001067983',  # Berkshire Hathaway Inc.
            'name': 'Berkshire Hathaway Inc.'
        },
        'li_lu': {
            'cik': '0001422183',  # Himalaya Capital Ventures LP
            'name': 'Himalaya Capital Ventures LP'
        }
    }
    
    def __init__(self):
        """Initialize SEC fetcher with proper headers"""
        self.headers = {
            'User-Agent': 'Alpha Research Platform contact@alpha-research.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
    
    def get_latest_13f_filings(self, investor_key: str) -> Optional[Dict]:
        """
        Get latest 13F-HR filing for an investor
        
        Args:
            investor_key: Key from INVESTORS dict ('warren_buffett', 'li_lu')
        
        Returns:
            Dict with filing metadata or None
        """
        if investor_key not in self.INVESTORS:
            logger.error(f"Unknown investor: {investor_key}")
            return None
        
        investor = self.INVESTORS[investor_key]
        cik = investor['cik']
        
        # Get submissions for this CIK
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find latest 13F-HR filing
            recent_filings = data.get('filings', {}).get('recent', {})
            forms = recent_filings.get('form', [])
            
            for i, form in enumerate(forms):
                if form == '13F-HR':
                    return {
                        'accession_number': recent_filings['accessionNumber'][i],
                        'filing_date': recent_filings['filingDate'][i],
                        'report_date': recent_filings['reportDate'][i],
                        'primary_document': recent_filings['primaryDocument'][i],
                        'cik': cik
                    }
            
            logger.warning(f"No 13F-HR filings found for {investor['name']}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching 13F filings for {investor_key}: {e}")
            return None
    
    def get_13f_holdings(self, investor_key: str) -> List[Dict]:
        """
        Get holdings from latest 13F filing
        
        Args:
            investor_key: Key from INVESTORS dict
        
        Returns:
            List of holdings with symbols, values, shares
        """
        filing = self.get_latest_13f_filings(investor_key)
        if not filing:
            return []
        
        # SEC format: CIK without leading zeros, accession with dashes
        cik = filing['cik'].lstrip('0')
        accession = filing['accession_number']
        
        # Primary document is usually the main filing
        # Try multiple possible file names
        possible_files = [
            'infotable.xml',
            'information-table.xml',
            'primary_doc.xml',
            filing.get('primary_document', '').replace('.htm', '.xml')
        ]
        
        for filename in possible_files:
            if not filename:
                continue
                
            info_table_url = f"{self.BASE_URL}/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{filename}"
            
            try:
                time.sleep(0.1)  # Rate limiting - be nice to SEC
                response = requests.get(info_table_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    holdings = self._parse_info_table_xml(response.text)
                    if holdings:
                        logger.info(f"Fetched {len(holdings)} holdings for {investor_key} from {filing['filing_date']}")
                        return holdings
                        
            except Exception as e:
                logger.debug(f"Failed to fetch {filename}: {e}")
                continue
        
        # If XML not found, try to parse the primary HTML document
        logger.warning(f"Could not find XML information table, trying primary document")
        return self._try_parse_primary_document(cik, accession, filing)
    
    def _parse_info_table_xml(self, xml_content: str) -> List[Dict]:
        """
        Parse SEC 13F information table XML
        
        Args:
            xml_content: Raw XML string
        
        Returns:
            List of holding dicts
        """
        import xml.etree.ElementTree as ET
        
        holdings = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # SEC XML uses namespace
            ns = {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}
            
            for info_table in root.findall('.//ns:infoTable', ns):
                try:
                    name_elem = info_table.find('.//ns:nameOfIssuer', ns)
                    ticker_elem = info_table.find('.//ns:titleOfClass', ns)
                    cusip_elem = info_table.find('.//ns:cusip', ns)
                    value_elem = info_table.find('.//ns:value', ns)
                    shares_elem = info_table.find('.//ns:sshPrnamt', ns)
                    
                    if name_elem is not None and value_elem is not None:
                        holding = {
                            'name': name_elem.text,
                            'cusip': cusip_elem.text if cusip_elem is not None else None,
                            'value_usd': int(value_elem.text) * 1000,  # SEC reports in thousands
                            'shares': int(shares_elem.text) if shares_elem is not None else None,
                            'title_of_class': ticker_elem.text if ticker_elem is not None else None
                        }
                        holdings.append(holding)
                        
                except Exception as e:
                    logger.warning(f"Error parsing holding entry: {e}")
                    continue
            
            # Sort by value descending
            holdings.sort(key=lambda x: x['value_usd'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
        
        return holdings
    
    def _try_parse_primary_document(self, cik: str, accession: str, filing: Dict) -> List[Dict]:
        """
        Try to parse holdings from primary HTML/XML document as fallback
        
        Args:
            cik: Company CIK
            accession: Accession number with dashes
            filing: Filing metadata
        
        Returns:
            List of holdings or empty list
        """
        try:
            # Get the filing detail page
            primary_doc = filing.get('primary_document', '')
            if not primary_doc:
                return []
            
            doc_url = f"{self.BASE_URL}/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{primary_doc}"
            
            time.sleep(0.1)
            response = requests.get(doc_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Try to extract from the HTML/XML table
                # This is a simplified parser - may need enhancement
                content = response.text
                
                # Look for XML within HTML
                if '<XML>' in content.upper():
                    start = content.upper().find('<XML>')
                    end = content.upper().find('</XML>', start)
                    if start != -1 and end != -1:
                        xml_content = content[start:end+6]
                        return self._parse_info_table_xml(xml_content)
            
            logger.warning("Could not parse primary document")
            return []
            
        except Exception as e:
            logger.error(f"Error parsing primary document: {e}")
            return []
    
    def get_portfolio_summary(self, investor_key: str, top_n: int = 15) -> Dict:
        """
        Get formatted portfolio summary
        
        Args:
            investor_key: Investor identifier
            top_n: Number of top holdings to return
        
        Returns:
            Dict with portfolio data and metadata
        """
        filing = self.get_latest_13f_filings(investor_key)
        if not filing:
            return {
                'investor': self.INVESTORS.get(investor_key, {}).get('name'),
                'status': 'error',
                'message': 'No 13F filing found'
            }
        
        holdings = self.get_13f_holdings(investor_key)
        
        total_value = sum(h['value_usd'] for h in holdings)
        
        # Calculate weights for top holdings
        top_holdings = holdings[:top_n]
        for holding in top_holdings:
            holding['weight_pct'] = round((holding['value_usd'] / total_value) * 100, 2) if total_value > 0 else 0
        
        return {
            'investor': self.INVESTORS[investor_key]['name'],
            'filing_date': filing['filing_date'],
            'report_date': filing['report_date'],
            'total_holdings': len(holdings),
            'total_value_usd': total_value,
            'top_holdings': top_holdings,
            'status': 'success'
        }


# Global instance
sec_13f_fetcher = SEC13FFetcher()
