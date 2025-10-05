"""
Backtest API Routes
Handles backtesting operations for trading strategies
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid
import random

from models.backtest import (
    BacktestRequest,
    BacktestResult,
    BacktestMetrics,
    TradeResult,
    BacktestSummary
)

router = APIRouter()

# In-memory storage for backtest results
backtest_results_db: dict[str, BacktestResult] = {}

# Accurate price ranges for instruments (Oct 2025)
INSTRUMENT_PRICES = {
    # Index Options
    'NIFTY': (50, 500),
    'BANKNIFTY': (50, 800),
    'FINNIFTY': (50, 400),
    'MIDCPNIFTY': (30, 300),
    'SENSEX': (50, 600),
    'BANKEX': (50, 500),
    
    # Equity
    'RELIANCE': (1250, 1350),
    'TCS': (4000, 4300),
    'INFY': (1800, 1950),
    'HDFCBANK': (1700, 1800),
    'ICICIBANK': (1250, 1350),
    'SBIN': (800, 900),
    'BHARTIARTL': (1550, 1650),
    'HINDUNILVR': (2350, 2500),
    'ITC': (460, 490),
    'KOTAKBANK': (1750, 1850),
    'LT': (3600, 3800),
    'AXISBANK': (1100, 1200),
    'WIPRO': (560, 600),
    'HCLTECH': (1350, 1450),
    'MARUTI': (12500, 13500),
    'TATAMOTORS': (750, 850),
    'SUNPHARMA': (1750, 1850),
    'BAJFINANCE': (6800, 7200),
    'TITAN': (3400, 3600),
    'ASIANPAINT': (2350, 2500),
    'ULTRACEMCO': (11000, 11800),
    'NESTLEIND': (2400, 2550),
    'ADANIENT': (2800, 3100),
    'ONGC': (280, 320),
    'NTPC': (350, 390),
    'POWERGRID': (310, 340),
    'COALINDIA': (450, 490),
    'JSWSTEEL': (950, 1050),
    'TATASTEEL': (155, 175),
    'HINDALCO': (650, 720),
    
    # Commodities
    'GOLD': (60000, 75000),
    'GOLDM': (6000, 7500),
    'SILVER': (70000, 90000),
    'SILVERM': (70, 90),
    'CRUDEOIL': (5500, 7500),
    'CRUDEOILM': (5500, 7500),
    'NATURALGAS': (180, 280),
    'COPPER': (700, 900),
    'ZINC': (230, 290),
    'LEAD': (180, 220),
    'ALUMINIUM': (210, 260),
    'NICKEL': (1800, 2200),
    
    # Currency
    'USDINR': (82, 85),
    'EURINR': (88, 92),
    'GBPINR': (100, 106),
    'JPYINR': (0.55, 0.62),
    'EURUSD': (1.05, 1.12),
    'GBPUSD': (1.22, 1.30),
}


def get_price_range(instrument: str) -> tuple[float, float]:
    """Get accurate price range for an instrument"""
    # Try exact match first
    if instrument in INSTRUMENT_PRICES:
        return INSTRUMENT_PRICES[instrument]
    
    # Try without FUT suffix for futures
    instrument_base = instrument.replace('FUT', '').replace('fut', '')
    if instrument_base in INSTRUMENT_PRICES:
        min_price, max_price = INSTRUMENT_PRICES[instrument_base]
        # Futures typically trade at index level for indices, same as spot for stocks
        if instrument_base in ['NIFTY', 'BANKNIFTY', 'FINNIFTY']:
            return (min_price * 100, max_price * 100)  # Index futures
        return (min_price, max_price)
    
    # Default fallback
    return (100, 500)


def generate_sample_trades(
    start_date: date,
    end_date: date,
    strategy_config: dict
) -> List[TradeResult]:
    """
    Generate sample trades with accurate pricing for demonstration
    In production, this would run actual backtest logic
    """
    trades = []
    current_date = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get instrument from strategy config
    instrument = strategy_config.get('instrument', 'NIFTY')
    min_price, max_price = get_price_range(instrument)
    
    trade_count = random.randint(20, 50)
    
    for _ in range(trade_count):
        if current_date >= end_datetime:
            break
        
        # Random entry time during market hours
        entry_hour = random.randint(9, 14)
        entry_minute = random.randint(15, 59)
        entry_time = current_date.replace(hour=entry_hour, minute=entry_minute)
        
        # Exit time (30 min to 3 hours later)
        exit_delta = timedelta(minutes=random.randint(30, 180))
        exit_time = entry_time + exit_delta
        
        # Make sure exit is within market hours
        if exit_time.hour > 15 or (exit_time.hour == 15 and exit_time.minute > 30):
            exit_time = exit_time.replace(hour=15, minute=30)
        
        # Generate trade data with accurate pricing
        entry_price = random.uniform(min_price, max_price)
        is_winner = random.random() < 0.55  # 55% win rate
        
        # More realistic profit/loss percentages
        if is_winner:
            profit_pct = random.uniform(0.02, 0.15)  # 2-15% profit
            exit_price = entry_price * (1 + profit_pct)
            exit_reason = "TARGET"
        else:
            loss_pct = random.uniform(0.02, 0.10)  # 2-10% loss
            exit_price = entry_price * (1 - loss_pct)
            exit_reason = random.choice(["STOP_LOSS", "TIME_BASED", "EOD"])
        
        # Determine quantity based on instrument type
        if instrument in INSTRUMENT_PRICES and INSTRUMENT_PRICES[instrument][0] > 10000:
            # High value stocks - smaller quantities
            quantity = random.choice([1, 2, 5, 10])
        elif instrument in ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']:
            # Index options - lot sizes
            quantity = random.choice([15, 25, 50])
        else:
            # Regular stocks
            quantity = random.choice([10, 25, 50, 100])
        
        profit_loss = (exit_price - entry_price) * quantity
        profit_loss_percent = ((exit_price - entry_price) / entry_price) * 100
        
        trade = TradeResult(
            entry_time=entry_time,
            exit_time=exit_time,
            entry_price=round(entry_price, 2),
            exit_price=round(exit_price, 2),
            quantity=quantity,
            position_type="LONG",
            profit_loss=round(profit_loss, 2),
            profit_loss_percent=round(profit_loss_percent, 2),
            exit_reason=exit_reason
        )
        
        trades.append(trade)
        
        # Move to next trading day
        current_date += timedelta(days=random.randint(1, 3))
    
    return trades


def calculate_metrics(trades: List[TradeResult], initial_capital: float) -> BacktestMetrics:
    """
    Calculate backtest metrics from trade results
    """
    if not trades:
        raise ValueError("No trades to calculate metrics")
    
    winning_trades = [t for t in trades if t.profit_loss > 0]
    losing_trades = [t for t in trades if t.profit_loss < 0]
    
    total_profit = sum(t.profit_loss for t in winning_trades)
    total_loss = abs(sum(t.profit_loss for t in losing_trades))
    net_profit = sum(t.profit_loss for t in trades)
    
    # Calculate drawdown
    equity = initial_capital
    peak_equity = initial_capital
    max_drawdown = 0
    
    for trade in trades:
        equity += trade.profit_loss
        if equity > peak_equity:
            peak_equity = equity
        drawdown = peak_equity - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Calculate consecutive wins/losses
    consecutive_wins = 0
    consecutive_losses = 0
    current_streak = 0
    
    for trade in trades:
        if trade.profit_loss > 0:
            if current_streak >= 0:
                current_streak += 1
            else:
                current_streak = 1
            consecutive_wins = max(consecutive_wins, current_streak)
        else:
            if current_streak <= 0:
                current_streak -= 1
            else:
                current_streak = -1
            consecutive_losses = max(consecutive_losses, abs(current_streak))
    
    avg_trade_duration = sum(
        (t.exit_time - t.entry_time).total_seconds() for t in trades
    ) / len(trades) / 3600  # Convert to hours
    
    metrics = BacktestMetrics(
        total_trades=len(trades),
        winning_trades=len(winning_trades),
        losing_trades=len(losing_trades),
        win_rate=round((len(winning_trades) / len(trades)) * 100, 2),
        
        total_profit=round(total_profit, 2),
        total_loss=round(total_loss, 2),
        net_profit=round(net_profit, 2),
        net_profit_percent=round((net_profit / initial_capital) * 100, 2),
        
        average_profit_per_trade=round(total_profit / len(winning_trades), 2) if winning_trades else 0,
        average_loss_per_trade=round(total_loss / len(losing_trades), 2) if losing_trades else 0,
        largest_profit=round(max(t.profit_loss for t in winning_trades), 2) if winning_trades else 0,
        largest_loss=round(min(t.profit_loss for t in losing_trades), 2) if losing_trades else 0,
        
        max_drawdown=round(max_drawdown, 2),
        max_drawdown_percent=round((max_drawdown / initial_capital) * 100, 2),
        sharpe_ratio=round(random.uniform(0.5, 2.5), 2),  # Placeholder
        profit_factor=round(total_profit / total_loss, 2) if total_loss > 0 else 0,
        
        average_trade_duration=f"{avg_trade_duration:.2f} hours",
        best_day_profit=round(max(t.profit_loss for t in trades), 2),
        worst_day_loss=round(min(t.profit_loss for t in trades), 2),
        consecutive_wins=consecutive_wins,
        consecutive_losses=consecutive_losses,
        
        actual_risk_reward_ratio=round(
            (total_profit / len(winning_trades)) / (total_loss / len(losing_trades)),
            2
        ) if winning_trades and losing_trades else 0,
        expectancy=round(
            ((len(winning_trades) / len(trades)) * (total_profit / len(winning_trades))) -
            ((len(losing_trades) / len(trades)) * (total_loss / len(losing_trades))),
            2
        ) if winning_trades and losing_trades else 0
    )
    
    return metrics


def generate_equity_curve(trades: List[TradeResult], initial_capital: float):
    """
    Generate equity curve data for visualization
    """
    equity_curve = []
    daily_returns = []
    
    current_equity = initial_capital
    peak_equity = initial_capital
    
    trades_by_date = {}
    for trade in trades:
        trade_date = trade.exit_time.date()
        if trade_date not in trades_by_date:
            trades_by_date[trade_date] = []
        trades_by_date[trade_date].append(trade)
    
    for trade_date in sorted(trades_by_date.keys()):
        daily_pl = sum(t.profit_loss for t in trades_by_date[trade_date])
        current_equity += daily_pl
        
        if current_equity > peak_equity:
            peak_equity = current_equity
        
        drawdown = ((peak_equity - current_equity) / peak_equity) * 100
        daily_return = (daily_pl / (current_equity - daily_pl)) * 100
        
        equity_curve.append({
            "date": trade_date.isoformat(),
            "equity": round(current_equity, 2),
            "drawdown": round(drawdown, 2)
        })
        
        daily_returns.append({
            "date": trade_date.isoformat(),
            "return_pct": round(daily_return, 2)
        })
    
    return equity_curve, daily_returns


async def run_backtest_simulation(
    backtest_id: str,
    strategy_id: str,
    strategy_name: str,
    request: BacktestRequest
):
    """
    Run the actual backtest simulation
    This runs in the background
    """
    import time
    start_time = time.time()
    
    # Extract instrument from strategy_id if present (format: temp-INSTRUMENT-timestamp)
    instrument = None
    if strategy_id.startswith('temp-'):
        parts = strategy_id.split('-')
        if len(parts) >= 3:
            instrument = parts[1]
    
    # Simulate backtest execution
    trades = generate_sample_trades(
        request.start_date,
        request.end_date,
        {"instrument": instrument} if instrument else {}
    )
    
    metrics = calculate_metrics(trades, request.initial_capital)
    equity_curve, daily_returns = generate_equity_curve(trades, request.initial_capital)
    
    final_capital = request.initial_capital + metrics.net_profit
    execution_time = time.time() - start_time
    
    result = BacktestResult(
        id=backtest_id,
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        final_capital=round(final_capital, 2),
        metrics=metrics,
        trades=trades,
        equity_curve=equity_curve,
        daily_returns=daily_returns,
        executed_at=datetime.now(),
        execution_time_seconds=round(execution_time, 2)
    )
    
    backtest_results_db[backtest_id] = result


@router.post("/run", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """
    Run a backtest for a strategy
    Returns immediately with backtest_id, actual processing happens in background
    """
    # Validate date range
    if request.start_date >= request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    if request.end_date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be in the future"
        )
    
    backtest_id = str(uuid.uuid4())
    
    # In production, you would fetch strategy from database
    strategy_name = f"Strategy {request.strategy_id[:8]}"
    
    # Add backtest task to background
    background_tasks.add_task(
        run_backtest_simulation,
        backtest_id,
        request.strategy_id,
        strategy_name,
        request
    )
    
    return {
        "backtest_id": backtest_id,
        "status": "PROCESSING",
        "message": "Backtest started. Use the backtest_id to check status and results."
    }


@router.get("/{backtest_id}", response_model=BacktestResult)
async def get_backtest_result(backtest_id: str):
    """
    Get backtest results by ID
    """
    if backtest_id not in backtest_results_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with id {backtest_id} not found or still processing"
        )
    
    return backtest_results_db[backtest_id]


@router.get("/strategy/{strategy_id}", response_model=List[BacktestSummary])
async def get_strategy_backtests(strategy_id: str):
    """
    Get all backtest results for a specific strategy
    """
    results = [
        BacktestSummary(
            id=result.id,
            strategy_id=result.strategy_id,
            strategy_name=result.strategy_name,
            start_date=result.start_date,
            end_date=result.end_date,
            net_profit=result.metrics.net_profit,
            net_profit_percent=result.metrics.net_profit_percent,
            win_rate=result.metrics.win_rate,
            total_trades=result.metrics.total_trades,
            max_drawdown_percent=result.metrics.max_drawdown_percent,
            executed_at=result.executed_at
        )
        for result in backtest_results_db.values()
        if result.strategy_id == strategy_id
    ]
    
    return results


@router.get("/{backtest_id}/trades", response_model=List[TradeResult])
async def get_backtest_trades(
    backtest_id: str,
    trade_type: Optional[str] = None,  # "WINNING" or "LOSING"
    skip: int = 0,
    limit: int = 100
):
    """
    Get individual trades from a backtest
    """
    if backtest_id not in backtest_results_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with id {backtest_id} not found"
        )
    
    trades = backtest_results_db[backtest_id].trades
    
    # Filter by trade type
    if trade_type == "WINNING":
        trades = [t for t in trades if t.profit_loss > 0]
    elif trade_type == "LOSING":
        trades = [t for t in trades if t.profit_loss < 0]
    
    # Apply pagination
    return trades[skip:skip + limit]


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(backtest_id: str):
    """
    Delete a backtest result
    """
    if backtest_id not in backtest_results_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with id {backtest_id} not found"
        )
    
    del backtest_results_db[backtest_id]
    return None


@router.post("/{backtest_id}/compare")
async def compare_backtests(backtest_id: str, compare_with: List[str]):
    """
    Compare multiple backtest results
    """
    if backtest_id not in backtest_results_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with id {backtest_id} not found"
        )
    
    results = [backtest_results_db[backtest_id]]
    
    for compare_id in compare_with:
        if compare_id in backtest_results_db:
            results.append(backtest_results_db[compare_id])
    
    comparison = {
        "backtests": [
            {
                "id": r.id,
                "strategy_name": r.strategy_name,
                "net_profit": r.metrics.net_profit,
                "net_profit_percent": r.metrics.net_profit_percent,
                "win_rate": r.metrics.win_rate,
                "total_trades": r.metrics.total_trades,
                "max_drawdown_percent": r.metrics.max_drawdown_percent,
                "sharpe_ratio": r.metrics.sharpe_ratio,
                "profit_factor": r.metrics.profit_factor
            }
            for r in results
        ]
    }
    
    return comparison
