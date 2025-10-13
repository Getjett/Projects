"""
Pydantic models for Strategy JSON and Backtest Result validation
Implements the exact JSON schemas from Sprint 3 specification
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


# Enums for validation
class CandleColor(str, Enum):
    RED = "red"
    GREEN = "green"


class CandleType(str, Enum):
    IMPULSE = "impulse"
    REJECTION_BOTTOM = "rejection_bottom"
    REJECTION_TOP = "rejection_top"
    BREAKOUT = "breakout"
    DOJI = "doji"
    HAMMER = "hammer"
    ENGULFING = "engulfing"


class ExecuteAt(str, Enum):
    OPEN = "open"
    CLOSE = "close"
    HIGH = "high"
    LOW = "low"
    MARKET_NEXT_OPEN = "market_next_open"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class ConditionType(str, Enum):
    CANDLE = "candle"
    INDICATOR = "indicator"
    ZONE = "zone"


class ConditionOperator(str, Enum):
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"


class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"


# Core Models
class CandlePattern(BaseModel):
    id: int = Field(description="Candle index (-1, -2, -3 for relative positions)")
    type: CandleType
    color: CandleColor
    body_ratio: float = Field(ge=0.0, le=1.0, description="Body size ratio vs total candle range")


class Indicator(BaseModel):
    name: str = Field(description="Indicator name (EMA, SMA, RSI, MACD, etc.)")
    period: Optional[int] = Field(default=None, description="Period for calculation")
    applied_to: str = Field(default="close", description="Price field to apply indicator to")
    multiplier: Optional[float] = Field(default=None, description="Multiplier for indicators like ATR")


class ValueReference(BaseModel):
    candle_id: Optional[int] = Field(default=None, description="Reference to candle by ID")
    field: Optional[str] = Field(default=None, description="Field name (close, open, high, low)")
    indicator: Optional[str] = Field(default=None, description="Reference to indicator value")


class TriggerMain(BaseModel):
    candle_id: Optional[int] = Field(default=None)
    point: Optional[str] = Field(default=None, description="Trigger point like 'close_above_prev_high'")


class Condition(BaseModel):
    type: ConditionType
    name: Optional[str] = Field(default=None, description="Indicator name if type is indicator")
    candle_id: Optional[int] = Field(default=None)
    field: Optional[str] = Field(default=None)
    op: ConditionOperator
    value: Optional[Union[float, int, str]] = Field(default=None)
    value_ref: Optional[ValueReference] = Field(default=None)


class EntryTrigger(BaseModel):
    main: Optional[TriggerMain] = Field(default=None)
    conditions: List[Condition] = Field(default_factory=list)
    logical_op: LogicalOperator = LogicalOperator.AND


class Entry(BaseModel):
    trigger: EntryTrigger
    execute_at: ExecuteAt = ExecuteAt.CLOSE
    order_type: OrderType = OrderType.MARKET


class StopLoss(BaseModel):
    mode: str = Field(description="fixed_price, fixed_pct, atr, prev_candle_low")
    value: Optional[float] = Field(default=None)
    multiplier: Optional[float] = Field(default=None)


class TakeProfit(BaseModel):
    mode: str = Field(description="fixed_price, ratio, price_target")
    value: Optional[float] = Field(default=None)


class Exit(BaseModel):
    take_profit: Optional[TakeProfit] = Field(default=None)
    stop_loss: Optional[StopLoss] = Field(default=None)
    exit_conditions: List[Condition] = Field(default_factory=list)
    logical_op: LogicalOperator = LogicalOperator.OR


class RiskManagement(BaseModel):
    capital: float = Field(gt=0, description="Total capital for trading")
    risk_per_trade_pct: float = Field(ge=0, le=100, description="Risk percentage per trade")
    max_open_trades: int = Field(ge=1, description="Maximum concurrent open positions")
    fixed_size: Optional[int] = Field(default=None, description="Fixed position size if not using risk %")


class StrategyMetadata(BaseModel):
    created_by: Optional[str] = Field(default=None)
    version: int = Field(default=1)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class StrategyJSON(BaseModel):
    """Main Strategy JSON schema matching Sprint 3 specification"""
    strategy_name: str = Field(min_length=1, max_length=100)
    symbol: str = Field(min_length=1, description="Trading symbol")
    timeframe: str = Field(description="Timeframe (1m, 5m, 15m, 1h, 1D)")
    description: Optional[str] = Field(default=None)
    candles: List[CandlePattern] = Field(default_factory=list)
    indicators: List[Indicator] = Field(default_factory=list)
    entry: Entry
    exit: Exit
    risk: RiskManagement
    metadata: Optional[StrategyMetadata] = Field(default=None)

    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W']
        if v not in valid_timeframes:
            raise ValueError(f'Timeframe must be one of: {valid_timeframes}')
        return v


# Backtest Result Models
class TradeResult(BaseModel):
    trade_id: int
    entry_time: datetime
    entry_index: int
    entry_price: float
    exit_time: datetime
    exit_index: int
    exit_price: float
    direction: Literal["LONG", "SHORT"] = "LONG"
    size: int
    pnl: float
    pnl_pct: float
    holding_period: Optional[str] = Field(default=None, description="Duration of trade")
    entry_rule: str
    exit_rule: str
    sl_hit: bool = False
    tp_hit: bool = False
    trade_equity_before: float
    trade_equity_after: float
    notes: Optional[str] = Field(default=None)


class BacktestSummary(BaseModel):
    net_profit: float
    gross_profit: float
    gross_loss: float
    win_rate: float = Field(ge=0, le=1)
    trades: int = Field(ge=0)
    max_drawdown: float
    sharpe: Optional[float] = Field(default=None)
    profit_factor: Optional[float] = Field(default=None)
    avg_trade_return: float
    max_consecutive_wins: Optional[int] = Field(default=None)
    max_consecutive_losses: Optional[int] = Field(default=None)
    expectancy: Optional[float] = Field(default=None)


class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float


class BacktestResult(BaseModel):
    """Backtest Result JSON schema matching Sprint 3 specification"""
    strategy_name: str
    symbol: str
    timeframe: str
    period: Dict[str, str] = Field(description="Date range with 'from' and 'to' keys")
    summary: BacktestSummary
    equity_curve: List[EquityPoint]
    trades: List[TradeResult]
    job_id: Optional[str] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


# API Request/Response Models
class BacktestRequest(BaseModel):
    strategy_json: StrategyJSON
    symbol: str
    timeframe: str
    from_date: str = Field(description="Start date in YYYY-MM-DD format")
    to_date: str = Field(description="End date in YYYY-MM-DD format")
    mode: Literal["fast", "detailed"] = "detailed"


class BacktestJobResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    message: Optional[str] = Field(default=None)


class StrategyImportRequest(BaseModel):
    strategy_json: StrategyJSON
    save_as_template: bool = False


class StrategyImportResponse(BaseModel):
    strategy_id: str
    message: str
    validation_errors: List[str] = Field(default_factory=list)


# Market Data Models
class CandleData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class MarketDataRequest(BaseModel):
    symbol: str
    timeframe: str
    from_date: str
    to_date: str


class MarketDataResponse(BaseModel):
    symbol: str
    timeframe: str
    candles: List[CandleData]
    indicators: Optional[Dict[str, List[float]]] = Field(default=None)