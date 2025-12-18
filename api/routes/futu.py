"""
Futu API routes for account positions and trading
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from market.fetchers.futu_fetcher import futu_fetcher
from futu import TrdEnv
from ..logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

class Position(BaseModel):
    symbol: str
    name: str
    quantity: int
    canSellQty: int
    costPrice: float
    currentPrice: float
    marketValue: float
    profitLoss: float
    profitLossPercent: float
    currency: str
    updateTime: str

class AccountInfo(BaseModel):
    totalAssets: float
    cash: float
    marketValue: float
    frozenCash: float
    availableFunds: float
    currency: str
    updateTime: str

class FutuQuote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: int
    turnover: float
    high: float
    low: float
    open: float
    previousClose: float
    timestamp: str

@router.get("/positions", response_model=List[Position])
async def get_positions(
    env: str = Query("simulate", description="Trading environment: simulate or real")
):
    """
    Get current account positions/holdings
    
    - **env**: Trading environment (simulate or real)
    """
    try:
        trd_env = TrdEnv.REAL if env.lower() == "real" else TrdEnv.SIMULATE
        positions = futu_fetcher.get_account_positions(trd_env=trd_env)
        
        if not positions:
            return []
        
        logger.info(f"Retrieved {len(positions)} positions from {env} environment")
        return positions
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch positions: {str(e)}")

@router.get("/account", response_model=AccountInfo)
async def get_account_info(
    env: str = Query("simulate", description="Trading environment: simulate or real")
):
    """
    Get account information including cash and total assets
    
    - **env**: Trading environment (simulate or real)
    """
    try:
        trd_env = TrdEnv.REAL if env.lower() == "real" else TrdEnv.SIMULATE
        account_info = futu_fetcher.get_account_info(trd_env=trd_env)
        
        if not account_info:
            raise HTTPException(status_code=404, detail="Account information not found")
        
        logger.info(f"Retrieved account info from {env} environment")
        return account_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch account info: {str(e)}")

@router.get("/quote/{symbol}", response_model=FutuQuote)
async def get_futu_quote(symbol: str):
    """
    Get real-time quote from Futu API
    
    - **symbol**: Stock code (e.g., HK.00700 for Tencent, US.AAPL for Apple)
    """
    try:
        quote = futu_fetcher.get_quote(symbol)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"Quote not found for symbol: {symbol}")
        
        return quote
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote: {str(e)}")
