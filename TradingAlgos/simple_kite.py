"""
Simple Kite Connect API Script
Based on official example code - simplified and ready to use
"""

import logging
from kiteconnect import KiteConnect
import config

# Disable debug logging from urllib3 and requests
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# Set up clean logging - only show INFO and above
logging.basicConfig(level=logging.INFO, format='%(message)s')

def connect_to_kite():
    """Simple function to connect to Kite API"""
    
    print("🚀 Connecting to Kite API...")
    
    # Initialize KiteConnect
    kite = KiteConnect(api_key=config.KITE_API_KEY)
    
    # Check if we have access token
    if config.KITE_ACCESS_TOKEN and config.KITE_ACCESS_TOKEN != "None":
        print("✅ Using saved access token")
        kite.set_access_token(config.KITE_ACCESS_TOKEN)
        
        # Test connection
        try:
            profile = kite.profile()
            print(f"✅ Connected! User: {profile['user_name']}")
            return kite
        except:
            print("❌ Saved token expired, need new token")
    
    # Get new access token
    print("\n🔗 Get login URL and request token:")
    login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={config.KITE_API_KEY}"
    print(f"Visit: {login_url}")
    
    request_token = input("Enter request_token from redirect URL: ").strip()
    
    if request_token:
        try:
            # Generate session
            data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
            kite.set_access_token(data["access_token"])
            
            print(f"✅ Connected! Access token: {data['access_token'][:10]}...")
            
            # Save token
            save = input("Save token to config? (y/n): ")
            if save.lower() == 'y':
                with open('config.py', 'r') as f:
                    content = f.read()
                content = content.replace(
                    f'KITE_ACCESS_TOKEN = "{config.KITE_ACCESS_TOKEN}"',
                    f'KITE_ACCESS_TOKEN = "{data["access_token"]}"'
                )
                with open('config.py', 'w') as f:
                    f.write(content)
                print("✅ Token saved!")
            
            return kite
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None
    
    return None

def main():
    """Main function - demonstrates all Kite API features"""
    
    # Connect to API
    kite = connect_to_kite()
    if not kite:
        print("❌ Failed to connect to Kite API")
        return
    
    print("\n" + "="*50)
    print("🧪 TESTING KITE API FUNCTIONS")
    print("="*50)
    
    # 1. Get profile
    try:
        profile = kite.profile()
        print(f"\n👤 Profile: {profile['user_name']} ({profile['user_id']})")
        logging.info(f"Profile fetched: {profile['user_name']}")
    except Exception as e:
        print(f"❌ Profile error: {e}")
    
    # 2. Fetch all orders
    try:
        orders = kite.orders()
        print(f"\n📋 Orders: {len(orders)} orders found")
        
        if orders:
            recent = orders[-1]
            print(f"   Latest: {recent.get('tradingsymbol')} - {recent.get('status')}")
        
        logging.info(f"Orders fetched: {len(orders)}")
    except Exception as e:
        print(f"❌ Orders error: {e}")
    
    # 3. Get instruments
    try:
        print(f"\n📊 Fetching NSE instruments...")
        instruments = kite.instruments("NSE")
        print(f"✅ NSE Instruments: {len(instruments):,} found")
        
        # Find INFY
        infy = next((i for i in instruments if i['tradingsymbol'] == 'INFY'), None)
        if infy:
            print(f"   📈 INFY found: {infy['name']}")
        
        logging.info(f"Instruments fetched: {len(instruments)}")
    except Exception as e:
        print(f"❌ Instruments error: {e}")
    
    # 4. Get mutual fund instruments
    try:
        print(f"\n💰 Fetching MF instruments...")
        mf_instruments = kite.mf_instruments()
        print(f"✅ MF Instruments: {len(mf_instruments):,} found")
        logging.info(f"MF Instruments fetched: {len(mf_instruments)}")
    except Exception as e:
        print(f"❌ MF Instruments error: {e}")
    
    # 5. Get live quotes
    try:
        quotes = kite.quote(["NSE:INFY", "NSE:RELIANCE"])
        print(f"\n📊 Live Quotes:")
        for symbol, data in quotes.items():
            name = symbol.split(':')[1]
            price = data['last_price']
            change = data.get('net_change', 0)
            print(f"   {name}: ₹{price} (₹{change:+.2f})")
    except Exception as e:
        print(f"❌ Quotes error: {e}")
    
    # 6. ORDER PLACEMENT (COMMENTED FOR SAFETY)
    print(f"\n⚠️  ORDER EXAMPLES (COMMENTED FOR SAFETY):")
    print("""
    # STOCK ORDER EXAMPLE:
    try:
        order_id = kite.place_order(
            tradingsymbol="INFY",
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=1,
            variety=kite.VARIETY_REGULAR,  # Changed from AMO
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_MIS,  # Changed to MIS for lower margin
            validity=kite.VALIDITY_DAY
        )
        print(f"✅ Order placed. ID: {order_id}")
        logging.info(f"Order placed. ID: {order_id}")
    except Exception as e:
        print(f"❌ Order failed: {e}")
        logging.error(f"Order failed: {e}")
    
    # MUTUAL FUND ORDER EXAMPLE:
    try:
        mf_order_id = kite.place_mf_order(
            tradingsymbol="INF090I01239",
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            amount=5000,
            tag="test_order"
        )
        print(f"✅ MF Order placed. ID: {mf_order_id}")
        
        # Cancel MF order
        kite.cancel_mf_order(order_id=mf_order_id)
        print(f"✅ MF Order cancelled: {mf_order_id}")
        
    except Exception as e:
        print(f"❌ MF Order failed: {e}")
    """)
    
    # 7. Account info
    try:
        margins = kite.margins()
        equity_cash = margins['equity']['available']['cash']
        print(f"\n💰 Available Cash: ₹{equity_cash:,.2f}")
    except Exception as e:
        print(f"❌ Margins error: {e}")
    
    print(f"\n✅ API testing complete!")
    print(f"💡 To place real orders, uncomment the order code above")

# Quick functions for direct use
def get_quote(symbol):
    """Quick function to get live quote"""
    kite = connect_to_kite()
    if kite:
        try:
            quote = kite.quote([f"NSE:{symbol}"])
            return quote[f"NSE:{symbol}"]["last_price"]
        except:
            return None
    return None

def get_balance():
    """Quick function to get account balance"""
    kite = connect_to_kite()
    if kite:
        try:
            margins = kite.margins()
            return margins['equity']['available']['cash']
        except:
            return None
    return None

if __name__ == "__main__":
    main()
    
    # Quick test examples
    print(f"\n🔍 Quick Tests:")
    print(f"RELIANCE Price: ₹{get_quote('RELIANCE')}")
    print(f"Account Balance: ₹{get_balance():,.2f}" if get_balance() else "Balance: Error")