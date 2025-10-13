"""
Market Data API routes for fetching and serving historical market data
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import pandas as pd

from models.schemas import MarketDataRequest, MarketDataResponse, CandleData
from core.data_fetcher import DataFetcher

router = APIRouter()
data_fetcher = DataFetcher()


@router.get("/candles")
async def get_market_data(
    symbol: str,
    timeframe: str,
    from_date: str,
    to_date: str
):
    """
    Fetch historical market data for a symbol
    Returns OHLCV data for the specified period
    """
    try:
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W']
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timeframe. Must be one of: {valid_timeframes}"
            )
        
        # Validate dates
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        if from_dt >= to_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date must be before to_date"
            )
        
        # Fetch data
        df = await data_fetcher.get_historical_data(symbol, timeframe, from_date, to_date)
        
        if df.empty:
            return MarketDataResponse(
                symbol=symbol,
                timeframe=timeframe,
                candles=[]
            )
        
        # Convert to response format
        candles = []
        for timestamp, row in df.iterrows():
            candle = CandleData(
                timestamp=timestamp,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            )
            candles.append(candle)
        
        return MarketDataResponse(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )


@router.get("/symbols")
async def get_available_symbols():
    """Get list of available trading symbols"""
    # In production, this would fetch from Kite instruments
    # For now, return common NSE symbols
    symbols = [
        {"symbol": "RELIANCE", "name": "Reliance Industries Limited", "exchange": "NSE"},
        {"symbol": "TCS", "name": "Tata Consultancy Services Limited", "exchange": "NSE"},
        {"symbol": "INFY", "name": "Infosys Limited", "exchange": "NSE"},
        {"symbol": "HDFC", "name": "HDFC Limited", "exchange": "NSE"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Limited", "exchange": "NSE"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Limited", "exchange": "NSE"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Limited", "exchange": "NSE"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel Limited", "exchange": "NSE"},
        {"symbol": "ITC", "name": "ITC Limited", "exchange": "NSE"},
        {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE"},
        {"symbol": "BANKNIFTY", "name": "Bank Nifty Index", "exchange": "NSE"},
        {"symbol": "NIFTY", "name": "Nifty 50 Index", "exchange": "NSE"}
    ]
    
    return {"symbols": symbols}


@router.get("/timeframes")
async def get_available_timeframes():
    """Get list of supported timeframes"""
    timeframes = [
        {"value": "1m", "label": "1 Minute", "intraday": True},
        {"value": "5m", "label": "5 Minutes", "intraday": True},
        {"value": "15m", "label": "15 Minutes", "intraday": True},
        {"value": "30m", "label": "30 Minutes", "intraday": True},
        {"value": "1h", "label": "1 Hour", "intraday": True},
        {"value": "4h", "label": "4 Hours", "intraday": True},
        {"value": "1D", "label": "1 Day", "intraday": False},
        {"value": "1W", "label": "1 Week", "intraday": False}
    ]
    
    return {"timeframes": timeframes}