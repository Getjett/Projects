"""
Universal Trading Strategy Platform - Backend API
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers (will be created)
# from api.routes import auth, strategies, backtest, instruments, data, patterns


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting Universal Trading Strategy Platform API...")
    # Initialize database connection
    # Initialize Redis connection
    # Start background tasks
    yield
    logger.info("🛑 Shutting down API...")
    # Cleanup resources


# Initialize FastAPI app
app = FastAPI(
    title="Universal Trading Strategy Platform API",
    description="Multi-asset trading strategy platform supporting Options, Equity, Commodities, Currency, and Futures",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Universal Trading Strategy Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "supported_assets": ["OPTIONS", "EQUITY", "COMMODITY", "CURRENCY", "FUTURES"]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",  # Check actual DB connection
        "redis": "connected",      # Check actual Redis connection
        "timestamp": "2025-10-04T00:00:00Z"
    }


# Include routers (uncomment when created)
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
# app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])
# app.include_router(instruments.router, prefix="/api/instruments", tags=["Instruments"])
# app.include_router(data.router, prefix="/api/data", tags=["Market Data"])
# app.include_router(patterns.router, prefix="/api/patterns", tags=["Patterns"])


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set False in production
        log_level="info"
    )
