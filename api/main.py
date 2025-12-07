"""
FastAPI application for Alpha Research
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import research, market

app = FastAPI(
    title="Alpha Research API",
    description="Investment research and market data API",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {"message": "Alpha Research API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
