"""
Backtest API routes for running strategy backtests
Implements Sprint 3 Backtest endpoints with async job processing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta
import uuid

from models.schemas import (
    BacktestRequest, BacktestJobResponse, BacktestResult
)
from core.database import get_db, create_backtest_job, get_backtest_job, update_backtest_job
from core.backtest_engine import BacktestEngine
from core.data_fetcher import DataFetcher

router = APIRouter()
backtest_engine = BacktestEngine()
data_fetcher = DataFetcher()


@router.post("/run", response_model=BacktestJobResponse)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a backtest job for execution
    Returns job_id for tracking progress
    """
    try:
        # Create job record
        job_data = {
            "id": str(uuid.uuid4()),
            "strategy_id": "manual",  # Will be linked to saved strategy if applicable
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "from_date": datetime.strptime(request.from_date, "%Y-%m-%d"),
            "to_date": datetime.strptime(request.to_date, "%Y-%m-%d"),
            "status": "queued"
        }
        
        job = await create_backtest_job(db, job_data)
        
        # Add to background processing
        if request.mode == "fast":
            # For fast mode, run synchronously for quick results
            background_tasks.add_task(
                run_backtest_task, 
                job.id, 
                request.strategy_json.dict(), 
                request.symbol,
                request.timeframe,
                request.from_date,
                request.to_date
            )
        else:
            # For detailed mode, queue for async processing
            background_tasks.add_task(
                run_backtest_task_detailed,
                job.id,
                request.strategy_json.dict(),
                request.symbol,
                request.timeframe, 
                request.from_date,
                request.to_date
            )
        
        return BacktestJobResponse(
            job_id=job.id,
            status="queued",
            message="Backtest job submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit backtest job: {str(e)}"
        )


@router.get("/{job_id}/status", response_model=BacktestJobResponse)
async def get_backtest_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get backtest job status"""
    try:
        job = await get_backtest_job(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest job {job_id} not found"
            )
        
        return BacktestJobResponse(
            job_id=job.id,
            status=job.status,
            message=job.error_message if job.status == "failed" else f"Progress: {job.progress:.1%}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/{job_id}/result", response_model=BacktestResult)
async def get_backtest_result(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get backtest results"""
    try:
        job = await get_backtest_job(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest job {job_id} not found"
            )
        
        if job.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Backtest job is not completed. Current status: {job.status}"
            )
        
        if not job.result_json:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Backtest completed but no results found"
            )
        
        # Return the stored result with job_id attached
        result = BacktestResult(**job.result_json)
        result.job_id = job.id
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backtest result: {str(e)}"
        )


@router.delete("/{job_id}")
async def cancel_backtest_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Cancel a running backtest job"""
    try:
        job = await get_backtest_job(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest job {job_id} not found"
            )
        
        if job.status in ["completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job with status: {job.status}"
            )
        
        await update_backtest_job(db, job_id, {
            "status": "cancelled",
            "error_message": "Job cancelled by user"
        })
        
        return {"message": f"Backtest job {job_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}"
        )


@router.get("/")
async def list_backtest_jobs(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List backtest jobs with optional filtering"""
    try:
        from core.database import BacktestJob
        
        query = db.query(BacktestJob)
        
        if status:
            query = query.filter(BacktestJob.status == status)
        if symbol:
            query = query.filter(BacktestJob.symbol == symbol)
        
        total = query.count()
        jobs = query.order_by(BacktestJob.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "jobs": [
                {
                    "id": job.id,
                    "symbol": job.symbol,
                    "timeframe": job.timeframe,
                    "from_date": job.from_date,
                    "to_date": job.to_date,
                    "status": job.status,
                    "progress": job.progress,
                    "created_at": job.created_at,
                    "completed_at": job.completed_at
                }
                for job in jobs
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


# Background task functions
async def run_backtest_task(
    job_id: str,
    strategy_json: dict,
    symbol: str,
    timeframe: str,
    from_date: str,
    to_date: str
):
    """Execute backtest task in background (fast mode)"""
    try:
        # Update job status
        from core.database import SessionLocal
        db = SessionLocal()
        
        await update_backtest_job(db, job_id, {
            "status": "running",
            "started_at": datetime.utcnow(),
            "progress": 0.1
        })
        
        # Fetch market data
        print(f"Fetching data for {symbol} {timeframe} from {from_date} to {to_date}")
        df = await data_fetcher.get_historical_data(symbol, timeframe, from_date, to_date)
        
        await update_backtest_job(db, job_id, {"progress": 0.3})
        
        if df.empty:
            raise Exception("No market data found for the specified period")
        
        # Prepare strategy
        from models.schemas import StrategyJSON
        strategy = StrategyJSON(**strategy_json)
        
        await update_backtest_job(db, job_id, {"progress": 0.5})
        
        # Run backtest
        print(f"Running backtest for strategy: {strategy.strategy_name}")
        result = backtest_engine.run_backtest(df, strategy)
        
        await update_backtest_job(db, job_id, {"progress": 0.9})
        
        # Store results
        await update_backtest_job(db, job_id, {
            "status": "completed",
            "progress": 1.0,
            "result_json": result.dict(),
            "completed_at": datetime.utcnow()
        })
        
        print(f"Backtest completed successfully for job {job_id}")
        
        db.close()
        
    except Exception as e:
        print(f"Backtest task failed for job {job_id}: {e}")
        
        from core.database import SessionLocal
        db = SessionLocal()
        
        await update_backtest_job(db, job_id, {
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.utcnow()
        })
        
        db.close()


async def run_backtest_task_detailed(
    job_id: str,
    strategy_json: dict,
    symbol: str,
    timeframe: str,
    from_date: str,
    to_date: str
):
    """Execute detailed backtest task with enhanced analytics"""
    # For now, use the same implementation as fast mode
    # In production, this would include additional analysis like:
    # - Monte Carlo simulations
    # - Rolling window analysis  
    # - Parameter sensitivity analysis
    # - Advanced risk metrics
    
    await run_backtest_task(job_id, strategy_json, symbol, timeframe, from_date, to_date)