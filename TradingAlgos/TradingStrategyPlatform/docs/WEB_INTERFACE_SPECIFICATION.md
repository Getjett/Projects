# Universal Trading Strategy Platform - Web Interface Specification

## 📋 Table of Contents
1. [Overview](#overview)
2. [Instrument Selection](#instrument-selection)
3. [Strategy Builder - Input Parameters](#strategy-builder---input-parameters)
4. [Backtesting Configuration](#backtesting-configuration)
5. [Pattern Creator Module](#pattern-creator-module)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [UI/UX Design Guidelines](#uiux-design-guidelines)

---

## 🎯 Overview

This document outlines the complete specification for building a **universal web-based trading strategy platform** that supports multiple asset classes:

### **Supported Instruments:**
- 📊 **Index Options** (Bank Nifty, Nifty, Fin Nifty)
- 📈 **Equity/Stocks** (NSE, BSE)
- 🌾 **Commodities** (MCX - Gold, Silver, Crude Oil, etc.)
- 💱 **Currency** (USD/INR, EUR/INR, etc.)
- 📉 **Futures** (Index Futures, Stock Futures)

### **Platform Capabilities:**
1. **Create custom strategies** for any instrument using various parameters
2. **Backtest strategies** on historical data for selected date ranges
3. **Build candlestick patterns** for entry/exit signals
4. **Visualize results** with detailed analytics and charts
5. **Multi-instrument portfolio** management
6. **Cross-asset strategy comparison**

---

## 🎯 Instrument Selection

### **Section 0: Instrument & Market Selection** (NEW)

#### 0.1 Asset Class Selection
```
Field Type: Radio Buttons / Tab Navigation
Options:
  ○ Index Options (Nifty, Bank Nifty, Fin Nifty)
  ○ Equity/Stocks (NSE, BSE)
  ○ Commodities (MCX)
  ○ Currency (CDS)
  ○ Futures (Index & Stock Futures)
```

#### 0.2 Instrument Selection (Dynamic based on Asset Class)

**For Index Options:**
```
Field Type: Dropdown
Options:
  - NIFTY (Nifty 50)
  - BANKNIFTY (Bank Nifty) [Default from existing strategy]
  - FINNIFTY (Fin Nifty)
  - MIDCPNIFTY (Midcap Nifty)
  
Option Type (Only for Options):
  - Call & Put (Both) [Default]
  - Call Only
  - Put Only
```

**For Equity/Stocks:**
```
Field Type: Searchable Dropdown with Auto-complete
Features:
  - Search by stock name or symbol
  - Filter by sector (Banking, IT, Pharma, Auto, etc.)
  - Filter by index membership (Nifty 50, Nifty 500, etc.)
  - Show current price and volume
  
Examples:
  - RELIANCE (Reliance Industries)
  - TCS (Tata Consultancy Services)
  - INFY (Infosys)
  - HDFCBANK (HDFC Bank)
  - Custom Watchlist
  
Multi-select: Checkbox to test strategy across multiple stocks
```

**For Commodities (MCX):**
```
Field Type: Dropdown with Categories
Categories:
  
  🥇 Bullion:
    - GOLD (Gold)
    - GOLDM (Gold Mini)
    - SILVER (Silver)
    - SILVERM (Silver Mini)
    
  🛢️ Energy:
    - CRUDEOIL (Crude Oil)
    - NATURALGAS (Natural Gas)
    
  🌾 Agriculture:
    - CARDAMOM
    - COTTON
    - MENTHAOIL
    
  🏭 Base Metals:
    - COPPER
    - ZINC
    - NICKEL
    - LEAD
    - ALUMINIUM
```

**For Currency:**
```
Field Type: Dropdown
Options:
  - USDINR (USD/INR)
  - EURINR (EUR/INR)
  - GBPINR (GBP/INR)
  - JPYINR (JPY/INR)
```

**For Futures:**
```
Field Type: Dropdown with Sub-categories
Options:
  Index Futures:
    - NIFTY FUT
    - BANKNIFTY FUT
    - FINNIFTY FUT
    
  Stock Futures:
    - (Same searchable list as Equity)
```

#### 0.3 Exchange Selection
```
Field Type: Dropdown (Auto-selected based on instrument)
Options:
  - NSE (National Stock Exchange) [Default for Equity/Options]
  - BSE (Bombay Stock Exchange)
  - NFO (NSE Futures & Options)
  - MCX (Multi Commodity Exchange)
  - CDS (Currency Derivatives Segment)
```

#### 0.4 Contract Specifications (Dynamic Info Display)
```
Display (Read-only, fetched from exchange):
  For Options:
    - Lot Size: 15 (Bank Nifty), 50 (Nifty), 40 (Fin Nifty)
    - Tick Size: 0.05
    - Contract Value: ₹X,XX,XXX
    - Expiry Day: Wednesday (Weekly), Last Thursday (Monthly)
    
  For Equity:
    - Lot Size: 1 (Cash Market)
    - Tick Size: 0.05
    - Circuit Limits: ±10%, ±20%
    
  For Commodities:
    - Lot Size: Varies (e.g., Gold: 100g, Silver: 30kg)
    - Tick Size: Varies by commodity
    - Contract Months: Available expiries
    
  For Futures:
    - Lot Size: Varies by underlying
    - Tick Size: 0.05
    - Expiry: Last Thursday of month
```

#### 0.5 Product Type (For Options & Futures)
```
Field Type: Dropdown
Options:
  - MIS (Margin Intraday Square-off) [Default for Intraday]
  - NRML (Normal - Carry Forward)
  - CNC (Cash & Carry - For Equity delivery)
  - BO (Bracket Order)
  - CO (Cover Order)
```

---

## 🛠 Strategy Builder - Input Parameters

### **Section 1: Basic Strategy Configuration**

#### 1.1 Strategy Name & Description
```
Field Type: Text Input
- Strategy Name (Required, Max 50 chars)
- Description (Optional, Max 200 chars)
- Tags (Multi-select: Scalping, Swing, Hedging, etc.)
```

#### 1.2 Trading Type (Instrument-Specific)
```
Field Type: Radio Button / Dropdown

For Options:
  ○ Intraday (9:15 AM - 3:15 PM) [Default]
  ○ Positional (Hold till expiry)
  ○ Swing (2-5 days before expiry)

For Equity:
  ○ Intraday (9:15 AM - 3:15 PM)
  ○ Short Term (1-5 days)
  ○ Swing (1-4 weeks)
  ○ Positional (1-6 months)
  ○ Long Term (6+ months)

For Commodities:
  ○ Intraday (9:00 AM - 11:30 PM) [Extended hours]
  ○ Short Term (1-5 days)
  ○ Swing (1-4 weeks)
  ○ Positional (Till contract expiry)

For Futures:
  ○ Intraday (9:15 AM - 3:30 PM)
  ○ Positional (Hold till expiry)
  ○ Rollover Strategy (Auto-roll to next month)
```

---

### **Section 2: Entry Logic Configuration**

#### 2.1 Signal Bar Selection (Market Hours Aware)
```
Field Type: Dropdown with Time Display

Options for EQUITY/OPTIONS (9:15 AM - 3:30 PM):
  - First Bar (9:15 - 9:20 AM)
  - Second Bar (9:20 - 9:25 AM) [Default for Options]
  - Third Bar (9:25 - 9:30 AM)
  - Opening Range (9:15 - 9:45 AM)
  - Custom Time Range (Time Picker)

Options for COMMODITIES (9:00 AM - 11:30 PM):
  - Opening Bar (9:00 - 9:05 AM)
  - Morning Session (9:00 AM - 5:00 PM)
  - Evening Session (5:00 PM - 11:30 PM)
  - Custom Time Range (Time Picker)
  
Time Frame: Dropdown
  - 1 Minute
  - 3 Minute
  - 5 Minute [Default]
  - 15 Minute
  - 30 Minute
  - 1 Hour
  - 1 Day (For Positional)
  - 1 Week (For Long Term)
```

#### 2.2 Breakout Strategy Type
```
Field Type: Dropdown
Options:
  - Opening Range Breakout (ORB)
  - Second Bar Breakout [Current Strategy]
  - First Hour Breakout
  - Previous Day High/Low Breakout
  - Custom Pattern Breakout (Link to Pattern Creator)
```

#### 2.3 Breakout Direction
```
Field Type: Radio Buttons
Options:
  ○ Bullish Only (Buy CE on upside breakout)
  ○ Bearish Only (Buy PE on downside breakout)
  ○ Both Directions [Default]
```

#### 2.4 Entry Confirmation
```
Field Type: Checkboxes (Multiple Selection)
Options:
  ☐ Require Volume Confirmation (Volume > Avg Volume by X%)
  ☐ Require Candle Close Beyond Level (vs. just touch)
  ☐ Wait for Retest of Breakout Level
  ☐ Additional Filter: RSI/MACD (Advanced)
  
Volume Threshold: Slider (100% - 300%, Default: 150%)
```

---

### **Section 3: Strike Selection & Option Parameters** (OPTIONS ONLY)
### **Section 3: Price & Quantity Selection** (EQUITY/COMMODITY/FUTURES)

#### 3.1 For OPTIONS - Expiry Selection
```
Field Type: Dropdown

For Index Options (Nifty, BankNifty, FinNifty):
  - Current Weekly Expiry (Wednesday)
  - Next Weekly Expiry
  - Current Monthly Expiry (Last Thursday)
  - Custom Days to Expiry (Number Input: 0-30 days)
  
For Stock Options:
  - Current Month Expiry (Last Thursday)
  - Next Month Expiry
  - Far Month Expiry
  
Days to Expiry Filter: Slider (0-90 days)
  - Min Days: 0 [Default]
  - Max Days: 7 [Default for Intraday]
  - Max Days: 30 [Default for Positional]
```

#### 3.1 For EQUITY/COMMODITY/FUTURES - Entry Price
```
Field Type: Radio Buttons + Number Input

Entry Price Type:
  ○ Market Price (At Signal) [Default]
  ○ Limit Order (Specify Price)
  ○ Stop Limit Order
  ○ Breakout Level (Signal Bar High/Low)
  
Limit Price Offset: Number Input (-5% to +5%)
  - For Buy: Entry Price - Offset
  - For Sell: Entry Price + Offset
  
Order Validity:
  - IOC (Immediate or Cancel)
  - DAY (Valid till EOD)
  - GTC (Good Till Cancelled) [Not available for all]
```

#### 3.2 For OPTIONS - Strike Selection Strategy
```
Field Type: Dropdown with Visual Strike Ladder
Options:
  - ATM (At The Money) [Default]
  - ITM 100 (In The Money - 100 points)
  - ITM 200 (In The Money - 200 points)
  - OTM 100 (Out of The Money - 100 points)
  - OTM 200 (Out of The Money - 200 points)
  - OTM 300 (Out of The Money - 300 points)
  - Custom Offset (Number Input: -500 to +500 points)
  
Strike Offset: Number Input with +/- buttons
  Range: -500 to +500 (in steps of 100)
  Default: 0 (ATM)
  
Strike Rounding:
  - Bank Nifty: 100 points
  - Nifty: 50 points
  - Stocks: As per exchange norms
```

#### 3.3 For OPTIONS - Option Type
```
Field Type: Dynamic (Auto-selected based on signal)
For Bullish Breakout:
  → CE (Call Option) - Auto Selected
  
For Bearish Breakout:
  → PE (Put Option) - Auto Selected
  
For Both Directions:
  → Auto-select based on signal
```

#### 3.2 For EQUITY/COMMODITY/FUTURES - Quantity & Position Side
```
Field Type: Number Input + Radio Buttons

Position Side:
  ○ Long (Buy) [Default for Bullish]
  ○ Short (Sell) [Requires Margin]
  ○ Both (Based on Signal)
  
Quantity Calculation:
  ○ Fixed Quantity
    - Equity: Number of Shares (1-10000)
    - Commodity: Number of Lots (1-100)
    - Futures: Number of Lots (1-100)
    
  ○ Fixed Capital Allocation
    - Capital Per Trade: ₹10,000 - ₹10,00,000
    - Auto-calculate quantity based on price
    
  ○ Percentage of Portfolio
    - Allocate X% of total capital (1-100%)
    
Leverage (For Margin Trading):
  - Slider: 1x to 5x [Default: 1x]
  - Available only for F&O segment
```

#### 3.4 For OPTIONS - Premium Range Filter (Optional)
```
Field Type: Range Slider
- Min Entry Premium: 50 [Default: 0]
- Max Entry Premium: 500 [Default: 1000]
  
Purpose: Filter out trades where option premium is too low/high
```

#### 3.4 For EQUITY/COMMODITY - Price Range Filter (Optional)
```
Field Type: Range Slider

For Equity:
  - Min Stock Price: ₹10 [Default: ₹0]
  - Max Stock Price: ₹10,000 [Default: ₹50,000]
  
For Commodity:
  - Min Price: As per commodity
  - Max Price: As per commodity
  
Purpose: Filter out trades based on instrument price range
Examples:
  - Avoid penny stocks (< ₹10)
  - Focus on high-value stocks only (> ₹500)
```

---

### **Section 4: Risk Management Parameters**

#### 4.1 Stop Loss Configuration
```
Field Type: Radio Buttons + Number Input
Stop Loss Type:
  ○ Fixed Points (Number Input: 10-500 points)
  ○ Fixed Percentage (Number Input: 1-50%)
  ○ Based on Signal Bar Range (Multiplier: 0.5x - 3x)
  ○ Trailing Stop Loss (Points/Percentage)
  ○ No Stop Loss
  
Default: Based on Signal Bar Low/High
  - For CE: Stop at Second Bar Low
  - For PE: Stop at Second Bar High
  
Stop Loss Buffer: Number Input (0-50 points)
  Add buffer beyond SL level for safety
```

#### 4.2 Target/Take Profit
```
Field Type: Radio Buttons + Number Input
Target Type:
  ○ Fixed Points (Number Input: 10-1000 points)
  ○ Fixed Percentage (Number Input: 5-200%)
  ○ Risk-Reward Ratio (Dropdown: 1:1, 1:2, 1:3, 1:4, 1:5)
  ○ Based on Signal Bar Range (Multiplier: 1x - 5x)
  ○ No Target (Hold till Exit Time)
  
Default: 3x Signal Bar Range
  Target = Entry ± (Signal Bar Range × 3)
```

#### 4.3 Position Size (Universal)
```
Field Type: Number Input + Dropdown

For OPTIONS:
  Lot Size: Number Input (1-50 lots)
    Default: 15 (Bank Nifty), 50 (Nifty), 40 (Fin Nifty)
  
For EQUITY:
  Quantity: Number Input (1-10000 shares)
    Default: Based on capital allocation
  
For COMMODITY:
  Lot Size: Number Input (1-100 lots)
    Default: 1 lot (varies by commodity)
    
For FUTURES:
  Lot Size: Number Input (1-100 lots)
    Default: Based on underlying (Nifty: 50, BankNifty: 15)

Max Capital per Trade: Number Input (₹10,000 - ₹50,00,000)
  Default: ₹50,000 (Options), ₹1,00,000 (Equity/Commodity)
  
Position Sizing Method:
  - Fixed Quantity/Lot Size [Default]
  - Fixed Risk Amount (Risk X rupees per trade)
  - Percentage of Capital (Risk X% of total capital)
  - Kelly Criterion (Advanced)
  - Optimal F (Advanced)
  
Total Capital: Number Input (₹1,00,000 - ₹1,00,00,000)
  Default: ₹5,00,000
  
Margin Requirements (Display Only):
  - Auto-calculated based on instrument and broker
  - Show Required Margin vs Available Capital
```

#### 4.4 Exit Time (For Intraday - Instrument Specific)
```
Field Type: Time Picker

For EQUITY/OPTIONS (NSE/BSE):
  Default Exit Time: 3:15 PM
  Range: 10:00 AM - 3:30 PM
  Market Close: 3:30 PM
  
For COMMODITIES (MCX):
  Default Exit Time: 11:00 PM
  Range: 10:00 AM - 11:30 PM
  Market Close: 11:30 PM (or 5:00 PM for some commodities)
  
For CURRENCY (CDS):
  Default Exit Time: 4:30 PM
  Range: 10:00 AM - 5:00 PM
  Market Close: 5:00 PM

Options:
  - Fixed Time Exit [Default]
  - Square off if Target/SL not hit
  - Trail till EOD (Keep trailing SL till market close)
  - Custom Exit Logic (Link to Pattern Creator)
  
Auto Square-off Warning:
  ☑ Alert 15 minutes before exit time
  ☑ Auto-exit all positions at specified time
```

---

### **Section 5: Advanced Filters & Conditions**

#### 5.1 Market Condition Filters
```
Field Type: Checkboxes + Number Inputs
☐ Trade only on Trending Days
  - Min Signal Bar Range: 50 points [Default]
  - Max Signal Bar Range: 500 points
  
☐ Skip High Volatility Days
  - VIX > X (Number Input: 15-50, Default: 30)
  
☐ Skip Low Volume Days
  - Skip if Volume < X% of avg (Slider: 50-100%)
  
☐ Day of Week Filter (Checkboxes)
  ☑ Monday
  ☑ Tuesday  
  ☑ Wednesday
  ☑ Thursday
  ☑ Friday
```

#### 5.2 Trend Filter (Optional)
```
Field Type: Dropdown
Options:
  - No Trend Filter [Default]
  - Use 20 EMA (Trade only if price > EMA for CE, < EMA for PE)
  - Use 50 SMA
  - Use Supertrend Indicator
  - Custom Indicator
```

#### 5.3 Time-based Entry Restrictions
```
Field Type: Time Range Picker
Allow Entry Only Between:
  - Start Time: 9:15 AM [Default]
  - End Time: 2:00 PM [Default]
  
No Entry After: Time Picker (2:00 PM - 3:00 PM)
```

---

### **Section 6: Backtesting-Specific Parameters**

#### 6.1 Date Range Selection
```
Field Type: Date Range Picker
From Date: Date Input
  - Default: 100 days ago
  - Min: 5 years ago
  - Max: Yesterday
  
To Date: Date Input
  - Default: Yesterday
  - Max: Yesterday (Cannot backtest future)
  
Quick Select Buttons:
  [Last 7 Days] [Last 1 Month] [Last 3 Months] 
  [Last 6 Months] [Last 1 Year] [Custom Range]
```

#### 6.2 Data Quality Settings
```
Field Type: Checkboxes
☑ Skip Days with Incomplete Data
☑ Skip Days with Gaps > 15 minutes
☐ Skip Days with Circuit Breakers
☐ Skip Expiry Days
☐ Skip Special Trading Sessions (Muhurat, etc.)
```

#### 6.3 Slippage & Transaction Costs
```
Field Type: Number Inputs
Slippage per Trade (Points): 2 [Default]
  Range: 0-20 points
  
Brokerage per Lot: ₹20 [Default]
  Range: ₹0-₹100
  
STT/Exchange Charges (%): 0.05% [Default]
  Range: 0-1%
  
Include GST (18%): Checkbox [Default: Checked]
```

---

## 🧪 Backtesting Configuration

### Backtest Results Display

#### Performance Metrics
```
Display Cards/Widgets:
- Total Trades: 156
- Winning Trades: 89 (57.05%)
- Losing Trades: 67 (42.95%)
- Total Profit/Loss: ₹4,32,500
- Average Profit per Trade: ₹2,772
- Max Drawdown: ₹45,000 (12.3%)
- Sharpe Ratio: 1.85
- Win Rate: 57.05%
- Average Win: ₹7,850
- Average Loss: ₹4,120
- Largest Win: ₹18,500
- Largest Loss: ₹12,300
- Profit Factor: 1.67 (Gross Profit / Gross Loss)
```

#### Equity Curve Chart
```
Chart Type: Line Chart
X-axis: Date
Y-axis: Cumulative P&L (₹)
Features:
  - Zoom & Pan
  - Hover tooltip with trade details
  - Drawdown overlay (optional)
  - Benchmark comparison (Buy & Hold vs Strategy)
```

#### Trade Distribution
```
Charts:
1. Win/Loss Distribution (Pie Chart)
2. P&L per Trade (Bar Chart)
3. Monthly Returns (Heatmap)
4. Trade Duration Analysis (Histogram)
5. Entry Time Distribution (Bar Chart)
6. Exit Reason Distribution (Pie Chart)
   - Target Hit: 45%
   - Stop Loss: 30%
   - EOD Exit: 25%
```

#### Detailed Trade Log Table
```
Columns:
- Date
- Entry Time
- Exit Time
- Signal (CE/PE)
- Strike
- Entry Price (Spot)
- Exit Price (Spot)
- Spot Move (Points & %)
- Entry Premium
- Exit Premium
- P&L (₹)
- P&L (%)
- Exit Reason (Target/SL/EOD)
- Days to Expiry

Filters:
- Filter by Signal Type (CE/PE/All)
- Filter by Exit Reason
- Filter by Profit/Loss
- Date Range Filter
- Export to CSV/Excel
```

---

## 🎨 Pattern Creator Module

### Candlestick Pattern Builder (Future Feature)

#### Pattern Configuration Interface
```
Visual Candle Builder:
- Drag-and-drop candle creation
- Set High, Low, Open, Close for each candle
- Define relationships between candles
```

#### Pattern Parameters
```
1. Number of Candles in Pattern: 1-5 candles
2. Candle Properties (For each candle):
   - Body Size: Small/Medium/Large
   - Upper Shadow: None/Small/Medium/Large
   - Lower Shadow: None/Small/Medium/Large
   - Color: Green/Red/Any
   
3. Candle Relationships:
   - Higher High
   - Lower Low
   - Engulfing
   - Inside Bar
   - Outside Bar
```

#### Pre-built Patterns (Dropdown)
```
Select from Library:
- Bullish Engulfing
- Bearish Engulfing
- Morning Star
- Evening Star
- Hammer
- Shooting Star
- Doji
- Three White Soldiers
- Three Black Crows
- Inside Bar
- Outside Bar
- Custom Pattern
```

#### Pattern Matching Settings
```
Strict Matching: Toggle (Yes/No)
  - Strict: Exact pattern match required
  - Flexible: Allow slight variations
  
Tolerance: Slider (0-20%)
  - How much variation to allow in pattern recognition
```

---

## 🗄 Database Schema

### Tables Required

#### 1. **strategies** (User-created strategies)
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Instrument Selection (NEW)
    asset_class VARCHAR(20), -- 'OPTIONS', 'EQUITY', 'COMMODITY', 'CURRENCY', 'FUTURES'
    instrument_symbol VARCHAR(50), -- 'BANKNIFTY', 'NIFTY', 'RELIANCE', 'GOLD', etc.
    exchange VARCHAR(10), -- 'NSE', 'BSE', 'NFO', 'MCX', 'CDS'
    product_type VARCHAR(10), -- 'MIS', 'NRML', 'CNC', 'BO', 'CO'
    lot_size_override INT, -- Custom lot size (NULL = use default)
    
    -- Trading Type
    trading_type VARCHAR(20), -- 'INTRADAY', 'POSITIONAL', 'SWING', 'LONG_TERM'
    
    -- Entry Logic
    signal_bar_index INT, -- 0=First, 1=Second, 2=Third
    timeframe VARCHAR(10), -- '1min', '5min', '15min', etc.
    breakout_type VARCHAR(50), -- 'ORB', 'SECOND_BAR', etc.
    breakout_direction VARCHAR(20), -- 'BULLISH', 'BEARISH', 'BOTH'
    require_volume_confirmation BOOLEAN DEFAULT FALSE,
    volume_threshold_pct DECIMAL(5,2) DEFAULT 150.00,
    
    -- Strike Selection (OPTIONS ONLY)
    expiry_type VARCHAR(20), -- 'WEEKLY', 'MONTHLY', 'CUSTOM'
    strike_selection VARCHAR(20), -- 'ATM', 'OTM_100', 'ITM_100', etc.
    strike_offset INT DEFAULT 0, -- Custom offset in points
    min_premium DECIMAL(10,2) DEFAULT 0,
    max_premium DECIMAL(10,2) DEFAULT 10000,
    option_type VARCHAR(5), -- 'CE', 'PE', 'BOTH'
    
    -- Position Side (EQUITY/COMMODITY/FUTURES)
    position_side VARCHAR(10), -- 'LONG', 'SHORT', 'BOTH'
    quantity_type VARCHAR(20), -- 'FIXED', 'CAPITAL_BASED', 'PERCENTAGE'
    fixed_quantity INT, -- For equity: shares, For others: lots
    min_price DECIMAL(10,2), -- Min instrument price filter
    max_price DECIMAL(10,2), -- Max instrument price filter
    
    -- Risk Management
    stop_loss_type VARCHAR(20), -- 'FIXED_POINTS', 'FIXED_PCT', 'SIGNAL_BAR'
    stop_loss_value DECIMAL(10,2),
    target_type VARCHAR(20), -- 'FIXED_POINTS', 'RR_RATIO', 'SIGNAL_BAR_MULTIPLE'
    target_value DECIMAL(10,2),
    lot_size INT DEFAULT 15,
    max_capital_per_trade DECIMAL(15,2),
    exit_time TIME DEFAULT '15:15:00',
    
    -- Filters
    min_signal_bar_range DECIMAL(10,2) DEFAULT 0,
    max_signal_bar_range DECIMAL(10,2) DEFAULT 10000,
    max_vix DECIMAL(5,2),
    trade_on_monday BOOLEAN DEFAULT TRUE,
    trade_on_tuesday BOOLEAN DEFAULT TRUE,
    trade_on_wednesday BOOLEAN DEFAULT TRUE,
    trade_on_thursday BOOLEAN DEFAULT TRUE,
    trade_on_friday BOOLEAN DEFAULT TRUE,
    
    -- Costs
    slippage_points DECIMAL(5,2) DEFAULT 2.00,
    brokerage_per_lot DECIMAL(10,2) DEFAULT 20.00,
    taxes_pct DECIMAL(5,4) DEFAULT 0.0500,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 2. **backtest_results** (Store backtest run results)
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INT NOT NULL,
    run_date TIMESTAMP DEFAULT NOW(),
    
    -- Date Range
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    
    -- Performance Metrics
    total_trades INT,
    winning_trades INT,
    losing_trades INT,
    win_rate DECIMAL(5,2),
    
    total_pnl DECIMAL(15,2),
    avg_pnl_per_trade DECIMAL(10,2),
    max_drawdown DECIMAL(15,2),
    max_drawdown_pct DECIMAL(5,2),
    
    largest_win DECIMAL(10,2),
    largest_loss DECIMAL(10,2),
    avg_win DECIMAL(10,2),
    avg_loss DECIMAL(10,2),
    
    profit_factor DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    
    -- Additional Stats
    total_ce_trades INT,
    total_pe_trades INT,
    target_hit_count INT,
    sl_hit_count INT,
    eod_exit_count INT,
    
    -- Execution Time
    execution_time_seconds INT,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);
```

#### 3. **trades** (Individual trade details)
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    backtest_id INT NOT NULL,
    trade_date DATE NOT NULL,
    
    -- Entry Details
    entry_time TIMESTAMP,
    entry_spot_price DECIMAL(10,2),
    entry_premium DECIMAL(10,2),
    
    -- Exit Details
    exit_time TIMESTAMP,
    exit_spot_price DECIMAL(10,2),
    exit_premium DECIMAL(10,2),
    exit_reason VARCHAR(20), -- 'TARGET', 'SL', 'EOD'
    
    -- Trade Details (Universal)
    asset_class VARCHAR(20), -- 'OPTIONS', 'EQUITY', 'COMMODITY', 'FUTURES'
    instrument_symbol VARCHAR(50), -- 'BANKNIFTY', 'RELIANCE', 'GOLD', etc.
    signal_type VARCHAR(10), -- 'CE', 'PE', 'LONG', 'SHORT'
    
    -- Options-specific fields
    strike_price DECIMAL(10,2), -- NULL for non-options
    expiry_date DATE, -- NULL for equity (non-expiry)
    days_to_expiry INT, -- NULL for equity
    option_type VARCHAR(5), -- 'CE', 'PE', NULL
    
    -- Signal Bar Details
    signal_bar_high DECIMAL(10,2),
    signal_bar_low DECIMAL(10,2),
    signal_bar_range DECIMAL(10,2),
    
    -- P&L
    spot_move DECIMAL(10,2),
    spot_move_pct DECIMAL(5,2),
    pnl DECIMAL(10,2),
    pnl_pct DECIMAL(5,2),
    
    -- Greeks & Risk
    entry_delta DECIMAL(5,4),
    exit_delta DECIMAL(5,4),
    gamma DECIMAL(5,6),
    theta_decay DECIMAL(10,2),
    
    -- Quantity/Lot Size (Universal)
    lot_size INT, -- For options/futures/commodity
    quantity INT, -- For equity (number of shares)
    contract_value DECIMAL(15,2), -- Total position value
    margin_required DECIMAL(15,2), -- Margin blocked
    
    FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
);
```

#### 4. **patterns** (User-created candlestick patterns)
```sql
CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    description TEXT,
    pattern_type VARCHAR(20), -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    num_candles INT,
    pattern_definition JSON, -- Store pattern rules as JSON
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 5. **users** (User authentication)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 🔌 API Endpoints

### Strategy Management APIs

#### Create Strategy
```
POST /api/strategies
Body: {strategy configuration JSON}
Response: {strategy_id, message}
```

#### Get All Strategies
```
GET /api/strategies
Query Params: ?user_id=X
Response: [{strategy1}, {strategy2}, ...]
```

#### Get Strategy by ID
```
GET /api/strategies/{strategy_id}
Response: {strategy details}
```

#### Update Strategy
```
PUT /api/strategies/{strategy_id}
Body: {updated strategy configuration}
Response: {message}
```

#### Delete Strategy
```
DELETE /api/strategies/{strategy_id}
Response: {message}
```

---

### Backtesting APIs

#### Run Backtest
```
POST /api/backtest/run
Body: {
    strategy_id: 123,
    from_date: "2024-01-01",
    to_date: "2024-10-04",
    data_source: "kite" or "csv"
}
Response: {
    backtest_id: 456,
    status: "running",
    estimated_time: 120 (seconds)
}
```

#### Get Backtest Status
```
GET /api/backtest/status/{backtest_id}
Response: {
    status: "completed",
    progress: 100,
    results_ready: true
}
```

#### Get Backtest Results
```
GET /api/backtest/results/{backtest_id}
Response: {
    performance_metrics: {...},
    trades: [...],
    equity_curve: [...]
}
```

#### Get Trade Details
```
GET /api/backtest/trades/{backtest_id}
Query Params: ?page=1&limit=50&signal_type=CE&exit_reason=TARGET
Response: {
    trades: [...],
    total_count: 156,
    page: 1,
    total_pages: 4
}
```

#### Export Backtest Results
```
GET /api/backtest/export/{backtest_id}
Query Params: ?format=csv or xlsx
Response: File download
```

---

### Data Management APIs

#### Fetch Market Data (Universal)
```
POST /api/data/fetch
Body: {
    asset_class: "OPTIONS" | "EQUITY" | "COMMODITY" | "FUTURES",
    symbol: "BANKNIFTY" | "RELIANCE" | "GOLD" | etc.,
    exchange: "NSE" | "BSE" | "MCX" | "NFO",
    from_date: "2024-01-01",
    to_date: "2024-10-04",
    interval: "5minute",
    include_options: true (only for OPTIONS asset class)
}
Response: {
    status: "success",
    candles_fetched: 12500,
    date_range: "...",
    instrument_info: {
        lot_size: 15,
        tick_size: 0.05,
        contract_value: 75000
    }
}
```

#### Get Instrument List
```
GET /api/instruments
Query Params: ?asset_class=EQUITY&exchange=NSE&search=TCS
Response: {
    instruments: [
        {
            symbol: "TCS",
            name: "Tata Consultancy Services",
            exchange: "NSE",
            lot_size: 1,
            last_price: 3450.50,
            sector: "IT"
        },
        ...
    ]
}
```

#### Get Contract Specifications
```
GET /api/instruments/{symbol}/specs
Query Params: ?exchange=NSE
Response: {
    symbol: "BANKNIFTY",
    exchange: "NFO",
    asset_class: "OPTIONS",
    lot_size: 15,
    tick_size: 0.05,
    expiry_day: "Wednesday",
    strike_interval: 100,
    available_expiries: ["2024-10-09", "2024-10-16", ...],
    margin_requirement: 75000
}
```

#### Get Available Data Range
```
GET /api/data/available
Query Params: ?symbol=BANKNIFTY
Response: {
    oldest_date: "2020-01-01",
    latest_date: "2024-10-04",
    total_days: 1248
}
```

---

### Pattern APIs (Future)

#### Create Pattern
```
POST /api/patterns
Body: {pattern configuration}
Response: {pattern_id, message}
```

#### Get Pattern Library
```
GET /api/patterns
Response: [{pattern1}, {pattern2}, ...]
```

#### Test Pattern on Data
```
POST /api/patterns/test
Body: {
    pattern_id: 789,
    test_date_range: {...}
}
Response: {
    matches_found: 23,
    match_dates: [...]
}
```

---

## 🎨 UI/UX Design Guidelines

### Page Structure

#### 1. **Strategy Builder Page**
```
Layout:
┌─────────────────────────────────────────┐
│ Header: Strategy Builder                │
├─────────────────────────────────────────┤
│ Left Sidebar (30%):                     │
│   - Strategy Name & Description         │
│   - Quick Actions:                      │
│     [Save Strategy]                     │
│     [Run Backtest]                      │
│     [Reset Form]                        │
├─────────────────────────────────────────┤
│ Main Content (70%):                     │
│   ┌─ Accordion Sections ─────────────┐ │
│   │ ▼ 1. Entry Logic                 │ │
│   │ ▼ 2. Strike Selection            │ │
│   │ ▼ 3. Risk Management             │ │
│   │ ▼ 4. Advanced Filters            │ │
│   │ ▶ 5. Pattern Configuration       │ │
│   └──────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### 2. **Backtest Results Page**
```
Layout:
┌─────────────────────────────────────────┐
│ Header: Backtest Results                │
│ Strategy: Opening Bar Breakout          │
│ Date Range: Jan 1, 2024 - Oct 4, 2024  │
├─────────────────────────────────────────┤
│ ┌─ Performance Cards (Row 1) ────────┐ │
│ │ [Total P&L] [Win Rate] [Trades]   │ │
│ │ [Max DD]    [Sharpe]   [Avg P&L]  │ │
│ └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ ┌─ Equity Curve Chart ───────────────┐ │
│ │     (Large Interactive Chart)      │ │
│ └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ ┌─ Distribution Charts (Row 2) ──────┐ │
│ │ [Win/Loss Pie] [Monthly Heatmap]  │ │
│ └───────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ ┌─ Trade Log Table ──────────────────┐ │
│ │ (Paginated, Sortable, Filterable)  │ │
│ │ [Export CSV] [Export Excel]        │ │
│ └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

#### 3. **Pattern Creator Page** (Future)
```
Layout:
┌─────────────────────────────────────────┐
│ Header: Pattern Creator                 │
├─────────────────────────────────────────┤
│ Left Panel (40%):                       │
│   - Pattern Library (Drag & Drop)      │
│   - Pre-built Patterns                  │
├─────────────────────────────────────────┤
│ Center Canvas (60%):                    │
│   - Visual Candle Builder               │
│   - Draw/Edit Candlesticks              │
│   - Set Conditions                      │
├─────────────────────────────────────────┤
│ Bottom Panel:                           │
│   - Pattern Properties                  │
│   - Test Pattern Button                 │
│   - Save Pattern Button                 │
└─────────────────────────────────────────┘
```

---

### Color Scheme
```
Primary: #1976d2 (Blue)
Success: #4caf50 (Green - Profits)
Danger: #f44336 (Red - Losses)
Warning: #ff9800 (Orange - Warnings)
Background: #f5f5f5 (Light Gray)
Text Primary: #212121 (Dark Gray)
Text Secondary: #757575 (Medium Gray)
```

---

### Interactive Elements

#### Tooltips
```
Show on hover:
- Field descriptions
- Formula explanations
- Risk warnings
- Example values
```

#### Validation
```
Real-time validation:
- Highlight invalid fields in red
- Show error messages below fields
- Disable "Save" button until valid
- Show success checkmarks for valid fields
```

#### Progress Indicators
```
For Backtesting:
- Show progress bar (0-100%)
- Estimated time remaining
- Current processing status
  "Fetching data... (25%)"
  "Running backtest... (75%)"
  "Generating results... (95%)"
```

---

## 📊 Additional Features

### Strategy Comparison
```
Feature: Compare multiple strategies side-by-side
- Select 2-4 strategies
- Show metrics in comparison table
- Overlay equity curves
- Highlight best performer
```

### Paper Trading
```
Feature: Test strategy in real-time (future)
- Connect to live market data
- Execute virtual trades
- Track real-time P&L
- Compare with backtest results
```

### Alerts & Notifications
```
Feature: Get notified when signals occur
- Email alerts
- Browser notifications
- SMS alerts (premium)
- Webhook integration
```

---

## 🔒 Security Considerations

### Authentication
```
- JWT-based authentication
- Session management
- Password hashing (bcrypt)
- Rate limiting on API calls
```

### Data Protection
```
- Encrypt sensitive data (API keys)
- HTTPS only
- CORS policy
- Input sanitization
- SQL injection prevention
```

---

## 🚀 Technology Stack Recommendations

### Frontend
```
- Framework: React.js (18+) or Vue.js (3+)
- UI Library: Material-UI (MUI) or Ant Design
- Charts: Chart.js, Plotly.js, or TradingView Widgets
- State Management: Redux Toolkit or Zustand
- HTTP Client: Axios with interceptors
- Real-time Data: WebSocket (Socket.io)
- Form Management: React Hook Form or Formik
```

### Backend
```
- Framework: Flask (Python 3.10+) or FastAPI (Recommended)
- Alternative: Node.js with Express or NestJS
- Database: PostgreSQL 14+ with TimescaleDB (for time-series data)
- API: RESTful (primary) + GraphQL (optional)
- Background Jobs: 
  - Celery (Python) with Redis broker
  - Bull (Node.js)
- Caching: Redis 7+
- Message Queue: RabbitMQ or Kafka (for real-time data)
- Market Data Integration:
  - Kite Connect API (Zerodha)
  - NSE/BSE Data APIs
  - MCX Data APIs
```

### Deployment
```
- Server: AWS EC2 or DigitalOcean
- Database: AWS RDS or managed PostgreSQL
- Static Files: AWS S3 + CloudFront
- Container: Docker
- Orchestration: Kubernetes (optional)
```

---

## 📝 Development Roadmap

### Phase 1 (MVP) - 4-6 weeks
```
✅ User authentication
✅ Strategy builder (basic parameters)
✅ Backtest engine
✅ Results visualization
✅ Trade log export
```

### Phase 2 - 6-8 weeks
```
🔲 Advanced filters
🔲 Pattern creator module
🔲 Strategy comparison
🔲 Real-time data integration
🔲 Mobile responsiveness
```

### Phase 3 - 8-10 weeks
```
🔲 Paper trading
🔲 Live trading integration
🔲 Alerts & notifications
🔲 Portfolio management
🔲 Risk analytics
```

---

## 📚 User Documentation

### Help Sections Required
```
1. Getting Started Guide
2. Strategy Builder Tutorial
3. Understanding Backtest Results
4. Pattern Creator Guide (Future)
5. API Documentation
6. FAQs
7. Video Tutorials
```

---

## 🎯 Success Metrics

### Key Performance Indicators (KPIs)
```
- User Registration: Target 1000+ users in 6 months
- Active Strategies: 50+ strategies created per month
- Backtests Run: 500+ backtests per month
- User Retention: 60% monthly active users
- Avg Session Duration: 15+ minutes
- Feature Adoption: 70% users use advanced filters
```

---

## 📞 Support & Maintenance

### Support Channels
```
- Email Support: support@tradingstrategy.com
- Live Chat: Business hours
- Documentation: Comprehensive guides
- Community Forum: User discussions
```

### Maintenance Schedule
```
- Database Backup: Daily
- Server Updates: Weekly
- Security Patches: As needed
- Feature Updates: Monthly
- Performance Monitoring: 24/7
```

---

## 🎉 Conclusion

This specification provides a comprehensive blueprint for building a **universal, multi-asset trading strategy platform** that supports:

✅ **Index Options** (Bank Nifty, Nifty, Fin Nifty)  
✅ **Equity Trading** (NSE, BSE stocks)  
✅ **Commodity Trading** (MCX - Gold, Silver, Crude, etc.)  
✅ **Currency Trading** (CDS - USD/INR, EUR/INR, etc.)  
✅ **Futures Trading** (Index & Stock Futures)  

The platform is designed to be:
- **Scalable**: Easily add new instruments and asset classes
- **Modular**: Each component can be developed independently
- **User-friendly**: Intuitive interface for strategy building
- **Robust**: Comprehensive backtesting with accurate simulation
- **Extensible**: Pattern creator and advanced features for power users

**Next Steps:**
1. Review and approve specification
2. Set up development environment
3. Create database schemas
4. Build API endpoints
5. Develop frontend components
6. Integrate backtesting engine
7. Testing and deployment

---

**Document Version:** 1.0  
**Last Updated:** October 4, 2025  
**Author:** Strategy Development Team  
**Status:** Ready for Implementation
