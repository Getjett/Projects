"""
Trading System - Lightweight Version
Live Trading with API Connection & Token Management
"""

import logging
from kiteconnect import KiteConnect
import config

# Suppress unnecessary logging
for logger in ['urllib3', 'requests']:
    logging.getLogger(logger).setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format='%(message)s')


# ============================================================================
# SECTION 1: KITE API CONNECTION & TOKEN MANAGEMENT
# ============================================================================

def connect_to_kite():
    """Connect to Kite API with saved or new token"""
    print(">> Connecting to Kite API...")
    kite = KiteConnect(api_key=config.KITE_API_KEY)
    
    # Try saved token first
    if config.KITE_ACCESS_TOKEN and config.KITE_ACCESS_TOKEN != "None":
        print(">> Using saved access token")
        kite.set_access_token(config.KITE_ACCESS_TOKEN)
        
        try:
            profile = kite.profile()
            print(f"✅ Connected! User: {profile['user_name']}")
            return kite
        except:
            print("❌ Saved token expired, need new token")
    
    # Get new token
    print("\n🔗 Get login URL and request token:")
    login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={config.KITE_API_KEY}"
    print(f"Visit: {login_url}")
    
    request_token = input("Enter request_token from redirect URL: ").strip()
    
    if request_token:
        try:
            data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
            kite.set_access_token(data["access_token"])
            print(f"✅ Connected! Access token: {data['access_token'][:10]}...")
            
            # Save token
            save = input("Save token to config? (y/n): ")
            if save.lower() == 'y':
                update_config_token(data["access_token"])
                print("✅ Token saved!")
            
            return kite
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None
    
    return None


