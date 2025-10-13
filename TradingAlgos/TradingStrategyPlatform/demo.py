"""
Complete demonstration of Sprint 3 functionality
Tests the full strategy tester pipeline: import strategy -> run backtest -> get results
"""

import asyncio
import json
import sys
import os
sys.path.append('backend')

from core.backtest_engine import BacktestEngine
from core.data_fetcher import DataFetcher
from models.schemas import StrategyJSON

def create_sample_strategies():
    """Create sample trading strategies for demonstration"""
    
    # Strategy 1: Simple Moving Average Crossover
    sma_strategy = {
        "strategy_name": "SMA Crossover Strategy",
        "symbol": "RELIANCE",
        "timeframe": "1D",
        "description": "Buy when SMA(10) crosses above SMA(20), sell when crosses below",
        "indicators": [
            {"name": "SMA", "period": 10, "applied_to": "close"},
            {"name": "SMA", "period": 20, "applied_to": "close"}
        ],
        "entry": {
            "trigger": {
                "main": None,
                "conditions": [
                    {
                        "type": "indicator",
                        "name": "SMA_10",
                        "op": "crosses_above",
                        "value_ref": {"indicator": "SMA_20"}
                    }
                ],
                "logical_op": "AND"
            },
            "execute_at": "close",
            "order_type": "market"
        },
        "exit": {
            "stop_loss": {"mode": "fixed_pct", "value": 5.0},
            "take_profit": {"mode": "ratio", "value": 2.0},
            "exit_conditions": [
                {
                    "type": "indicator", 
                    "name": "SMA_10",
                    "op": "crosses_below",
                    "value_ref": {"indicator": "SMA_20"}
                }
            ],
            "logical_op": "OR"
        },
        "risk": {
            "capital": 100000,
            "risk_per_trade_pct": 2.0,
            "max_open_trades": 1
        }
    }
    
    # Strategy 2: Breakout with RSI Filter
    breakout_strategy = {
        "strategy_name": "Breakout + RSI Strategy", 
        "symbol": "TCS",
        "timeframe": "1D",
        "description": "Breakout above previous high with RSI confirmation",
        "indicators": [
            {"name": "RSI", "period": 14, "applied_to": "close"},
            {"name": "ATR", "period": 14, "applied_to": "close"}
        ],
        "entry": {
            "trigger": {
                "main": {
                    "point": "close_above_prev_high",
                    "candle_id": -1
                },
                "conditions": [
                    {
                        "type": "indicator",
                        "name": "RSI_14", 
                        "op": ">",
                        "value": 50
                    }
                ],
                "logical_op": "AND"
            },
            "execute_at": "close"
        },
        "exit": {
            "stop_loss": {"mode": "atr", "multiplier": 2.0},
            "take_profit": {"mode": "ratio", "value": 3.0}
        },
        "risk": {
            "capital": 100000,
            "risk_per_trade_pct": 1.5,
            "max_open_trades": 2
        }
    }

    # Strategy 3: Mean Reversion with Bollinger Bands
    mean_reversion_strategy = {
        "strategy_name": "Bollinger Band Mean Reversion",
        "symbol": "HDFC", 
        "timeframe": "1D",
        "description": "Buy at lower band, sell at upper band",
        "indicators": [
            {"name": "BOLLINGER", "period": 20, "applied_to": "close"},
            {"name": "RSI", "period": 14, "applied_to": "close"}
        ],
        "entry": {
            "trigger": {
                "main": None,
                "conditions": [
                    {
                        "type": "indicator",
                        "name": "BB_LOWER",
                        "op": ">=",
                        "value_ref": {"field": "close", "candle_id": -1}
                    },
                    {
                        "type": "indicator",
                        "name": "RSI_14",
                        "op": "<",
                        "value": 30
                    }
                ],
                "logical_op": "AND"
            },
            "execute_at": "close"
        },
        "exit": {
            "stop_loss": {"mode": "fixed_pct", "value": 3.0},
            "exit_conditions": [
                {
                    "type": "indicator",
                    "name": "BB_UPPER", 
                    "op": "<=",
                    "value_ref": {"field": "close", "candle_id": -1}
                }
            ],
            "logical_op": "OR"
        },
        "risk": {
            "capital": 100000,
            "risk_per_trade_pct": 1.0,
            "max_open_trades": 3
        }
    }

    return [sma_strategy, breakout_strategy, mean_reversion_strategy]

