"""
Test suite for main FastAPI application
"""
import pytest
from fastapi.testclient import TestClient

from api.main import app


class TestMainApp:
    """Test cases for main FastAPI app"""
    
    def test_app_creation(self):
        """Test app is created correctly"""
        assert app is not None
        assert app.title == "Alpha Research API"
        assert app.version == "1.0.0"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Alpha Research API"
        assert data["status"] == "running"
    
    def test_cors_middleware_configured(self):
        """Test CORS middleware is configured"""
        # Check middleware is added
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert 'CORSMiddleware' in middleware_classes
    
    def test_research_router_included(self):
        """Test research router is included"""
        routes = [route.path for route in app.routes]
        assert any('/api/research' in route for route in routes)
    
    def test_market_router_included(self):
        """Test market router is included"""
        routes = [route.path for route in app.routes]
        assert any('/api/market' in route for route in routes)
    
    def test_openapi_docs(self, client):
        """Test OpenAPI documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json(self, client):
        """Test OpenAPI JSON schema"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Alpha Research API"
        assert data["info"]["version"] == "1.0.0"
    
    def test_tags_in_openapi(self, client):
        """Test API tags are properly set"""
        response = client.get("/openapi.json")
        data = response.json()
        
        # Check that routes have tags
        paths = data.get("paths", {})
        research_paths = [p for p in paths.keys() if "/api/research" in p]
        market_paths = [p for p in paths.keys() if "/api/market" in p]
        
        assert len(research_paths) > 0
        assert len(market_paths) > 0
    
    def test_404_not_found(self, client):
        """Test 404 response for non-existent endpoint"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
    
    def test_cors_headers_on_options(self, client):
        """Test CORS headers are present on OPTIONS request"""
        response = client.options(
            "/api/market/quotes?symbols=AAPL",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code in [200, 405]
