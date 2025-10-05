"""
Strategies API Routes
Handles CRUD operations for trading strategies
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import datetime
import uuid

from models.strategy import (
    Strategy,
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse
)

router = APIRouter()

# In-memory storage (replace with database in production)
strategies_db: dict[str, Strategy] = {}


@router.post("/", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate):
    """
    Create a new trading strategy
    """
    strategy_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_strategy = Strategy(
        id=strategy_id,
        created_at=now,
        updated_at=now,
        backtest_count=0,
        **strategy.dict()
    )
    
    strategies_db[strategy_id] = new_strategy
    
    return new_strategy


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    asset_class: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get list of all strategies with optional filtering
    """
    strategies = list(strategies_db.values())
    
    # Apply filters
    if asset_class:
        strategies = [s for s in strategies if s.asset_class == asset_class]
    
    if is_active is not None:
        strategies = [s for s in strategies if s.is_active == is_active]
    
    # Apply pagination
    strategies = strategies[skip:skip + limit]
    
    # Convert to response model
    return [
        StrategyResponse(
            id=s.id,
            strategy_name=s.strategy_name,
            description=s.description,
            asset_class=s.asset_class,
            instrument=s.instrument,
            created_at=s.created_at,
            is_active=s.is_active,
            backtest_count=s.backtest_count
        )
        for s in strategies
    ]


@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(strategy_id: str):
    """
    Get a specific strategy by ID
    """
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    return strategies_db[strategy_id]


@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(strategy_id: str, strategy_update: StrategyUpdate):
    """
    Update an existing strategy
    """
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    strategy = strategies_db[strategy_id]
    
    # Update only provided fields
    update_data = strategy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(strategy, field, value)
    
    strategy.updated_at = datetime.now()
    strategies_db[strategy_id] = strategy
    
    return strategy


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: str):
    """
    Delete a strategy (soft delete by setting is_active to False)
    """
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    # Soft delete
    strategies_db[strategy_id].is_active = False
    strategies_db[strategy_id].updated_at = datetime.now()
    
    return None


@router.post("/{strategy_id}/clone", response_model=Strategy)
async def clone_strategy(strategy_id: str, new_name: Optional[str] = None):
    """
    Clone an existing strategy
    """
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    original = strategies_db[strategy_id]
    
    # Create a new strategy with same parameters
    new_strategy_id = str(uuid.uuid4())
    now = datetime.now()
    
    cloned_strategy = Strategy(
        **original.dict(exclude={'id', 'created_at', 'updated_at', 'backtest_count'}),
        id=new_strategy_id,
        strategy_name=new_name or f"{original.strategy_name} (Copy)",
        created_at=now,
        updated_at=now,
        backtest_count=0
    )
    
    strategies_db[new_strategy_id] = cloned_strategy
    
    return cloned_strategy


@router.get("/{strategy_id}/validate")
async def validate_strategy(strategy_id: str):
    """
    Validate strategy configuration before backtesting
    """
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with id {strategy_id} not found"
        )
    
    strategy = strategies_db[strategy_id]
    validation_results = {
        "is_valid": True,
        "warnings": [],
        "errors": []
    }
    
    # Validate risk/reward ratio
    if strategy.risk_reward_ratio < 1:
        validation_results["warnings"].append(
            "Risk/Reward ratio is less than 1:1. Consider adjusting targets."
        )
    
    # Validate stop loss vs target
    if strategy.stop_loss_value >= strategy.target_value:
        validation_results["errors"].append(
            "Stop loss is greater than or equal to target. This will result in poor risk/reward."
        )
        validation_results["is_valid"] = False
    
    # Validate max loss per day
    if strategy.max_loss_per_day < 1000:
        validation_results["warnings"].append(
            "Max loss per day is very low. May limit trading opportunities."
        )
    
    # Asset-specific validations
    if strategy.asset_class == "OPTIONS":
        if not strategy.expiry:
            validation_results["errors"].append("Expiry must be specified for options strategies")
            validation_results["is_valid"] = False
        
        if not strategy.strike_selection:
            validation_results["errors"].append("Strike selection must be specified for options strategies")
            validation_results["is_valid"] = False
    
    return validation_results
