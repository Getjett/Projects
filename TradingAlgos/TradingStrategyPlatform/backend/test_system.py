"""
Comprehensive System Tests
Tests for the complete AstraCharts Trading Platform
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import json
from datetime import datetime

# Import application
from main import app
from core.backtest_engine import BacktestEngine, IndicatorCalculator
from core.data_fetcher import DataFetcher
from core.chart_visualization import ChartVisualization
from models.schemas import StrategyJSON, BacktestRequest, CandleData

# Test client
client = TestClient(app)


class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    def test_api_health(self):
        """Test API is responding"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_strategy_import_api(self):
        """Test strategy import endpoint"""
        
        strategy_data = {
            "name": "Test Strategy",
            "version": "1.0", 
            "description": "Test strategy for API",
            "parameters": {"capital": 100000},
            "indicators": [{"name": "SMA", "period": 20}],
            "entry_conditions": [{"type": "price", "operator": ">", "value": 100}],
            "exit_conditions": [{"type": "price", "operator": "<", "value": 95}],
            "metadata": {"author": "Test", "created": "2024-01-01T00:00:00"}
        }
        
        response = client.post("/api/strategies/import", json=strategy_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "strategy_id" in data["data"]
    
    def test_market_data_api(self):
        """Test market data endpoint"""
        
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
    
    def test_backtest_api(self):
        """Test backtest execution endpoint"""
        
        strategy_data = {
            "name": "Test Backtest Strategy",
            "version": "1.0",
            "description": "Simple test strategy",
            "parameters": {"capital": 100000, "position_size": 0.1},
            "indicators": [{"name": "SMA", "period": 10}],
            "entry_conditions": [{"type": "price", "operator": ">", "value": 100}],
            "exit_conditions": [{"type": "price", "operator": "<", "value": 95}],
            "metadata": {"author": "Test", "created": "2024-01-01T00:00:00"}
        }
        
        backtest_request = {
            "strategy": strategy_data,
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
    
    def test_chart_generation_api(self):
        """Test chart generation endpoint"""
        
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
        assert "main_chart" in data["data"]["charts"]
    
    def test_indicator_chart_api(self):
        """Test indicator-specific chart endpoint"""
        
        response = client.get(
            "/api/charts/TESTSTOCK/indicators",
            params={
                "indicators": "SMA,RSI",
                "timeframe": "1d",
                "periods": "20,14"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "chart" in data["data"]


class TestCoreComponents:
    """Tests for core system components"""
    
    @pytest.mark.asyncio
    async def test_data_fetcher(self):
        """Test data fetching functionality"""
        
        fetcher = DataFetcher()
        df = await fetcher.get_historical_data("TESTSTOCK", "1d", "2024-01-01", "2024-01-10")
        
        assert not df.empty
        assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
        assert (df['high'] >= df['low']).all()
        assert (df['volume'] > 0).all()
    
    def test_indicator_calculator(self):
        """Test technical indicator calculations"""
        
        import pandas as pd
        
        calc = IndicatorCalculator()
        
        # Create test data
        df = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [102, 103, 104, 105, 106],
            'low': [99, 100, 101, 102, 103],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Test SMA calculation
        result = calc.calculate_indicators(df, [{"name": "SMA", "period": 3}])
        assert "SMA_3" in result.columns
        assert not result["SMA_3"].iloc[-1] == 0  # Should have valid values
        
        # Test multiple indicators
        indicators = [
            {"name": "SMA", "period": 3},
            {"name": "EMA", "period": 3},
            {"name": "RSI", "period": 4}
        ]
        result = calc.calculate_indicators(df, indicators)
        
        expected_cols = ["SMA_3", "EMA_3", "RSI_4"]
        for col in expected_cols:
            assert col in result.columns
    
    def test_chart_visualization(self):
        """Test chart generation functionality"""
        
        viz = ChartVisualization()
        
        # Create test candles
        candles = [
            CandleData(
                timestamp=f"2024-01-0{i}T00:00:00",
                open=100 + i,
                high=105 + i,
                low=95 + i, 
                close=102 + i,
                volume=1000000
            )
            for i in range(1, 6)
        ]
        
        # Test basic chart
        chart = viz.create_candlestick_chart(candles, title="Test Chart")
        
        assert isinstance(chart, dict)
        assert "data" in chart
        assert "layout" in chart
        assert chart["layout"]["title"]["text"] == "Test Chart"
        
        # Test chart with indicators
        indicators = {"SMA_10": [100, 101, 102, 103, 104]}
        chart_with_indicators = viz.create_candlestick_chart(candles, indicators=indicators)
        
        assert len(chart_with_indicators["data"]) >= len(chart["data"])
    
    @pytest.mark.asyncio
    async def test_backtest_engine(self):
        """Test backtest engine functionality"""
        
        engine = BacktestEngine()
        
        # Create simple test strategy
        strategy = StrategyJSON(
            name="Test Engine Strategy",
            version="1.0",
            description="Engine test",
            parameters={"capital": 100000, "position_size": 0.1},
            indicators=[{"name": "SMA", "period": 5}],
            entry_conditions=[{"type": "price", "operator": ">", "value": 100}],
            exit_conditions=[{"type": "price", "operator": "<", "value": 95}],
            metadata={"author": "Test", "created": "2024-01-01T00:00:00"}
        )
        
        request = BacktestRequest(
            strategy=strategy,
            symbol="TESTENGINE",
            timeframe="1d", 
            from_date="2024-01-01",
            to_date="2024-01-10"
        )
        
        result = await engine.run_backtest(request)
        
        assert result.success is True
        assert result.strategy_name == "Test Engine Strategy"
        assert result.summary is not None
        assert isinstance(result.summary.trades, int)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_strategy_import(self):
        """Test handling of invalid strategy data"""
        
        invalid_strategy = {"invalid": "data"}
        response = client.post("/api/strategies/import", json=invalid_strategy)
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_symbol(self):
        """Test handling of non-existent trading symbols"""
        
        # Should gracefully handle and return sample data
        response = client.get("/api/market-data/NONEXISTENT")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_invalid_date_range(self):
        """Test handling of invalid date ranges"""
        
        response = client.get(
            "/api/market-data/TESTSTOCK",
            params={
                "from_date": "2024-12-31",  # Future date
                "to_date": "2024-01-01"     # Past date
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self):
        """Test system with larger datasets"""
        
        # Test with longer date range
        response = client.get(
            "/api/market-data/TESTSTOCK",
            params={
                "timeframe": "1d",
                "from_date": "2023-01-01",
                "to_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Should handle large datasets
        candle_count = len(data["data"]["candles"])
        assert candle_count > 0
    
    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/api/market-data/CONCURRENT_TEST")
            results.append(response.status_code == 200)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        execution_time = time.time() - start_time
        
        # All requests should succeed
        assert all(results)
        assert len(results) == 5
        
        # Should complete within reasonable time
        assert execution_time < 10.0


def run_comprehensive_tests():
    """Run all tests and generate report"""
    
    print("🧪 Running Comprehensive System Tests")
    print("=" * 50)
    
    # Run pytest with custom configuration
    test_results = pytest.main([
        __file__,
        "-v",  # Verbose
        "-s",  # Don't capture stdout  
        "--tb=short",  # Short traceback
        "--durations=5"  # Show 5 slowest tests
    ])
    
    return test_results


if __name__ == "__main__":
    # Run comprehensive test suite
    result_code = run_comprehensive_tests()
    
    if result_code == 0:
        print("\n🎉 All tests passed!")
        print("✅ System is fully functional")
    else:
        print(f"\n⚠️  Some tests failed (exit code: {result_code})")
        print("❌ Check test output for details")