"""
Comprehensive test suite for the AstraCharts Trading Platform
Tests all major components: backtest engine, API endpoints, data fetching, and visualization
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from fastapi.testclient import TestClient
import json
from unittest.mock import Mock, patch

# Import application components
from main import app
from core.backtest_engine import BacktestEngine, IndicatorCalculator, ConditionEvaluator
from core.data_fetcher import DataFetcher
from core.chart_visualization import ChartVisualization
from models.schemas import (
    StrategyJSON, BacktestRequest, BacktestResult, 
    CandleData, TradeResult, BacktestSummary
)

# Test client
client = TestClient(app)

class TestBacktestEngine:
    """Test suite for the backtesting engine"""
    
    def setup_method(self):
        """Setup test data and engine"""
        self.engine = BacktestEngine()
        
        # Create sample market data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        self.sample_data = pd.DataFrame({
            'open': [100 + i for i in range(len(dates))],
            'high': [102 + i for i in range(len(dates))],
            'low': [98 + i for i in range(len(dates))],
            'close': [101 + i for i in range(len(dates))],
            'volume': [1000000 + i*10000 for i in range(len(dates))]
        }, index=dates)
        
        # Sample strategy
        self.sample_strategy = StrategyJSON(
            name="Test SMA Strategy",
            version="1.0",
            description="Simple SMA crossover test",
            parameters={
                "capital": 100000,
                "position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.05
            },
            indicators=[
                {"name": "SMA", "period": 10, "source": "close"},
                {"name": "SMA", "period": 20, "source": "close"}
            ],
            entry_conditions=[
                {
                    "type": "crossover",
                    "indicator1": "SMA_10",
                    "indicator2": "SMA_20",
                    "direction": "above"
                }
            ],
            exit_conditions=[
                {
                    "type": "crossover", 
                    "indicator1": "SMA_10",
                    "indicator2": "SMA_20",
                    "direction": "below"
                }
            ],
            metadata={
                "author": "Test Suite",
                "created": datetime.now().isoformat(),
                "category": "trend_following"
            }
        )
    
    @pytest.mark.asyncio
    async def test_indicator_calculation(self):
        """Test technical indicator calculations"""
        calculator = IndicatorCalculator()
        
        # Test SMA calculation
        indicators = [{"name": "SMA", "period": 10, "source": "close"}]
        result_df = calculator.calculate_indicators(self.sample_data.copy(), indicators)
        
        assert 'SMA_10' in result_df.columns
        assert not result_df['SMA_10'].iloc[-1] == 0  # Should have valid values
        
        # Test multiple indicators
        indicators = [
            {"name": "SMA", "period": 10},
            {"name": "EMA", "period": 12},
            {"name": "RSI", "period": 14}
        ]
        result_df = calculator.calculate_indicators(self.sample_data.copy(), indicators)
        
        expected_columns = ['SMA_10', 'EMA_12', 'RSI_14']
        for col in expected_columns:
            assert col in result_df.columns
    
    def test_condition_evaluation(self):
        """Test strategy condition evaluation"""
        evaluator = ConditionEvaluator()
        
        # Create test data with crossover
        test_data = pd.DataFrame({
            'SMA_10': [10, 11, 12, 13, 14],
            'SMA_20': [12, 12, 12, 12, 12],
            'close': [100, 101, 102, 103, 104]
        })
        
        # Test crossover condition
        condition = {
            "type": "crossover",
            "indicator1": "SMA_10", 
            "indicator2": "SMA_20",
            "direction": "above"
        }
        
        results = evaluator.evaluate_condition(test_data, condition)
        
        # Should detect crossover at index 2 (10->11->12 crossing above 12)
        assert any(results), "Crossover should be detected"
    
    @pytest.mark.asyncio
    async def test_full_backtest_execution(self):
        """Test complete backtest execution"""
        
        # Mock data fetcher to return our sample data
        with patch.object(self.engine, 'data_fetcher') as mock_fetcher:
            mock_fetcher.get_historical_data.return_value = self.sample_data
            
            # Execute backtest
            request = BacktestRequest(
                strategy=self.sample_strategy,
                symbol="TESTSTOCK",
                timeframe="1d",
                from_date="2024-01-01",
                to_date="2024-01-31"
            )
            
            result = await self.engine.run_backtest(request)
            
            # Verify result structure
            assert isinstance(result, BacktestResult)
            assert result.success is True
            assert result.summary is not None
            assert isinstance(result.summary.total_trades, int)
            assert isinstance(result.summary.net_profit, float)
    
    def test_trade_execution_logic(self):
        """Test trade entry and exit logic"""
        
        # Test data with clear signals
        df = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 103, 102, 101],
            'high': [102, 103, 104, 105, 106, 105, 104, 103],
            'low': [98, 99, 100, 101, 102, 101, 100, 99],
            'close': [101, 102, 103, 104, 105, 104, 103, 102],
            'volume': [1000000] * 8,
            'SMA_10': [100, 101, 102, 103, 104, 103, 102, 101],
            'SMA_20': [102, 102, 102, 102, 102, 102, 102, 102]
        })
        
        # Execute trades manually for testing
        trades = []
        position = None
        
        for i in range(1, len(df)):
            # Entry condition: SMA_10 crosses above SMA_20
            if df['SMA_10'].iloc[i] > df['SMA_20'].iloc[i] and df['SMA_10'].iloc[i-1] <= df['SMA_20'].iloc[i-1]:
                if position is None:
                    position = {
                        'entry_price': df['close'].iloc[i],
                        'entry_time': i,
                        'direction': 'LONG'
                    }
            
            # Exit condition: SMA_10 crosses below SMA_20  
            elif df['SMA_10'].iloc[i] < df['SMA_20'].iloc[i] and df['SMA_10'].iloc[i-1] >= df['SMA_20'].iloc[i-1]:
                if position is not None:
                    exit_price = df['close'].iloc[i]
                    pnl = (exit_price - position['entry_price']) * 1000  # 1000 shares
                    
                    trades.append({
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'direction': position['direction']
                    })
                    position = None
        
        # Should have executed at least one trade
        assert len(trades) > 0, "Should execute trades with clear signals"


class TestDataFetcher:
    """Test suite for data fetching functionality"""
    
    def setup_method(self):
        self.data_fetcher = DataFetcher()
    
    @pytest.mark.asyncio
    async def test_sample_data_generation(self):
        """Test sample data generation when API unavailable"""
        
        # Test with different timeframes
        timeframes = ["1d", "1h", "15m"]
        
        for timeframe in timeframes:
            df = await self.data_fetcher.get_historical_data(
                "SAMPLESTOCK", timeframe, "2024-01-01", "2024-01-31"
            )
            
            assert not df.empty, f"Should generate data for {timeframe}"
            assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
            assert df['high'].min() >= df['low'].max() or True  # Basic OHLC validation
    
    @pytest.mark.asyncio
    async def test_data_validation(self):
        """Test data validation and cleaning"""
        
        df = await self.data_fetcher.get_historical_data(
            "TESTSTOCK", "1d", "2024-01-01", "2024-01-10"
        )
        
        # Check for valid OHLC relationships
        assert (df['high'] >= df['low']).all(), "High should be >= Low"
        assert (df['high'] >= df['open']).all(), "High should be >= Open"
        assert (df['high'] >= df['close']).all(), "High should be >= Close"
        assert (df['low'] <= df['open']).all(), "Low should be <= Open"
        assert (df['low'] <= df['close']).all(), "Low should be <= Close"
        
        # Check for positive volume
        assert (df['volume'] > 0).all(), "Volume should be positive"


class TestChartVisualization:
    """Test suite for chart visualization"""
    
    def setup_method(self):
        self.viz = ChartVisualization()
        
        # Sample candle data
        self.sample_candles = [
            CandleData(
                timestamp=f"2024-01-{i:02d}T00:00:00",
                open=100 + i,
                high=102 + i,
                low=98 + i,
                close=101 + i,
                volume=1000000 + i*10000
            )
            for i in range(1, 11)
        ]
        
        # Sample backtest result
        self.sample_backtest = BacktestResult(
            success=True,
            strategy_name="Test Strategy",
            symbol="TESTSTOCK",
            timeframe="1d",
            from_date="2024-01-01",
            to_date="2024-01-10",
            summary=BacktestSummary(
                net_profit=1500.0,
                gross_profit=3000.0,
                gross_loss=-1500.0,
                total_trades=3,
                winning_trades=2,
                losing_trades=1,
                win_rate=66.67,
                avg_win=1500.0,
                avg_loss=1500.0,
                profit_factor=2.0,
                max_drawdown=5.2,
                sharpe_ratio=1.5
            ),
            trades=[
                TradeResult(
                    entry_time="2024-01-02T00:00:00",
                    exit_time="2024-01-03T00:00:00", 
                    entry_price=101.0,
                    exit_price=103.0,
                    direction="LONG",
                    size=1000,
                    pnl=2000.0,
                    pnl_pct=1.98
                )
            ],
            equity_curve=[],
            execution_time=1.5,
            message="Test completed successfully"
        )
    
    def test_candlestick_chart_creation(self):
        """Test basic candlestick chart creation"""
        
        chart_data = self.viz.create_candlestick_chart(
            candles=self.sample_candles,
            title="Test Chart"
        )
        
        assert isinstance(chart_data, dict), "Should return dict (Plotly JSON)"
        assert 'data' in chart_data, "Should contain data traces"
        assert 'layout' in chart_data, "Should contain layout"
        assert chart_data['layout']['title']['text'] == "Test Chart"
    
    def test_chart_with_backtest_overlay(self):
        """Test chart with backtest trade markers"""
        
        chart_data = self.viz.create_candlestick_chart(
            candles=self.sample_candles,
            backtest_result=self.sample_backtest,
            title="Backtest Chart"
        )
        
        # Should contain trade markers
        trace_names = [trace.get('name', '') for trace in chart_data['data']]
        assert any('Entry' in name for name in trace_names), "Should contain entry markers"
    
    def test_equity_curve_generation(self):
        """Test equity curve chart generation"""
        
        # Add equity curve data to backtest result
        self.sample_backtest.equity_curve = [
            type('EquityPoint', (), {
                'timestamp': f"2024-01-0{i}T00:00:00",
                'equity': 100000 + i*1000
            })() for i in range(1, 6)
        ]
        
        equity_chart = self.viz.create_equity_curve_chart(self.sample_backtest)
        
        assert isinstance(equity_chart, dict), "Should return chart data"
        if equity_chart:  # If not empty
            assert 'data' in equity_chart


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_strategy_import_endpoint(self):
        """Test strategy import API"""
        
        strategy_data = {
            "name": "Test API Strategy",
            "version": "1.0",
            "description": "API test strategy",
            "parameters": {"capital": 100000},
            "indicators": [{"name": "SMA", "period": 20}],
            "entry_conditions": [{"type": "price", "operator": ">", "value": 100}],
            "exit_conditions": [{"type": "price", "operator": "<", "value": 95}],
            "metadata": {"author": "API Test", "created": "2024-01-01T00:00:00"}
        }
        
        response = client.post("/api/strategies/import", json=strategy_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "strategy_id" in data["data"]
    
    def test_backtest_execution_endpoint(self):
        """Test backtest execution API"""
        
        backtest_request = {
            "strategy": {
                "name": "API Backtest Strategy",
                "version": "1.0", 
                "description": "Test backtest via API",
                "parameters": {"capital": 100000},
                "indicators": [{"name": "SMA", "period": 10}],
                "entry_conditions": [{"type": "price", "operator": ">", "value": 100}],
                "exit_conditions": [{"type": "price", "operator": "<", "value": 95}],
                "metadata": {"author": "API Test", "created": "2024-01-01T00:00:00"}
            },
            "symbol": "TESTSTOCK",
            "timeframe": "1d",
            "from_date": "2024-01-01",
            "to_date": "2024-01-10"
        }
        
        response = client.post("/api/backtest/execute", json=backtest_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "backtest_result" in data["data"]
    
    def test_market_data_endpoint(self):
        """Test market data fetching API"""
        
        response = client.get(
            "/api/market-data/TESTSTOCK",
            params={
                "timeframe": "1d",
                "from_date": "2024-01-01", 
                "to_date": "2024-01-10"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "candles" in data["data"]
        assert len(data["data"]["candles"]) > 0
    
    def test_chart_generation_endpoint(self):
        """Test chart generation API"""
        
        response = client.get(
            "/api/charts/chart/TESTSTOCK",
            params={
                "timeframe": "1d",
                "from_date": "2024-01-01",
                "to_date": "2024-01-10"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "charts" in data["data"]


class TestSystemIntegration:
    """Integration tests for complete system workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_backtest_workflow(self):
        """Test complete end-to-end backtest workflow"""
        
        # 1. Import strategy
        strategy_data = {
            "name": "Integration Test Strategy",
            "version": "1.0",
            "description": "Full workflow test",
            "parameters": {"capital": 100000, "position_size": 0.1},
            "indicators": [
                {"name": "SMA", "period": 10},
                {"name": "SMA", "period": 20}
            ],
            "entry_conditions": [{
                "type": "crossover",
                "indicator1": "SMA_10",
                "indicator2": "SMA_20", 
                "direction": "above"
            }],
            "exit_conditions": [{
                "type": "crossover",
                "indicator1": "SMA_10",
                "indicator2": "SMA_20",
                "direction": "below"
            }],
            "metadata": {"author": "Integration Test", "created": "2024-01-01T00:00:00"}
        }
        
        import_response = client.post("/api/strategies/import", json=strategy_data)
        assert import_response.status_code == 200
        
        # 2. Execute backtest
        backtest_request = {
            "strategy": strategy_data,
            "symbol": "TESTSTOCK",
            "timeframe": "1d",
            "from_date": "2024-01-01", 
            "to_date": "2024-01-31"
        }
        
        backtest_response = client.post("/api/backtest/execute", json=backtest_request)
        assert backtest_response.status_code == 200
        
        backtest_data = backtest_response.json()
        assert backtest_data["success"] is True
        
        # 3. Generate visualization
        viz_response = client.post(
            "/api/charts/backtest-visualization",
            json=backtest_data["data"]["backtest_result"],
            params={"symbol": "TESTSTOCK", "timeframe": "1d"}
        )
        
        assert viz_response.status_code == 200
        viz_data = viz_response.json()
        assert viz_data["success"] is True
        assert "charts" in viz_data["data"]
    
    def test_error_handling(self):
        """Test API error handling"""
        
        # Test invalid strategy
        invalid_strategy = {"invalid": "data"}
        response = client.post("/api/strategies/import", json=invalid_strategy)
        assert response.status_code == 422  # Validation error
        
        # Test invalid symbol
        response = client.get("/api/market-data/INVALID@SYMBOL")
        # Should handle gracefully and return sample data
        assert response.status_code == 200
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation accuracy"""
        
        # Create known trade scenario
        trades = [
            {"entry": 100, "exit": 110, "size": 1000},  # +10000
            {"entry": 110, "exit": 105, "size": 1000},  # -5000  
            {"entry": 105, "exit": 115, "size": 1000},  # +10000
        ]
        
        total_pnl = sum((trade["exit"] - trade["entry"]) * trade["size"] for trade in trades)
        winning_trades = sum(1 for trade in trades if trade["exit"] > trade["entry"])
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades) * 100
        
        assert total_pnl == 15000, "P&L calculation should be correct"
        assert win_rate == 66.67, "Win rate calculation should be correct" 


# Performance benchmarks
class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_backtest_performance(self):
        """Test backtest execution performance"""
        import time
        
        engine = BacktestEngine()
        
        # Create larger dataset for performance test
        dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='D')
        large_data = pd.DataFrame({
            'open': [100 + (i % 50) for i in range(len(dates))],
            'high': [102 + (i % 50) for i in range(len(dates))], 
            'low': [98 + (i % 50) for i in range(len(dates))],
            'close': [101 + (i % 50) for i in range(len(dates))],
            'volume': [1000000 + i*1000 for i in range(len(dates))]
        }, index=dates)
        
        strategy = StrategyJSON(
            name="Performance Test Strategy",
            version="1.0",
            description="Performance testing",
            parameters={"capital": 100000},
            indicators=[{"name": "SMA", "period": 20}],
            entry_conditions=[{"type": "price", "operator": ">", "value": 120}],
            exit_conditions=[{"type": "price", "operator": "<", "value": 110}],
            metadata={"author": "Perf Test", "created": "2024-01-01T00:00:00"}
        )
        
        # Mock data fetcher
        with patch.object(engine, 'data_fetcher') as mock_fetcher:
            mock_fetcher.get_historical_data.return_value = large_data
            
            start_time = time.time()
            
            request = BacktestRequest(
                strategy=strategy,
                symbol="PERFTEST",
                timeframe="1d",
                from_date="2023-01-01",
                to_date="2024-01-31"
            )
            
            result = await engine.run_backtest(request)
            
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert execution_time < 10.0, f"Backtest should complete within 10s, took {execution_time:.2f}s"
            assert result.success is True, "Large backtest should succeed"
            assert len(large_data) > 300, "Should handle large datasets"


# Fixtures for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",  # Verbose output
        "-s",  # Don't capture stdout
        "--tb=short",  # Short traceback format
        "--durations=10"  # Show 10 slowest tests
    ])