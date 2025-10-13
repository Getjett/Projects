"""
FastAPI main application for Tradiapp.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(charts.router, prefix="/api/charts", tags=["charts"])Strategy Platform
Implements Sprint 3: Strategy Tester / Backtester
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import strategy, backtest, market_data, charts
try:
    from api.routes import async_jobs
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    async_jobs = None
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    yield


app = FastAPI(
    title="AstraCharts Trading Platform API",
    description="AI-powered Trading & Backtesting Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(strategy.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(charts.router, prefix="/api/charts", tags=["charts"])

# Include async routes if available
if ASYNC_AVAILABLE and async_jobs:
    app.include_router(async_jobs.router, prefix="/api/async", tags=["async-processing"])


@app.get("/")
async def root():
    return {"message": "AstraCharts Trading Platform API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )