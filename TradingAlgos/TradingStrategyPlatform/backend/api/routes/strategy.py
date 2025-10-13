"""
Strategy API routes for importing, exporting, and managing trading strategies
Implements Sprint 3 Strategy Management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.schemas import (
    StrategyJSON, StrategyImportRequest, StrategyImportResponse
)
from core.database import get_db, create_strategy, get_strategy, update_strategy
import uuid
import json

router = APIRouter()


@router.post("/import", response_model=StrategyImportResponse)
async def import_strategy(
    request: StrategyImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import a strategy JSON from Live Chart or manual input
    Validates schema and saves to database
    """
    try:
        # Validate the strategy JSON (Pydantic handles this automatically)
        strategy_json = request.strategy_json
        
        # Create strategy record in database
        strategy_data = {
            "id": str(uuid.uuid4()),
            "name": strategy_json.strategy_name,
            "symbol": strategy_json.symbol,
            "timeframe": strategy_json.timeframe,
            "description": strategy_json.description,
            "strategy_json": strategy_json.dict(),
            "is_template": request.save_as_template,
            "created_by": strategy_json.metadata.created_by if strategy_json.metadata else None
        }
        
        strategy = await create_strategy(db, strategy_data)
        
        return StrategyImportResponse(
            strategy_id=strategy.id,
            message=f"Strategy '{strategy.name}' imported successfully",
            validation_errors=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import strategy: {str(e)}"
        )


@router.get("/{strategy_id}", response_model=StrategyJSON)
async def get_strategy_by_id(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """Get strategy JSON by ID"""
    strategy = await get_strategy(db, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    return StrategyJSON(**strategy.strategy_json)


@router.put("/{strategy_id}", response_model=StrategyImportResponse)
async def update_strategy_by_id(
    strategy_id: str,
    strategy_json: StrategyJSON,
    db: Session = Depends(get_db)
):
    """Update existing strategy"""
    try:
        # Check if strategy exists
        existing_strategy = await get_strategy(db, strategy_id)
        if not existing_strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with id {strategy_id} not found"
            )
        
        # Update strategy data
        updates = {
            "name": strategy_json.strategy_name,
            "symbol": strategy_json.symbol,
            "timeframe": strategy_json.timeframe,
            "description": strategy_json.description,
            "strategy_json": strategy_json.dict()
        }
        
        updated_strategy = await update_strategy(db, strategy_id, updates)
        
        return StrategyImportResponse(
            strategy_id=updated_strategy.id,
            message=f"Strategy '{updated_strategy.name}' updated successfully",
            validation_errors=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update strategy: {str(e)}"
        )


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """Delete strategy (soft delete by setting is_active=False)"""
    try:
        strategy = await get_strategy(db, strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with id {strategy_id} not found"
            )
        
        await update_strategy(db, strategy_id, {"is_active": False})
        
        return {"message": f"Strategy '{strategy.name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete strategy: {str(e)}"
        )


@router.get("/")
async def list_strategies(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    is_template: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List strategies with optional filtering"""
    try:
        from core.database import Strategy
        
        query = db.query(Strategy).filter(Strategy.is_active == True)
        
        if symbol:
            query = query.filter(Strategy.symbol == symbol)
        if timeframe:
            query = query.filter(Strategy.timeframe == timeframe)
        if is_template is not None:
            query = query.filter(Strategy.is_template == is_template)
        
        total = query.count()
        strategies = query.offset(offset).limit(limit).all()
        
        return {
            "strategies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "symbol": s.symbol,
                    "timeframe": s.timeframe,
                    "description": s.description,
                    "is_template": s.is_template,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at
                }
                for s in strategies
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list strategies: {str(e)}"
        )


@router.post("/{strategy_id}/duplicate")
async def duplicate_strategy(
    strategy_id: str,
    new_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Duplicate an existing strategy"""
    try:
        # Get original strategy
        original_strategy = await get_strategy(db, strategy_id)
        if not original_strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with id {strategy_id} not found"
            )
        
        # Create duplicate
        strategy_data = {
            "id": str(uuid.uuid4()),
            "name": new_name or f"{original_strategy.name} (Copy)",
            "symbol": original_strategy.symbol,
            "timeframe": original_strategy.timeframe,
            "description": original_strategy.description,
            "strategy_json": original_strategy.strategy_json,
            "is_template": original_strategy.is_template,
            "created_by": original_strategy.created_by
        }
        
        new_strategy = await create_strategy(db, strategy_data)
        
        return {
            "strategy_id": new_strategy.id,
            "message": f"Strategy duplicated successfully as '{new_strategy.name}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate strategy: {str(e)}"
        )


@router.post("/{strategy_id}/export")
async def export_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    """Export strategy as JSON file"""
    try:
        strategy = await get_strategy(db, strategy_id)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with id {strategy_id} not found"
            )
        
        # Return strategy JSON with metadata
        export_data = {
            "strategy_json": strategy.strategy_json,
            "metadata": {
                "exported_at": str(datetime.utcnow()),
                "exported_from": "AstraCharts Trading Platform",
                "strategy_id": strategy.id,
                "original_name": strategy.name
            }
        }
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export strategy: {str(e)}"
        )