"""
Clean Backtesting with Table Results
Professional table-based output for strategy comparison
"""

from simple_kite import connect_to_kite
import pandas as pd
from datetime import datetime, timedelta
import config
import logging

# Disable debug logging
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

def get_stock_data(symbol, days=60, kite_connection=None):
    """Fetch 5-minute historical data for a stock over longer period"""
    
    if kite_connection is None:
        kite = connect_to_kite()
        if not kite:
            return None
    else:
        kite = kite_connection
    
    try:
        instruments = kite.instruments("NSE")
        instrument = next((item for item in instruments if item['tradingsymbol'] == symbol), None)
        
        if not instrument:
            return None
        
        instrument_token = instrument['instrument_token']
        from_date = datetime.now() - timedelta(days=days)
        to_date = datetime.now()
        
        # Fetch 5-minute data for more granular analysis
        historical_data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval="5minute"
        )
        
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter to market hours only (9:15 AM - 3:30 PM)
        df = df[df['date'].dt.time >= pd.Timestamp('09:15:00').time()]
        df = df[df['date'].dt.time <= pd.Timestamp('15:30:00').time()]
        
        return df
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def simple_moving_average_strategy(df, short_period=5, long_period=20):
    """Simple Moving Average Strategy"""
    
    if df is None or len(df) < long_period:
        return None
    
    df['MA_Short'] = df['close'].rolling(window=short_period).mean()
    df['MA_Long'] = df['close'].rolling(window=long_period).mean()
    df['Signal'] = 0
    df['Position'] = 0
    
    buy_condition = (df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1))
    df.loc[buy_condition, 'Signal'] = 1
    
    sell_condition = (df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1))
    df.loc[sell_condition, 'Signal'] = -1
    
    position = 0
    for i in range(len(df)):
        if df.iloc[i]['Signal'] == 1:
            position = 1
        elif df.iloc[i]['Signal'] == -1:
            position = 0
        df.iloc[i, df.columns.get_loc('Position')] = position
    
    return df

def simple_rsi_strategy(df, period=14, oversold=30, overbought=70):
    """Simple RSI Strategy"""
    
    if df is None or len(df) < period + 1:
        return None
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Signal'] = 0
    df['Position'] = 0
    
    buy_condition = (df['RSI'] < oversold) & (df['RSI'].shift(1) >= oversold)
    df.loc[buy_condition, 'Signal'] = 1
    
    sell_condition = (df['RSI'] > overbought) & (df['RSI'].shift(1) <= overbought)
    df.loc[sell_condition, 'Signal'] = -1
    
    position = 0
    for i in range(len(df)):
        if df.iloc[i]['Signal'] == 1:
            position = 1
        elif df.iloc[i]['Signal'] == -1:
            position = 0
        df.iloc[i, df.columns.get_loc('Position')] = position
    
    return df

def calculate_returns(df, initial_capital=100000):
    """Calculate returns from the strategy"""
    
    if df is None:
        return None
    
    capital = initial_capital
    shares = 0
    trades = []
    
    for i, row in df.iterrows():
        if row['Signal'] == 1 and shares == 0:  # Buy
            shares = capital // row['close']
            capital = capital - (shares * row['close'])
            trades.append({
                'date': row['date'],
                'action': 'BUY',
                'price': row['close'],
                'shares': shares,
                'capital': capital
            })
            
        elif row['Signal'] == -1 and shares > 0:  # Sell
            capital = capital + (shares * row['close'])
            trades.append({
                'date': row['date'],
                'action': 'SELL',
                'price': row['close'],
                'shares': shares,
                'capital': capital
            })
            shares = 0
    
    # If still holding shares at the end, sell them
    if shares > 0:
        final_price = df.iloc[-1]['close']
        capital = capital + (shares * final_price)
        trades.append({
            'date': df.iloc[-1]['date'],
            'action': 'SELL',
            'price': final_price,
            'shares': shares,
            'capital': capital
        })
    
    total_return = ((capital - initial_capital) / initial_capital) * 100
    
    return {
        'initial_capital': initial_capital,
        'final_capital': capital,
        'total_return': total_return,
        'trades': trades
    }

