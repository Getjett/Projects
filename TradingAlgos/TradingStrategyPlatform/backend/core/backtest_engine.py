"""
Core backtesting engine implementing the strategy evaluation logic
Matches Sprint 3 specification for condition evaluation and trade execution
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from models.schemas import StrategyJSON, BacktestResult, TradeResult, BacktestSummary, EquityPoint


class IndicatorCalculator:
    """Calculate technical indicators using TA-Lib"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> pd.DataFrame:
        """Calculate all required indicators and add to dataframe"""
        df = df.copy()
        
        for indicator in indicators:
            name = indicator['name'].upper()
            period = indicator.get('period', 14)
            applied_to = indicator.get('applied_to', 'close')
            
            if name == 'SMA':
                df[f'SMA_{period}'] = talib.SMA(df[applied_to], timeperiod=period)
            elif name == 'EMA':
                df[f'EMA_{period}'] = talib.EMA(df[applied_to], timeperiod=period)
            elif name == 'RSI':
                df[f'RSI_{period}'] = talib.RSI(df[applied_to], timeperiod=period)
            elif name == 'MACD':
                macd, signal, hist = talib.MACD(df[applied_to])
                df['MACD'] = macd
                df['MACD_SIGNAL'] = signal
                df['MACD_HIST'] = hist
            elif name == 'BOLLINGER' or name == 'BB':
                upper, middle, lower = talib.BBANDS(df[applied_to], timeperiod=period)
                df['BB_UPPER'] = upper
                df['BB_MIDDLE'] = middle
                df['BB_LOWER'] = lower
            elif name == 'ATR':
                df[f'ATR_{period}'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
            elif name == 'VWAP':
                # Simple VWAP calculation
                df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
            elif name == 'STOCH':
                slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'])
                df['STOCH_K'] = slowk
                df['STOCH_D'] = slowd
        
        return df


class ConditionEvaluator:
    """Evaluate trading conditions based on candles and indicators"""
    
    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], df: pd.DataFrame, index: int) -> bool:
        """
        Evaluate a single condition at given index
        Returns True if condition is met, False otherwise
        """
        try:
            condition_type = condition.get('type', 'candle')
            
            if condition_type == 'candle':
                return ConditionEvaluator._evaluate_candle_condition(condition, df, index)
            elif condition_type == 'indicator':
                return ConditionEvaluator._evaluate_indicator_condition(condition, df, index)
            elif condition_type == 'zone':
                return ConditionEvaluator._evaluate_zone_condition(condition, df, index)
            
            return False
            
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    @staticmethod
    def _evaluate_candle_condition(condition: Dict[str, Any], df: pd.DataFrame, index: int) -> bool:
        """Evaluate candle-based conditions"""
        if index < 1:  # Need at least one previous candle
            return False
            
        candle_id = condition.get('candle_id', -1)
        field = condition.get('field', 'close')
        op = condition.get('op', '>')
        value = condition.get('value')
        value_ref = condition.get('value_ref')
        
        # Get candle index (relative positioning)
        target_index = index + candle_id if candle_id < 0 else candle_id
        if target_index < 0 or target_index >= len(df):
            return False
        
        # Get left side value
        if field in ['open', 'high', 'low', 'close', 'volume']:
            left_value = df.iloc[target_index][field]
        elif field == 'body_ratio':
            candle = df.iloc[target_index]
            body = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            left_value = body / total_range if total_range > 0 else 0
        elif field == 'wick_top':
            candle = df.iloc[target_index]
            left_value = candle['high'] - max(candle['open'], candle['close'])
        elif field == 'wick_bottom':
            candle = df.iloc[target_index]
            left_value = min(candle['open'], candle['close']) - candle['low']
        else:
            return False
        
        # Get right side value
        if value_ref:
            if value_ref.get('ref') == 'prev_high':
                right_value = df.iloc[target_index - 1]['high']
            elif value_ref.get('ref') == 'prev_low':
                right_value = df.iloc[target_index - 1]['low']
            elif value_ref.get('ref') == 'prev_close':
                right_value = df.iloc[target_index - 1]['close']
            elif value_ref.get('indicator'):
                indicator_name = value_ref['indicator']
                if indicator_name in df.columns:
                    right_value = df.iloc[target_index][indicator_name]
                else:
                    return False
            else:
                return False
        else:
            right_value = value
        
        # Evaluate condition
        if op == '>':
            return left_value > right_value
        elif op == '<':
            return left_value < right_value
        elif op == '>=':
            return left_value >= right_value
        elif op == '<=':
            return left_value <= right_value
        elif op == '==':
            return abs(left_value - right_value) < 1e-8
        elif op == 'crosses_above':
            prev_left = df.iloc[target_index - 1][field] if target_index > 0 else left_value
            return prev_left <= right_value and left_value > right_value
        elif op == 'crosses_below':
            prev_left = df.iloc[target_index - 1][field] if target_index > 0 else left_value
            return prev_left >= right_value and left_value < right_value
        
        return False
    
    @staticmethod
    def _evaluate_indicator_condition(condition: Dict[str, Any], df: pd.DataFrame, index: int) -> bool:
        """Evaluate indicator-based conditions"""
        indicator_name = condition.get('name')
        op = condition.get('op', '>')
        value = condition.get('value')
        value_ref = condition.get('value_ref')
        
        # Build full indicator column name
        period = condition.get('period')
        if period:
            indicator_col = f"{indicator_name.upper()}_{period}"
        else:
            indicator_col = indicator_name.upper()
        
        if indicator_col not in df.columns:
            print(f"Indicator {indicator_col} not found in dataframe")
            return False
        
        left_value = df.iloc[index][indicator_col]
        
        # Get right side value
        if value_ref:
            if value_ref.get('indicator'):
                right_indicator = value_ref['indicator']
                if right_indicator in df.columns:
                    right_value = df.iloc[index][right_indicator]
                else:
                    return False
            elif value_ref.get('field'):
                field = value_ref['field']
                candle_id = value_ref.get('candle_id', 0)
                target_index = index + candle_id if candle_id < 0 else candle_id
                if 0 <= target_index < len(df):
                    right_value = df.iloc[target_index][field]
                else:
                    return False
            else:
                return False
        else:
            right_value = value
        
        # Evaluate condition
        if op == '>':
            return left_value > right_value
        elif op == '<':
            return left_value < right_value
        elif op == '>=':
            return left_value >= right_value
        elif op == '<=':
            return left_value <= right_value
        elif op == '==':
            return abs(left_value - right_value) < 1e-8
        elif op == 'crosses_above':
            if index > 0:
                prev_left = df.iloc[index - 1][indicator_col]
                return prev_left <= right_value and left_value > right_value
        elif op == 'crosses_below':
            if index > 0:
                prev_left = df.iloc[index - 1][indicator_col]
                return prev_left >= right_value and left_value < right_value
        
        return False
    
    @staticmethod
    def _evaluate_zone_condition(condition: Dict[str, Any], df: pd.DataFrame, index: int) -> bool:
        """Evaluate zone-based conditions (placeholder for future implementation)"""
        # TODO: Implement zone-based conditions
        return False
    
    @staticmethod
    def evaluate_main_trigger(trigger_main: Dict[str, Any], df: pd.DataFrame, index: int) -> bool:
        """Evaluate main trigger conditions like 'close_above_prev_high'"""
        if not trigger_main:
            return True
        
        point = trigger_main.get('point')
        candle_id = trigger_main.get('candle_id', -1)
        
        target_index = index + candle_id if candle_id < 0 else candle_id
        if target_index < 1 or target_index >= len(df):
            return False
        
        current = df.iloc[target_index]
        previous = df.iloc[target_index - 1]
        
        if point == 'close_above_prev_high':
            return current['close'] > previous['high']
        elif point == 'close_below_prev_low':
            return current['close'] < previous['low']
        elif point == 'high_above_prev_high':
            return current['high'] > previous['high']
        elif point == 'low_below_prev_low':
            return current['low'] < previous['low']
        elif point == 'breakout':
            # Simple breakout: high breaks above recent highs
            lookback = 5
            start_idx = max(0, target_index - lookback)
            recent_high = df.iloc[start_idx:target_index]['high'].max()
            return current['high'] > recent_high
        
        return False


