"""
FastAPI application for Alpha Research
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import research, market, futu, portfolio, live_portfolio
from .logging_config import get_logger, api_logger
import time
import traceback

# Initialize logger
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🚀 Alpha Research API starting up...")
    logger.info("📊 Market data routes: /api/market/*")
    logger.info("🔬 Research routes: /api/research/*")
    logger.info("💰 Futu account routes: /api/futu/*")
    logger.info("🎯 Portfolio strategy routes: /api/portfolio/*")
    logger.info("� Live 13F data routes: /api/live-portfolio/*")
    logger.info("�📝 Logs available at: /api/research/logs/{api|research|errors}")
    yield
    # Shutdown
    logger.info("🛑 Alpha Research API shutting down...")

app = FastAPI(
    title="Alpha Research API",
    description="Investment research and market data API with comprehensive logging",
    version="1.0.0",
    lifespan=lifespan
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information"""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path} | Client: {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            f"← {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration_ms:.2f}ms"
        )
        
        return response
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"✗ {request.method} {request.url.path} | "
            f"Error: {str(e)} | "
            f"Duration: {duration_ms:.2f}ms\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Return JSON error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(e),
                "path": request.url.path,
                "suggestion": "Check logs/api.log or logs/errors.log for details"
            }
        )

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(futu.router, prefix="/api/futu", tags=["futu"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(live_portfolio.router)  # Live 13F data (has its own prefix)

@app.get("/")
async def root():
    """API health check endpoint"""
    logger.debug("Health check requested")
    return {
        "message": "Alpha Research API",
        "status": "running",
        "version": "1.0.0",
        "logs": {
            "api": "/api/research/logs/api",
            "research": "/api/research/logs/research",
            "errors": "/api/research/logs/errors"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server via uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

