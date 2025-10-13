"""
Chart visualization API routes
Provides endpoints for generating trading charts with backtest results
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from models.schemas import BacktestResult
from core.chart_visualization import ChartVisualization, get_chart_data
from core.backtest_engine import BacktestEngine
from core.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)
router = APIRouter()

# Chart visualization service
chart_viz = ChartVisualization()


@router.get("/chart/{symbol}", response_model=Dict[str, Any])
async def get_trading_chart(
    symbol: str,
    timeframe: str = Query("1d", regex="^(1m|5m|15m|30m|1h|4h|1d)$"),
    from_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    backtest_id: Optional[str] = Query(None, description="Include backtest results")
):
    """
    Get trading chart data with optional backtest overlay
    
    Args:
        symbol: Trading symbol (e.g., 'RELIANCE', 'NIFTY50')
        timeframe: Chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
        from_date: Start date for chart data
        to_date: End date for chart data  
        backtest_id: Optional backtest ID to overlay results
        
    Returns:
        Complete chart data package with Plotly JSON
    """
    
    try:
        # Set default date range if not provided
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_dt = datetime.now() - timedelta(days=90)  # 3 months default
            from_date = from_dt.strftime("%Y-%m-%d")
        
        # Get backtest result if ID provided
        backtest_result = None
        if backtest_id:
            # TODO: Retrieve from database when implemented
            logger.info(f"Backtest overlay requested: {backtest_id}")
            pass
        
        # Generate chart data
        chart_data = await get_chart_data(
            symbol=symbol,
            timeframe=timeframe,
            from_date=from_date,
            to_date=to_date,
            backtest_result=backtest_result
        )
        
        return {
            "success": True,
            "data": chart_data,
            "message": f"Chart data generated for {symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error generating chart for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chart: {str(e)}"
        )


@router.post("/chart/backtest-visualization")
async def create_backtest_chart(
    backtest_result: BacktestResult,
    symbol: str = Query(..., description="Trading symbol"),
    timeframe: str = Query("1d", regex="^(1m|5m|15m|30m|1h|4h|1d)$")
):
    """
    Create comprehensive visualization for backtest results
    
    Args:
        backtest_result: Complete backtest results
        symbol: Trading symbol for market data
        timeframe: Chart timeframe
        
    Returns:
        Multi-chart visualization package
    """
    
    try:
        # Determine date range from backtest results
        if backtest_result.trades:
            from_date = min(trade.entry_time for trade in backtest_result.trades)[:10]
            to_date = max(trade.exit_time for trade in backtest_result.trades)[:10]
        else:
            # Default range if no trades
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_dt = datetime.now() - timedelta(days=30)
            from_date = from_dt.strftime("%Y-%m-%d")
        
        # Generate complete chart package
        chart_data = await get_chart_data(
            symbol=symbol,
            timeframe=timeframe,
            from_date=from_date,
            to_date=to_date,
            backtest_result=backtest_result
        )
        
        # Add backtest summary to response
        response_data = {
            "charts": chart_data["charts"],
            "backtest_summary": {
                "net_profit": backtest_result.summary.net_profit,
                "total_trades": backtest_result.summary.total_trades,
                "win_rate": backtest_result.summary.win_rate,
                "max_drawdown": backtest_result.summary.max_drawdown,
                "sharpe_ratio": backtest_result.summary.sharpe_ratio,
                "profit_factor": backtest_result.summary.profit_factor
            },
            "period": chart_data["period"],
            "symbol": symbol,
            "timeframe": timeframe
        }
        
        return {
            "success": True,
            "data": response_data,
            "message": "Backtest visualization created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating backtest visualization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backtest visualization: {str(e)}"
        )


@router.get("/chart/{symbol}/indicators")
async def get_indicator_chart(
    symbol: str,
    indicators: str = Query(..., description="Comma-separated indicator names"),
    timeframe: str = Query("1d"),
    from_date: str = Query(None),
    to_date: str = Query(None),
    periods: str = Query("14", description="Comma-separated periods for indicators")
):
    """
    Get chart focused on specific indicators
    
    Args:
        symbol: Trading symbol
        indicators: Comma-separated list (e.g., "RSI,MACD,SMA")
        timeframe: Chart timeframe
        from_date: Start date
        to_date: End date  
        periods: Comma-separated periods matching indicators
        
    Returns:
        Chart with specified indicators highlighted
    """
    
    try:
        # Parse indicator specifications
        indicator_names = [name.strip() for name in indicators.split(",")]
        indicator_periods = [int(p.strip()) for p in periods.split(",")]
        
        if len(indicator_periods) == 1:
            # Use same period for all indicators
            indicator_periods = indicator_periods * len(indicator_names)
        elif len(indicator_periods) != len(indicator_names):
            raise ValueError("Number of periods must match number of indicators")
        
        # Set date defaults
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_dt = datetime.now() - timedelta(days=60)
            from_date = from_dt.strftime("%Y-%m-%d")
        
        # Fetch and prepare data
        data_fetcher = DataFetcher()
        df = await data_fetcher.get_historical_data(symbol, timeframe, from_date, to_date)
        
        # Calculate requested indicators
        from core.backtest_engine import IndicatorCalculator
        indicator_calc = IndicatorCalculator()
        
        indicator_specs = [
            {"name": name, "period": period}
            for name, period in zip(indicator_names, indicator_periods)
        ]
        
        df_with_indicators = indicator_calc.calculate_indicators(df.copy(), indicator_specs)
        
        # Convert to candle data
        from models.schemas import CandleData
        candles = [
            CandleData(
                timestamp=timestamp.isoformat(),
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume']
            )
            for timestamp, row in df_with_indicators.iterrows()
        ]
        
        # Extract indicators
        indicators_dict = {}
        for col in df_with_indicators.columns:
            if col not in ['open', 'high', 'low', 'close', 'volume']:
                indicators_dict[col] = df_with_indicators[col].fillna(0).tolist()
        
        # Create focused indicator chart
        chart_json = chart_viz.create_candlestick_chart(
            candles=candles,
            indicators=indicators_dict,
            title=f"{symbol} - {', '.join(indicator_names)} Analysis"
        )
        
        return {
            "success": True,
            "data": {
                "chart": chart_json,
                "indicators": list(indicators_dict.keys()),
                "symbol": symbol,
                "timeframe": timeframe,
                "period": {"from": from_date, "to": to_date}
            },
            "message": f"Indicator chart created for {symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error creating indicator chart: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create indicator chart: {str(e)}"
        )


@router.get("/chart/equity-curves/compare")
async def compare_equity_curves(
    backtest_ids: str = Query(..., description="Comma-separated backtest IDs"),
    normalize: bool = Query(False, description="Normalize to percentage returns")
):
    """
    Compare equity curves from multiple backtests
    
    Args:
        backtest_ids: Comma-separated list of backtest IDs
        normalize: Whether to normalize curves for comparison
        
    Returns:
        Comparative equity curve chart
    """
    
    try:
        # TODO: Implement when database storage is added
        # For now, return placeholder
        
        ids = [id.strip() for id in backtest_ids.split(",")]
        
        # Placeholder response
        fig_data = {
            "data": [],
            "layout": {
                "title": "Equity Curve Comparison",
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Equity ($)" if not normalize else "Returns (%)"},
                "template": "plotly_white"
            }
        }
        
        return {
            "success": True,
            "data": {
                "chart": fig_data,
                "backtest_ids": ids,
                "normalized": normalize
            },
            "message": "Comparison chart placeholder (requires database implementation)"
        }
        
    except Exception as e:
        logger.error(f"Error comparing equity curves: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare equity curves: {str(e)}"
        )