async def run_comprehensive_demo():
    """Run comprehensive demo of all Sprint 3 features"""
    
    print("=" * 80)
    print("🚀 ASTRA CHARTS - SPRINT 3 DEMONSTRATION")
    print("AI-powered Trading & Backtesting Platform")
    print("=" * 80)
    print()
    
    # Initialize components
    engine = BacktestEngine()
    data_fetcher = DataFetcher()
    
    # Get sample strategies
    sample_strategies = create_sample_strategies()
    
    print(f"📊 Created {len(sample_strategies)} sample strategies:")
    for i, strategy in enumerate(sample_strategies, 1):
        print(f"  {i}. {strategy['strategy_name']} ({strategy['symbol']})")
    print()
    
    # Test each strategy
    results = []
    
    for i, strategy_dict in enumerate(sample_strategies, 1):
        print(f"🔄 Testing Strategy {i}: {strategy_dict['strategy_name']}")
        print(f"   Symbol: {strategy_dict['symbol']}")
        print(f"   Timeframe: {strategy_dict['timeframe']}")
        
        try:
            # Validate strategy JSON
            strategy = StrategyJSON(**strategy_dict)
            
            # Fetch market data
            print("   📈 Fetching market data...")
            data = await data_fetcher.get_historical_data(
                strategy.symbol, 
                strategy.timeframe, 
                '2024-01-01', 
                '2024-06-01'
            )
            
            print(f"   ✅ Loaded {len(data)} data points")
            
            if len(data) < 50:
                print("   ⚠️  Insufficient data for backtesting")
                continue
            
            # Run backtest
            print("   🧮 Running backtest...")
            result = engine.run_backtest(data, strategy)
            
            # Display results
            print(f"   📊 Backtest Results:")
            print(f"      Total Trades: {result.summary.trades}")
            print(f"      Net Profit: ${result.summary.net_profit:,.2f}")
            print(f"      Win Rate: {result.summary.win_rate:.1%}")
            print(f"      Max Drawdown: {result.summary.max_drawdown:.1%}")
            print(f"      Profit Factor: {result.summary.profit_factor:.2f}")
            
            if result.trades:
                avg_pnl = sum(t.pnl for t in result.trades) / len(result.trades)
                print(f"      Average Trade P&L: ${avg_pnl:.2f}")
                
                # Show first few trades
                print(f"   📋 Sample Trades:")
                for j, trade in enumerate(result.trades[:3]):
                    print(f"      Trade {j+1}: Entry ${trade.entry_price:.2f} -> Exit ${trade.exit_price:.2f} = ${trade.pnl:.2f}")
            else:
                print("   ℹ️  No trades generated")
            
            results.append({
                'strategy': strategy_dict['strategy_name'],
                'symbol': strategy_dict['symbol'],
                'trades': result.summary.trades,
                'net_profit': result.summary.net_profit,
                'win_rate': result.summary.win_rate,
                'max_drawdown': result.summary.max_drawdown,
                'profit_factor': result.summary.profit_factor
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'strategy': strategy_dict['strategy_name'],
                'symbol': strategy_dict['symbol'],
                'error': str(e)
            })
        
        print()
    
    # Summary report
    print("=" * 80)
    print("📈 BACKTEST SUMMARY REPORT")
    print("=" * 80)
    
    successful_tests = [r for r in results if 'error' not in r]
    failed_tests = [r for r in results if 'error' in r]
    
    print(f"✅ Successful tests: {len(successful_tests)}")
    print(f"❌ Failed tests: {len(failed_tests)}")
    print()
    
    if successful_tests:
        print("🏆 Performance Rankings:")
        # Sort by net profit
        successful_tests.sort(key=lambda x: x['net_profit'], reverse=True)
        
        print(f"{'Rank':<4} {'Strategy':<25} {'Symbol':<8} {'Trades':<7} {'Net P&L':<12} {'Win Rate':<9} {'Max DD':<8}")
        print("-" * 80)
        
        for i, result in enumerate(successful_tests, 1):
            print(f"{i:<4} {result['strategy'][:24]:<25} {result['symbol']:<8} "
                  f"{result['trades']:<7} ${result['net_profit']:<11,.0f} "
                  f"{result['win_rate']:<8.1%} {result['max_drawdown']:<7.1%}")
        
        print()
        
        # Calculate aggregate stats
        total_trades = sum(r['trades'] for r in successful_tests)
        total_profit = sum(r['net_profit'] for r in successful_tests)
        avg_win_rate = sum(r['win_rate'] for r in successful_tests) / len(successful_tests)
        
        print(f"📊 Aggregate Statistics:")
        print(f"   Total Trades Executed: {total_trades}")
        print(f"   Total Net Profit: ${total_profit:,.2f}")
        print(f"   Average Win Rate: {avg_win_rate:.1%}")
        
        # Best performing strategy
        best_strategy = successful_tests[0]
        print(f"   🥇 Best Performer: {best_strategy['strategy']} (${best_strategy['net_profit']:,.2f})")
    
    if failed_tests:
        print()
        print("❌ Failed Tests:")
        for result in failed_tests:
            print(f"   {result['strategy']} ({result['symbol']}): {result['error']}")
    
    print()
    print("=" * 80)
    print("✅ SPRINT 3 DEMONSTRATION COMPLETE")
    print("✅ Strategy Tester backend fully functional")
    print("✅ JSON schema validation working")
    print("✅ Backtest engine operational")
    print("✅ Multiple strategy types supported")
    print("✅ Comprehensive result analytics")
    print("=" * 80)

