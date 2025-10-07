"""
AI Optimization API Routes
Provides AI-powered strategy optimization suggestions
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel

from ml.strategy_optimizer import optimizer

router = APIRouter()


class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    backtest_id: str
    trades: list
    strategy_config: Dict[str, Any]


class OptimizationResponse(BaseModel):
    """Response model for optimization"""
    status: str
    analysis: Dict[str, Any]
    recommendations: list
    optimized_parameters: Dict[str, Any]
    confidence_score: int


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_strategy(request: OptimizationRequest):
    """
    Analyze backtest results and provide AI-powered optimization suggestions
    
    Args:
        request: Contains backtest results and current strategy configuration
        
    Returns:
        Comprehensive analysis and recommendations
    """
    try:
        # Run AI analysis
        result = optimizer.analyze_backtest(
            trades=request.trades,
            strategy_config=request.strategy_config
        )
        
        if result['status'] == 'insufficient_data':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['message']
            )
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.get("/optimization-tips")
async def get_optimization_tips():
    """
    Get general optimization tips and best practices
    """
    return {
        "tips": [
            {
                "category": "Win Rate",
                "tip": "Aim for 50-60% win rate for consistent profitability",
                "details": "Higher isn't always better - focus on profit factor"
            },
            {
                "category": "Risk/Reward",
                "tip": "Maintain at least 1.5:1 risk/reward ratio",
                "details": "This allows profitability even with 50% win rate"
            },
            {
                "category": "Entry Timing",
                "tip": "Avoid first 15 minutes of market open",
                "details": "High volatility can cause false breakouts"
            },
            {
                "category": "Direction",
                "tip": "Analyze which direction (Bull/Bear) works best",
                "details": "Markets often have directional bias"
            },
            {
                "category": "Consistency",
                "tip": "Lower variance = more predictable results",
                "details": "Add filters to reduce random entries"
            }
        ]
    }
