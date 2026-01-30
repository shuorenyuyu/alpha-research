"""
Live Portfolio API Routes
Fetch real-time institutional holdings from 13F filings
NOTE: Currently using Q3 2024 mock data - production version will use real-time API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from market.fetchers.live_13f_mock import live_13f_mock

router = APIRouter(prefix="/api/live-portfolio", tags=["live-portfolio"])
logger = logging.getLogger(__name__)


@router.get("/warren-buffett")
async def get_live_warren_buffett() -> Dict[str, Any]:
    """
    Get Warren Buffett's LIVE portfolio from latest 13F filing
    
    Data source: SEC 13F-HR filings for Berkshire Hathaway
    Updated quarterly within 45 days of quarter end.
    
    NOTE: Currently using Q3 2024 data. Production version will fetch real-time from SEC/aggregator API.
    
    Returns actual holdings with current market values and weights.
    """
    try:
        logger.info("Fetching live Warren Buffett portfolio...")
        
        summary = live_13f_mock.get_portfolio_summary('warren_buffett')
        
        if summary['status'] != 'success':
            raise HTTPException(status_code=500, detail=summary.get('message', 'Failed to fetch portfolio'))
        
        return {
            'investor': summary['investor'],
            'report_date': summary.get('report_date'),
            'data_source': summary['data_source'],
            'total_holdings': summary['total_holdings'],
            'total_value_usd': summary['total_value_usd'],
            'total_value_billions': round(summary['total_value_usd'] / 1_000_000_000, 2),
            'holdings': summary['holdings'],
            'note': 'Q3 2024 13F data. Production version will auto-update quarterly from SEC API.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching live Buffett portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live portfolio: {str(e)}")


@router.get("/li-lu")
async def get_live_li_lu() -> Dict[str, Any]:
    """
    Get Li Lu's LIVE portfolio from latest 13F filing
    
    Data source: SEC 13F-HR filings for Himalaya Capital
    Updated quarterly within 45 days of quarter end.
    
    NOTE: Currently using Q3 2024 data - shows PDD holding! Production version will fetch real-time.
    
    Returns actual holdings with current market values and weights.
    """
    try:
        logger.info("Fetching live Li Lu portfolio...")
        
        summary = live_13f_mock.get_portfolio_summary('li_lu')
        
        if summary['status'] != 'success':
            raise HTTPException(status_code=500, detail=summary.get('message', 'Failed to fetch portfolio'))
        
        return {
            'investor': summary['investor'],
            'report_date': summary.get('report_date'),
            'data_source': summary['data_source'],
            'total_holdings': summary['total_holdings'],
            'total_value_usd': summary['total_value_usd'],
            'total_value_millions': round(summary['total_value_usd'] / 1_000_000, 2),
            'holdings': summary['holdings'],
            'note': 'Q3 2024 13F data including PDD position. Production version will auto-update quarterly.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching live Li Lu portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live portfolio: {str(e)}")


@router.get("/compare")
async def compare_investors() -> Dict[str, Any]:
    """
    Compare holdings across multiple investors
    
    Shows overlapping positions and unique holdings.
    """
    try:
        buffett_data = await get_live_warren_buffett()
        li_lu_data = await get_live_li_lu()
        
        # Extract tickers
        buffett_tickers = {h['ticker'] for h in buffett_data['holdings']}
        li_lu_tickers = {h['ticker'] for h in li_lu_data['holdings']}
        
        # Find overlaps
        common_holdings = buffett_tickers & li_lu_tickers
        buffett_only = buffett_tickers - li_lu_tickers
        li_lu_only = li_lu_tickers - buffett_tickers
        
        # Get detailed info for common holdings
        common_details = []
        for ticker in common_holdings:
            buffett_holding = next((h for h in buffett_data['holdings'] if h['ticker'] == ticker), None)
            li_lu_holding = next((h for h in li_lu_data['holdings'] if h['ticker'] == ticker), None)
            
            if buffett_holding and li_lu_holding:
                common_details.append({
                    'ticker': ticker,
                    'name': buffett_holding['name'],
                    'buffett_weight': buffett_holding['weight_pct'],
                    'li_lu_weight': li_lu_holding['weight_pct'],
                    'buffett_value_millions': buffett_holding['value_millions'],
                    'li_lu_value_millions': li_lu_holding['value_millions']
                })
        
        # Sort by combined importance
        common_details.sort(key=lambda x: x['buffett_weight'] + x['li_lu_weight'], reverse=True)
        
        return {
            'report_date': buffett_data.get('report_date'),
            'investors': {
                'warren_buffett': {
                    'total_value_billions': buffett_data['total_value_billions'],
                    'total_holdings': buffett_data['total_holdings'],
                    'report_date': buffett_data.get('report_date')
                },
                'li_lu': {
                    'total_value_millions': li_lu_data['total_value_millions'],
                    'total_holdings': li_lu_data['total_holdings'],
                    'report_date': li_lu_data.get('report_date')
                }
            },
            'common_holdings': common_details,
            'common_count': len(common_holdings),
            'buffett_only': sorted(list(buffett_only)),
            'li_lu_only': sorted(list(li_lu_only)),
            'overlap_rate': round((len(common_holdings) / len(buffett_tickers)) * 100, 1) if buffett_tickers else 0
        }
        
    except Exception as e:
        logger.error(f"Error comparing portfolios: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare: {str(e)}")
