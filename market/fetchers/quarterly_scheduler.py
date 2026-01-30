"""
Quarterly 13F Update Scheduler

Automatically fetches new 13F filings on a quarterly basis:
- Q1 ends March 31 → Filing due by May 15
- Q2 ends June 30 → Filing due by August 15
- Q3 ends September 30 → Filing due by November 15
- Q4 ends December 31 → Filing due by February 15

This scheduler can be run as:
1. Cron job: Run daily, checks if filing is available
2. Manual trigger: Force update via API
3. Startup check: Check on server startup
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

from market.fetchers.sec_edgar_api import sec_edgar_api
from market.fetchers.cusip_ticker_mapper import cusip_mapper
from market.fetchers.live_13f_mock import live_13f_mock

logger = logging.getLogger(__name__)


class QuarterlyFilingScheduler:
    """Manages automatic quarterly 13F filing updates"""
    
    # Filing deadlines: 45 days after quarter end
    QUARTER_ENDS = {
        'Q1': ('03', '31'),
        'Q2': ('06', '30'),
        'Q3': ('09', '30'),
        'Q4': ('12', '31')
    }
    
    FILING_DEADLINE_DAYS = 45
    
    def __init__(self, data_dir: str = "data/13f_filings"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.data_dir / "update_status.json"
        self.load_status()
    
    def load_status(self):
        """Load last update status"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        else:
            self.status = {
                'last_check': None,
                'last_updates': {},
                'next_expected': {}
            }
    
    def save_status(self):
        """Save update status"""
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def get_current_quarter(self) -> tuple[str, str]:
        """Get current quarter and year"""
        now = datetime.now()
        quarter = f"Q{(now.month - 1) // 3 + 1}"
        year = str(now.year)
        return quarter, year
    
    def get_filing_deadline(self, quarter: str, year: str) -> datetime:
        """Get filing deadline for a quarter"""
        month, day = self.QUARTER_ENDS[quarter]
        quarter_end = datetime(int(year), int(month), int(day))
        return quarter_end + timedelta(days=self.FILING_DEADLINE_DAYS)
    
    def should_check_for_updates(self, investor: str) -> bool:
        """
        Determine if we should check for new filings
        
        Logic:
        - Always check if never checked
        - Check once per day if within filing window
        - Check once per week outside filing window
        """
        last_check = self.status.get('last_check')
        if not last_check:
            return True
        
        last_check_date = datetime.fromisoformat(last_check)
        now = datetime.now()
        
        # Check if we're in filing window (quarter end + 15 to 50 days)
        current_quarter, current_year = self.get_current_quarter()
        filing_deadline = self.get_filing_deadline(current_quarter, current_year)
        
        days_since_check = (now - last_check_date).days
        
        # Within 50 days after quarter end: check daily
        if now < filing_deadline + timedelta(days=5):
            return days_since_check >= 1
        
        # Outside window: check weekly
        return days_since_check >= 7
    
    def check_and_update_filings(self, investors: List[str] = None) -> Dict[str, any]:
        """
        Check for new filings and update if available
        
        Args:
            investors: List of investor names, defaults to all
        
        Returns:
            Dict with update status for each investor
        """
        if investors is None:
            investors = ['warren_buffett', 'li_lu']
        
        results = {}
        
        for investor in investors:
            if not self.should_check_for_updates(investor):
                results[investor] = {
                    'status': 'skipped',
                    'reason': 'Too soon since last check'
                }
                continue
            
            try:
                logger.info(f"Checking for {investor} 13F updates...")
                
                # Fetch latest filing from SEC
                filing_data = sec_edgar_api.get_latest_13f(investor)
                
                if not filing_data:
                    results[investor] = {
                        'status': 'no_filing',
                        'reason': 'No filings found or parsing error'
                    }
                    continue
                
                # Check if this is newer than last update
                last_update = self.status['last_updates'].get(investor, {}).get('report_period')
                current_period = filing_data.get('report_period')
                
                if last_update and current_period <= last_update:
                    results[investor] = {
                        'status': 'unchanged',
                        'current_period': current_period,
                        'reason': f'Already have {current_period} filing'
                    }
                    continue
                
                # Map CUSIPs to tickers
                holdings_with_tickers = cusip_mapper.add_tickers_to_holdings(
                    filing_data['holdings']
                )
                
                # Save filing data
                self._save_filing_data(investor, filing_data, holdings_with_tickers)
                
                # Update status
                self.status['last_updates'][investor] = {
                    'report_period': current_period,
                    'updated_at': datetime.now().isoformat(),
                    'holdings_count': len(holdings_with_tickers),
                    'total_value': filing_data['total_value']
                }
                
                results[investor] = {
                    'status': 'updated',
                    'report_period': current_period,
                    'holdings_count': len(holdings_with_tickers),
                    'total_value': filing_data['total_value']
                }
                
                logger.info(f"✅ Updated {investor} to {current_period} ({len(holdings_with_tickers)} holdings)")
                
            except Exception as e:
                logger.error(f"Error updating {investor}: {e}")
                results[investor] = {
                    'status': 'error',
                    'reason': str(e)
                }
        
        # Update last check time
        self.status['last_check'] = datetime.now().isoformat()
        self.save_status()
        
        return results
    
    def _save_filing_data(self, investor: str, filing_data: dict, holdings: list):
        """Save filing data to JSON file"""
        period = filing_data['report_period']
        filename = self.data_dir / f"{investor}_{period}.json"
        
        data = {
            **filing_data,
            'holdings_with_tickers': holdings,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {investor} filing to {filename}")
    
    def get_next_filing_date(self) -> Dict[str, str]:
        """Get expected date for next filing"""
        current_quarter, current_year = self.get_current_quarter()
        
        # Determine next quarter
        quarter_map = {'Q1': 'Q2', 'Q2': 'Q3', 'Q3': 'Q4', 'Q4': 'Q1'}
        next_quarter = quarter_map[current_quarter]
        next_year = current_year if next_quarter != 'Q1' else str(int(current_year) + 1)
        
        deadline = self.get_filing_deadline(next_quarter, next_year)
        
        return {
            'current_quarter': f"{current_quarter} {current_year}",
            'next_quarter': f"{next_quarter} {next_year}",
            'expected_filing_date': deadline.strftime('%Y-%m-%d'),
            'days_until_filing': (deadline - datetime.now()).days
        }
    
    def force_update(self, investor: str) -> Dict[str, any]:
        """Force immediate update for an investor"""
        logger.info(f"Force updating {investor}...")
        return self.check_and_update_filings([investor])
    
    def get_status_summary(self) -> Dict[str, any]:
        """Get summary of current status"""
        return {
            'last_check': self.status.get('last_check'),
            'last_updates': self.status.get('last_updates', {}),
            'next_filing': self.get_next_filing_date(),
            'data_directory': str(self.data_dir)
        }


# Global instance
filing_scheduler = QuarterlyFilingScheduler()


# CLI tool for manual updates
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 Force updating all 13F filings...")
        results = filing_scheduler.force_update('warren_buffett')
        results.update(filing_scheduler.force_update('li_lu'))
    else:
        print("🔍 Checking for 13F filing updates...")
        results = filing_scheduler.check_and_update_filings()
    
    print("\n📊 Update Results:")
    print(json.dumps(results, indent=2))
    
    print("\n📅 Next Filing Info:")
    print(json.dumps(filing_scheduler.get_next_filing_date(), indent=2))
