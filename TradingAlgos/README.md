# 📈 Trading System - Lightweight# 📈 Trading System - All-in-One# Simple Kite Connect Trading



Live trading system with Kite API integration - clean, simple, and powerful.



## 📁 FilesComplete trading system with Kite API integration, backtesting, and strategy analysis.## 📁 Files (Ultra-Minimal Setup)



- **`trading_system.py`** - 🚀 **Complete trading system** (~450 lines)

- **`config.py`** - 🔧 **API credentials** (keep separate for security!)

- **`requirements.txt`** - 📦 Dependencies## 📁 Files- **`simple_kite.py`** - 🚀 **Main script** - Complete Kite API connection & trading



## 🚀 Quick Start- **`config.py`** - 🔧 API credentials  



```powershell- **`trading_system.py`** - 🚀 **Complete trading system** (all-in-one)- **`requirements.txt`** - 📦 Dependencies

# 1. Install dependencies

pip install -r requirements.txt- **`config.py`** - 🔧 API credentials  



# 2. Update config.py with your API credentials- **`requirements.txt`** - 📦 Dependencies## 🚀 Setup & Run



# 3. Run the system

python trading_system.py

```## 🚀 Quick Start```powershell



## ✨ Features# 1. Install dependencies



### 🔐 Connection & Token Management```powershellpip install -r requirements.txt

- Auto-connect with saved tokens

- Fresh token generation# 1. Install dependencies

- Token expiry handling

pip install -r requirements.txt# 2. Update config.py with your API credentials

### 📊 Live Market Data

- Live quotes (single & multiple)

- Watchlist display

- Instrument search# 2. Update config.py with your API credentials# 3. Run the script



### 💰 Account Managementpython simple_kite.py

- Check balance & margins

- View orders, positions, holdings# 3. Run the system```

- P&L tracking

python trading_system.py

### 📝 Trading Operations

- Place orders (Market/Limit)```## ✅ What it does

- Cancel orders

- Modify orders

- Order confirmation prompts

## ✨ Features- 🔐 Auto-connects to Kite API

### 📋 Interactive Menu

Easy-to-use menu system for all functions- 📊 Fetches live market data



## 🎯 Usage Examples### 🔐 Connection & Token Management- 💰 Shows account balance



```python- Auto-connect with saved tokens- 📋 Gets order history

from trading_system import *

- Fresh token generation- 🏪 Lists available instruments

# Quick connection

connect_to_kite()- Token refresh utilities- 💡 Ready for order placement (uncomment code)



# Get live data

price = get_quote("RELIANCE")

balance = get_balance()### 📊 Live Trading Functions**That's it!** Everything you need in one simple script.

- Get live quotes

# View multiple quotes- Check account balance

quotes = get_multiple_quotes(["RELIANCE", "TCS", "INFY"])- Place orders (with safety)

- View order history

# Show watchlist- Get user profile

show_watchlist(["RELIANCE", "TCS", "INFY", "HDFC"])

### 📈 Backtesting System

# Interactive menu- 5-minute historical data

main_menu()- Moving Average strategies

```- RSI strategies

- Intraday rules (EOD closure, no first/last 30 min)

## 🛡️ Why config.py is separate?- Performance analysis



✅ **Security** - API keys separate from code  ### 📋 Interactive Menu

✅ **Git Safety** - Can `.gitignore` config.py  Run `main_menu()` for easy access to all features

✅ **Easy Updates** - Change credentials without touching code  

✅ **Best Practice** - Standard in production systems## 🎯 Usage Examples



**Clean, lightweight, ready to trade!** 🎉```python

from trading_system import *

# Connect
connect_to_kite()

# Get live data
price = get_quote("RELIANCE")
balance = get_balance()

# Run backtest
run_backtest(symbols=["RELIANCE", "TCS", "INFY"], days=300)

# Or use interactive menu
main_menu()
```

**Everything you need in ONE file!** 🎉
