"""
Bank Nifty Options - Opening Bar Breakout Strategy
Strategy: Buy options on opening bar breakout, hold till end of day (3:15 PM)
"""

import logging
from datetime import datetime, timedelta
import pandas as pd
from kiteconnect import KiteConnect
import config

# Suppress unnecessary logging
for logger in ['urllib3', 'requests']:
    logging.getLogger(logger).setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)


# ============================================================================
# SECTION 1: KITE API CONNECTION
# ============================================================================

def connect_to_kite():
    """Connect to Kite API"""
    print(">> Connecting to Kite API...")
    kite = KiteConnect(api_key=config.KITE_API_KEY)
    
    if config.KITE_ACCESS_TOKEN and config.KITE_ACCESS_TOKEN != "None":
        kite.set_access_token(config.KITE_ACCESS_TOKEN)
        try:
            profile = kite.profile()
            print(f"✅ Connected! User: {profile['user_name']}")
            return kite
        except:
            print("❌ Token expired")
            return None
    
    print("❌ No valid token. Run trading_system.py to generate token first.")
    return None


# ============================================================================
# SECTION 2: DATA FETCHING
# ============================================================================

def get_banknifty_data(days=100, kite_connection=None):
    """Fetch Bank Nifty spot 5-minute data"""
    kite = kite_connection or connect_to_kite()
    if not kite:
        return None
    
    try:
        # Get Bank Nifty instrument
        instruments = kite.instruments("NSE")
        banknifty = next((item for item in instruments if item['tradingsymbol'] == 'NIFTY BANK'), None)
        
        if not banknifty:
            print("❌ Bank Nifty instrument not found")
            return None
        
        instrument_token = banknifty['instrument_token']
        all_data = []
        chunk_size = 90
        end_date = datetime.now()
        
        print(f"📊 Fetching Bank Nifty data for {days} days...")
        
        # Fetch in chunks
        while days > 0:
            current_chunk = min(chunk_size, days)
            start_date = end_date - timedelta(days=current_chunk)
            
            print(f"    {start_date.date()} to {end_date.date()}...", end=" ")
            
            try:
                data = kite.historical_data(
                    instrument_token=instrument_token,
                    from_date=start_date,
                    to_date=end_date,
                    interval="5minute"
                )
                if data:
                    all_data.extend(data)
                    print(f"{len(data)} candles")
            except Exception as e:
                print(f"Failed: {e}")
            
            end_date = start_date
            days -= current_chunk
        
        if not all_data:
            return None
        
        # Process data
        df = pd.DataFrame(all_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').drop_duplicates(subset=['date']).reset_index(drop=True)
        
        # Filter market hours (9:15 AM - 3:30 PM)
        df['time'] = df['date'].dt.time
        market_hours = (df['time'] >= pd.Timestamp('09:15:00').time()) & \
                      (df['time'] <= pd.Timestamp('15:30:00').time())
        df = df[market_hours].reset_index(drop=True)
        
        # Add date column for grouping
        df['trade_date'] = df['date'].dt.date
        
        print(f"✅ Total: {len(df):,} candles, {df['trade_date'].nunique()} trading days")
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_options_data(symbol, expiry_date, strike, option_type, from_date, to_date, kite_connection):
    """
    Fetch options data for a specific strike
    Note: Kite API has limited historical options data
    This is a placeholder - in real backtesting you'd need options premium data
    """
    # In real scenario, you'd fetch actual option chain data
    # For now, we'll simulate based on spot movement
    return None


# ============================================================================
# SECTION 3: EXPIRY & STRIKE SELECTION LOGIC
# ============================================================================

def get_next_weekly_expiry(trade_date):
    """
    Get next weekly expiry for Bank Nifty (Wednesdays)
    
    Bank Nifty weekly options expire every Wednesday
    If today is Wednesday, use today's expiry
    Otherwise, use next Wednesday
    """
    from datetime import datetime, timedelta
    
    if isinstance(trade_date, pd.Timestamp):
        trade_date = trade_date.date()
    elif isinstance(trade_date, str):
        trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
    
    # Get day of week (0=Monday, 6=Sunday)
    weekday = trade_date.weekday()
    
    # Wednesday is day 2
    if weekday <= 2:  # Monday, Tuesday, or Wednesday
        # Days until next Wednesday
        days_ahead = 2 - weekday
    else:  # Thursday, Friday
        # Days until next week's Wednesday
        days_ahead = (2 - weekday) + 7
    
    expiry_date = trade_date + timedelta(days=days_ahead)
    return expiry_date


def get_monthly_expiry(trade_date):
    """
    Get monthly expiry (last Thursday of the month)
    Bank Nifty monthly options expire on last Thursday
    """
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    if isinstance(trade_date, pd.Timestamp):
        trade_date = trade_date.date()
    elif isinstance(trade_date, str):
        trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
    
    # Get last day of current month
    last_day = monthrange(trade_date.year, trade_date.month)[1]
    month_end = trade_date.replace(day=last_day)
    
    # Find last Thursday (weekday 3)
    while month_end.weekday() != 3:  # 3 = Thursday
        month_end -= timedelta(days=1)
    
    # If we're past the monthly expiry, get next month's
    if trade_date > month_end:
        next_month = trade_date.replace(day=1) + timedelta(days=32)
        last_day = monthrange(next_month.year, next_month.month)[1]
        month_end = next_month.replace(day=last_day)
        while month_end.weekday() != 3:
            month_end -= timedelta(days=1)
    
    return month_end


def select_expiry(trade_date, expiry_type="WEEKLY"):
    """
    Select appropriate expiry based on trade date
    
    Args:
        trade_date: Date of trade
        expiry_type: "WEEKLY" or "MONTHLY"
    
    Returns:
        Expiry date
    """
    if expiry_type == "WEEKLY":
        return get_next_weekly_expiry(trade_date)
    else:
        return get_monthly_expiry(trade_date)


def calculate_atm_strike(spot_price):
    """Calculate ATM (At The Money) strike - rounded to nearest 100"""
    return round(spot_price / 100) * 100


def select_strikes(spot_price, strategy="ATM"):
    """
    Select option strikes based on strategy
    
    Args:
        spot_price: Bank Nifty spot price at 9:15 AM
        strategy: "ATM", "OTM_100", "OTM_200", "ITM_100"
    
    Returns:
        dict with CE and PE strikes
    """
    atm = calculate_atm_strike(spot_price)
    
    strategies = {
        "ATM": {
            "CE": atm,
            "PE": atm,
            "name": "At The Money"
        },
        "OTM_100": {
            "CE": atm + 100,
            "PE": atm - 100,
            "name": "100 Points OTM"
        },
        "OTM_200": {
            "CE": atm + 200,
            "PE": atm - 200,
            "name": "200 Points OTM"
        },
        "ITM_100": {
            "CE": atm - 100,
            "PE": atm + 100,
            "name": "100 Points ITM"
        }
    }
    
    return strategies.get(strategy, strategies["ATM"])


# ============================================================================
# SECTION 4: OPENING BAR BREAKOUT STRATEGY
# ============================================================================

def detect_opening_bar_breakout(df, expiry_type="WEEKLY"):
    """
    Modified Strategy: Second Bar Breakout with Stop Loss & Target
    
    Strategy:
    - Second bar: 9:20-9:25 AM (2nd 5-min candle)
    - Entry: When price breaks second bar high/low
    - Stop Loss: Slightly below/above second bar (opposite side)
    - Target: 3x the second bar range
    
    Args:
        df: DataFrame with Bank Nifty data
        expiry_type: "WEEKLY" or "MONTHLY"
    """
    results = []
    
    # Group by trading date
    for trade_date, day_data in df.groupby('trade_date'):
        day_data = day_data.reset_index(drop=True)
        
        if len(day_data) < 3:  # Need at least 3 candles
            continue
        
        # Calculate expiry for this trade date
        expiry_date = select_expiry(trade_date, expiry_type)
        
        # Calculate days to expiry
        if isinstance(trade_date, pd.Timestamp):
            trade_date_dt = trade_date
        else:
            trade_date_dt = pd.Timestamp(trade_date)
        
        days_to_expiry = (pd.Timestamp(expiry_date) - trade_date_dt).days
        
        # First candle (9:15-9:20 AM) - for reference
        first_bar = day_data.iloc[0]
        
        # SECOND BAR (9:20-9:25 AM) - Our signal bar
        second_bar = day_data.iloc[1]
        second_bar_high = second_bar['high']
        second_bar_low = second_bar['low']
        second_bar_close = second_bar['close']
        second_bar_range = second_bar_high - second_bar_low
        
        # Wait for breakout signal
        signal = None
        entry_time = None
        entry_price = None
        stop_loss = None
        target = None
        entry_candle_idx = None
        
        # Check subsequent candles for breakout (starting from 3rd candle)
        for idx in range(2, len(day_data)):
            candle = day_data.iloc[idx]
            
            # Bullish breakout - candle breaks above second bar high
            if candle['high'] > second_bar_high and signal is None:
                signal = "CE"  # Call option
                entry_time = candle['date']
                entry_price = second_bar_high  # Entry at breakout level
                
                # Stop loss: Low of second bar
                stop_loss = second_bar_low
                
                # Target: 3x the second bar range from entry
                target = entry_price + (second_bar_range * 3)
                
                entry_candle_idx = idx
                break
            
            # Bearish breakout - candle breaks below second bar low
            elif candle['low'] < second_bar_low and signal is None:
                signal = "PE"  # Put option
                entry_time = candle['date']
                entry_price = second_bar_low  # Entry at breakout level
                
                # Stop loss: High of second bar
                stop_loss = second_bar_high
                
                # Target: 3x the second bar range from entry
                target = entry_price - (second_bar_range * 3)
                
                entry_candle_idx = idx
                break
        
        # If no breakout, skip this day
        if signal is None:
            results.append({
                'date': trade_date,
                'expiry_date': expiry_date,
                'days_to_expiry': days_to_expiry,
                'second_bar_high': second_bar_high,
                'second_bar_low': second_bar_low,
                'second_bar_range': second_bar_range,
                'signal': 'NO_BREAKOUT',
                'entry_time': None,
                'entry_price': None,
                'stop_loss': None,
                'target': None,
                'exit_time': None,
                'exit_price': None,
                'exit_reason': None,
                'spot_move': 0
            })
            continue
        
        # Track the trade for stop loss and target
        exit_price = None
        exit_time = None
        exit_reason = None
        sl_hit = False
        target_hit = False
        
        # Check each candle after entry for SL/Target
        for idx in range(entry_candle_idx, len(day_data)):
            candle = day_data.iloc[idx]
            
            if signal == "CE":  # Call option - bullish
                # Check if stop loss hit
                if candle['low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_time = candle['date']
                    exit_reason = "STOP_LOSS"
                    sl_hit = True
                    break
                
                # Check if target hit
                elif candle['high'] >= target:
                    exit_price = target
                    exit_time = candle['date']
                    exit_reason = "TARGET"
                    target_hit = True
                    break
            
            else:  # PE - Put option - bearish
                # Check if stop loss hit
                if candle['high'] >= stop_loss:
                    exit_price = stop_loss
                    exit_time = candle['date']
                    exit_reason = "STOP_LOSS"
                    sl_hit = True
                    break
                
                # Check if target hit
                elif candle['low'] <= target:
                    exit_price = target
                    exit_time = candle['date']
                    exit_reason = "TARGET"
                    target_hit = True
                    break
        
        # If neither SL nor Target hit, exit at 3:15 PM
        if not sl_hit and not target_hit:
            exit_candle = day_data.iloc[-2]  # 3:15-3:20 PM candle
            exit_price = exit_candle['close']
            exit_time = exit_candle['date']
            exit_reason = "EOD"
        
        # Calculate spot movement
        spot_move = exit_price - entry_price if signal == "CE" else entry_price - exit_price
        spot_move_pct = (spot_move / entry_price) * 100
        
        # Calculate ATM strike for reference
        atm_strike = calculate_atm_strike(second_bar_close)
        
        # Calculate risk-reward
        risk = abs(entry_price - stop_loss)
        reward = abs(target - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        results.append({
            'date': trade_date,
            'expiry_date': expiry_date,
            'days_to_expiry': days_to_expiry,
            'atm_strike': atm_strike,
            'second_bar_high': second_bar_high,
            'second_bar_low': second_bar_low,
            'second_bar_range': second_bar_range,
            'signal': signal,
            'entry_time': entry_time,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target': target,
            'risk_reward_ratio': risk_reward_ratio,
            'exit_time': exit_time,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'spot_move': spot_move,
            'spot_move_pct': spot_move_pct,
            'day_high': day_data['high'].max(),
            'day_low': day_data['low'].min()
        })
    
    return pd.DataFrame(results)


# ============================================================================
# SECTION 5: OPTIONS P&L SIMULATION
# ============================================================================

def calculate_option_delta(spot_price, strike_price, option_type, days_to_expiry, iv=0.20):
    """
    Calculate option delta using Black-Scholes approximation
    
    Delta ranges:
    - ATM: ~0.50 (Call), ~-0.50 (Put)
    - ITM: 0.60-0.95 (Call), -0.60 to -0.95 (Put)
    - OTM: 0.05-0.40 (Call), -0.05 to -0.40 (Put)
    
    Args:
        spot_price: Current Bank Nifty price
        strike_price: Option strike price
        option_type: "CE" or "PE"
        days_to_expiry: Days until expiry
        iv: Implied volatility (default 20%)
    
    Returns:
        Delta value between 0 and 1 (or 0 and -1 for puts)
    """
    import math
    
    # Simplified Black-Scholes delta calculation
    # Using risk-free rate ~6% (RBI rate)
    r = 0.06
    
    # Moneyness: how far strike is from spot
    moneyness = (spot_price - strike_price) / spot_price
    
    # Time to expiry in years
    t = days_to_expiry / 365.0
    
    # Avoid division by zero
    if t < 0.001:
        t = 0.001
    
    # Simplified delta calculation based on moneyness
    if option_type == "CE":
        # Call option delta
        if moneyness > 0.02:  # ITM (spot > strike by 2%)
            base_delta = 0.70 + (moneyness * 5)  # ITM calls increase delta
            delta = min(0.95, base_delta)
        elif moneyness < -0.02:  # OTM (spot < strike by 2%)
            base_delta = 0.30 + (moneyness * 5)  # OTM calls decrease delta
            delta = max(0.05, base_delta)
        else:  # ATM (within 2%)
            delta = 0.50
    else:  # PE
        # Put option delta (negative)
        if moneyness < -0.02:  # ITM (spot < strike by 2%)
            base_delta = -0.70 + (moneyness * 5)  # ITM puts increase absolute delta
            delta = max(-0.95, base_delta)
        elif moneyness > 0.02:  # OTM (spot > strike by 2%)
            base_delta = -0.30 + (moneyness * 5)  # OTM puts decrease absolute delta
            delta = min(-0.05, base_delta)
        else:  # ATM (within 2%)
            delta = -0.50
    
    # Adjust for time decay - delta moves toward 0 or 1 near expiry
    if days_to_expiry <= 1:
        # Near expiry, ITM moves to 1, OTM moves to 0
        if abs(moneyness) > 0.01:
            delta = delta * 1.2 if abs(delta) > 0.5 else delta * 0.8
    
    return delta


def calculate_option_gamma(delta, spot_price, days_to_expiry):
    """
    Calculate gamma (rate of change of delta)
    Gamma is highest for ATM options near expiry
    
    Args:
        delta: Current delta value
        spot_price: Current Bank Nifty price
        days_to_expiry: Days until expiry
    
    Returns:
        Gamma value (delta change per 1 point spot move)
    """
    # ATM options have highest gamma
    # Gamma increases as expiry approaches
    
    # Base gamma depends on how close to ATM (delta ~0.5)
    atm_distance = abs(abs(delta) - 0.5)
    base_gamma = 0.01 * (1 - atm_distance * 2)  # Max at ATM
    
    # Time multiplier - gamma increases near expiry
    if days_to_expiry <= 1:
        time_mult = 3.0  # High gamma on expiry day
    elif days_to_expiry <= 3:
        time_mult = 2.0  # Elevated gamma in last week
    elif days_to_expiry <= 7:
        time_mult = 1.5
    else:
        time_mult = 1.0
    
    gamma = base_gamma * time_mult
    return max(0, gamma)


def simulate_option_premium(spot_move, spot_move_pct, option_type, strike_type, days_to_expiry=3, 
                           spot_entry=50000, spot_exit=50000):
    """
    Simulate option premium change based on spot movement with DELTA TRACKING
    
    Enhanced model with:
    - Dynamic delta calculation based on moneyness
    - Gamma effect (delta changes as spot moves)
    - Theta decay (time decay)
    - Vega impact (volatility)
    
    Approximations:
    - ATM options: ~0.5-0.6 delta
    - OTM 100: ~0.3-0.4 delta
    - OTM 200: ~0.15-0.25 delta
    - ITM 100: ~0.6-0.7 delta
    
    Entry premium estimates (Bank Nifty):
    - ATM: ~250-350 per lot
    - OTM 100: ~150-200 per lot
    - OTM 200: ~50-100 per lot
    - ITM 100: ~400-500 per lot
    
    Args:
        spot_move: Spot price movement
        spot_move_pct: Spot price movement percentage
        option_type: "CE" or "PE"
        strike_type: "ATM", "OTM_100", "OTM_200", "ITM_100"
        days_to_expiry: Days to expiry
        spot_entry: Entry spot price
        spot_exit: Exit spot price
    """
    
    # Initial delta approximations (how much premium moves with 1 point spot move)
    initial_deltas = {
        "ATM": 0.55,
        "OTM_100": 0.35,
        "OTM_200": 0.20,
        "ITM_100": 0.65
    }
    
    # Entry premiums (rough estimates for Bank Nifty)
    # These adjust based on days to expiry
    base_premiums = {
        "ATM": 300,
        "OTM_100": 175,
        "OTM_200": 75,
        "ITM_100": 450
    }
    
    delta = initial_deltas.get(strike_type, 0.5)
    base_premium = base_premiums.get(strike_type, 250)
    
    # Adjust premium based on days to expiry
    # More time = higher premium due to time value
    if days_to_expiry <= 1:
        time_multiplier = 0.6  # Expiry day - low time value
    elif days_to_expiry <= 3:
        time_multiplier = 1.0  # Current week
    elif days_to_expiry <= 7:
        time_multiplier = 1.3  # Next week
    else:
        time_multiplier = 1.5  # 2+ weeks
    
    entry_premium = base_premium * time_multiplier
    
    # ENHANCED DELTA TRACKING - Calculate premium change with gamma effect
    # As spot moves, delta changes (gamma effect)
    
    # Entry delta
    entry_delta = abs(delta)
    
    # Calculate gamma (delta change rate)
    gamma = calculate_option_gamma(delta, spot_entry, days_to_expiry)
    
    # As spot moves, delta changes: new_delta = old_delta + (gamma * spot_move)
    # For multi-step moves, integrate the effect
    num_steps = max(1, int(abs(spot_move) / 10))  # Split into 10-point steps
    step_size = spot_move / num_steps
    
    cumulative_premium_change = 0
    current_delta = entry_delta
    
    for step in range(num_steps):
        # Premium change for this step
        step_premium_change = current_delta * step_size
        cumulative_premium_change += step_premium_change
        
        # Update delta with gamma effect
        current_delta = current_delta + (gamma * step_size)
        current_delta = max(0.01, min(0.99, current_delta))  # Keep delta in valid range
    
    # Final delta at exit
    exit_delta = current_delta
    
    # Calculate exit premium
    # For CE: spot up = premium up, spot down = premium down
    # For PE: spot down = premium up, spot up = premium down
    if option_type == "CE":
        if spot_move > 0:  # Favorable
            exit_premium = entry_premium + cumulative_premium_change
            profit = cumulative_premium_change
        else:  # Unfavorable
            exit_premium = max(entry_premium + cumulative_premium_change, 0)  # spot_move is negative
            profit = cumulative_premium_change
    else:  # PE
        if spot_move < 0:  # Favorable (spot down)
            exit_premium = entry_premium + abs(cumulative_premium_change)
            profit = abs(cumulative_premium_change)
        else:  # Unfavorable (spot up)
            exit_premium = max(entry_premium - cumulative_premium_change, 0)
            profit = -cumulative_premium_change
    
    # Apply theta decay (time decay) - increases near expiry
    # For a 6-hour hold (9:30 AM to 3:15 PM)
    if days_to_expiry <= 1:
        theta_decay_pct = 0.15  # 15% decay on expiry day
    elif days_to_expiry <= 3:
        theta_decay_pct = 0.08  # 8% decay for current week
    elif days_to_expiry <= 7:
        theta_decay_pct = 0.05  # 5% decay for next week
    else:
        theta_decay_pct = 0.03  # 3% decay for distant expiry
    
    theta_decay = entry_premium * theta_decay_pct
    profit -= theta_decay
    exit_premium = max(exit_premium - theta_decay, 0)
    
    return {
        'entry_premium': entry_premium,
        'exit_premium': exit_premium,
        'entry_delta': entry_delta,
        'exit_delta': exit_delta,
        'gamma': gamma,
        'theta_decay': theta_decay,
        'profit': profit,
        'profit_pct': (profit / entry_premium) * 100 if entry_premium > 0 else 0
    }


def calculate_strategy_pnl(breakout_df, strike_strategy="ATM", lot_size=15):
    """
    Calculate P&L for the strategy with stop loss and target
    
    Args:
        breakout_df: DataFrame with breakout signals
        strike_strategy: "ATM", "OTM_100", "OTM_200", "ITM_100"
        lot_size: Bank Nifty lot size 
                  - Current (Oct 2024): 15
                  - Previous (before Oct 2024): 25
                  - Check NSE for latest: https://www.nseindia.com/products-services/indices-bankex-bank-nifty
    """
    results = []
    
    for _, row in breakout_df.iterrows():
        if row['signal'] == 'NO_BREAKOUT':
            results.append({
                'date': row['date'],
                'expiry_date': row.get('expiry_date', None),
                'days_to_expiry': row.get('days_to_expiry', 0),
                'signal': 'NO_BREAKOUT',
                'strike_type': strike_strategy,
                'exit_reason': None,
                'spot_move': 0,
                'entry_premium': 0,
                'exit_premium': 0,
                'profit_per_lot': 0,
                'total_profit': 0,
                'profit_pct': 0
            })
            continue
        
        # Get days to expiry for this trade
        days_to_expiry = row.get('days_to_expiry', 3)
        exit_reason = row.get('exit_reason', 'EOD')
        
        # Calculate strike based on strategy
        second_bar_close = (row.get('second_bar_high', 0) + row.get('second_bar_low', 0)) / 2
        atm_strike = row.get('atm_strike', calculate_atm_strike(second_bar_close))
        selected_strikes = select_strikes(second_bar_close, strike_strategy)
        
        if row['signal'] == 'CE':
            selected_strike = selected_strikes['CE']
        else:
            selected_strike = selected_strikes['PE']
        
        # Get spot prices
        spot_entry = row.get('entry_price', 50000)
        spot_exit = row.get('exit_price', 50000)
        
        # Simulate option P&L based on exit reason with DELTA TRACKING
        if exit_reason == "STOP_LOSS":
            # Stop loss hit - calculate loss based on spot movement
            option_pnl = simulate_option_premium(
                row['spot_move'],
                row['spot_move_pct'],
                row['signal'],
                strike_strategy,
                days_to_expiry,
                spot_entry,
                spot_exit
            )
        elif exit_reason == "TARGET":
            # Target hit - calculate profit based on 3x range
            option_pnl = simulate_option_premium(
                row['spot_move'],
                row['spot_move_pct'],
                row['signal'],
                strike_strategy,
                days_to_expiry,
                spot_entry,
                spot_exit
            )
        else:  # EOD
            # Held till end of day
            option_pnl = simulate_option_premium(
                row['spot_move'],
                row['spot_move_pct'],
                row['signal'],
                strike_strategy,
                days_to_expiry,
                spot_entry,
                spot_exit
            )
        
        # Calculate total P&L for lot size
        profit_per_lot = option_pnl['profit']
        total_profit = profit_per_lot * lot_size
        
        results.append({
            'date': row['date'],
            'expiry_date': row.get('expiry_date', None),
            'days_to_expiry': days_to_expiry,
            'signal': row['signal'],
            'strike_type': strike_strategy,
            'atm_strike': atm_strike,
            'selected_strike': selected_strike,
            'entry_price': row['entry_price'],
            'stop_loss': row.get('stop_loss', 0),
            'target': row.get('target', 0),
            'exit_price': row['exit_price'],
            'exit_reason': exit_reason,
            'risk_reward_ratio': row.get('risk_reward_ratio', 0),
            'spot_move': row['spot_move'],
            'spot_move_pct': row['spot_move_pct'],
            'entry_premium': option_pnl['entry_premium'],
            'exit_premium': option_pnl['exit_premium'],
            'entry_delta': option_pnl.get('entry_delta', 0),
            'exit_delta': option_pnl.get('exit_delta', 0),
            'gamma': option_pnl.get('gamma', 0),
            'theta_decay': option_pnl.get('theta_decay', 0),
            'profit_per_lot': profit_per_lot,
            'total_profit': total_profit,
            'profit_pct': option_pnl['profit_pct']
        })
    
    return pd.DataFrame(results)


# ============================================================================
# SECTION 6: BACKTEST RUNNER
# ============================================================================

def run_banknifty_backtest(days=100, strike_strategies=None, expiry_type="WEEKLY", lot_size=15):
    """
    Run complete Bank Nifty options backtest
    
    Args:
        days: Number of days to backtest
        strike_strategies: List of strategies to test (default: all)
        expiry_type: "WEEKLY" (Wednesday) or "MONTHLY" (Last Thursday)
        lot_size: Bank Nifty lot size (current: 15, previous: 25)
    """
    if strike_strategies is None:
        strike_strategies = ["ATM", "OTM_100", "OTM_200", "ITM_100"]
    
    print("=" * 80)
    print("        BANK NIFTY OPTIONS - OPENING BAR BREAKOUT BACKTEST")
    print(f"              Expiry: {expiry_type} | Lot Size: {lot_size}")
    print("=" * 80)
    
    # Connect to Kite
    kite = connect_to_kite()
    if not kite:
        print("❌ Connection failed")
        return
    
    # Fetch Bank Nifty data
    df = get_banknifty_data(days=days, kite_connection=kite)
    if df is None or len(df) < 100:
        print("❌ Insufficient data")
        return
    
    # Detect opening bar breakouts
    print(f"\n🔍 Detecting opening bar breakouts (Using {expiry_type} expiry)...")
    breakout_df = detect_opening_bar_breakout(df, expiry_type=expiry_type)
    
    total_days = len(breakout_df)
    breakout_days = len(breakout_df[breakout_df['signal'] != 'NO_BREAKOUT'])
    ce_days = len(breakout_df[breakout_df['signal'] == 'CE'])
    pe_days = len(breakout_df[breakout_df['signal'] == 'PE'])
    
    print(f"✅ Total trading days: {total_days}")
    print(f"   Breakout days: {breakout_days} ({(breakout_days/total_days)*100:.1f}%)")
    print(f"   - CE (Bullish): {ce_days} days")
    print(f"   - PE (Bearish): {pe_days} days")
    print(f"   - No Breakout: {total_days - breakout_days} days")
    
    # Test each strike strategy
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON")
    print("=" * 80)
    
    all_results = {}
    
    for strategy in strike_strategies:
        print(f"\n📊 Testing {strategy} strategy...")
        pnl_df = calculate_strategy_pnl(breakout_df, strike_strategy=strategy, lot_size=lot_size)
        
        # Calculate statistics
        total_trades = len(pnl_df[pnl_df['signal'] != 'NO_BREAKOUT'])
        winning_trades = len(pnl_df[pnl_df['total_profit'] > 0])
        losing_trades = len(pnl_df[pnl_df['total_profit'] < 0])
        
        # Exit reason statistics
        sl_hits = len(pnl_df[pnl_df['exit_reason'] == 'STOP_LOSS'])
        target_hits = len(pnl_df[pnl_df['exit_reason'] == 'TARGET'])
        eod_exits = len(pnl_df[pnl_df['exit_reason'] == 'EOD'])
        
        total_profit = pnl_df['total_profit'].sum()
        avg_profit = pnl_df[pnl_df['signal'] != 'NO_BREAKOUT']['total_profit'].mean()
        max_profit = pnl_df['total_profit'].max()
        max_loss = pnl_df['total_profit'].min()
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        target_hit_rate = (target_hits / total_trades * 100) if total_trades > 0 else 0
        sl_hit_rate = (sl_hits / total_trades * 100) if total_trades > 0 else 0
        
        all_results[strategy] = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'sl_hits': sl_hits,
            'target_hits': target_hits,
            'eod_exits': eod_exits,
            'sl_hit_rate': sl_hit_rate,
            'target_hit_rate': target_hit_rate,
            'total_profit': total_profit,
            'avg_profit': avg_profit,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'pnl_df': pnl_df
        }
        
        print(f"   Total Trades: {total_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Exit Breakdown:")
        print(f"     - Target Hit: {target_hits} ({target_hit_rate:.1f}%)")
        print(f"     - Stop Loss: {sl_hits} ({sl_hit_rate:.1f}%)")
        print(f"     - EOD Exit: {eod_exits} ({(eod_exits/total_trades*100 if total_trades > 0 else 0):.1f}%)")
        print(f"   Total P&L: ₹{total_profit:,.2f}")
        print(f"   Avg P&L/Trade: ₹{avg_profit:,.2f}")
        print(f"   Max Profit: ₹{max_profit:,.2f}")
        print(f"   Max Loss: ₹{max_loss:,.2f}")
    
    # Summary comparison
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON")
    print("=" * 80)
    print(f"{'Strategy':<12} {'Trades':<8} {'Win%':<8} {'Total P&L':<15} {'Avg P&L':<12}")
    print("-" * 80)
    
    for strategy, results in all_results.items():
        print(f"{strategy:<12} {results['total_trades']:<8} "
              f"{results['win_rate']:<7.1f}% ₹{results['total_profit']:<14,.0f} "
              f"₹{results['avg_profit']:<11,.0f}")
    
    # Best strategy
    best_strategy = max(all_results.items(), key=lambda x: x[1]['total_profit'])
    print(f"\n🏆 BEST STRATEGY: {best_strategy[0]}")
    print(f"   Total P&L: ₹{best_strategy[1]['total_profit']:,.2f}")
    print(f"   Win Rate: {best_strategy[1]['win_rate']:.1f}%")
    
    # Show last 10 trades of best strategy with DELTA ANALYTICS
    print(f"\n📋 LAST 10 TRADES ({best_strategy[0]}) - WITH DELTA TRACKING:")
    print("-" * 140)
    print(f"{'Date':<12} {'Sig':<4} {'Strike':<7} {'DTE':<4} {'Entry₹':<8} {'Exit₹':<8} "
          f"{'δ Entry':<8} {'δ Exit':<8} {'Gamma':<7} {'Theta₹':<7} {'Exit':<10} {'P&L':<12}")
    print("-" * 140)
    
    best_pnl = best_strategy[1]['pnl_df']
    recent_trades = best_pnl[best_pnl['signal'] != 'NO_BREAKOUT'].tail(10)
    
    for _, trade in recent_trades.iterrows():
        signal_emoji = "📈" if trade['signal'] == 'CE' else "📉"
        profit_emoji = "✅" if trade['total_profit'] > 0 else "❌"
        expiry_str = trade['expiry_date'].strftime('%d-%b') if pd.notna(trade.get('expiry_date')) else 'N/A'
        exit_reason = trade.get('exit_reason', 'EOD')
        exit_emoji = "🎯" if exit_reason == 'TARGET' else "🛑" if exit_reason == 'STOP_LOSS' else "⏰"
        
        # Show option premiums and delta information
        entry_premium = trade.get('entry_premium', 0)
        exit_premium = trade.get('exit_premium', 0)
        entry_delta = trade.get('entry_delta', 0)
        exit_delta = trade.get('exit_delta', 0)
        gamma = trade.get('gamma', 0)
        theta = trade.get('theta_decay', 0)
        
        date_str = str(trade['date']).split()[0] if isinstance(trade['date'], pd.Timestamp) else str(trade['date'])[:10]
        
        print(f"{profit_emoji} {date_str:<9} {signal_emoji}{trade['signal']:<3} "
              f"{trade.get('selected_strike', 'N/A'):<7} {trade.get('days_to_expiry', 0):<4} "
              f"₹{entry_premium:<7.0f} ₹{exit_premium:<7.0f} "
              f"{entry_delta:<8.3f} {exit_delta:<8.3f} {gamma:<7.4f} ₹{theta:<6.0f} "
              f"{exit_emoji}{exit_reason:<9} "
              f"₹{trade['total_profit']:>+6,.0f} ({trade.get('profit_pct', 0):+.1f}%)")
    
    print("\n" + "=" * 80)
    print("NOTE: This is a SIMULATION using simplified options pricing model")
    print("Real options trading involves: IV, Theta, Gamma, Vega, and liquidity")
    print("Use this for strategy understanding, not exact P&L prediction")
    print("=" * 80)
    
    return all_results, breakout_df


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("       BANK NIFTY OPTIONS - OPENING BAR BREAKOUT STRATEGY")
    print("=" * 80)
    
    # Lot size selection
    print("\n📦 Bank Nifty Lot Size:")
    print("   Current (Oct 2024 onwards): 15")
    print("   Previous (before Oct 2024): 25")
    lot_input = input("Enter lot size (default 15): ").strip()
    lot_size = int(lot_input) if lot_input.isdigit() else 15
    
    # Choose expiry type
    print("\n📅 Select Expiry Type:")
    print("1. WEEKLY (Wednesdays) - Recommended")
    print("2. MONTHLY (Last Thursday)")
    choice = input("Enter choice (1/2) or press Enter for WEEKLY: ").strip()
    
    expiry_type = "MONTHLY" if choice == "2" else "WEEKLY"
    
    # Run backtest
    print(f"\n🚀 Running backtest with {expiry_type} expiry and lot size {lot_size}...\n")
    results, breakouts = run_banknifty_backtest(days=300, expiry_type=expiry_type, lot_size=lot_size)
    
    print("\n💡 Strategy Insights:")
    print("- Opening bar breakout works best in trending markets")
    print("- ATM options offer best balance of risk/reward")
    print("- OTM options need stronger moves but offer higher returns")
    print("- Weekly options have less theta decay than monthly")
    print("- Avoid trading on expiry day (high theta decay)")
    print("- Consider adding filters: trend, volatility, gap analysis")
    
    print("\n⚠️  Important Notes:")
    print(f"- Results shown are for LOT SIZE: {lot_size}")
    print(f"- Bank Nifty lot size changed from 25 to 15 in Oct 2024")
    print(f"- For historical accuracy, use lot_size=25 for trades before Oct 2024")
    print(f"- Capital required: ~₹{50000 * (lot_size/15):,.0f} - ₹{100000 * (lot_size/15):,.0f} per lot")