def update_config_token(new_token):
    """Update config.py with new access token"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('KITE_ACCESS_TOKEN'):
                lines[i] = f'KITE_ACCESS_TOKEN = "{new_token}"'
                break
        
        with open('config.py', 'w') as f:
            f.write('\n'.join(lines))
        
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False


def generate_fresh_token():
    """Generate fresh access token (when token expires)"""
    print("=" * 60)
    print("🔧 KITE API TOKEN GENERATOR")
    print("=" * 60)
    
    kite = KiteConnect(api_key=config.KITE_API_KEY)
    login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={config.KITE_API_KEY}"
    
    print(f"🔗 Login URL: {login_url}")
    print("\nSteps:")
    print("1. Visit the URL above")
    print("2. Login and authorize")
    print("3. Copy request_token from redirect URL")
    print("4. Paste below (expires in 2-3 minutes!)\n")
    
    request_token = input("🔑 Enter request_token: ").strip()
    
    if request_token:
        try:
            data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
            access_token = data["access_token"]
            
            kite.set_access_token(access_token)
            profile = kite.profile()
            
            print(f"✅ Token verified! User: {profile['user_name']}")
            update_config_token(access_token)
            return access_token
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    return None


# ============================================================================
# SECTION 2: LIVE TRADING FUNCTIONS
# ============================================================================

def get_quote(symbol):
    """Get live quote for a symbol"""
    kite = connect_to_kite()
    if kite:
        try:
            quote = kite.quote([f"NSE:{symbol}"])
            return quote[f"NSE:{symbol}"]["last_price"]
        except:
            return None
    return None


def get_multiple_quotes(symbols):
    """Get live quotes for multiple symbols"""
    kite = connect_to_kite()
    if kite:
        try:
            symbols_with_exchange = [f"NSE:{s}" for s in symbols]
            quotes = kite.quote(symbols_with_exchange)
            
            result = {}
            for key, data in quotes.items():
                symbol = key.split(':')[1]
                result[symbol] = {
                    'price': data['last_price'],
                    'change': data.get('net_change', 0),
                    'change_pct': data.get('change_percent', 0)
                }
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None
    return None


def get_balance():
    """Get account balance"""
    kite = connect_to_kite()
    if kite:
        try:
            margins = kite.margins()
            return margins['equity']['available']['cash']
        except:
            return None
    return None


def get_margins():
    """Get detailed margin information"""
    kite = connect_to_kite()
    if kite:
        try:
            margins = kite.margins()
            return {
                'cash': margins['equity']['available']['cash'],
                'collateral': margins['equity']['available']['collateral'],
                'intraday_payin': margins['equity']['available']['intraday_payin'],
                'used': margins['equity']['utilised']['debits']
            }
        except:
            return None
    return None


def get_profile():
    """Get user profile"""
    kite = connect_to_kite()
    if kite:
        try:
            return kite.profile()
        except:
            return None
    return None


def get_orders():
    """Get all orders"""
    kite = connect_to_kite()
    if kite:
        try:
            return kite.orders()
        except:
            return None
    return None


def get_positions():
    """Get all positions"""
    kite = connect_to_kite()
    if kite:
        try:
            return kite.positions()
        except:
            return None
    return None


def get_holdings():
    """Get all holdings"""
    kite = connect_to_kite()
    if kite:
        try:
            return kite.holdings()
        except:
            return None
    return None


def place_order(symbol, quantity, transaction_type="BUY", order_type="MARKET", product="MIS", price=None):
    """
    Place an order (USE WITH CAUTION!)
    
    Args:
        symbol: Stock symbol (e.g., "INFY")
        quantity: Number of shares
        transaction_type: "BUY" or "SELL"
        order_type: "MARKET", "LIMIT", "SL", "SL-M"
        product: "MIS" (intraday), "CNC" (delivery), "NRML" (normal)
        price: Required for LIMIT orders
    """
    kite = connect_to_kite()
    if kite:
        try:
            order_params = {
                'tradingsymbol': symbol,
                'exchange': kite.EXCHANGE_NSE,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'variety': kite.VARIETY_REGULAR,
                'order_type': order_type,
                'product': product,
                'validity': kite.VALIDITY_DAY
            }
            
            # Add price for limit orders
            if order_type == "LIMIT" and price:
                order_params['price'] = price
            
            order_id = kite.place_order(**order_params)
            print(f"✅ Order placed. ID: {order_id}")
            return order_id
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None
    return None


def cancel_order(order_id, variety="regular"):
    """Cancel an order"""
    kite = connect_to_kite()
    if kite:
        try:
            kite.cancel_order(variety=variety, order_id=order_id)
            print(f"✅ Order {order_id} cancelled")
            return True
        except Exception as e:
            print(f"❌ Cancel failed: {e}")
            return False
    return False


def modify_order(order_id, quantity=None, price=None, order_type=None, variety="regular"):
    """Modify an existing order"""
    kite = connect_to_kite()
    if kite:
        try:
            params = {'variety': variety, 'order_id': order_id}
            
            if quantity:
                params['quantity'] = quantity
            if price:
                params['price'] = price
            if order_type:
                params['order_type'] = order_type
            
            kite.modify_order(**params)
            print(f"✅ Order {order_id} modified")
            return True
        except Exception as e:
            print(f"❌ Modify failed: {e}")
            return False
    return False


# ============================================================================
# SECTION 3: TESTING & UTILITIES
# ============================================================================

def test_api():
    """Test all Kite API features"""
    kite = connect_to_kite()
    if not kite:
        print("❌ Failed to connect")
        return
    
    print("\n" + "="*50)
    print("🧪 TESTING KITE API")
    print("="*50)
    
    # Profile
    try:
        profile = kite.profile()
        print(f"\n👤 User: {profile['user_name']} ({profile['user_id']})")
        print(f"📧 Email: {profile['email']}")
    except Exception as e:
        print(f"❌ Profile error: {e}")
    
    # Orders
    try:
        orders = kite.orders()
        print(f"\n📋 Orders: {len(orders)} found")
        if orders:
            recent = orders[-1]
            print(f"   Latest: {recent.get('tradingsymbol')} - {recent.get('status')}")
    except Exception as e:
        print(f"❌ Orders error: {e}")
    
    # Positions
    try:
        positions = kite.positions()
        net_positions = positions['net']
        print(f"\n📊 Positions: {len(net_positions)} open")
        for pos in net_positions[:3]:  # Show first 3
            print(f"   {pos['tradingsymbol']}: {pos['quantity']} @ ₹{pos['average_price']}")
    except Exception as e:
        print(f"❌ Positions error: {e}")
    
    # Holdings
    try:
        holdings = kite.holdings()
        print(f"\n💼 Holdings: {len(holdings)} stocks")
        for holding in holdings[:3]:  # Show first 3
            print(f"   {holding['tradingsymbol']}: {holding['quantity']} @ ₹{holding['average_price']}")
    except Exception as e:
        print(f"❌ Holdings error: {e}")
    
    # Quotes
    try:
        quotes = kite.quote(["NSE:INFY", "NSE:RELIANCE", "NSE:TCS"])
        print(f"\n📈 Live Quotes:")
        for symbol, data in quotes.items():
            name = symbol.split(':')[1]
            print(f"   {name}: ₹{data['last_price']} ({data.get('net_change', 0):+.2f})")
    except Exception as e:
        print(f"❌ Quotes error: {e}")
    
    # Balance
    try:
        margins = kite.margins()
        cash = margins['equity']['available']['cash']
        used = margins['equity']['utilised']['debits']
        print(f"\n💰 Available Cash: ₹{cash:,.2f}")
        print(f"💸 Margin Used: ₹{used:,.2f}")
    except Exception as e:
        print(f"❌ Margins error: {e}")
    
    print(f"\n✅ API testing complete!")


def show_watchlist(symbols):
    """Display a watchlist of symbols with live prices"""
    quotes = get_multiple_quotes(symbols)
    
    if quotes:
        print("\n" + "=" * 60)
        print("                    WATCHLIST")
        print("=" * 60)
        print(f"{'Symbol':<12} {'Price':>10} {'Change':>10} {'Change %':>10}")
        print("-" * 60)
        
        for symbol, data in quotes.items():
            print(f"{symbol:<12} ₹{data['price']:>9.2f} ₹{data['change']:>9.2f} {data['change_pct']:>9.2f}%")
        
        print("=" * 60)
    else:
        print("❌ Failed to fetch watchlist")


def get_instruments(exchange="NSE"):
    """Get all instruments for an exchange"""
    kite = connect_to_kite()
    if kite:
        try:
            return kite.instruments(exchange)
        except:
            return None
    return None


def search_instrument(keyword, exchange="NSE"):
    """Search for instruments by keyword"""
    instruments = get_instruments(exchange)
    if instruments:
        matches = [i for i in instruments if keyword.upper() in i['tradingsymbol'].upper()]
        return matches[:10]  # Return top 10 matches
    return None


# ============================================================================
# SECTION 4: INTERACTIVE MENU
# ============================================================================

def main_menu():
    """Interactive menu for all functions"""
    while True:
        print("\n" + "=" * 60)
        print("           TRADING SYSTEM - MAIN MENU")
        print("=" * 60)
        print("\n📡 CONNECTION")
        print("1. Connect to Kite API")
        print("2. Generate Fresh Token")
        print("3. Test API Functions")
        
        print("\n📊 LIVE DATA")
        print("4. Get Live Quote")
        print("5. Show Watchlist")
        print("6. Search Instrument")
        
        print("\n💰 ACCOUNT")
        print("7. Check Balance")
        print("8. View Margins")
        print("9. View Orders")
        print("10. View Positions")
        print("11. View Holdings")
        
        print("\n📝 TRADING (USE WITH CAUTION)")
        print("12. Place Order")
        print("13. Cancel Order")
        
        print("\n0. Exit")
        
        choice = input("\n➤ Enter choice: ").strip()
        
        if choice == "1":
            connect_to_kite()
            
        elif choice == "2":
            generate_fresh_token()
            
        elif choice == "3":
            test_api()
            
        elif choice == "4":
            symbol = input("Enter symbol (e.g., RELIANCE): ").strip().upper()
            price = get_quote(symbol)
            print(f"{symbol}: ₹{price}" if price else "Failed to fetch quote")
            
        elif choice == "5":
            symbols_input = input("Enter symbols (comma-separated): ").strip().upper()
            symbols = [s.strip() for s in symbols_input.split(",")]
            show_watchlist(symbols)
            
        elif choice == "6":
            keyword = input("Enter search keyword: ").strip()
            matches = search_instrument(keyword)
            if matches:
                print(f"\nFound {len(matches)} matches:")
                for i, inst in enumerate(matches, 1):
                    print(f"{i}. {inst['tradingsymbol']} - {inst['name']}")
            else:
                print("No matches found")
                
        elif choice == "7":
            balance = get_balance()
            print(f"💰 Balance: ₹{balance:,.2f}" if balance else "Failed to fetch balance")
            
        elif choice == "8":
            margins = get_margins()
            if margins:
                print(f"\n💰 Cash: ₹{margins['cash']:,.2f}")
                print(f"💎 Collateral: ₹{margins['collateral']:,.2f}")
                print(f"💸 Used: ₹{margins['used']:,.2f}")
            else:
                print("Failed to fetch margins")
                
        elif choice == "9":
            orders = get_orders()
            if orders:
                print(f"\n📋 Found {len(orders)} orders")
                for order in orders[-10:]:  # Show last 10
                    print(f"  {order.get('order_id')}: {order.get('tradingsymbol')} - {order.get('status')}")
            else:
                print("No orders or failed to fetch")
                
        elif choice == "10":
            positions = get_positions()
            if positions:
                net = positions['net']
                print(f"\n📊 Found {len(net)} positions")
                for pos in net:
                    print(f"  {pos['tradingsymbol']}: {pos['quantity']} @ ₹{pos['average_price']}")
            else:
                print("No positions or failed to fetch")
                
        elif choice == "11":
            holdings = get_holdings()
            if holdings:
                print(f"\n💼 Found {len(holdings)} holdings")
                for holding in holdings:
                    pnl = (holding['last_price'] - holding['average_price']) * holding['quantity']
                    print(f"  {holding['tradingsymbol']}: {holding['quantity']} @ ₹{holding['average_price']} (P&L: ₹{pnl:+.2f})")
            else:
                print("No holdings or failed to fetch")
                
        elif choice == "12":
            print("\n⚠️  PLACE ORDER - USE WITH CAUTION!")
            symbol = input("Symbol: ").strip().upper()
            quantity = int(input("Quantity: ").strip())
            trans_type = input("Transaction (BUY/SELL): ").strip().upper()
            order_type = input("Order Type (MARKET/LIMIT): ").strip().upper()
            product = input("Product (MIS/CNC): ").strip().upper()
            
            price = None
            if order_type == "LIMIT":
                price = float(input("Limit Price: ").strip())
            
            confirm = input(f"\nConfirm {trans_type} {quantity} {symbol} @ {order_type} in {product}? (yes/no): ")
            if confirm.lower() == "yes":
                place_order(symbol, quantity, trans_type, order_type, product, price)
            else:
                print("Order cancelled")
                
        elif choice == "13":
            order_id = input("Enter Order ID to cancel: ").strip()
            confirm = input(f"Confirm cancel order {order_id}? (yes/no): ")
            if confirm.lower() == "yes":
                cancel_order(order_id)
            else:
                print("Cancellation aborted")
                
        elif choice == "0":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice!")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("         TRADING SYSTEM - LIGHTWEIGHT VERSION")
    print("=" * 60)
    print("\nRun main_menu() for interactive menu")
    print("Or use individual functions directly")
    
    # Uncomment to start interactive menu automatically
    # main_menu()
    
    # Quick connection test
    print("\n🔍 Quick Status Check:")
    profile = get_profile()
    if profile:
        print(f"✅ Connected! User: {profile['user_name']}")
        balance = get_balance()
        if balance:
            print(f"💰 Balance: ₹{balance:,.2f}")
    else:
        print("❌ Not connected. Run connect_to_kite() or main_menu()")