def run_clean_backtest():
    """Run backtest with 5-minute data over longer period"""
    
    print("=" * 80)
    print("                         STRATEGY BACKTEST RESULTS")
    print("                        (5-Minute Charts - 60 Days)")
    print("=" * 80)
    
    # Connect once
    print("Connecting to Kite API...", end=" ")
    kite = connect_to_kite()
    if not kite:
        print("FAILED")
        return
    print("SUCCESS")

    # More symbols for better analysis (reduced for faster processing)
    symbols = ["RELIANCE", "TCS", "INFY"]
    
    # 5-minute optimized strategies (key ones only)
    strategies = [
        # Moving Average - shorter periods for 5-min charts
        ("MA_5_15", simple_moving_average_strategy, {"short_period": 5, "long_period": 15}),
        ("MA_9_21", simple_moving_average_strategy, {"short_period": 9, "long_period": 21}),
        
        # RSI - different thresholds for intraday
        ("RSI_30_70", simple_rsi_strategy, {"period": 14, "oversold": 30, "overbought": 70}),
        ("RSI_35_65", simple_rsi_strategy, {"period": 14, "oversold": 35, "overbought": 65}),
        ("RSI_Fast", simple_rsi_strategy, {"period": 7, "oversold": 20, "overbought": 80}),
    ]
    
    results = []
    
    print(f"\nFetching 5-minute data and running strategies...")
    print("Note: Processing larger dataset - this may take a moment...")
    
    for symbol in symbols:
        print(f"Processing {symbol}...", end=" ")
        
        # Get 60 days of 5-minute data
        df = get_stock_data(symbol, days=60, kite_connection=kite)
        if df is None or len(df) < 50:
            print("FAILED")
            continue
        
        print(f"Got {len(df)} candles")
        
        for strategy_name, strategy_func, params in strategies:
            try:
                df_copy = df.copy()
                df_with_signals = strategy_func(df_copy, **params)
                
                if df_with_signals is not None:
                    result = calculate_returns(df_with_signals)
                    if result is not None:
                        results.append({
                            'Symbol': symbol,
                            'Strategy': strategy_name,
                            'Return %': round(result['total_return'], 2),
                            'Final Capital': int(result['final_capital']),
                            'Trades': len(result['trades']),
                            'Profit/Loss': int(result['final_capital'] - result['initial_capital']),
                            'Data Points': len(df)
                        })
            except Exception as e:
                continue
        
        print("DONE")
    
    # Create results table
    if results:
        df_results = pd.DataFrame(results)
        
        print("\n" + "=" * 80)
        print("                         ASSET-WISE BACKTEST RESULTS")
        print("=" * 80)
        
        # Asset-wise detailed results
        for symbol in symbols:
            symbol_results = df_results[df_results['Symbol'] == symbol]
            if not symbol_results.empty:
                print(f"\n📈 {symbol} PERFORMANCE:")
                print("-" * 60)
                
                # Show detailed results for this asset
                asset_table = symbol_results[['Strategy', 'Return %', 'Final Capital', 'Trades', 'Profit/Loss', 'Data Points']].copy()
                asset_table = asset_table.sort_values('Return %', ascending=False)
                print(asset_table.to_string(index=False))
                
                # Asset summary stats
                best_strategy = asset_table.iloc[0]
                worst_strategy = asset_table.iloc[-1]
                profitable_strategies = len(asset_table[asset_table['Return %'] > 0])
                total_strategies = len(asset_table)
                
                print(f"\n  🏆 Best Strategy:  {best_strategy['Strategy']} ({best_strategy['Return %']:+.2f}%)")
                print(f"  📉 Worst Strategy: {worst_strategy['Strategy']} ({worst_strategy['Return %']:+.2f}%)")
                print(f"  ✅ Profitable:    {profitable_strategies}/{total_strategies} strategies")
                print(f"  📊 Avg Return:    {asset_table['Return %'].mean():+.2f}%")
                print(f"  📈 Max Profit:    ₹{asset_table['Profit/Loss'].max():,}")
                print(f"  📉 Max Loss:      ₹{asset_table['Profit/Loss'].min():,}")
        
        print("\n" + "=" * 80)
        print("                         POOLED ANALYSIS - ALL ASSETS")
        print("=" * 80)
        
        # Overall pooled results table
        print("\n📊 COMPLETE RESULTS TABLE:")
        print("-" * 80)
        pooled_table = df_results.sort_values(['Return %', 'Symbol'], ascending=[False, True])
        print(pooled_table.to_string(index=False))
        
        # Pooled strategy performance analysis
        print("\n\n📈 STRATEGY PERFORMANCE ANALYSIS:")
        print("-" * 70)
        strategy_summary = df_results.groupby('Strategy').agg({
            'Return %': ['count', 'mean', 'std', 'max', 'min'],
            'Trades': 'mean',
            'Profit/Loss': ['sum', 'mean']
        }).round(2)
        
        strategy_summary.columns = ['Tests', 'Avg Return %', 'Std Dev %', 'Max Return %', 'Min Return %', 'Avg Trades', 'Total P&L', 'Avg P&L']
        print(strategy_summary)
        
        # Win rate and success metrics
        print("\n\n🎯 SUCCESS METRICS BY STRATEGY:")
        print("-" * 50)
        print(f"{'Strategy':<12} {'Win Rate':<10} {'Avg Return':<12} {'Total P&L':<12}")
        print("-" * 50)
        
        for strategy in df_results['Strategy'].unique():
            strategy_data = df_results[df_results['Strategy'] == strategy]
            wins = len(strategy_data[strategy_data['Return %'] > 0])
            total = len(strategy_data)
            win_rate = (wins / total) * 100 if total > 0 else 0
            avg_return = strategy_data['Return %'].mean()
            total_pnl = strategy_data['Profit/Loss'].sum()
            
            print(f"{strategy:<12} {win_rate:5.1f}%     {avg_return:+6.2f}%      ₹{total_pnl:+,}")
        
        # Best combinations
        print("\n\n🏆 TOP 10 BEST ASSET-STRATEGY COMBINATIONS:")
        print("-" * 65)
        top_10 = df_results.nlargest(10, 'Return %')
        print(f"{'Rank':<5} {'Asset':<10} {'Strategy':<12} {'Return %':<10} {'Profit/Loss':<12}")
        print("-" * 65)
        
        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            print(f"{i:<5} {row['Symbol']:<10} {row['Strategy']:<12} {row['Return %']:+6.2f}%   ₹{row['Profit/Loss']:+,}")
        
        # Risk-adjusted metrics
        print("\n\n⚖️  RISK-ADJUSTED PERFORMANCE:")
        print("-" * 55)
        print(f"{'Strategy':<12} {'Sharpe Ratio*':<15} {'Max Drawdown':<15}")
        print("-" * 55)
        
        for strategy in df_results['Strategy'].unique():
            strategy_data = df_results[df_results['Strategy'] == strategy]
            returns = strategy_data['Return %']
            
            # Simple Sharpe ratio approximation
            if returns.std() > 0:
                sharpe = returns.mean() / returns.std()
            else:
                sharpe = 0
            
            # Max drawdown (simplified as worst single loss)
            max_loss = returns.min()
            
            print(f"{strategy:<12} {sharpe:+8.2f}        {max_loss:+6.2f}%")
        
        print("\n* Simplified Sharpe Ratio = Mean Return / Std Dev of Returns")
        
        # Portfolio allocation suggestion
        print("\n\n💼 SUGGESTED PORTFOLIO ALLOCATION:")
        print("-" * 45)
        
        # Find best strategy for each asset
        best_combos = []
        for symbol in symbols:
            symbol_results = df_results[df_results['Symbol'] == symbol]
            if not symbol_results.empty:
                best = symbol_results.loc[symbol_results['Return %'].idxmax()]
                best_combos.append({
                    'Asset': symbol,
                    'Strategy': best['Strategy'],
                    'Expected Return': best['Return %']
                })
        
        if best_combos:
            portfolio_df = pd.DataFrame(best_combos)
            print(portfolio_df.to_string(index=False))
            
            portfolio_return = portfolio_df['Expected Return'].mean()
            print(f"\n📊 Portfolio Expected Return: {portfolio_return:+.2f}%")
        
        print("\n" + "=" * 80)
        print("DETAILED BACKTEST ANALYSIS COMPLETED")
        print("=" * 80)
    
    else:
        print("No results generated. Check your data connection.")

if __name__ == "__main__":
    run_clean_backtest()