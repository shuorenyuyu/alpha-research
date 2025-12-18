"""
Futu (Futubull) API fetcher for account positions and market data
"""
from futu import OpenQuoteContext, OpenSecTradeContext, TrdEnv, TrdMarket, ModifyOrderOp
from typing import List, Dict, Optional
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FutuFetcher:
    """Fetcher for Futu account positions and market data"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 11111):
        """
        Initialize Futu API connection
        
        Args:
            host: FutuOpenD host (default: localhost)
            port: FutuOpenD port (default: 11111)
        """
        self.host = host
        self.port = port
        self.quote_ctx = None
        self.trade_ctx = None
        
    def _ensure_quote_connection(self):
        """Ensure quote context is connected"""
        if self.quote_ctx is None:
            self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
        return self.quote_ctx
    
    def _ensure_trade_connection(self):
        """Ensure trade context is connected"""
        if self.trade_ctx is None:
            # Use simulated trading environment by default (change to REAL for production)
            self.trade_ctx = OpenSecTradeContext(
                host=self.host, 
                port=self.port,
                filter_trdmarket=TrdMarket.HK  # HK market, change as needed
            )
        return self.trade_ctx
    
    def get_account_positions(self, trd_env: TrdEnv = TrdEnv.SIMULATE) -> List[Dict]:
        """
        Get current account positions/holdings
        
        Args:
            trd_env: Trading environment (SIMULATE or REAL)
            
        Returns:
            List of position dictionaries with stock info
        """
        try:
            trade_ctx = self._ensure_trade_connection()
            
            # Get position list
            ret, data = trade_ctx.position_list_query(trd_env=trd_env)
            
            if ret != 0:
                logger.error(f"Failed to get positions: {data}")
                return []
            
            if data.empty:
                logger.info("No positions found")
                return []
            
            positions = []
            for _, row in data.iterrows():
                position = {
                    'symbol': row['code'],
                    'name': row['stock_name'],
                    'quantity': int(row['qty']),
                    'canSellQty': int(row['can_sell_qty']),
                    'costPrice': float(row['cost_price']),
                    'currentPrice': float(row['price']),
                    'marketValue': float(row['market_val']),
                    'profitLoss': float(row['pl_val']),
                    'profitLossPercent': float(row['pl_ratio']) * 100,
                    'currency': row['currency'],
                    'updateTime': datetime.now().isoformat()
                }
                positions.append(position)
            
            logger.info(f"Retrieved {len(positions)} positions")
            return positions
            
        except Exception as e:
            logger.error(f"Error getting account positions: {e}")
            return []
    
    def get_account_info(self, trd_env: TrdEnv = TrdEnv.SIMULATE) -> Optional[Dict]:
        """
        Get account information including cash and total assets
        
        Args:
            trd_env: Trading environment (SIMULATE or REAL)
            
        Returns:
            Account info dictionary
        """
        try:
            trade_ctx = self._ensure_trade_connection()
            
            # Get account list
            ret, data = trade_ctx.accinfo_query(trd_env=trd_env)
            
            if ret != 0:
                logger.error(f"Failed to get account info: {data}")
                return None
            
            if data.empty:
                return None
            
            # Get first account (usually there's only one)
            row = data.iloc[0]
            
            account_info = {
                'totalAssets': float(row['total_assets']),
                'cash': float(row['cash']),
                'marketValue': float(row['market_val']),
                'frozenCash': float(row.get('frozen_cash', 0)),
                'availableFunds': float(row.get('available_funds', row['cash'])),
                'currency': row.get('currency', 'HKD'),
                'updateTime': datetime.now().isoformat()
            }
            
            return account_info
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote for a stock
        
        Args:
            symbol: Stock code (e.g., 'HK.00700' for Tencent)
            
        Returns:
            Quote dictionary
        """
        try:
            quote_ctx = self._ensure_quote_connection()
            
            ret, data = quote_ctx.get_market_snapshot([symbol])
            
            if ret != 0 or data.empty:
                logger.error(f"Failed to get quote for {symbol}")
                return None
            
            row = data.iloc[0]
            
            quote = {
                'symbol': symbol,
                'name': row.get('stock_name', symbol),
                'price': float(row['last_price']),
                'change': float(row['change_val']),
                'changePercent': float(row['change_rate']),
                'volume': int(row['volume']),
                'turnover': float(row['turnover']),
                'high': float(row['high']),
                'low': float(row['low']),
                'open': float(row['open_price']),
                'previousClose': float(row['prev_close_price']),
                'timestamp': datetime.now().isoformat()
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    def close(self):
        """Close all connections"""
        if self.quote_ctx:
            self.quote_ctx.close()
            self.quote_ctx = None
        if self.trade_ctx:
            self.trade_ctx.close()
            self.trade_ctx = None

# Global instance
futu_fetcher = FutuFetcher()
