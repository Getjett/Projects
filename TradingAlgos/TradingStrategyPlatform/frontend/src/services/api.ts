/**
 * API Service for Strategy Builder
 * Handles all backend API calls for strategies and backtesting
 */

import axios from 'axios';

// Configure API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    // Add better error messages
    if (!error.response) {
      error.message = 'Cannot connect to backend server. Please ensure the backend is running at http://localhost:8000';
    }
    
    return Promise.reject(error);
  }
);

// Strategy Types
export interface StrategyConfig {
  strategyName: string;
  description?: string;
  tags: string[];
  assetClass: string;
  instrument: string;
  exchange: string;
  productType: string;
  tradingType: string;
  signalBar: string;
  timeFrame: string;
  breakoutType: string;
  breakoutDirection: string;
  entryConfirmation: {
    volumeConfirmation: boolean;
    candleClose: boolean;
    retest: boolean;
  };
  volumeThreshold: number;
  expiry?: string;
  strikeSelection?: string;
  strikeOffset?: number;
  optionType?: string;
  premiumMin?: number;
  premiumMax?: number;
  positionSide?: string;
  quantityType?: string;
  quantity?: number;
  capitalPerTrade?: number;
  portfolioPercentage?: number;
  leverage?: number;
  targetType: string;
  targetValue: number;
  stopLossType: string;
  stopLossValue: number;
  trailingStop: boolean;
  trailingStopValue?: number;
  maxLossPerDay: number;
  maxTradesPerDay: number;
  riskRewardRatio: number;
}

export interface Strategy extends StrategyConfig {
  id: string;
  userId?: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
  backtestCount: number;
}

export interface StrategyResponse {
  id: string;
  strategyName: string;
  description?: string;
  assetClass: string;
  instrument: string;
  createdAt: string;
  isActive: boolean;
  backtestCount: number;
}

// Backtest Types
// Note: Using snake_case to match Python FastAPI backend
export interface BacktestRequest {
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital?: number;
  commission_per_trade?: number;
  slippage_percent?: number;
  market_condition?: string;
  include_weekends?: boolean;
}

export interface TradeResult {
  entry_time: string;
  exit_time: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  position_type: string;
  profit_loss: number;
  profit_loss_percent: number;
  exit_reason: string;
}

export interface BacktestMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  total_loss: number;
  net_profit: number;
  net_profit_percent: number;
  average_profit_per_trade: number;
  average_loss_per_trade: number;
  largest_profit: number;
  largest_loss: number;
  max_drawdown: number;
  max_drawdown_percent: number;
  sharpe_ratio?: number;
  profit_factor: number;
  average_trade_duration: string;
  best_day_profit: number;
  worst_day_loss: number;
  consecutive_wins: number;
  consecutive_losses: number;
  actual_risk_reward_ratio: number;
  expectancy: number;
}

export interface BacktestResult {
  id: string;
  strategy_id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  metrics: BacktestMetrics;
  trades: TradeResult[];
  equity_curve: Array<{ date: string; equity: number; drawdown: number }>;
  daily_returns: Array<{ date: string; return_pct: number }>;
  executed_at: string;
  execution_time_seconds: number;
}

// Strategy API Services
export const strategyService = {
  /**
   * Create a new strategy
   */
  createStrategy: async (strategy: StrategyConfig): Promise<Strategy> => {
    const response = await apiClient.post('/strategies/', strategy);
    return response.data;
  },

  /**
   * Get all strategies
   */
  getStrategies: async (params?: {
    assetClass?: string;
    isActive?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<StrategyResponse[]> => {
    const response = await apiClient.get('/strategies/', { params });
    return response.data;
  },

  /**
   * Get a specific strategy by ID
   */
  getStrategy: async (strategyId: string): Promise<Strategy> => {
    const response = await apiClient.get(`/strategies/${strategyId}`);
    return response.data;
  },

  /**
   * Update a strategy
   */
  updateStrategy: async (
    strategyId: string,
    updates: Partial<StrategyConfig>
  ): Promise<Strategy> => {
    const response = await apiClient.put(`/strategies/${strategyId}`, updates);
    return response.data;
  },

  /**
   * Delete a strategy (soft delete)
   */
  deleteStrategy: async (strategyId: string): Promise<void> => {
    await apiClient.delete(`/strategies/${strategyId}`);
  },

  /**
   * Clone a strategy
   */
  cloneStrategy: async (
    strategyId: string,
    newName?: string
  ): Promise<Strategy> => {
    const response = await apiClient.post(`/strategies/${strategyId}/clone`, {
      new_name: newName,
    });
    return response.data;
  },

  /**
   * Validate a strategy
   */
  validateStrategy: async (strategyId: string): Promise<{
    isValid: boolean;
    warnings: string[];
    errors: string[];
  }> => {
    const response = await apiClient.get(`/strategies/${strategyId}/validate`);
    return response.data;
  },
};

// Backtest API Services
export const backtestService = {
  /**
   * Run a backtest
   */
  runBacktest: async (
    request: BacktestRequest
  ): Promise<{ backtest_id: string; status: string; message: string }> => {
    const response = await apiClient.post('/backtest/run', request);
    return response.data;
  },

  /**
   * Get backtest result by ID
   */
  getBacktestResult: async (backtestId: string): Promise<BacktestResult> => {
    const response = await apiClient.get(`/backtest/${backtestId}`);
    return response.data;
  },

  /**
   * Get all backtests for a strategy
   */
  getStrategyBacktests: async (strategyId: string): Promise<BacktestResult[]> => {
    const response = await apiClient.get(`/backtest/strategy/${strategyId}`);
    return response.data;
  },

  /**
   * Get trades from a backtest
   */
  getBacktestTrades: async (
    backtestId: string,
    params?: {
      tradeType?: 'WINNING' | 'LOSING';
      skip?: number;
      limit?: number;
    }
  ): Promise<TradeResult[]> => {
    const response = await apiClient.get(`/backtest/${backtestId}/trades`, {
      params,
    });
    return response.data;
  },

  /**
   * Delete a backtest
   */
  deleteBacktest: async (backtestId: string): Promise<void> => {
    await apiClient.delete(`/backtest/${backtestId}`);
  },

  /**
   * Compare multiple backtests
   */
  compareBacktests: async (
    backtestId: string,
    compareWith: string[]
  ): Promise<any> => {
    const response = await apiClient.post(`/backtest/${backtestId}/compare`, {
      compare_with: compareWith,
    });
    return response.data;
  },
};

export default {
  strategy: strategyService,
  backtest: backtestService,
};
