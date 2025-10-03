"""
Configuration file for Kite Connect API
Store your API credentials here or use environment variables for better security.

Get your credentials from: https://developers.kite.trade/
1. Create a new Kite Connect app
2. Note down your API Key and API Secret
3. Set up redirect URL (can be any valid URL you control)
4. Update the values below
"""

# =============================================================================
# KITE CONNECT API CREDENTIALS
# =============================================================================
# Get these from: https://developers.kite.trade/
KITE_API_KEY = "vzjdzah3bi95wlv1"
KITE_API_SECRET = "8wddbiym6c3mpt0eg59a15fez8gzv26v"

# Optional: Saved access token (if you want to reuse without login each time)
# Note: Access tokens expire at 6 AM next day (regulatory requirement)
KITE_ACCESS_TOKEN = "VI3zxnLzf5y7U95wJZZFvi1yblfsry1O"


# Redirect URL (set this in your Kite Connect app settings)
REDIRECT_URL = "http://127.0.0.1:8000"  # Replace with your actual redirect URL

# =============================================================================
# TRADING CONFIGURATION
# =============================================================================
DEFAULT_EXCHANGE = "NSE"
DEFAULT_PRODUCT = "MIS"  # MIS for intraday, CNC for delivery, NRML for normal
DEFAULT_ORDER_TYPE = "MARKET"  # MARKET, LIMIT, SL, SL-M

# Order Varieties
DEFAULT_VARIETY = "regular"  # regular, bo (bracket order), co (cover order), amo (after market order)

# Exchanges
EXCHANGES = {
    "NSE": "National Stock Exchange",
    "BSE": "Bombay Stock Exchange", 
    "NFO": "NSE Futures & Options",
    "BFO": "BSE Futures & Options",
    "CDS": "Currency Derivatives",
    "MCX": "Multi Commodity Exchange",
    "BCD": "BSE Currency Derivatives",
    "MF": "Mutual Funds"
}

# Products
PRODUCTS = {
    "CNC": "Cash and Carry (Delivery)",
    "MIS": "Margin Intraday Square-off",
    "NRML": "Normal (Overnight positions)"
}

# =============================================================================
# RISK MANAGEMENT
# =============================================================================
MAX_POSITION_SIZE = 100000  # Maximum position size in rupees
MAX_DAILY_LOSS = 5000      # Maximum daily loss limit in rupees
MAX_ORDERS_PER_DAY = 100   # Maximum orders per day
STOP_LOSS_PERCENTAGE = 2.0  # Default stop loss percentage

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "trading.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# =============================================================================
# DATA CONFIGURATION
# =============================================================================
# Data refresh intervals (in seconds)
QUOTE_REFRESH_INTERVAL = 1
POSITION_REFRESH_INTERVAL = 5
MARGIN_REFRESH_INTERVAL = 30

# Historical data settings
DEFAULT_CANDLE_INTERVAL = "minute"  # minute, 3minute, 5minute, 15minute, 30minute, day
MAX_HISTORICAL_DAYS = 60