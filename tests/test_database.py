"""
Test suite for database models and connections
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import tempfile
import os

from market.database.models import Base, Stock, StockPrice, Portfolio, PortfolioItem, MarketIndex
from market.database.connection import get_db, init_db


class TestDatabaseModels:
    """Test cases for SQLAlchemy models"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database for each test"""
        # Create in-memory SQLite database
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()
        
        yield
        
        self.session.close()
    
    def test_stock_model_creation(self):
        """Test Stock model creation"""
        stock = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            industry='Consumer Electronics',
            market_cap=3000000000000.0
        )
        self.session.add(stock)
        self.session.commit()
        
        result = self.session.query(Stock).filter_by(symbol='AAPL').first()
        assert result is not None
        assert result.symbol == 'AAPL'
        assert result.name == 'Apple Inc.'
        assert result.sector == 'Technology'
        assert result.created_at is not None
    
    def test_stock_unique_symbol(self):
        """Test stock symbol uniqueness constraint"""
        stock1 = Stock(symbol='AAPL', name='Apple Inc.')
        stock2 = Stock(symbol='AAPL', name='Apple Inc. Duplicate')
        
        self.session.add(stock1)
        self.session.commit()
        
        self.session.add(stock2)
        with pytest.raises(Exception):  # IntegrityError
            self.session.commit()
    
    def test_stock_price_model(self):
        """Test StockPrice model creation"""
        stock = Stock(symbol='AAPL', name='Apple Inc.')
        self.session.add(stock)
        self.session.commit()
        
        price = StockPrice(
            stock_id=stock.id,
            date=datetime(2023, 12, 11),
            open=150.0,
            high=152.0,
            low=148.0,
            close=151.0,
            volume=1000000,
            adjusted_close=151.0
        )
        self.session.add(price)
        self.session.commit()
        
        result = self.session.query(StockPrice).filter_by(stock_id=stock.id).first()
        assert result is not None
        assert result.open == 150.0
        assert result.close == 151.0
    
    def test_stock_price_relationship(self):
        """Test Stock-StockPrice relationship"""
        stock = Stock(symbol='AAPL', name='Apple Inc.')
        price1 = StockPrice(date=datetime.now(), open=150.0, high=152.0, low=148.0, close=151.0, volume=1000000)
        price2 = StockPrice(date=datetime.now(), open=151.0, high=153.0, low=149.0, close=152.0, volume=1100000)
        
        stock.prices.append(price1)
        stock.prices.append(price2)
        self.session.add(stock)
        self.session.commit()
        
        result = self.session.query(Stock).filter_by(symbol='AAPL').first()
        assert len(result.prices) == 2
    
    def test_portfolio_model(self):
        """Test Portfolio model creation"""
        portfolio = Portfolio(
            name='My Portfolio',
            description='Test portfolio',
            total_value=10000.0,
            cash=5000.0
        )
        self.session.add(portfolio)
        self.session.commit()
        
        result = self.session.query(Portfolio).filter_by(name='My Portfolio').first()
        assert result is not None
        assert result.total_value == 10000.0
        assert result.cash == 5000.0
    
    def test_portfolio_item_model(self):
        """Test PortfolioItem model creation"""
        stock = Stock(symbol='AAPL', name='Apple Inc.')
        portfolio = Portfolio(name='Test Portfolio', total_value=0.0, cash=10000.0)
        
        self.session.add(stock)
        self.session.add(portfolio)
        self.session.commit()
        
        item = PortfolioItem(
            portfolio_id=portfolio.id,
            stock_id=stock.id,
            shares=10.0,
            average_cost=150.0,
            current_price=155.0
        )
        self.session.add(item)
        self.session.commit()
        
        result = self.session.query(PortfolioItem).filter_by(portfolio_id=portfolio.id).first()
        assert result is not None
        assert result.shares == 10.0
        assert result.average_cost == 150.0
    
    def test_portfolio_items_relationship(self):
        """Test Portfolio-PortfolioItem relationship"""
        stock1 = Stock(symbol='AAPL', name='Apple Inc.')
        stock2 = Stock(symbol='MSFT', name='Microsoft Corp.')
        portfolio = Portfolio(name='Test Portfolio', total_value=0.0, cash=10000.0)
        
        item1 = PortfolioItem(stock=stock1, shares=10.0, average_cost=150.0)
        item2 = PortfolioItem(stock=stock2, shares=5.0, average_cost=300.0)
        
        portfolio.items.append(item1)
        portfolio.items.append(item2)
        self.session.add(portfolio)
        self.session.commit()
        
        result = self.session.query(Portfolio).filter_by(name='Test Portfolio').first()
        assert len(result.items) == 2
    
    def test_cascade_delete_stock_prices(self):
        """Test cascade delete of stock prices when stock is deleted"""
        stock = Stock(symbol='AAPL', name='Apple Inc.')
        price = StockPrice(stock=stock, date=datetime.now(), open=150.0, high=152.0, low=148.0, close=151.0, volume=1000000)
        
        self.session.add(stock)
        self.session.commit()
        
        stock_id = stock.id
        self.session.delete(stock)
        self.session.commit()
        
        result = self.session.query(StockPrice).filter_by(stock_id=stock_id).all()
        assert len(result) == 0
    
    def test_market_index_model(self):
        """Test MarketIndex model creation"""
        index = MarketIndex(
            symbol='^GSPC',
            name='S&P 500',
            current_value=4500.0,
            change=50.0,
            change_percent=1.12
        )
        self.session.add(index)
        self.session.commit()
        
        result = self.session.query(MarketIndex).filter_by(symbol='^GSPC').first()
        assert result is not None
        assert result.name == 'S&P 500'
        assert result.current_value == 4500.0
    
    def test_market_index_unique_symbol(self):
        """Test market index symbol uniqueness"""
        index1 = MarketIndex(symbol='^GSPC', name='S&P 500', current_value=4500.0)
        index2 = MarketIndex(symbol='^GSPC', name='Duplicate', current_value=4600.0)
        
        self.session.add(index1)
        self.session.commit()
        
        self.session.add(index2)
        with pytest.raises(Exception):
            self.session.commit()
    
    def test_updated_at_timestamp(self):
        """Test that updated_at timestamp is set"""
        stock = Stock(symbol='AAPL', name='Apple Inc.')
        self.session.add(stock)
        self.session.commit()
        
        original_updated = stock.updated_at
        
        # Update the stock
        stock.name = 'Apple Inc. Updated'
        self.session.commit()
        
        assert stock.updated_at >= original_updated


class TestDatabaseConnection:
    """Test cases for database connection functions"""
    
    def test_get_db_generator(self):
        """Test get_db returns a generator"""
        gen = get_db()
        assert gen is not None
        
        # Should yield a session
        session = next(gen)
        assert session is not None
        
        # Cleanup
        try:
            next(gen)
        except StopIteration:
            pass
    
    def test_init_db_creates_tables(self):
        """Test init_db creates all tables"""
        # Create temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            tmp_path = tmp.name
        
        try:
            # Create engine for test database
            test_engine = create_engine(f"sqlite:///{tmp_path}")
            
            # Bind Base to test engine temporarily
            original_metadata = Base.metadata
            Base.metadata.create_all(bind=test_engine)
            
            # Check tables exist
            from sqlalchemy import inspect
            inspector = inspect(test_engine)
            tables = inspector.get_table_names()
            
            assert 'stocks' in tables
            assert 'stock_prices' in tables
            assert 'portfolios' in tables
            assert 'portfolio_items' in tables
            assert 'market_indices' in tables
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
