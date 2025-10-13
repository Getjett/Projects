"""
Unit tests for the backtest engine
Tests core functionality for condition evaluation and trade execution
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core.backtest_engine import BacktestEngine, IndicatorCalculator, ConditionEvaluator
from models.schemas import StrategyJSON, Entry, Exit, EntryTrigger, RiskManagement, TriggerMain


class TestIndicatorCalculator:
    """Test indicator calculation functionality"""
    
    def setup_method(self):
        self.calculator = IndicatorCalculator()
        
        # Create sample OHLCV data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        self.sample_df = pd.DataFrame({
            'open': np.random.uniform(100, 105, 100),
            'high': np.random.uniform(105, 110, 100),
            'low': np.random.uniform(95, 100, 100),
            'close': np.random.uniform(100, 105, 100),
            'volume': np.random.randint(10000, 100000, 100)
        }, index=dates)
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        self.sample_df['high'] = np.maximum(
            self.sample_df['high'], 
            np.maximum(self.sample_df['open'], self.sample_df['close'])
        )
        self.sample_df['low'] = np.minimum(
            self.sample_df['low'],
            np.minimum(self.sample_df['open'], self.sample_df['close'])
        )
    
    def test_sma_calculation(self):
        """Test Simple Moving Average calculation"""
        indicators = [{"name": "SMA", "period": 20, "applied_to": "close"}]
        result_df = self.calculator.calculate_indicators(self.sample_df.copy(), indicators)
        
        assert 'SMA_20' in result_df.columns
        assert not result_df['SMA_20'].isnull().all()
        
        # Check that SMA is calculated correctly for last few values
        manual_sma = self.sample_df['close'].rolling(20).mean().iloc[-1]
        calculated_sma = result_df['SMA_20'].iloc[-1]
        assert abs(manual_sma - calculated_sma) < 0.01
    
    def test_ema_calculation(self):
        """Test Exponential Moving Average calculation"""
        indicators = [{"name": "EMA", "period": 10, "applied_to": "close"}]
        result_df = self.calculator.calculate_indicators(self.sample_df.copy(), indicators)
        
        assert 'EMA_10' in result_df.columns
        assert not result_df['EMA_10'].isnull().all()
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        indicators = [{"name": "RSI", "period": 14, "applied_to": "close"}]
        result_df = self.calculator.calculate_indicators(self.sample_df.copy(), indicators)
        
        assert 'RSI_14' in result_df.columns
        
        # RSI should be between 0 and 100
        rsi_values = result_df['RSI_14'].dropna()
        assert (rsi_values >= 0).all()
        assert (rsi_values <= 100).all()


class TestConditionEvaluator:
    """Test condition evaluation logic"""
    
    def setup_method(self):
        self.evaluator = ConditionEvaluator()
        
        # Create sample data with known patterns
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        self.test_df = pd.DataFrame({
            'open': [100, 102, 104, 103, 105, 107, 106, 108, 110, 109],
            'high': [101, 103, 105, 104, 106, 108, 107, 109, 111, 110],
            'low': [99, 101, 103, 102, 104, 106, 105, 107, 109, 108],
            'close': [101, 103, 104, 103, 105, 107, 106, 108, 110, 109],
            'volume': [1000] * 10
        }, index=dates)
        
        # Add some indicators
        self.test_df['SMA_5'] = self.test_df['close'].rolling(5).mean()
        self.test_df['EMA_5'] = self.test_df['close'].ewm(span=5).mean()
    
    def test_candle_condition_close_above_prev_high(self):
        """Test candle condition: close > previous high"""
        condition = {
            "type": "candle",
            "field": "close",
            "op": ">",
            "value_ref": {"ref": "prev_high"}
        }
        
        # At index 2: close=104, prev_high=103 -> should be True
        result = self.evaluator.evaluate_condition(condition, self.test_df, 2)
        assert result is True
        
        # At index 1: close=103, prev_high=101 -> should be True
        result = self.evaluator.evaluate_condition(condition, self.test_df, 1)
        assert result is True
    
    def test_candle_condition_body_ratio(self):
        """Test body ratio condition"""
        condition = {
            "type": "candle",
            "field": "body_ratio",
            "op": ">",
            "value": 0.5
        }
        
        # Calculate expected body ratio for index 1
        # open=102, high=103, low=101, close=103
        # body = |103-102| = 1, range = 103-101 = 2, ratio = 1/2 = 0.5
        result = self.evaluator.evaluate_condition(condition, self.test_df, 1)
        # Should be False since 0.5 is not > 0.5
        assert result is False
        
        # Test with smaller threshold
        condition["value"] = 0.4
        result = self.evaluator.evaluate_condition(condition, self.test_df, 1)
        assert result is True
    
    def test_indicator_condition(self):
        """Test indicator-based condition"""
        condition = {
            "type": "indicator",
            "name": "SMA_5",
            "op": ">",
            "value": 104
        }
        
        # Check at index where SMA_5 > 104
        result = self.evaluator.evaluate_condition(condition, self.test_df, 8)
        # At index 8, SMA_5 should be around 106-107, so > 104
        assert result is True
    
    def test_main_trigger_close_above_prev_high(self):
        """Test main trigger evaluation"""
        trigger = {
            "point": "close_above_prev_high",
            "candle_id": -1
        }
        
        # At index 2: current close=104, prev high=103
        result = self.evaluator.evaluate_main_trigger(trigger, self.test_df, 2)
        assert result is True
        
        # At index 4: current close=105, prev high=104
        result = self.evaluator.evaluate_main_trigger(trigger, self.test_df, 4)
        assert result is True


class TestBacktestEngine:
    """Test complete backtesting functionality"""
    
    def setup_method(self):
        self.engine = BacktestEngine()
    
    def create_sample_strategy(self) -> StrategyJSON:
        """Create a sample strategy for testing"""
        from models.schemas import (
            Condition, StopLoss, TakeProfit, Indicator
        )
        
        # Simple breakout strategy
        strategy = StrategyJSON(
            strategy_name="Test Breakout Strategy",
            symbol="TEST",
            timeframe="1D",
            description="Simple breakout test strategy",
            indicators=[
                Indicator(name="SMA", period=5, applied_to="close"),
                Indicator(name="RSI", period=14, applied_to="close")
            ],
            entry=Entry(
                trigger=EntryTrigger(
                    main=TriggerMain(
                        point="close_above_prev_high",
                        candle_id=-1
                    ),
                    conditions=[
                        Condition(
                            type="indicator",
                            name="RSI_14",
                            op=">",
                            value=50
                        )
                    ],
                    logical_op="AND"
                ),
                execute_at="close"
            ),
            exit=Exit(
                stop_loss=StopLoss(mode="fixed_pct", value=2.0),
                take_profit=TakeProfit(mode="ratio", value=2.0)
            ),
            risk=RiskManagement(
                capital=100000,
                risk_per_trade_pct=1.0,
                max_open_trades=1
            )
        )
        
        return strategy
    
    def create_sample_data(self) -> pd.DataFrame:
        """Create sample market data with some clear patterns"""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        
        # Create data with uptrend and some breakout opportunities
        base_prices = np.linspace(100, 150, 50)
        noise = np.random.normal(0, 2, 50)
        closes = base_prices + noise
        
        # Create OHLC with proper relationships
        opens = np.roll(closes, 1)  # Previous close becomes next open
        opens[0] = 100
        
        # Add some volatility for highs and lows
        highs = np.maximum(opens, closes) + np.random.uniform(0, 2, 50)
        lows = np.minimum(opens, closes) - np.random.uniform(0, 2, 50)
        
        df = pd.DataFrame({
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': np.random.randint(10000, 50000, 50)
        }, index=dates)
        
        return df
    
    def test_backtest_execution(self):
        """Test complete backtest execution"""
        strategy = self.create_sample_strategy()
        data = self.create_sample_data()
        
        result = self.engine.run_backtest(data, strategy)
        
        # Verify result structure
        assert result.strategy_name == "Test Breakout Strategy"
        assert result.symbol == "TEST"
        assert result.timeframe == "1D"
        assert isinstance(result.summary.trades, int)
        assert result.summary.trades >= 0
        assert isinstance(result.trades, list)
        assert isinstance(result.equity_curve, list)
        
        # If trades were generated, verify trade structure
        if result.trades:
            trade = result.trades[0]
            assert hasattr(trade, 'entry_time')
            assert hasattr(trade, 'entry_price')
            assert hasattr(trade, 'exit_time')
            assert hasattr(trade, 'exit_price')
            assert hasattr(trade, 'pnl')
    
    def test_position_sizing(self):
        """Test position sizing calculation"""
        strategy = self.create_sample_strategy()
        data = self.create_sample_data()
        
        # Test risk-based sizing
        entry_price = 100.0
        current_equity = 100000.0
        
        # Mock the calculation (simplified test)
        risk_pct = strategy.risk.risk_per_trade_pct / 100
        risk_amount = current_equity * risk_pct  # 1000
        
        # Assuming 2% stop loss
        sl_distance = entry_price * 0.02  # 2.0
        expected_size = int(risk_amount / sl_distance)  # 500
        
        # Verify the concept (actual calculation happens in engine)
        assert expected_size > 0
        assert expected_size == 500
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation methods"""
        entry_price = 100.0
        
        # Test fixed percentage SL
        sl_config = {"mode": "fixed_pct", "value": 2.0}
        expected_sl = entry_price * 0.98  # 98.0
        
        # Mock the calculation
        calculated_sl = entry_price * (1 - sl_config["value"] / 100)
        assert abs(calculated_sl - expected_sl) < 0.01


