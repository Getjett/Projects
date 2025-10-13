"""
Data fetcher for market data from Kite Connect API
Handles caching and data preparation for backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from kiteconnect import KiteConnect
    import config
    
    class DataFetcher:
        """Fetch market data from Kite Connect API"""
        
        def __init__(self):
            self.kite = None
            self._initialize_kite()
        
        def _initialize_kite(self):
            """Initialize Kite Connect client"""
            try:
                self.kite = KiteConnect(api_key=config.KITE_API_KEY)
                if config.KITE_ACCESS_TOKEN:
                    self.kite.set_access_token(config.KITE_ACCESS_TOKEN)
            except Exception as e:
                print(f"Failed to initialize Kite Connect: {e}")
                self.kite = None
        
        async def get_historical_data(
            self, 
            symbol: str, 
            timeframe: str, 
            from_date: str, 
            to_date: str
        ) -> pd.DataFrame:
            """
            Fetch historical OHLCV data
            Returns pandas DataFrame with OHLCV columns
            """
            try:
                # Convert timeframe to Kite format
                kite_interval = self._convert_timeframe(timeframe)
                
                # Convert dates
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                
                # If Kite is not available, return sample data
                if not self.kite:
                    return self._generate_sample_data(symbol, from_dt, to_dt, timeframe)
                
                # Fetch from Kite API
                instrument_token = self._get_instrument_token(symbol)
                if not instrument_token:
                    # Fallback to sample data
                    return self._generate_sample_data(symbol, from_dt, to_dt, timeframe)
                
                records = self.kite.historical_data(
                    instrument_token=instrument_token,
                    from_date=from_dt,
                    to_date=to_dt,
                    interval=kite_interval
                )
                
                # Convert to DataFrame
                df = pd.DataFrame(records)
                if not df.empty:
                    df.set_index('date', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    
                    # Rename columns to standard format
                    df = df.rename(columns={
                        'open': 'open',
                        'high': 'high', 
                        'low': 'low',
                        'close': 'close',
                        'volume': 'volume'
                    })
                
                return df
                
            except Exception as e:
                print(f"Error fetching data from Kite: {e}")
                # Fallback to sample data
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                return self._generate_sample_data(symbol, from_dt, to_dt, timeframe)
        
        def _convert_timeframe(self, timeframe: str) -> str:
            """Convert timeframe to Kite format"""
            conversion = {
                "1m": "minute",
                "5m": "5minute", 
                "15m": "15minute",
                "30m": "30minute",
                "1h": "60minute",
                "1D": "day",
                "1W": "week"
            }
            return conversion.get(timeframe, "day")
        
        def _get_instrument_token(self, symbol: str) -> Optional[str]:
            """Get instrument token for symbol"""
            try:
                if not self.kite:
                    return None
                
                # This is a simplified version - in production you'd cache instruments
                instruments = self.kite.instruments("NSE")
                for instrument in instruments:
                    if instrument['tradingsymbol'] == symbol:
                        return instrument['instrument_token']
                
                return None
            except Exception as e:
                print(f"Error getting instrument token: {e}")
                return None
        
        def _generate_sample_data(
            self, 
            symbol: str, 
            from_dt: datetime, 
            to_dt: datetime, 
            timeframe: str
        ) -> pd.DataFrame:
            """Generate sample market data for testing"""
            print(f"Generating sample data for {symbol} from {from_dt} to {to_dt}")
            
            # Calculate number of periods
            if timeframe == "1m":
                freq = "1T"
                # Market hours: 9:15 to 15:30 (6.25 hours = 375 minutes)
                periods_per_day = 375
            elif timeframe == "5m":
                freq = "5T"
                periods_per_day = 75
            elif timeframe == "15m":
                freq = "15T"
                periods_per_day = 25
            elif timeframe == "1h":
                freq = "1H"
                periods_per_day = 6
            else:  # 1D
                freq = "1D"
                periods_per_day = 1
            
            # Create date range (market days only)
            date_range = pd.bdate_range(start=from_dt, end=to_dt, freq='B')
            
            # Generate time series
            timestamps = []
            if timeframe in ["1m", "5m", "15m", "1h"]:
                # Intraday data
                for date in date_range:
                    # Market hours: 9:15 to 15:30
                    market_start = date.replace(hour=9, minute=15)
                    market_end = date.replace(hour=15, minute=30)
                    
                    if timeframe == "1m":
                        times = pd.date_range(market_start, market_end, freq=freq)
                    else:
                        times = pd.date_range(market_start, market_end, freq=freq)
                    
                    timestamps.extend(times)
            else:
                # Daily data
                timestamps = date_range
            
            if len(timestamps) == 0:
                # Return empty DataFrame with correct structure
                return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
            
            # Generate realistic price data
            num_points = len(timestamps)
            base_price = 1000 + hash(symbol) % 1000  # Base price between 1000-2000
            
            # Random walk with some trend and volatility
            np.random.seed(hash(symbol) % 10000)  # Deterministic but different per symbol
            
            returns = np.random.normal(0.0001, 0.02, num_points)  # Small positive drift with 2% volatility
            price_series = base_price * np.exp(np.cumsum(returns))
            
            # Generate OHLCV data
            data = []
            for i, timestamp in enumerate(timestamps):
                if i == 0:
                    open_price = price_series[i]
                else:
                    open_price = data[-1]['close']  # Previous close
                
                close_price = price_series[i]
                
                # Add some intrabar volatility
                volatility = abs(np.random.normal(0, 0.01)) + 0.005  # Min 0.5% volatility
                high_price = max(open_price, close_price) * (1 + volatility)
                low_price = min(open_price, close_price) * (1 - volatility)
                
                # Volume (random but reasonable)
                volume = int(np.random.uniform(50000, 500000))
                
                data.append({
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
            
            # Create DataFrame
            df = pd.DataFrame(data, index=timestamps)
            df.index.name = 'timestamp'
            
            print(f"Generated {len(df)} data points for {symbol}")
            
            return df

except ImportError as e:
    print(f"Import error: {e}")
    print("Kite Connect or config not available, using sample data only")
    
    class DataFetcher:
        """Fallback data fetcher with sample data only"""
        
        def __init__(self):
            pass
        
        async def get_historical_data(
            self, 
            symbol: str, 
            timeframe: str, 
            from_date: str, 
            to_date: str
        ) -> pd.DataFrame:
            """Generate sample data only"""
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            return self._generate_sample_data(symbol, from_dt, to_dt, timeframe)
        
        def _generate_sample_data(
            self, 
            symbol: str, 
            from_dt: datetime, 
            to_dt: datetime, 
            timeframe: str
        ) -> pd.DataFrame:
            """Generate sample market data for testing"""
            print(f"Generating sample data for {symbol} from {from_dt} to {to_dt}")
            
            # Calculate number of periods
            if timeframe == "1m":
                freq = "1T"
            elif timeframe == "5m":
                freq = "5T"
            elif timeframe == "15m":
                freq = "15T"
            elif timeframe == "1h":
                freq = "1H"
            else:  # 1D
                freq = "1D"
            
            # Create date range
            if timeframe == "1D":
                timestamps = pd.bdate_range(start=from_dt, end=to_dt, freq='B')
            else:
                # Intraday: limit to reasonable size
                days = (to_dt - from_dt).days
                if days > 30:  # Limit intraday data to 30 days max for performance
                    to_dt = from_dt + timedelta(days=30)
                
                timestamps = pd.bdate_range(start=from_dt, end=to_dt, freq='B')
                
                # Generate intraday timestamps (simplified)
                intraday_timestamps = []
                for date in timestamps[:min(10, len(timestamps))]:  # Limit to 10 days for demo
                    market_start = date.replace(hour=9, minute=15)
                    market_end = date.replace(hour=15, minute=30)
                    times = pd.date_range(market_start, market_end, freq=freq)
                    intraday_timestamps.extend(times[:50])  # Limit per day
                
                timestamps = intraday_timestamps
            
            if len(timestamps) == 0:
                return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
            
            # Generate realistic price data
            num_points = len(timestamps)
            base_price = 1000 + hash(symbol) % 1000
            
            np.random.seed(hash(symbol) % 10000)
            
            # Generate price series with trend
            trend = np.linspace(0, 0.1, num_points)  # 10% upward trend over period
            volatility = np.random.normal(0, 0.02, num_points)
            price_multipliers = np.exp(trend + np.cumsum(volatility))
            
            prices = base_price * price_multipliers
            
            # Generate OHLCV
            data = []
            for i in range(num_points):
                if i == 0:
                    open_price = prices[i]
                else:
                    open_price = data[-1]['close']
                
                close_price = prices[i]
                
                # Intrabar range
                range_pct = abs(np.random.normal(0, 0.01)) + 0.002
                high_price = max(open_price, close_price) * (1 + range_pct)
                low_price = min(open_price, close_price) * (1 - range_pct)
                
                volume = int(np.random.uniform(10000, 100000))
                
                data.append({
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
            
            df = pd.DataFrame(data, index=timestamps)
            df.index.name = 'timestamp'
            
            print(f"Generated {len(df)} sample data points for {symbol}")
            return df