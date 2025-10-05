"""
Strategy Model
Defines the data structure for trading strategies
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AssetClass(str, Enum):
    OPTIONS = "OPTIONS"
    EQUITY = "EQUITY"
    COMMODITY = "COMMODITY"
    CURRENCY = "CURRENCY"
    FUTURES = "FUTURES"


class BreakoutDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    BOTH = "BOTH"


class OptionType(str, Enum):
    CE = "CE"
    PE = "PE"
    BOTH = "BOTH"


class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    BOTH = "BOTH"


class EntryConfirmation(BaseModel):
    volume_confirmation: bool = False
    candle_close: bool = True
    retest: bool = False


class StrategyCreate(BaseModel):
    # Basic Info
    strategy_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = []
    
    # Instrument Selection
    asset_class: AssetClass
    instrument: str
    exchange: str
    product_type: str
    trading_type: str
    
    # Entry Logic
    signal_bar: str
    time_frame: str
    breakout_type: str
    breakout_direction: BreakoutDirection
    entry_confirmation: EntryConfirmation
    volume_threshold: int = 150
    
    # Options-specific fields
    expiry: Optional[str] = None
    strike_selection: Optional[str] = None
    strike_offset: Optional[int] = 0
    option_type: Optional[OptionType] = None
    premium_min: Optional[float] = None
    premium_max: Optional[float] = None
    
    # Equity/Commodity/Futures fields
    position_side: Optional[PositionSide] = None
    quantity_type: Optional[str] = None
    quantity: Optional[int] = None
    capital_per_trade: Optional[float] = None
    portfolio_percentage: Optional[float] = None
    leverage: Optional[float] = 1.0
    
    # Exit Logic
    target_type: str
    target_value: float
    stop_loss_type: str
    stop_loss_value: float
    trailing_stop: bool = False
    trailing_stop_value: Optional[float] = None
    
    # Risk Management
    max_loss_per_day: float
    max_trades_per_day: int
    risk_reward_ratio: float


class Strategy(StrategyCreate):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    backtest_count: int = 0
    
    class Config:
        from_attributes = True


class StrategyUpdate(BaseModel):
    strategy_name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    # Add other fields as needed


class StrategyResponse(BaseModel):
    id: str
    strategy_name: str
    description: Optional[str]
    asset_class: AssetClass
    instrument: str
    created_at: datetime
    is_active: bool
    backtest_count: int
    
    class Config:
        from_attributes = True