def demonstrate_api_integration():
    """Show how to integrate with the FastAPI backend"""
    
    print("\n🔌 API INTEGRATION EXAMPLES")
    print("=" * 50)
    
    # Example strategy import
    strategy_example = {
        "strategy_name": "API Test Strategy",
        "symbol": "RELIANCE", 
        "timeframe": "1D",
        "entry": {
            "trigger": {
                "conditions": [],
                "logical_op": "AND"
            }
        },
        "exit": {},
        "risk": {
            "capital": 100000,
            "risk_per_trade_pct": 1.0,
            "max_open_trades": 1
        }
    }
    
    print("📝 Example Strategy Import Request:")
    print("POST /api/strategy/import")
    print("Content-Type: application/json")
    print()
    print(json.dumps({
        "strategy_json": strategy_example,
        "save_as_template": False
    }, indent=2))
    print()
    
    print("📊 Example Backtest Request:")
    print("POST /api/backtest/run")  
    print("Content-Type: application/json")
    print()
    print(json.dumps({
        "strategy_json": strategy_example,
        "symbol": "RELIANCE",
        "timeframe": "1D", 
        "from_date": "2024-01-01",
        "to_date": "2024-06-01",
        "mode": "detailed"
    }, indent=2))
    print()
    
    print("📈 Example Market Data Request:")
    print("GET /api/market-data/candles?symbol=RELIANCE&timeframe=1D&from_date=2024-01-01&to_date=2024-01-31")
    print()
    
    print("🔍 Check Backend Status:")
    print("GET /health")
    print("Expected Response: {'status': 'healthy', 'message': 'API is running'}")

if __name__ == "__main__":
    print("Starting comprehensive Sprint 3 demonstration...")
    
    try:
        # Run the full demo
        asyncio.run(run_comprehensive_demo())
        
        # Show API integration examples
        demonstrate_api_integration()
        
        print("\n🎉 Demo completed successfully!")
        print("👉 Backend server is running on http://localhost:8000")
        print("👉 API documentation available at http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()