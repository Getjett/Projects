-- Universal Trading Strategy Platform Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable TimescaleDB extension (for time-series data)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- USER MANAGEMENT
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    
    -- Additional Info
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Indexes
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ============================================================================
-- STRATEGIES
-- ============================================================================

CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Instrument Selection
    asset_class VARCHAR(20) NOT NULL, -- 'OPTIONS', 'EQUITY', 'COMMODITY', 'CURRENCY', 'FUTURES'
    instrument_symbol VARCHAR(50) NOT NULL, -- 'BANKNIFTY', 'NIFTY', 'RELIANCE', 'GOLD', etc.
    exchange VARCHAR(10) NOT NULL, -- 'NSE', 'BSE', 'NFO', 'MCX', 'CDS'
    product_type VARCHAR(10) DEFAULT 'MIS', -- 'MIS', 'NRML', 'CNC', 'BO', 'CO'
    lot_size_override INT, -- Custom lot size (NULL = use default)
    
    -- Trading Type
    trading_type VARCHAR(20) NOT NULL, -- 'INTRADAY', 'POSITIONAL', 'SWING', 'LONG_TERM'
    
    -- Entry Logic
    signal_bar_index INT DEFAULT 1, -- 0=First, 1=Second, 2=Third
    timeframe VARCHAR(10) DEFAULT '5min', -- '1min', '5min', '15min', etc.
    breakout_type VARCHAR(50) DEFAULT 'SECOND_BAR', -- 'ORB', 'SECOND_BAR', etc.
    breakout_direction VARCHAR(20) DEFAULT 'BOTH', -- 'BULLISH', 'BEARISH', 'BOTH'
    require_volume_confirmation BOOLEAN DEFAULT FALSE,
    volume_threshold_pct DECIMAL(5,2) DEFAULT 150.00,
    entry_time_start TIME DEFAULT '09:15:00',
    entry_time_end TIME DEFAULT '14:00:00',
    
    -- Strike Selection (OPTIONS ONLY)
    expiry_type VARCHAR(20), -- 'WEEKLY', 'MONTHLY', 'CUSTOM'
    strike_selection VARCHAR(20) DEFAULT 'ATM', -- 'ATM', 'OTM_100', 'ITM_100', etc.
    strike_offset INT DEFAULT 0, -- Custom offset in points
    min_premium DECIMAL(10,2) DEFAULT 0,
    max_premium DECIMAL(10,2) DEFAULT 10000,
    option_type VARCHAR(5), -- 'CE', 'PE', 'BOTH'
    
    -- Position Side (EQUITY/COMMODITY/FUTURES)
    position_side VARCHAR(10) DEFAULT 'LONG', -- 'LONG', 'SHORT', 'BOTH'
    quantity_type VARCHAR(20) DEFAULT 'FIXED', -- 'FIXED', 'CAPITAL_BASED', 'PERCENTAGE'
    fixed_quantity INT, -- For equity: shares, For others: lots
    min_price DECIMAL(10,2), -- Min instrument price filter
    max_price DECIMAL(10,2), -- Max instrument price filter
    
    -- Risk Management
    stop_loss_type VARCHAR(20) DEFAULT 'SIGNAL_BAR', -- 'FIXED_POINTS', 'FIXED_PCT', 'SIGNAL_BAR'
    stop_loss_value DECIMAL(10,2),
    stop_loss_buffer DECIMAL(10,2) DEFAULT 0, -- Additional buffer points
    target_type VARCHAR(20) DEFAULT 'SIGNAL_BAR_MULTIPLE', -- 'FIXED_POINTS', 'RR_RATIO', 'SIGNAL_BAR_MULTIPLE'
    target_value DECIMAL(10,2) DEFAULT 3.00, -- Default 3x signal bar range
    risk_reward_ratio DECIMAL(5,2),
    trailing_stop_loss BOOLEAN DEFAULT FALSE,
    trailing_sl_value DECIMAL(10,2),
    
    -- Position Sizing
    max_capital_per_trade DECIMAL(15,2) DEFAULT 50000.00,
    total_capital DECIMAL(15,2) DEFAULT 500000.00,
    max_positions INT DEFAULT 1, -- Max concurrent positions
    leverage DECIMAL(5,2) DEFAULT 1.00, -- For margin trading
    
    -- Exit Rules
    exit_time TIME DEFAULT '15:15:00',
    exit_on_target BOOLEAN DEFAULT TRUE,
    exit_on_stoploss BOOLEAN DEFAULT TRUE,
    exit_on_eod BOOLEAN DEFAULT TRUE,
    
    -- Filters
    min_signal_bar_range DECIMAL(10,2) DEFAULT 0,
    max_signal_bar_range DECIMAL(10,2) DEFAULT 10000,
    max_vix DECIMAL(5,2),
    min_volume INT,
    
    -- Day of Week Filter
    trade_on_monday BOOLEAN DEFAULT TRUE,
    trade_on_tuesday BOOLEAN DEFAULT TRUE,
    trade_on_wednesday BOOLEAN DEFAULT TRUE,
    trade_on_thursday BOOLEAN DEFAULT TRUE,
    trade_on_friday BOOLEAN DEFAULT TRUE,
    
    -- Transaction Costs
    slippage_points DECIMAL(5,2) DEFAULT 2.00,
    brokerage_per_lot DECIMAL(10,2) DEFAULT 20.00,
    stt_pct DECIMAL(5,4) DEFAULT 0.0500,
    exchange_charges_pct DECIMAL(5,4) DEFAULT 0.0050,
    gst_pct DECIMAL(5,2) DEFAULT 18.00,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_backtested BOOLEAN DEFAULT FALSE,
    is_live BOOLEAN DEFAULT FALSE,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT valid_asset_class CHECK (asset_class IN ('OPTIONS', 'EQUITY', 'COMMODITY', 'CURRENCY', 'FUTURES')),
    CONSTRAINT valid_exchange CHECK (exchange IN ('NSE', 'BSE', 'NFO', 'MCX', 'CDS', 'BFO'))
);