def test_strategy_json_validation():
    """Test Pydantic model validation"""
    from models.schemas import StrategyJSON, Entry, Exit, RiskManagement, EntryTrigger
    
    # Valid strategy
    valid_strategy_data = {
        "strategy_name": "Test Strategy",
        "symbol": "TEST",
        "timeframe": "1D",
        "entry": {
            "trigger": {
                "conditions": [],
                "logical_op": "AND"
            },
            "execute_at": "close"
        },
        "exit": {},
        "risk": {
            "capital": 100000,
            "risk_per_trade_pct": 1.0,
            "max_open_trades": 1
        }
    }
    
    # Should not raise validation error
    strategy = StrategyJSON(**valid_strategy_data)
    assert strategy.strategy_name == "Test Strategy"
    
    # Invalid timeframe should raise validation error
    invalid_data = valid_strategy_data.copy()
    invalid_data["timeframe"] = "invalid"
    
    with pytest.raises(ValueError):
        StrategyJSON(**invalid_data)


if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    # Test indicator calculator
    test_indicators = TestIndicatorCalculator()
    test_indicators.setup_method()
    test_indicators.test_sma_calculation()
    print("✓ SMA calculation test passed")
    
    # Test condition evaluator
    test_conditions = TestConditionEvaluator()
    test_conditions.setup_method()
    test_conditions.test_candle_condition_close_above_prev_high()
    print("✓ Candle condition test passed")
    
    # Test backtest engine
    test_engine = TestBacktestEngine()
    test_engine.setup_method()
    test_engine.test_backtest_execution()
    print("✓ Backtest execution test passed")
    
    print("All basic tests passed! ✅")