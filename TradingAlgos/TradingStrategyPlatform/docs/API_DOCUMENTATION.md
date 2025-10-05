# Strategy Builder - Backend API Documentation

## Overview
The Strategy Builder backend provides RESTful APIs for creating, managing, and backtesting trading strategies across multiple asset classes.

## Getting Started

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python app.py
```

The server will start at `http://localhost:8000`

### 3. Access API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Strategies API (`/api/strategies`)

#### Create Strategy
```http
POST /api/strategies/
Content-Type: application/json

{
  "strategy_name": "BankNifty ORB Strategy",
  "description": "Opening Range Breakout on BankNifty",
  "tags": ["scalping", "options"],
  "asset_class": "OPTIONS",
  "instrument": "BANKNIFTY",
  "exchange": "NFO",
  "product_type": "MIS",
  "trading_type": "Intraday",
  "signal_bar": "Second Bar",
  "time_frame": "5 Minute",
  "breakout_type": "Second Bar Breakout",
  "breakout_direction": "BOTH",
  "entry_confirmation": {
    "volume_confirmation": false,
    "candle_close": true,
    "retest": false
  },
  "volume_threshold": 150,
  "expiry": "Current Weekly",
  "strike_selection": "ATM",
  "strike_offset": 0,
  "option_type": "BOTH",
  "premium_min": 50,
  "premium_max": 500,
  "target_type": "PERCENTAGE",
  "target_value": 50,
  "stop_loss_type": "PERCENTAGE",
  "stop_loss_value": 30,
  "trailing_stop": false,
  "max_loss_per_day": 5000,
  "max_trades_per_day": 5,
  "risk_reward_ratio": 1.5
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "strategy_name": "BankNifty ORB Strategy",
  "created_at": "2025-10-04T10:00:00",
  "updated_at": "2025-10-04T10:00:00",
  "is_active": true,
  "backtest_count": 0,
  ...
}
```

#### Get All Strategies
```http
GET /api/strategies/?asset_class=OPTIONS&is_active=true&skip=0&limit=100
```

#### Get Strategy by ID
```http
GET /api/strategies/{strategy_id}
```

#### Update Strategy
```http
PUT /api/strategies/{strategy_id}
Content-Type: application/json

{
  "strategy_name": "Updated Strategy Name",
  "is_active": true
}
```

#### Delete Strategy
```http
DELETE /api/strategies/{strategy_id}
```

#### Clone Strategy
```http
POST /api/strategies/{strategy_id}/clone
Content-Type: application/json

{
  "new_name": "Cloned Strategy"
}
```

#### Validate Strategy
```http
GET /api/strategies/{strategy_id}/validate
```

**Response:**
```json
{
  "is_valid": true,
  "warnings": ["Risk/Reward ratio is less than 1:1"],
  "errors": []
}
```

---

### Backtest API (`/api/backtest`)

#### Run Backtest
```http
POST /api/backtest/run
Content-Type: application/json

{
  "strategy_id": "uuid-here",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "commission_per_trade": 20,
  "slippage_percent": 0.1,
  "market_condition": null,
  "include_weekends": false
}
```

**Response:**
```json
{
  "backtest_id": "uuid-here",
  "status": "PROCESSING",
  "message": "Backtest started. Use the backtest_id to check status and results."
}
```

#### Get Backtest Result
```http
GET /api/backtest/{backtest_id}
```

**Response:**
```json
{
  "id": "uuid-here",
  "strategy_id": "uuid-here",
  "strategy_name": "BankNifty ORB Strategy",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 100000,
  "final_capital": 125000,
  "metrics": {
    "total_trades": 45,
    "winning_trades": 25,
    "losing_trades": 20,
    "win_rate": 55.56,
    "total_profit": 35000,
    "total_loss": 10000,
    "net_profit": 25000,
    "net_profit_percent": 25.0,
    "average_profit_per_trade": 1400,
    "average_loss_per_trade": 500,
    "largest_profit": 5000,
    "largest_loss": -1500,
    "max_drawdown": 8000,
    "max_drawdown_percent": 8.0,
    "sharpe_ratio": 1.5,
    "profit_factor": 3.5,
    "average_trade_duration": "2.5 hours",
    "best_day_profit": 7500,
    "worst_day_loss": -3000,
    "consecutive_wins": 5,
    "consecutive_losses": 3,
    "actual_risk_reward_ratio": 2.8,
    "expectancy": 555.56
  },
  "trades": [...],
  "equity_curve": [...],
  "daily_returns": [...],
  "executed_at": "2025-10-04T10:00:00",
  "execution_time_seconds": 2.5
}
```

#### Get Strategy Backtests
```http
GET /api/backtest/strategy/{strategy_id}
```

