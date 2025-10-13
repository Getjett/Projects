"""
Async Processing API Routes
Handles job submission, status tracking, and result retrieval
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from async_processing import async_service, job_manager
from models.schemas import BacktestRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/submit")
async def submit_async_backtest(
    backtest_request: Dict[str, Any],  # Using Dict for now to avoid validation issues
    background_tasks: BackgroundTasks
):
    """
    Submit backtest for async execution
    
    Args:
        backtest_request: Backtest configuration
        background_tasks: FastAPI background tasks
        
    Returns:
        Job submission result with job ID
    """
    
    try:
        # Submit job for async processing
        job_id = async_service.submit_backtest(backtest_request)
        
        # Schedule cleanup task
        background_tasks.add_task(job_manager.cleanup_old_jobs, 24)
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "SUBMITTED",
                "message": "Backtest job submitted for async execution",
                "estimated_time": "2-5 minutes",
                "check_status_url": f"/api/async/status/{job_id}"
            },
            "message": "Backtest submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit async backtest: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit backtest: {str(e)}"
        )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job execution status and progress
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    
    try:
        status = async_service.get_job_status(job_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}"
            )
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                **status
            },
            "message": f"Job status retrieved: {status['status']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/result/{job_id}")
async def get_job_result(job_id: str):
    """
    Get completed job result
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job execution result
    """
    
    try:
        # Check job status first
        status = async_service.get_job_status(job_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Job not found: {job_id}"
            )
        
        if status['status'] != 'SUCCESS':
            return {
                "success": False,
                "data": {
                    "job_id": job_id,
                    "status": status['status'],
                    "message": status.get('message', 'Job not completed'),
                    "progress": status.get('progress', 0)
                },
                "message": f"Job not completed yet. Status: {status['status']}"
            }
        
        # Get result
        result = async_service.get_job_result(job_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Job result not available"
            )
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "backtest_result": result,
                "retrieved_at": datetime.utcnow().isoformat()
            },
            "message": "Job result retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job result {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job result: {str(e)}"
        )


@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel running job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Cancellation result
    """
    
    try:
        cancelled = async_service.cancel_job(job_id)
        
        if cancelled:
            return {
                "success": True,
                "data": {
                    "job_id": job_id,
                    "status": "CANCELLED",
                    "cancelled_at": datetime.utcnow().isoformat()
                },
                "message": "Job cancelled successfully"
            }
        else:
            return {
                "success": False,
                "data": {
                    "job_id": job_id,
                    "status": "CANCEL_FAILED"
                },
                "message": "Failed to cancel job"
            }
        
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )


@router.get("/jobs")
async def list_jobs(
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, description="Filter by status")
):
    """
    List recent jobs
    
    Args:
        limit: Maximum number of jobs to return
        status_filter: Optional status filter
        
    Returns:
        List of recent jobs
    """
    
    try:
        jobs = async_service.list_jobs(limit)
        
        # Apply status filter if provided
        if status_filter:
            jobs = [job for job in jobs if job.get('status') == status_filter.upper()]
        
        return {
            "success": True,
            "data": {
                "jobs": jobs,
                "total_count": len(jobs),
                "filter": status_filter,
                "limit": limit
            },
            "message": f"Retrieved {len(jobs)} jobs"
        }
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list jobs: {str(e)}"
        )


@router.get("/workers/status")
async def get_worker_status():
    """
    Get Celery worker status
    
    Returns:
        Worker status and statistics
    """
    
    try:
        status = async_service.get_worker_status()
        
        return {
            "success": True,
            "data": {
                **status,
                "timestamp": datetime.utcnow().isoformat()
            },
            "message": "Worker status retrieved"
        }
        
    except Exception as e:
        logger.error(f"Failed to get worker status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get worker status: {str(e)}"
        )


@router.post("/test-job")
async def submit_test_job():
    """
    Submit a test job for system verification
    
    Returns:
        Test job result
    """
    
    try:
        # Create test backtest request
        test_request = {
            "strategy": {
                "name": "Test Async Strategy",
                "version": "1.0",
                "description": "Test strategy for async processing",
                "parameters": {"capital": 100000},
                "indicators": [{"name": "SMA", "period": 20}],
                "entry_conditions": [{"type": "price", "operator": ">", "value": 100}],
                "exit_conditions": [{"type": "price", "operator": "<", "value": 95}],
                "metadata": {"author": "Async Test", "created": datetime.utcnow().isoformat()}
            },
            "symbol": "ASYNCTEST",
            "timeframe": "1d",
            "from_date": "2024-01-01",
            "to_date": "2024-01-10"
        }
        
        job_id = async_service.submit_backtest(test_request)
        
        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "test_request": test_request,
                "submitted_at": datetime.utcnow().isoformat(),
                "note": "This is a test job for system verification"
            },
            "message": "Test job submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit test job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit test job: {str(e)}"
        )


@router.get("/stats")
async def get_async_stats():
    """
    Get async processing statistics
    
    Returns:
        Processing statistics and metrics
    """
    
    try:
        # Get all jobs
        all_jobs = async_service.list_jobs(1000)  # Get up to 1000 recent jobs
        
        # Calculate statistics
        total_jobs = len(all_jobs)
        
        status_counts = {}
        for job in all_jobs:
            status = job.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average execution time for completed jobs
        completed_jobs = [job for job in all_jobs if job.get('status') == 'SUCCESS']
        avg_execution_time = 0
        
        if completed_jobs:
            execution_times = []
            for job in completed_jobs:
                if job.get('started_at') and job.get('completed_at'):
                    start = datetime.fromisoformat(job['started_at'])
                    end = datetime.fromisoformat(job['completed_at'])
                    execution_times.append((end - start).total_seconds())
            
            if execution_times:
                avg_execution_time = sum(execution_times) / len(execution_times)
        
        # Worker status
        worker_status = async_service.get_worker_status()
        
        stats = {
            "total_jobs": total_jobs,
            "status_distribution": status_counts,
            "completed_jobs": len(completed_jobs),
            "success_rate": (len(completed_jobs) / total_jobs * 100) if total_jobs > 0 else 0,
            "average_execution_time_seconds": round(avg_execution_time, 2),
            "workers": {
                "online": worker_status.get('workers_online', 0),
                "active_tasks": worker_status.get('active_tasks', 0)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "Async processing statistics retrieved"
        }
        
    except Exception as e:
        logger.error(f"Failed to get async stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get async stats: {str(e)}"
        )