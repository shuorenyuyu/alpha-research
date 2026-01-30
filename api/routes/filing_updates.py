"""
API routes for managing 13F filing updates

Provides endpoints for:
- Manual filing updates
- Check update status
- View filing history
- Force refresh
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from market.fetchers.quarterly_scheduler import filing_scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/13f-updates", tags=["13F Updates"])


@router.post("/check")
async def check_for_updates() -> Dict[str, Any]:
    """
    Check for new 13F filings and update if available
    
    This endpoint can be called manually or via cron job.
    Will respect rate limiting (daily/weekly checks).
    """
    try:
        logger.info("Manual check for 13F filing updates triggered")
        results = filing_scheduler.check_and_update_filings()
        
        return {
            'status': 'success',
            'results': results,
            'next_filing': filing_scheduler.get_next_filing_date()
        }
        
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/force/{investor}")
async def force_update(investor: str) -> Dict[str, Any]:
    """
    Force immediate update for a specific investor
    
    Args:
        investor: 'warren_buffett' or 'li_lu'
    
    Bypasses rate limiting and forces fetch from SEC.
    """
    if investor not in ['warren_buffett', 'li_lu']:
        raise HTTPException(status_code=400, detail=f"Unknown investor: {investor}")
    
    try:
        logger.info(f"Force update triggered for {investor}")
        results = filing_scheduler.force_update(investor)
        
        return {
            'status': 'success',
            'investor': investor,
            'result': results.get(investor, {}),
            'next_filing': filing_scheduler.get_next_filing_date()
        }
        
    except Exception as e:
        logger.error(f"Error forcing update for {investor}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get current update status and schedule
    
    Returns:
        - Last check time
        - Last update for each investor
        - Next expected filing date
        - Days until next filing
    """
    try:
        status = filing_scheduler.get_status_summary()
        return {
            'status': 'success',
            **status
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-filing")
async def get_next_filing_info() -> Dict[str, Any]:
    """
    Get information about next expected filing
    
    Returns quarter info and expected filing date.
    """
    try:
        next_filing = filing_scheduler.get_next_filing_date()
        return {
            'status': 'success',
            **next_filing
        }
        
    except Exception as e:
        logger.error(f"Error getting next filing info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
