# 📊 Bank Nifty Options Strategy - Quick Guide

## 🎯 Strategy Overview

**Opening Ba5. **Days to Expiry**: Avoid trading on expiry day (0 DTE = high theta)
6. **Brokerage**: Add transaction costs
7. **Capital Requirements**:
   - **Current lot (15)**: ~₹50,000-100,000 margin per lot
   - **Previous lot (25)**: ~₹80,000-160,000 margin per lot
   - Margin varies with volatility and strike selectionreakout Strategy**
- **Entry**: Buy CE/PE when price breaks opening bar (9:15-9:20 AM) high/low
- **Exit**: Hold till 3:15 PM
- **Instrument**: Bank Nifty options
- **Expiry**: Weekly (Wednesdays) or Monthly (Last Thursday)

## 🚀 How to Run

```powershell
# Make sure you're connected to Kite API first
python trading_system.py  # Connect and generate token if needed

# Then run the backtest
python banknifty_options_strategy.py
```

## � Bank Nifty Lot Size

**Important:** Bank Nifty lot size has changed!

| Period | Lot Size | Capital Required* |
|--------|----------|-------------------|
| **Current (Oct 2024+)** | **15** | ₹50,000 - ₹1,00,000 |
| Previous (Before Oct 2024) | 25 | ₹80,000 - ₹1,60,000 |

*Approximate margin requirement per lot

**The script uses lot size 15 by default** (current lot size).

## �📈 Strike Strategies Tested

| Strategy | Strike Selection | Risk Level | Best For |
|----------|-----------------|------------|----------|
| **ATM** | At The Money | Medium | Balanced approach ⭐⭐⭐⭐⭐ |
| **OTM_100** | 100 points OTM | High | Strong trends ⭐⭐⭐⭐ |
| **OTM_200** | 200 points OTM | Very High | Explosive moves ⭐⭐⭐ |
| **ITM_100** | 100 points ITM | Low | Conservative ⭐⭐⭐ |

## 📊 What the Script Does

1. **Fetches Data**: Gets 100 days of Bank Nifty 5-minute data
2. **Selects Expiry**: Automatically calculates weekly/monthly expiry for each trade date
3. **Detects Breakouts**: Identifies opening bar breakouts each day
4. **Simulates Options**: Calculates option premium changes (simplified model)
5. **Applies Theta Decay**: Adjusts for time decay based on days to expiry
6. **Compares Strategies**: Tests all 4 strike strategies
7. **Shows Results**: Win rate, P&L, expiry dates, strikes used

## 💡 Understanding Results

```
Expiry: WEEKLY | Lot Size: 15

Strategy     Trades   Win%    Total P&L       Avg P&L
ATM          65       58.5%   ₹45,000        ₹692
OTM_100      65       52.3%   ₹38,000        ₹585

LAST 10 TRADES:
✅ 2024-09-25 📈 CE Strike:44500 Exp:25-Sep DTE:0 | Spot: +150 pts | P&L: ₹+4,500
❌ 2024-09-26 📉 PE Strike:44400 Exp:02-Oct DTE:4 | Spot: -80 pts | P&L: ₹-2,100
```

- **Lot Size**: Number of shares per lot (currently 15, previously 25)
- **Win Rate**: % of profitable trades
- **Total P&L**: Cumulative profit/loss (for specified lot size)
- **Avg P&L**: Average profit per trade
- **DTE**: Days To Expiry (affects theta decay)
- **Strike**: Actual strike selected (ATM/OTM/ITM)
- **Exp**: Expiry date for that trade

**Note:** All P&L shown is for the lot size displayed at the top!

## ⚠️ Important Notes

### This is a SIMULATION
- Uses simplified option pricing (Delta-based)
- Real options have: Theta decay, IV changes, Gamma, Vega
- Actual results will vary based on market conditions

### Real Trading Considerations
1. **Slippage**: Entry/exit prices may differ
2. **Liquidity**: Check option chain OI and volume
3. **Expiry Selection**: 
   - **Weekly** (Wednesday) - Better for this strategy (less theta)
   - **Monthly** (Last Thursday) - More time value but slower movement
4. **Days to Expiry**: Avoid trading on expiry day (0 DTE = high theta)
5. **Brokerage**: Add transaction costs
6. **Capital**: 1 lot requires ~₹50,000-100,000 margin

## 🔧 Customization

Edit the script to customize:

```python
# Change number of days
run_banknifty_backtest(days=200)  # Test 200 days

# Use monthly expiry instead of weekly
run_banknifty_backtest(days=100, expiry_type="MONTHLY")

# Test specific strategies
run_banknifty_backtest(
    days=100, 
    strike_strategies=["ATM", "OTM_100"],
    expiry_type="WEEKLY"
)

# Change lot size (for multiple lots or historical comparison)
run_banknifty_backtest(days=100, lot_size=15)  # Current lot size
run_banknifty_backtest(days=100, lot_size=25)  # Previous lot size
run_banknifty_backtest(days=100, lot_size=30)  # 2 lots current size
```

### 📊 Lot Size History

```python
# For historical accuracy in backtesting:
# Use lot_size=25 for data before October 2024
# Use lot_size=15 for data from October 2024 onwards
```

## 📈 Next Steps

1. **Add Filters**: 
   - Gap up/down analysis
   - Trend filter (moving averages)
   - Volatility filter (VIX)

2. **Risk Management**:
   - Stop loss at 30-40% of premium
   - Trail profits after 50% gain
   - Max 2-3 trades per week

3. **Position Sizing**:
   - Risk 2-3% of capital per trade
   - Scale in/out based on conviction

## 🎓 Learning Resources

- Opening bar breakout works best in trending markets
- Check market trend before trading (Nifty 50 direction)
- Avoid trading on consolidation days
- Best results typically in first 30-60 minutes after breakout

---

**Ready to backtest? Run the script and analyze results!** 🚀
