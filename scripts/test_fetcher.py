#!/usr/bin/env python3
"""
Test script for market data fetcher
Fetches data for a few stocks and saves to database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market.database import SessionLocal, init_db
from market.fetchers import MarketDataFetcher, get_market_overview

def main():
    print("🚀 Testing Market Data Fetcher\n")
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Create database session
    db = SessionLocal()
    fetcher = MarketDataFetcher(db)
    
    # Test stocks
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
    
    print(f"\n📈 Fetching data for: {', '.join(test_symbols)}\n")
    
    # Fetch and save stock info
    for symbol in test_symbols:
        print(f"--- {symbol} ---")
        
        # Save stock info
        stock = fetcher.save_stock_to_db(symbol)
        if stock:
            print(f"  Name: {stock.name}")
            print(f"  Sector: {stock.sector}")
        
        # Fetch current price
        price_data = fetcher.fetch_current_price(symbol)
        if price_data:
            print(f"  Price: ${price_data['price']:.2f}")
            print(f"  Change: {price_data['change']:+.2f} ({price_data['change_percent']:+.2f}%)")
        
        # Save historical data (last month)
        count = fetcher.save_historical_data(symbol, period="1mo")
        print(f"  Historical: {count} records saved")
        print()
    
    # Test market overview
    print("\n📊 Market Overview:\n")
    overview = get_market_overview()
    for name, data in overview.items():
        if data['value']:
            print(f"{name:15} {data['value']:10,.2f}  {data['change']:+8.2f} ({data['change_percent']:+.2f}%)")
    
    db.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
