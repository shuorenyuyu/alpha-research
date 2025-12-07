"""
Database initialization script
Run this to create the database and tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market.database import init_db

if __name__ == "__main__":
    print("🚀 Initializing Alpha Research database...")
    init_db()
    print("✅ Database initialization complete!")
