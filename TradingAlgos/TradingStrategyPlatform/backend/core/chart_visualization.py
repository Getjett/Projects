"""
Chart visualization service for displaying candlestick charts with trade markers
Integrates with Plotly.js for interactive trading charts
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.schemas import BacktestResult, TradeResult, CandleData


class ChartVisualization:
    """Creates interactive trading charts with trade markers and indicators"""
    
    def __init__(self):
        self.default_colors = {
            'candle_up': '#26a69a',
            'candle_down': '#ef5350',
            'entry_long': '#4caf50',
            'entry_short': '#f44336',
            'exit_profit': '#2196f3',
            'exit_loss': '#ff9800',
            'volume': '#9e9e9e'
        }
    
    def create_candlestick_chart(
        self,
        candles: List[CandleData],
        backtest_result: Optional[BacktestResult] = None,
        indicators: Optional[Dict[str, List[float]]] = None,
        title: str = "Trading Chart"
    ) -> Dict[str, Any]:
        """
        Create a comprehensive candlestick chart with trade markers and indicators
        
        Returns Plotly JSON that can be used directly in frontend
        """
        
        # Convert candles to DataFrame for easier manipulation
        df = pd.DataFrame([{
            'timestamp': pd.to_datetime(candle.timestamp),
            'open': candle.open,
            'high': candle.high,
            'low': candle.low,
            'close': candle.close,
            'volume': candle.volume
        } for candle in candles])
        
        # Create subplots: main chart + volume + indicators
        subplot_titles = ["Price", "Volume"]
        subplot_count = 2
        
        # Add indicator subplots if provided
        if indicators:
            oscillators = ['RSI', 'STOCH_K', 'STOCH_D', 'MACD']  # 0-100 range indicators
            for indicator_name in indicators:
                if any(osc in indicator_name.upper() for osc in oscillators):
                    subplot_titles.append(indicator_name)
                    subplot_count += 1
        
        fig = make_subplots(
            rows=subplot_count,
            cols=1,
            shared_xaxes=True,
            subplot_titles=subplot_titles,
            vertical_spacing=0.08,
            row_heights=[0.6] + [0.2] * (subplot_count - 1)  # Main chart larger
        )
        
        # 1. Add Candlestick Chart
        candlestick = go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Price",
            increasing_line_color=self.default_colors['candle_up'],
            decreasing_line_color=self.default_colors['candle_down'],
            showlegend=False
        )
        fig.add_trace(candlestick, row=1, col=1)
        
        # 2. Add Moving Averages and Trend Indicators to Main Chart
        if indicators:
            trend_indicators = ['SMA', 'EMA', 'BB_UPPER', 'BB_MIDDLE', 'BB_LOWER', 'VWAP']
            colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
            
            for i, (indicator_name, values) in enumerate(indicators.items()):
                if any(trend in indicator_name.upper() for trend in trend_indicators):
                    if len(values) == len(df):
                        fig.add_trace(
                            go.Scatter(
                                x=df['timestamp'],
                                y=values,
                                mode='lines',
                                name=indicator_name,
                                line=dict(color=colors[i % len(colors)], width=2),
                                opacity=0.8
                            ),
                            row=1, col=1
                        )
        
        # 3. Add Trade Entry/Exit Markers
        if backtest_result and backtest_result.trades:
            self._add_trade_markers(fig, backtest_result.trades, df)
        
        # 4. Add Volume Chart
        volume_colors = [
            self.default_colors['candle_up'] if close >= open 
            else self.default_colors['candle_down']
            for open, close in zip(df['open'], df['close'])
        ]
        
        volume_trace = go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name="Volume",
            marker_color=volume_colors,
            opacity=0.6,
            showlegend=False
        )
        fig.add_trace(volume_trace, row=2, col=1)
        
        # 5. Add Oscillator Indicators (RSI, Stochastic, etc.)
        if indicators:
            current_row = 3
            oscillators = ['RSI', 'MACD', 'STOCH']
            
            for indicator_name, values in indicators.items():
                if any(osc in indicator_name.upper() for osc in oscillators) and current_row <= subplot_count:
                    if len(values) == len(df):
                        fig.add_trace(
                            go.Scatter(
                                x=df['timestamp'],
                                y=values,
                                mode='lines',
                                name=indicator_name,
                                line=dict(width=2)
                            ),
                            row=current_row, col=1
                        )
                        
                        # Add reference lines for RSI
                        if 'RSI' in indicator_name.upper():
                            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                                        opacity=0.5, row=current_row, col=1)
                            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                                        opacity=0.5, row=current_row, col=1)
                        
                        current_row += 1
        
        # 6. Update Layout
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            height=800,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date", row=subplot_count, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig.to_dict()
    
    def _add_trade_markers(self, fig, trades: List[TradeResult], df: pd.DataFrame):
        """Add trade entry and exit markers to the chart"""
        
        entry_x, entry_y = [], []
        exit_x, exit_y = [], []
        entry_colors, exit_colors = [], []
        entry_text, exit_text = [], []
        
        for trade in trades:
            # Find corresponding candle data
            entry_time = pd.to_datetime(trade.entry_time)
            exit_time = pd.to_datetime(trade.exit_time)
            
            # Entry marker
            entry_x.append(entry_time)
            entry_y.append(trade.entry_price)
            entry_colors.append(self.default_colors['entry_long'] if trade.direction == 'LONG' else self.default_colors['entry_short'])
            entry_text.append(f"Entry: {trade.direction}<br>Price: ${trade.entry_price:.2f}<br>Size: {trade.size}")
            
            # Exit marker
            exit_x.append(exit_time)
            exit_y.append(trade.exit_price)
            exit_colors.append(self.default_colors['exit_profit'] if trade.pnl > 0 else self.default_colors['exit_loss'])
            exit_text.append(f"Exit: {'PROFIT' if trade.pnl > 0 else 'LOSS'}<br>Price: ${trade.exit_price:.2f}<br>P&L: ${trade.pnl:.2f}")
        
        # Add entry markers
        if entry_x:
            fig.add_trace(
                go.Scatter(
                    x=entry_x,
                    y=entry_y,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color=entry_colors,
                        line=dict(color='white', width=2)
                    ),
                    name="Entry",
                    text=entry_text,
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Add exit markers
        if exit_x:
            fig.add_trace(
                go.Scatter(
                    x=exit_x,
                    y=exit_y,
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color=exit_colors,
                        line=dict(color='white', width=2)
                    ),
                    name="Exit",
                    text=exit_text,
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=1, col=1
            )
    
    def create_equity_curve_chart(self, backtest_result: BacktestResult) -> Dict[str, Any]:
        """Create equity curve visualization"""
        
        if not backtest_result.equity_curve:
            return {}
        
        df = pd.DataFrame([{
            'timestamp': pd.to_datetime(point.timestamp),
            'equity': point.equity
        } for point in backtest_result.equity_curve])
        
        fig = go.Figure()
        
        # Equity line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['equity'],
                mode='lines',
                name='Portfolio Equity',
                line=dict(color='#2196f3', width=3),
                fill='tonexty' if len(df) > 0 else None,
                fillcolor='rgba(33, 150, 243, 0.1)'
            )
        )
        
        # Add horizontal line for initial capital
        initial_capital = backtest_result.summary.net_profit + backtest_result.summary.gross_loss + 100000  # Estimate
        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital"
        )
        
        fig.update_layout(
            title="Portfolio Equity Curve",
            xaxis_title="Date",
            yaxis_title="Equity ($)",
            template="plotly_white",
            height=400,
            hovermode='x'
        )
        
        return fig.to_dict()
    
    def create_performance_metrics_chart(self, backtest_result: BacktestResult) -> Dict[str, Any]:
        """Create performance metrics visualization"""
        
        if not backtest_result.trades:
            return {}
        
        # Calculate monthly returns
        trades_df = pd.DataFrame([{
            'timestamp': pd.to_datetime(trade.exit_time),
            'pnl': trade.pnl,
            'pnl_pct': trade.pnl_pct
        } for trade in backtest_result.trades])
        
        trades_df['month'] = trades_df['timestamp'].dt.to_period('M')
        monthly_pnl = trades_df.groupby('month')['pnl'].sum().reset_index()
        monthly_pnl['month_str'] = monthly_pnl['month'].astype(str)
        
        # Create bar chart of monthly P&L
        fig = go.Figure()
        
        colors = [
            '#4caf50' if pnl >= 0 else '#f44336' 
            for pnl in monthly_pnl['pnl']
        ]
        
        fig.add_trace(
            go.Bar(
                x=monthly_pnl['month_str'],
                y=monthly_pnl['pnl'],
                name='Monthly P&L',
                marker_color=colors,
                text=[f'${pnl:.0f}' for pnl in monthly_pnl['pnl']],
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title="Monthly P&L Distribution",
            xaxis_title="Month",
            yaxis_title="P&L ($)",
            template="plotly_white",
            height=300,
            showlegend=False
        )
        
        return fig.to_dict()
    
    def create_trade_analysis_chart(self, backtest_result: BacktestResult) -> Dict[str, Any]:
        """Create trade analysis charts (win/loss distribution, etc.)"""
        
        if not backtest_result.trades:
            return {}
        
        # Prepare trade data
        trades_data = []
        for trade in backtest_result.trades:
            trades_data.append({
                'pnl': trade.pnl,
                'duration': (pd.to_datetime(trade.exit_time) - pd.to_datetime(trade.entry_time)).days,
                'size': trade.size,
                'win': trade.pnl > 0
            })
        
        trades_df = pd.DataFrame(trades_data)
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["P&L Distribution", "Win/Loss Ratio", "Trade Duration", "Position Sizes"],
            specs=[[{"type": "histogram"}, {"type": "pie"}],
                   [{"type": "box"}, {"type": "scatter"}]]
        )
        
        # 1. P&L Histogram
        fig.add_trace(
            go.Histogram(
                x=trades_df['pnl'],
                nbinsx=20,
                name="P&L Distribution",
                marker_color='rgba(33, 150, 243, 0.7)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # 2. Win/Loss Pie Chart
        win_count = trades_df['win'].sum()
        loss_count = len(trades_df) - win_count
        
        fig.add_trace(
            go.Pie(
                labels=['Wins', 'Losses'],
                values=[win_count, loss_count],
                marker_colors=['#4caf50', '#f44336'],
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Trade Duration Box Plot
        fig.add_trace(
            go.Box(
                y=trades_df['duration'],
                name="Duration (days)",
                marker_color='rgba(76, 175, 80, 0.7)',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. P&L vs Size Scatter
        fig.add_trace(
            go.Scatter(
                x=trades_df['size'],
                y=trades_df['pnl'],
                mode='markers',
                marker=dict(
                    color=trades_df['pnl'],
                    colorscale='RdYlGn',
                    size=8,
                    showscale=False
                ),
                name="P&L vs Size",
                showlegend=False
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Trade Analysis Dashboard",
            height=600,
            template="plotly_white"
        )
        
        return fig.to_dict()


# API endpoint for chart data
async def get_chart_data(
    symbol: str,
    timeframe: str, 
    from_date: str,
    to_date: str,
    backtest_result: Optional[BacktestResult] = None
) -> Dict[str, Any]:
    """
    Generate complete chart data package for frontend
    Returns all charts needed for visualization
    """
    
    from core.data_fetcher import DataFetcher
    from core.backtest_engine import IndicatorCalculator
    
    # Fetch market data
    data_fetcher = DataFetcher()
    df = await data_fetcher.get_historical_data(symbol, timeframe, from_date, to_date)
    
    # Convert to CandleData objects
    candles = [
        CandleData(
            timestamp=timestamp.isoformat(),
            open=row['open'],
            high=row['high'], 
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        )
        for timestamp, row in df.iterrows()
    ]
    
    # Calculate indicators if requested
    indicators = {}
    if len(df) > 50:  # Only if enough data
        indicator_calc = IndicatorCalculator()
        indicator_specs = [
            {"name": "SMA", "period": 20},
            {"name": "EMA", "period": 12},
            {"name": "RSI", "period": 14},
            {"name": "MACD", "period": 12}
        ]
        df_with_indicators = indicator_calc.calculate_indicators(df.copy(), indicator_specs)
        
        # Extract indicator values
        for col in df_with_indicators.columns:
            if col not in ['open', 'high', 'low', 'close', 'volume']:
                indicators[col] = df_with_indicators[col].fillna(0).tolist()
    
    # Create visualization service
    viz = ChartVisualization()
    
    # Generate all chart data
    charts = {
        "main_chart": viz.create_candlestick_chart(
            candles=candles,
            backtest_result=backtest_result,
            indicators=indicators,
            title=f"{symbol} - {timeframe}"
        )
    }
    
    if backtest_result:
        charts.update({
            "equity_curve": viz.create_equity_curve_chart(backtest_result),
            "performance_metrics": viz.create_performance_metrics_chart(backtest_result),
            "trade_analysis": viz.create_trade_analysis_chart(backtest_result)
        })
    
    return {
        "charts": charts,
        "symbol": symbol,
        "timeframe": timeframe,
        "period": {"from": from_date, "to": to_date},
        "data_points": len(candles),
        "indicators_available": list(indicators.keys()) if indicators else []
    }