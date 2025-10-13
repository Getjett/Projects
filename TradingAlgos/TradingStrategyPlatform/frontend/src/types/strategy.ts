// TypeScript interfaces matching the Pydantic models from the backend

export interface StrategyJSON {
  strategy_name: string;
  symbol: string;
  timeframe: string;
  description?: string;
  candles?: CandlePattern[];
  indicators?: Indicator[];
  entry: Entry;
  exit: Exit;
  risk: RiskManagement;
  metadata?: StrategyMetadata;
}

export interface CandlePattern {
  id: number;
  type: string;
  color: 'red' | 'green';
  body_ratio: number;
}

export interface Indicator {
  name: string;
  period?: number;
  applied_to?: string;
  multiplier?: number;
}

export interface Entry {
  trigger: EntryTrigger;
  execute_at?: string;
  order_type?: string;
}

export interface EntryTrigger {
  main?: TriggerMain;
  conditions: Condition[];
  logical_op: 'AND' | 'OR';
}

export interface TriggerMain {
  candle_id?: number;
  point?: string;
}

export interface Condition {
  type: 'candle' | 'indicator' | 'zone';
  name?: string;
  candle_id?: number;
  field?: string;
  op: '>' | '<' | '>=' | '<=' | '==' | 'crosses_above' | 'crosses_below';
  value?: number | string;
  value_ref?: ValueReference;
}

export interface ValueReference {
  candle_id?: number;
  field?: string;
  indicator?: string;
}

export interface Exit {
  take_profit?: TakeProfit;
  stop_loss?: StopLoss;
  exit_conditions?: Condition[];
  logical_op?: 'AND' | 'OR';
}

export interface StopLoss {
  mode: string;
  value?: number;
  multiplier?: number;
}

export interface TakeProfit {
  mode: string;
  value?: number;
}

export interface RiskManagement {
  capital: number;
  risk_per_trade_pct: number;
  max_open_trades: number;
  fixed_size?: number;
}

export interface StrategyMetadata {
  created_by?: string;
  version?: number;
  created_at?: string;
  updated_at?: string;
}

// Backtest Result Types
export interface BacktestResult {
  strategy_name: string;
  symbol: string;
  timeframe: string;
  period: {
    from: string;
    to: string;
  };
  summary: BacktestSummary;
  equity_curve: EquityPoint[];
  trades: TradeResult[];
  job_id?: string;
  completed_at?: string;
}

export interface BacktestSummary {
  net_profit: number;
  gross_profit: number;
  gross_loss: number;
  win_rate: number;
  trades: number;
  max_drawdown: number;
  sharpe?: number;
  profit_factor?: number;
  avg_trade_return: number;
  max_consecutive_wins?: number;
  max_consecutive_losses?: number;
  expectancy?: number;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface TradeResult {
  trade_id: number;
  entry_time: string;
  entry_index: number;
  entry_price: number;
  exit_time: string;
  exit_index: number;
  exit_price: number;
  direction: 'LONG' | 'SHORT';
  size: number;
  pnl: number;
  pnl_pct: number;
  holding_period?: string;
  entry_rule: string;
  exit_rule: string;
  sl_hit: boolean;
  tp_hit: boolean;
  trade_equity_before: number;
  trade_equity_after: number;
  notes?: string;
}

// Market Data Types
export interface CandleData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketDataResponse {
  symbol: string;
  timeframe: string;
  candles: CandleData[];
  indicators?: Record<string, number[]>;
}

// UI State Types
export interface DateRange {
  from: string;
  to: string;
}

export interface BacktestJobResponse {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  message?: string;
}