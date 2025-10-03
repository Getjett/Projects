"""
Kite API Connection Utility
This script helps you reconnect to Kite API when the access token expires
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from simple_kite import connect_to_kite
import config

def refresh_kite_connection():
    """
    Refresh Kite API connection and update config with new access token
    """
    print("=" * 60)
    print("🔄 KITE API CONNECTION REFRESH")
    print("=" * 60)
    
    try:
        # Try to connect using existing token first
        kite = connect_to_kite()
        
        if kite:
            print("✅ Connection successful!")
            
            # Test the connection
            try:
                profile = kite.profile()
                print(f"👤 User: {profile['user_name']}")
                print(f"📧 Email: {profile['email']}")
                print("🎯 API Status: CONNECTED")
                return True
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
                return False
        else:
            print("❌ Failed to establish connection")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def update_access_token_in_config(new_token):
    """
    Update the access token in config.py file
    """
    try:
        # Read current config file
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Find and replace the access token line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('KITE_ACCESS_TOKEN'):
                lines[i] = f'KITE_ACCESS_TOKEN = "{new_token}"'
                break
        
        # Write back to file
        with open('config.py', 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Config file updated with new access token")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def main():
    """
    Main function to refresh Kite connection
    """
    print("Starting Kite API connection refresh...")
    
    # Check current connection status
    success = refresh_kite_connection()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ KITE API IS NOW CONNECTED!")
        print("✅ Your trading platform should show 'Connected' status")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ KITE API CONNECTION FAILED")
        print("📋 Manual steps:")
        print("1. Check your API credentials in config.py")
        print("2. Ensure you have active Kite Connect subscription")
        print("3. Try running simple_kite.py directly for detailed setup")
        print("=" * 60)

if __name__ == "__main__":
    main()