#### Get Backtest Trades
```http
GET /api/backtest/{backtest_id}/trades?trade_type=WINNING&skip=0&limit=100
```

Query Parameters:
- `trade_type`: Filter by "WINNING" or "LOSING"
- `skip`: Number of records to skip
- `limit`: Maximum number of records to return

#### Delete Backtest
```http
DELETE /api/backtest/{backtest_id}
```

#### Compare Backtests
```http
POST /api/backtest/{backtest_id}/compare
Content-Type: application/json

{
  "compare_with": ["backtest-id-1", "backtest-id-2"]
}
```

---

## Data Models

### Strategy Model
```python
{
  "id": "string",
  "strategy_name": "string",
  "description": "string | null",
  "tags": ["string"],
  "asset_class": "OPTIONS | EQUITY | COMMODITY | CURRENCY | FUTURES",
  "instrument": "string",
  "exchange": "string",
  "product_type": "string",
  "trading_type": "string",
  "signal_bar": "string",
  "time_frame": "string",
  "breakout_type": "string",
  "breakout_direction": "BULLISH | BEARISH | BOTH",
  "entry_confirmation": {
    "volume_confirmation": "boolean",
    "candle_close": "boolean",
    "retest": "boolean"
  },
  "volume_threshold": "integer",
  "expiry": "string | null",
  "strike_selection": "string | null",
  "strike_offset": "integer | null",
  "option_type": "CE | PE | BOTH | null",
  "premium_min": "number | null",
  "premium_max": "number | null",
  "position_side": "LONG | SHORT | BOTH | null",
  "quantity_type": "FIXED | CAPITAL | PERCENTAGE | null",
  "quantity": "integer | null",
  "capital_per_trade": "number | null",
  "portfolio_percentage": "number | null",
  "leverage": "number | null",
  "target_type": "string",
  "target_value": "number",
  "stop_loss_type": "string",
  "stop_loss_value": "number",
  "trailing_stop": "boolean",
  "trailing_stop_value": "number | null",
  "max_loss_per_day": "number",
  "max_trades_per_day": "integer",
  "risk_reward_ratio": "number",
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_active": "boolean",
  "backtest_count": "integer"
}
```

### Backtest Request Model
```python
{
  "strategy_id": "string",
  "start_date": "date",
  "end_date": "date",
  "initial_capital": "number (default: 100000)",
  "commission_per_trade": "number (default: 20)",
  "slippage_percent": "number (default: 0.1)",
  "market_condition": "string | null",
  "include_weekends": "boolean (default: false)"
}
```

### Trade Result Model
```python
{
  "entry_time": "datetime",
  "exit_time": "datetime",
  "entry_price": "number",
  "exit_price": "number",
  "quantity": "integer",
  "position_type": "LONG | SHORT",
  "profit_loss": "number",
  "profit_loss_percent": "number",
  "exit_reason": "TARGET | STOP_LOSS | TIME_BASED | EOD"
}
```

---

## Frontend Integration

### Installing Dependencies
```bash
cd frontend
npm install axios
```

### Using the API Service

```typescript
import { strategyService, backtestService } from './services/api';

// Create a strategy
const strategy = await strategyService.createStrategy({
  strategyName: 'My Strategy',
  assetClass: 'OPTIONS',
  // ... other fields
});

// Get all strategies
const strategies = await strategyService.getStrategies({
  assetClass: 'OPTIONS',
  isActive: true
});

// Run a backtest
const backtestResponse = await backtestService.runBacktest({
  strategyId: strategy.id,
  startDate: '2024-01-01',
  endDate: '2024-12-31',
  initialCapital: 100000
});

// Get backtest results
const results = await backtestService.getBacktestResult(
  backtestResponse.backtestId
);
```

---

## Error Handling

All API endpoints return standard HTTP status codes:

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error Response Format:
```json
{
  "detail": "Error message description"
}
```

---

## Development Notes

### Current Implementation
- In-memory storage (for demo purposes)
- Background task processing for backtests
- Sample data generation for backtest results

### Production Requirements
- Replace in-memory storage with PostgreSQL database
- Add authentication and authorization
- Implement real market data integration
- Add caching layer with Redis
- Set up background job queue with Celery
- Add comprehensive logging and monitoring

---

## Testing

Run the backend tests:
```bash
cd backend
pytest
```

Test the API with curl:
```bash
# Create a strategy
curl -X POST http://localhost:8000/api/strategies/ \
  -H "Content-Type: application/json" \
  -d @strategy.json

# Get all strategies
curl http://localhost:8000/api/strategies/

# Run a backtest
curl -X POST http://localhost:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "your-strategy-id",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 100000
  }'
```

---

## Support

For issues or questions, please refer to the main project documentation or create an issue in the repository.
