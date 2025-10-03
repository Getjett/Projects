"""
Simple Kite API Token Generator
This script will help you get a fresh access token step by step
"""

from kiteconnect import KiteConnect
import config

def get_fresh_access_token():
    """
    Get a fresh access token from Kite API
    """
    print("=" * 60)
    print("🔧 KITE API TOKEN GENERATOR")
    print("=" * 60)
    
    # Initialize KiteConnect
    kite = KiteConnect(api_key=config.KITE_API_KEY)
    
    # Generate login URL
    login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={config.KITE_API_KEY}"
    
    print(f"📋 API Key: {config.KITE_API_KEY}")
    print(f"🔗 Login URL: {login_url}")
    print()
    print("🚨 IMPORTANT STEPS:")
    print("1. Click the login URL above")
    print("2. Login with your Zerodha credentials")
    print("3. You will be redirected to a URL like:")
    print("   http://127.0.0.1:8000/?request_token=XXXXX&action=login&status=success")
    print("4. Copy ONLY the request_token value (the part after request_token=)")
    print("5. Paste it below IMMEDIATELY (request tokens expire in 2-3 minutes)")
    print()
    
    # Get request token from user
    request_token = input("🔑 Enter request_token: ").strip()
    
    if not request_token:
        print("❌ No request token provided")
        return None
    
    try:
        print("🔄 Generating access token...")
        
        # Generate session with request token and API secret
        data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
        access_token = data["access_token"]
        
        print("✅ Success! Generated new access token")
        print(f"🔑 Access Token: {access_token}")
        
        # Test the access token
        kite.set_access_token(access_token)
        profile = kite.profile()
        
        print(f"✅ Token verified! User: {profile['user_name']}")
        print(f"📧 Email: {profile['email']}")
        
        # Update config file
        update_config_with_token(access_token)
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        print()
        print("🔍 Common issues:")
        print("- Request token expired (get a fresh one)")
        print("- Request token already used (get a fresh one)")
        print("- Wrong API credentials")
        print("- Network connectivity issues")
        return None

def update_config_with_token(access_token):
    """
    Update config.py with new access token
    """
    try:
        # Read current config
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the access token line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('KITE_ACCESS_TOKEN'):
                lines[i] = f'KITE_ACCESS_TOKEN = "{access_token}"'
                break
        
        # Write back to file
        with open('config.py', 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated config.py with new access token")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")

if __name__ == "__main__":
    print("Starting Kite API token generation...")
    token = get_fresh_access_token()
    
    if token:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! KITE API IS NOW CONNECTED!")
        print("🔄 You can now refresh your trading platform")
        print("💡 Access tokens expire daily at 6 AM IST")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED TO CONNECT")
        print("📞 Check your Kite Connect app settings:")
        print("   https://developers.kite.trade/")
        print("=" * 60)