class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self):
        self.indicator_calculator = IndicatorCalculator()
        self.condition_evaluator = ConditionEvaluator()
    
    def run_backtest(self, df: pd.DataFrame, strategy: StrategyJSON) -> BacktestResult:
        """
        Run complete backtest on historical data
        Returns detailed backtest results
        """
        try:
            # Prepare data
            df = self._prepare_data(df, strategy)
            
            # Initialize tracking variables
            capital = strategy.risk.capital
            current_equity = capital
            position = None
            trades = []
            equity_curve = []
            
            # Start from index that allows for indicator warmup
            start_index = max(50, len([i for i in strategy.indicators if i.period]) + 10)
            
            # Main backtest loop
            for i in range(start_index, len(df) - 1):
                # Update equity curve
                equity_curve.append(EquityPoint(
                    timestamp=df.index[i],
                    equity=current_equity
                ))
                
                # Entry logic
                if position is None:
                    if self._check_entry_conditions(strategy.entry, df, i):
                        position = self._open_position(strategy, df, i, current_equity)
                        if position:
                            print(f"Opened position at {df.index[i]} - Price: {position['entry_price']}")
                
                # Exit logic
                elif position is not None:
                    exit_result = self._check_exit_conditions(strategy.exit, df, i, position)
                    if exit_result:
                        trade = self._close_position(position, exit_result, df, i)
                        trades.append(trade)
                        current_equity += trade.pnl
                        position = None
                        print(f"Closed position at {df.index[i]} - P&L: {trade.pnl:.2f}")
            
            # Close any remaining position
            if position is not None:
                exit_result = {
                    'exit_price': df.iloc[-1]['close'],
                    'exit_reason': 'end_of_data'
                }
                trade = self._close_position(position, exit_result, df, len(df) - 1)
                trades.append(trade)
                current_equity += trade.pnl
            
            # Calculate summary metrics
            summary = self._calculate_summary(trades, capital, current_equity)
            
            # Build result
            result = BacktestResult(
                strategy_name=strategy.strategy_name,
                symbol=strategy.symbol,
                timeframe=strategy.timeframe,
                period={
                    "from": df.index[0].strftime("%Y-%m-%d"),
                    "to": df.index[-1].strftime("%Y-%m-%d")
                },
                summary=summary,
                equity_curve=equity_curve,
                trades=trades,
                completed_at=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            print(f"Backtest error: {e}")
            raise e
    
    def _prepare_data(self, df: pd.DataFrame, strategy: StrategyJSON) -> pd.DataFrame:
        """Prepare data with indicators"""
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Calculate indicators
        if strategy.indicators:
            df = self.indicator_calculator.calculate_indicators(df, [i.dict() for i in strategy.indicators])
        
        return df
    
    def _check_entry_conditions(self, entry: Any, df: pd.DataFrame, index: int) -> bool:
        """Check if entry conditions are met"""
        trigger = entry.trigger
        
        # Check main trigger
        if trigger.main:
            if not self.condition_evaluator.evaluate_main_trigger(trigger.main.dict(), df, index):
                return False
        
        # Check additional conditions
        if trigger.conditions:
            condition_results = []
            for condition in trigger.conditions:
                result = self.condition_evaluator.evaluate_condition(condition.dict(), df, index)
                condition_results.append(result)
            
            # Apply logical operator
            if trigger.logical_op == "AND":
                return all(condition_results)
            elif trigger.logical_op == "OR":
                return any(condition_results)
        
        return True
    
    def _open_position(self, strategy: StrategyJSON, df: pd.DataFrame, index: int, current_equity: float) -> Optional[Dict]:
        """Open a new position"""
        try:
            # Determine entry price based on execute_at
            if strategy.entry.execute_at == "close":
                entry_price = df.iloc[index]['close']
            elif strategy.entry.execute_at == "market_next_open":
                if index + 1 < len(df):
                    entry_price = df.iloc[index + 1]['open']
                else:
                    return None
            else:
                entry_price = df.iloc[index]['close']
            
            # Calculate position size
            position_size = self._calculate_position_size(strategy, entry_price, current_equity, df, index)
            
            if position_size <= 0:
                return None
            
            # Calculate stop loss and take profit
            sl_price = self._calculate_stop_loss(strategy.exit.stop_loss, entry_price, df, index)
            tp_price = self._calculate_take_profit(strategy.exit.take_profit, entry_price, sl_price)
            
            return {
                'entry_time': df.index[index],
                'entry_index': index,
                'entry_price': entry_price,
                'size': position_size,
                'stop_loss': sl_price,
                'take_profit': tp_price,
                'equity_before': current_equity
            }
            
        except Exception as e:
            print(f"Error opening position: {e}")
            return None
    
    def _calculate_position_size(self, strategy: StrategyJSON, entry_price: float, current_equity: float, df: pd.DataFrame, index: int) -> int:
        """Calculate position size based on risk management"""
        if strategy.risk.fixed_size:
            return strategy.risk.fixed_size
        
        # Risk-based sizing
        risk_amount = current_equity * (strategy.risk.risk_per_trade_pct / 100)
        
        # Calculate stop loss distance for risk calculation
        sl_price = self._calculate_stop_loss(strategy.exit.stop_loss, entry_price, df, index)
        if sl_price:
            sl_distance = abs(entry_price - sl_price)
            if sl_distance > 0:
                position_size = int(risk_amount / sl_distance)
                return max(1, position_size)
        
        # Fallback to fixed percentage of equity
        return max(1, int(current_equity * 0.1 / entry_price))
    
    def _calculate_stop_loss(self, stop_loss: Any, entry_price: float, df: pd.DataFrame, index: int) -> Optional[float]:
        """Calculate stop loss price"""
        if not stop_loss:
            return None
        
        mode = stop_loss.mode
        
        if mode == "fixed_price":
            return stop_loss.value
        elif mode == "fixed_pct":
            return entry_price * (1 - stop_loss.value / 100)
        elif mode == "atr":
            atr_cols = [col for col in df.columns if 'ATR' in col]
            if atr_cols and index > 0:
                atr_value = df.iloc[index][atr_cols[0]]
                multiplier = stop_loss.multiplier or 1.0
                return entry_price - (atr_value * multiplier)
        elif mode == "prev_candle_low":
            if index > 0:
                return df.iloc[index - 1]['low']
        
        # Default: 2% stop loss
        return entry_price * 0.98
    
    def _calculate_take_profit(self, take_profit: Any, entry_price: float, sl_price: Optional[float]) -> Optional[float]:
        """Calculate take profit price"""
        if not take_profit:
            return None
        
        mode = take_profit.mode
        
        if mode == "fixed_price":
            return take_profit.value
        elif mode == "fixed":
            return entry_price + take_profit.value
        elif mode == "ratio" and sl_price:
            risk = abs(entry_price - sl_price)
            return entry_price + (risk * take_profit.value)
        
        return None
    
    def _check_exit_conditions(self, exit_config: Any, df: pd.DataFrame, index: int, position: Dict) -> Optional[Dict]:
        """Check if exit conditions are met"""
        current_candle = df.iloc[index]
        
        # Check stop loss hit (intrabar)
        if position.get('stop_loss'):
            if current_candle['low'] <= position['stop_loss'] <= current_candle['high']:
                return {
                    'exit_price': position['stop_loss'],
                    'exit_reason': 'stop_loss'
                }
        
        # Check take profit hit (intrabar)
        if position.get('take_profit'):
            if current_candle['low'] <= position['take_profit'] <= current_candle['high']:
                return {
                    'exit_price': position['take_profit'],
                    'exit_reason': 'take_profit'
                }
        
        # Check exit conditions
        if exit_config.exit_conditions:
            condition_results = []
            for condition in exit_config.exit_conditions:
                result = self.condition_evaluator.evaluate_condition(condition.dict(), df, index)
                condition_results.append(result)
            
            # Apply logical operator
            conditions_met = False
            if exit_config.logical_op == "AND":
                conditions_met = all(condition_results)
            elif exit_config.logical_op == "OR":
                conditions_met = any(condition_results)
            
            if conditions_met:
                return {
                    'exit_price': current_candle['close'],
                    'exit_reason': 'exit_condition'
                }
        
        return None
    
    def _close_position(self, position: Dict, exit_result: Dict, df: pd.DataFrame, index: int) -> TradeResult:
        """Close position and create trade result"""
        exit_price = exit_result['exit_price']
        exit_reason = exit_result['exit_reason']
        
        pnl = (exit_price - position['entry_price']) * position['size']
        pnl_pct = (exit_price - position['entry_price']) / position['entry_price'] * 100
        
        holding_period = df.index[index] - position['entry_time']
        
        return TradeResult(
            trade_id=len([]) + 1,  # Will be set by caller
            entry_time=position['entry_time'],
            entry_index=position['entry_index'],
            entry_price=position['entry_price'],
            exit_time=df.index[index],
            exit_index=index,
            exit_price=exit_price,
            direction="LONG",  # Assuming long for now
            size=position['size'],
            pnl=pnl,
            pnl_pct=pnl_pct,
            holding_period=str(holding_period),
            entry_rule="strategy_entry",
            exit_rule=exit_reason,
            sl_hit=exit_reason == 'stop_loss',
            tp_hit=exit_reason == 'take_profit',
            trade_equity_before=position['equity_before'],
            trade_equity_after=position['equity_before'] + pnl
        )
    
    def _calculate_summary(self, trades: List[TradeResult], initial_capital: float, final_equity: float) -> BacktestSummary:
        """Calculate summary statistics"""
        if not trades:
            return BacktestSummary(
                net_profit=0,
                gross_profit=0,
                gross_loss=0,
                win_rate=0,
                trades=0,
                max_drawdown=0,
                avg_trade_return=0
            )
        
        # Basic metrics
        total_trades = len(trades)
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]
        
        net_profit = final_equity - initial_capital
        gross_profit = sum(t.pnl for t in wins)
        gross_loss = sum(t.pnl for t in losses)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        
        # Calculate max drawdown
        equity_values = [initial_capital]
        running_equity = initial_capital
        for trade in trades:
            running_equity += trade.pnl
            equity_values.append(running_equity)
        
        peak = initial_capital
        max_drawdown = 0
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Other metrics
        avg_trade_return = net_profit / total_trades if total_trades > 0 else 0
        profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else 0
        
        return BacktestSummary(
            net_profit=net_profit,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            win_rate=win_rate,
            trades=total_trades,
            max_drawdown=max_drawdown,
            avg_trade_return=avg_trade_return,
            profit_factor=profit_factor if profit_factor != float('inf') else 0
        )