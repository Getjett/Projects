"""
Backtest Model
Defines the data structure for backtesting requests and results
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: date
    end_date: date
    initial_capital: float = Field(default=100000, ge=10000)
    commission_per_trade: float = Field(default=20, ge=0)
    slippage_percent: float = Field(default=0.1, ge=0, le=5)
    
    # Optional filters
    market_condition: Optional[str] = None  # "TRENDING", "RANGING", "VOLATILE"
    include_weekends: bool = False
    
    # Strategy Configuration
    strategy_config: Optional[Dict[str, Any]] = None  # Full strategy configuration from frontend


class TradeResult(BaseModel):
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: int
    position_type: str  # "LONG" or "SHORT"
    profit_loss: float
    profit_loss_percent: float
    exit_reason: str  # "TARGET", "STOP_LOSS", "TIME_BASED", "EOD"


class BacktestMetrics(BaseModel):
    # Performance Metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Financial Metrics
    total_profit: float
    total_loss: float
    net_profit: float
    net_profit_percent: float
    
    # Returns
    average_profit_per_trade: float
    average_loss_per_trade: float
    largest_profit: float
    largest_loss: float
    
    # Risk Metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: Optional[float] = None
    profit_factor: float  # Total Profit / Total Loss
    
    # Additional Stats
    average_trade_duration: str
    best_day_profit: float
    worst_day_loss: float
    consecutive_wins: int
    consecutive_losses: int
    
    # Risk/Reward
    actual_risk_reward_ratio: float
    expectancy: float  # (Win% × Avg Win) - (Loss% × Avg Loss)


class BacktestResult(BaseModel):
    id: str
    strategy_id: str
    strategy_name: str
    
    # Backtest Parameters
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    
    # Results
    metrics: BacktestMetrics
    trades: List[TradeResult]
    
    # Equity Curve Data (for charts)
    equity_curve: List[Dict[str, Any]]  # [{date, equity, drawdown}, ...]
    daily_returns: List[Dict[str, Any]]  # [{date, return_pct}, ...]
    
    # Execution Details
    executed_at: datetime
    execution_time_seconds: float
    
    class Config:
        from_attributes = True


class BacktestSummary(BaseModel):
    id: str
    strategy_id: str
    strategy_name: str
    start_date: date
    end_date: date
    net_profit: float
    net_profit_percent: float
    win_rate: float
    total_trades: int
    max_drawdown_percent: float
    executed_at: datetime
    
    class Config:
        from_attributes = True