CREATE INDEX idx_strategies_user_id ON strategies(user_id);
CREATE INDEX idx_strategies_asset_class ON strategies(asset_class);
CREATE INDEX idx_strategies_instrument ON strategies(instrument_symbol, exchange);
CREATE INDEX idx_strategies_active ON strategies(is_active);

-- ============================================================================
-- BACKTEST RESULTS
-- ============================================================================

CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INT NOT NULL,
    run_date TIMESTAMP DEFAULT NOW(),
    
    -- Date Range
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    total_trading_days INT,
    
    -- Performance Metrics
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    no_trade_days INT DEFAULT 0,
    win_rate DECIMAL(5,2),
    
    -- P&L Metrics
    total_pnl DECIMAL(15,2),
    gross_profit DECIMAL(15,2),
    gross_loss DECIMAL(15,2),
    avg_pnl_per_trade DECIMAL(10,2),
    avg_win DECIMAL(10,2),
    avg_loss DECIMAL(10,2),
    largest_win DECIMAL(10,2),
    largest_loss DECIMAL(10,2),
    
    -- Drawdown
    max_drawdown DECIMAL(15,2),
    max_drawdown_pct DECIMAL(5,2),
    avg_drawdown DECIMAL(15,2),
    
    -- Risk Metrics
    profit_factor DECIMAL(8,4), -- Gross Profit / Gross Loss
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    calmar_ratio DECIMAL(8,4),
    
    -- Additional Stats
    total_ce_trades INT DEFAULT 0,
    total_pe_trades INT DEFAULT 0,
    total_long_trades INT DEFAULT 0,
    total_short_trades INT DEFAULT 0,
    
    -- Exit Breakdown
    target_hit_count INT DEFAULT 0,
    sl_hit_count INT DEFAULT 0,
    eod_exit_count INT DEFAULT 0,
    
    -- Costs
    total_brokerage DECIMAL(15,2),
    total_taxes DECIMAL(15,2),
    net_pnl DECIMAL(15,2),
    
    -- Execution
    execution_time_seconds INT,
    status VARCHAR(20) DEFAULT 'COMPLETED', -- 'RUNNING', 'COMPLETED', 'FAILED'
    error_message TEXT,
    
    -- Foreign Keys
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

CREATE INDEX idx_backtest_strategy ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_date_range ON backtest_results(from_date, to_date);
CREATE INDEX idx_backtest_status ON backtest_results(status);

-- ============================================================================
-- TRADES (Individual Trade Details)
-- ============================================================================

CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    backtest_id INT NOT NULL,
    trade_date DATE NOT NULL,
    
    -- Entry Details
    entry_time TIMESTAMP NOT NULL,
    entry_spot_price DECIMAL(10,2) NOT NULL,
    entry_premium DECIMAL(10,2), -- For options
    
    -- Exit Details
    exit_time TIMESTAMP,
    exit_spot_price DECIMAL(10,2),
    exit_premium DECIMAL(10,2),
    exit_reason VARCHAR(20), -- 'TARGET', 'SL', 'EOD', 'MANUAL'
    
    -- Trade Details (Universal)
    asset_class VARCHAR(20) NOT NULL,
    instrument_symbol VARCHAR(50) NOT NULL,
    signal_type VARCHAR(10) NOT NULL, -- 'CE', 'PE', 'LONG', 'SHORT'
    
    -- Options-specific fields
    strike_price DECIMAL(10,2),
    expiry_date DATE,
    days_to_expiry INT,
    option_type VARCHAR(5), -- 'CE', 'PE', NULL
    
    -- Signal Bar Details
    signal_bar_high DECIMAL(10,2),
    signal_bar_low DECIMAL(10,2),
    signal_bar_range DECIMAL(10,2),
    signal_bar_volume BIGINT,
    
    -- Price Movement
    spot_move DECIMAL(10,2),
    spot_move_pct DECIMAL(5,2),
    day_high DECIMAL(10,2),
    day_low DECIMAL(10,2),
    
    -- P&L
    pnl DECIMAL(10,2),
    pnl_pct DECIMAL(5,2),
    brokerage DECIMAL(10,2),
    taxes DECIMAL(10,2),
    net_pnl DECIMAL(10,2),
    
    -- Greeks & Risk (Options)
    entry_delta DECIMAL(5,4),
    exit_delta DECIMAL(5,4),
    gamma DECIMAL(5,6),
    theta_decay DECIMAL(10,2),
    vega DECIMAL(5,4),
    implied_volatility DECIMAL(5,2),
    
    -- Quantity/Lot Size (Universal)
    lot_size INT, -- For options/futures/commodity
    quantity INT, -- For equity (number of shares)
    contract_value DECIMAL(15,2), -- Total position value
    margin_required DECIMAL(15,2), -- Margin blocked
    
    -- Risk Management
    stop_loss_level DECIMAL(10,2),
    target_level DECIMAL(10,2),
    risk_amount DECIMAL(10,2),
    reward_amount DECIMAL(10,2),
    risk_reward_ratio DECIMAL(5,2),
    
    -- Foreign Keys
    FOREIGN KEY (backtest_id) REFERENCES backtest_results(id) ON DELETE CASCADE
);

CREATE INDEX idx_trades_backtest ON trades(backtest_id);
CREATE INDEX idx_trades_date ON trades(trade_date);
CREATE INDEX idx_trades_signal ON trades(signal_type);
CREATE INDEX idx_trades_exit_reason ON trades(exit_reason);
CREATE INDEX idx_trades_instrument ON trades(instrument_symbol);

-- Convert trades table to hypertable for time-series optimization
SELECT create_hypertable('trades', 'entry_time', if_not_exists => TRUE);

-- ============================================================================
-- MARKET DATA CACHE
-- ============================================================================

CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    instrument_token BIGINT NOT NULL,
    instrument_symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- OHLCV Data
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    
    -- Additional Data
    oi BIGINT, -- Open Interest (for F&O)
    
    -- Metadata
    timeframe VARCHAR(10) NOT NULL, -- '1min', '5min', '15min', 'day'
    fetched_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    UNIQUE(instrument_token, timestamp, timeframe)
);

CREATE INDEX idx_market_data_symbol ON market_data(instrument_symbol, exchange);
CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX idx_market_data_timeframe ON market_data(timeframe);

