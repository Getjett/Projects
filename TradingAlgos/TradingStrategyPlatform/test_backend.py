"""
Simple test script to verify the Strategy Builder backend is working
Run this after starting the backend server: python app.py
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """Test if the backend is running"""
    print("\n1. Testing Health Check...")
    response = requests.get("http://localhost:8000/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ Health check passed!")

def test_create_strategy():
    """Test creating a strategy"""
    print("\n2. Testing Create Strategy...")
    
    strategy_data = {
        "strategy_name": "Test BankNifty Strategy",
        "description": "Test strategy for verification",
        "tags": ["test", "options"],
        "asset_class": "OPTIONS",
        "instrument": "BANKNIFTY",
        "exchange": "NFO",
        "product_type": "MIS",
        "trading_type": "Intraday",
        "signal_bar": "Second Bar",
        "time_frame": "5 Minute",
        "breakout_type": "Second Bar Breakout",
        "breakout_direction": "BOTH",
        "entry_confirmation": {
            "volume_confirmation": False,
            "candle_close": True,
            "retest": False
        },
        "volume_threshold": 150,
        "expiry": "Current Weekly",
        "strike_selection": "ATM",
        "strike_offset": 0,
        "option_type": "BOTH",
        "premium_min": 50,
        "premium_max": 500,
        "target_type": "PERCENTAGE",
        "target_value": 50,
        "stop_loss_type": "PERCENTAGE",
        "stop_loss_value": 30,
        "trailing_stop": False,
        "max_loss_per_day": 5000,
        "max_trades_per_day": 5,
        "risk_reward_ratio": 1.5
    }
    
    response = requests.post(f"{BASE_URL}/strategies/", json=strategy_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        strategy = response.json()
        print(f"   Created Strategy ID: {strategy['id']}")
        print(f"   Strategy Name: {strategy['strategy_name']}")
        print("   ✅ Strategy creation passed!")
        return strategy['id']
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_get_strategies():
    """Test getting all strategies"""
    print("\n3. Testing Get All Strategies...")
    
    response = requests.get(f"{BASE_URL}/strategies/")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        strategies = response.json()
        print(f"   Found {len(strategies)} strategies")
        print("   ✅ Get strategies passed!")
        return strategies
    else:
        print(f"   ❌ Error: {response.text}")
        return []

def test_get_strategy(strategy_id):
    """Test getting a specific strategy"""
    print(f"\n4. Testing Get Strategy by ID: {strategy_id}...")
    
    response = requests.get(f"{BASE_URL}/strategies/{strategy_id}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        strategy = response.json()
        print(f"   Strategy Name: {strategy['strategy_name']}")
        print(f"   Asset Class: {strategy['asset_class']}")
        print(f"   Instrument: {strategy['instrument']}")
        print("   ✅ Get strategy passed!")
    else:
        print(f"   ❌ Error: {response.text}")

def test_validate_strategy(strategy_id):
    """Test strategy validation"""
    print(f"\n5. Testing Validate Strategy: {strategy_id}...")
    
    response = requests.get(f"{BASE_URL}/strategies/{strategy_id}/validate")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        validation = response.json()
        print(f"   Is Valid: {validation['is_valid']}")
        print(f"   Warnings: {validation['warnings']}")
        print(f"   Errors: {validation['errors']}")
        print("   ✅ Validate strategy passed!")
    else:
        print(f"   ❌ Error: {response.text}")

def test_run_backtest(strategy_id):
    """Test running a backtest"""
    print(f"\n6. Testing Run Backtest for Strategy: {strategy_id}...")
    
    backtest_data = {
        "strategy_id": strategy_id,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 100000,
        "commission_per_trade": 20,
        "slippage_percent": 0.1
    }
    
    response = requests.post(f"{BASE_URL}/backtest/run", json=backtest_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 202:
        result = response.json()
        print(f"   Backtest ID: {result['backtest_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print("   ✅ Run backtest passed!")
        return result['backtest_id']
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_get_backtest_result(backtest_id):
    """Test getting backtest results"""
    print(f"\n7. Testing Get Backtest Result: {backtest_id}...")
    
    import time
    time.sleep(2)  # Wait for backtest to complete
    
    response = requests.get(f"{BASE_URL}/backtest/{backtest_id}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        metrics = result['metrics']
        print(f"\n   📊 Backtest Results:")
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Winning Trades: {metrics['winning_trades']}")
        print(f"   Losing Trades: {metrics['losing_trades']}")
        print(f"   Win Rate: {metrics['win_rate']}%")
        print(f"   Net Profit: ₹{metrics['net_profit']}")
        print(f"   Net Profit %: {metrics['net_profit_percent']}%")
        print(f"   Max Drawdown: ₹{metrics['max_drawdown']} ({metrics['max_drawdown_percent']}%)")
        print(f"   Profit Factor: {metrics['profit_factor']}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']}")
        print("   ✅ Get backtest result passed!")
    else:
        print(f"   ❌ Error: {response.text}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Strategy Builder Backend API Tests")
    print("="*60)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Create strategy
        strategy_id = test_create_strategy()
        
        if strategy_id:
            # Test 3: Get all strategies
            test_get_strategies()
            
            # Test 4: Get specific strategy
            test_get_strategy(strategy_id)
            
            # Test 5: Validate strategy
            test_validate_strategy(strategy_id)
            
            # Test 6: Run backtest
            backtest_id = test_run_backtest(strategy_id)
            
            if backtest_id:
                # Test 7: Get backtest results
                test_get_backtest_result(backtest_id)
        
        print("\n" + "="*60)
        print("  ✅ All tests completed successfully!")
        print("="*60)
        print("\n  The Strategy Builder backend is working correctly! 🎉")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to backend server!")
        print("   Make sure the backend is running:")
        print("   cd backend && python app.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
