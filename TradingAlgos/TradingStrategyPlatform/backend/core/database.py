"""
Database models and setup for the Trading Strategy Platform
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import os

# Database URL - can be configured via environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/trading_platform"
)

# For development, fall back to SQLite if PostgreSQL not available
if "postgresql" in DATABASE_URL:
    try:
        test_engine = create_engine(DATABASE_URL)
        test_engine.connect()
        test_engine.dispose()
    except Exception:
        # Fallback to SQLite for development
        DATABASE_URL = "sqlite:///./trading_platform.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Strategy(Base):
    """Strategy storage model"""
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    description = Column(Text)
    strategy_json = Column(JSON, nullable=False)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class BacktestJob(Base):
    """Backtest job tracking"""
    __tablename__ = "backtest_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    from_date = Column(DateTime, nullable=False)
    to_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="queued", index=True)  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    result_json = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class MarketData(Base):
    """Cached market data"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite index for efficient querying
    __table_args__ = (
        {"extend_existing": True}
    )


async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_strategy(db, strategy_data: dict) -> Strategy:
    """Create a new strategy"""
    strategy = Strategy(**strategy_data)
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


async def get_strategy(db, strategy_id: str) -> Strategy:
    """Get strategy by ID"""
    return db.query(Strategy).filter(Strategy.id == strategy_id).first()


async def update_strategy(db, strategy_id: str, updates: dict) -> Strategy:
    """Update existing strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if strategy:
        for key, value in updates.items():
            setattr(strategy, key, value)
        strategy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(strategy)
    return strategy


async def create_backtest_job(db, job_data: dict) -> BacktestJob:
    """Create a new backtest job"""
    job = BacktestJob(**job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def get_backtest_job(db, job_id: str) -> BacktestJob:
    """Get backtest job by ID"""
    return db.query(BacktestJob).filter(BacktestJob.id == job_id).first()


async def update_backtest_job(db, job_id: str, updates: dict) -> BacktestJob:
    """Update backtest job status and results"""
    job = db.query(BacktestJob).filter(BacktestJob.id == job_id).first()
    if job:
        for key, value in updates.items():
            setattr(job, key, value)
        db.commit()
        db.refresh(job)
    return job