-- Convert to hypertable
SELECT create_hypertable('market_data', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- INSTRUMENTS MASTER
-- ============================================================================

CREATE TABLE instruments (
    id SERIAL PRIMARY KEY,
    instrument_token BIGINT UNIQUE NOT NULL,
    exchange_token BIGINT,
    trading_symbol VARCHAR(100) NOT NULL,
    name VARCHAR(200),
    
    -- Classification
    exchange VARCHAR(10) NOT NULL,
    asset_class VARCHAR(20) NOT NULL,
    instrument_type VARCHAR(50), -- 'EQ', 'OPTIDX', 'FUTIDX', 'FUTSTK', 'OPTSTK'
    segment VARCHAR(20),
    
    -- Contract Details
    expiry DATE,
    strike DECIMAL(10,2),
    option_type VARCHAR(5), -- 'CE', 'PE', NULL
    lot_size INT NOT NULL,
    tick_size DECIMAL(10,4),
    
    -- Trading Info
    last_price DECIMAL(10,2),
    last_updated TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_instruments_symbol ON instruments(trading_symbol);
CREATE INDEX idx_instruments_token ON instruments(instrument_token);
CREATE INDEX idx_instruments_exchange ON instruments(exchange);
CREATE INDEX idx_instruments_asset_class ON instruments(asset_class);
CREATE INDEX idx_instruments_expiry ON instruments(expiry);

-- ============================================================================
-- PATTERNS (Candlestick Patterns)
-- ============================================================================

CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    description TEXT,
    pattern_type VARCHAR(20), -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    num_candles INT NOT NULL,
    
    -- Pattern Definition (JSON)
    pattern_definition JSONB NOT NULL,
    
    -- Matching Settings
    strict_matching BOOLEAN DEFAULT TRUE,
    tolerance_pct DECIMAL(5,2) DEFAULT 10.00,
    
    -- Usage Stats
    times_used INT DEFAULT 0,
    success_rate DECIMAL(5,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_patterns_user ON patterns(user_id);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);

-- ============================================================================
-- ALERTS & NOTIFICATIONS
-- ============================================================================

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    strategy_id INT,
    
    -- Alert Details
    alert_type VARCHAR(20) NOT NULL, -- 'SIGNAL', 'TARGET', 'SL', 'CUSTOM'
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'INFO', -- 'INFO', 'WARNING', 'ERROR'
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    is_sent BOOLEAN DEFAULT FALSE,
    
    -- Delivery Channels
    send_email BOOLEAN DEFAULT TRUE,
    send_sms BOOLEAN DEFAULT FALSE,
    send_push BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP,
    sent_at TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE SET NULL
);

CREATE INDEX idx_alerts_user ON alerts(user_id);
CREATE INDEX idx_alerts_status ON alerts(is_read, is_sent);

-- ============================================================================
-- AUDIT LOG
-- ============================================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50), -- 'STRATEGY', 'BACKTEST', 'TRADE', etc.
    entity_id INT,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Strategy Performance Summary
CREATE VIEW strategy_performance_summary AS
SELECT 
    s.id AS strategy_id,
    s.strategy_name,
    s.asset_class,
    s.instrument_symbol,
    COUNT(br.id) AS total_backtests,
    AVG(br.total_pnl) AS avg_pnl,
    AVG(br.win_rate) AS avg_win_rate,
    AVG(br.profit_factor) AS avg_profit_factor,
    MAX(br.run_date) AS last_backtest_date
FROM strategies s
LEFT JOIN backtest_results br ON s.id = br.strategy_id
WHERE s.is_active = TRUE
GROUP BY s.id, s.strategy_name, s.asset_class, s.instrument_symbol;

-- User Statistics
CREATE VIEW user_statistics AS
SELECT 
    u.id AS user_id,
    u.username,
    COUNT(DISTINCT s.id) AS total_strategies,
    COUNT(DISTINCT br.id) AS total_backtests,
    COALESCE(SUM(br.total_trades), 0) AS total_trades,
    COALESCE(AVG(br.win_rate), 0) AS avg_win_rate,
    u.created_at,
    u.last_login
FROM users u
LEFT JOIN strategies s ON u.id = s.user_id
LEFT JOIN backtest_results br ON s.id = br.strategy_id
GROUP BY u.id, u.username, u.created_at, u.last_login;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_instruments_updated_at BEFORE UPDATE ON instruments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA / SEEDS
-- ============================================================================

-- Insert admin user (password: admin123 - hashed with bcrypt)
INSERT INTO users (username, email, password_hash, is_admin, is_verified)
VALUES ('admin', 'admin@tradingstrategy.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/6BkMPwpC4qu', TRUE, TRUE);

-- Insert sample instruments (to be updated via API)
-- This will be populated by the instrument sync job

COMMIT;
