"""
Database Models for Trading Platform
SQLAlchemy models for strategies, backtests, ML models, and user management
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    strategies = db.relationship('Strategy', backref='user', lazy=True)
    backtests = db.relationship('Backtest', backref='user', lazy=True)
    ml_models = db.relationship('MLModel', backref='user', lazy=True)

class Strategy(db.Model):
    """Trading strategy definition"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategy_type = db.Column(db.String(50), nullable=False)  # 'technical', 'ml', 'hybrid'
    
    # Strategy configuration as JSON
    config = db.Column(db.Text)  # Stores JSON configuration
    
    # Strategy code (for custom strategies)
    code = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    backtests = db.relationship('Backtest', backref='strategy', lazy=True)
    
    @property
    def config_dict(self):
        """Return config as dictionary"""
        return json.loads(self.config) if self.config else {}
    
    @config_dict.setter
    def config_dict(self, value):
        """Set config from dictionary"""
        self.config = json.dumps(value)

class Backtest(db.Model):
    """Backtest results and configuration"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Backtest parameters
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    initial_capital = db.Column(db.Float, default=100000)
    
    # Results
    final_capital = db.Column(db.Float)
    return_percentage = db.Column(db.Float)
    total_trades = db.Column(db.Integer)
    winning_trades = db.Column(db.Integer)
    losing_trades = db.Column(db.Integer)
    max_drawdown = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
    
    # Detailed results as JSON
    trades_data = db.Column(db.Text)  # JSON array of trades
    equity_curve = db.Column(db.Text)  # JSON array of equity points
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)

class MLModel(db.Model):
    """Machine Learning model definition and metadata"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # 'lstm', 'random_forest', 'xgboost', etc.
    
    # Model configuration
    config = db.Column(db.Text)  # JSON configuration
    features = db.Column(db.Text)  # JSON array of feature names
    target = db.Column(db.String(50))  # Target variable
    
    # Training data
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(20), nullable=False)
    training_start = db.Column(db.DateTime)
    training_end = db.Column(db.DateTime)
    
    # Model performance
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    mse = db.Column(db.Float)
    mae = db.Column(db.Float)
    
    # Model file path
    model_path = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, training, trained, failed
    training_progress = db.Column(db.Float, default=0.0)
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trained_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class MarketData(db.Model):
    """Historical market data storage"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    # OHLCV data
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    
    # Technical indicators (can be computed and stored)
    sma_20 = db.Column(db.Float)
    ema_20 = db.Column(db.Float)
    rsi_14 = db.Column(db.Float)
    macd = db.Column(db.Float)
    macd_signal = db.Column(db.Float)
    bb_upper = db.Column(db.Float)
    bb_lower = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('symbol', 'timeframe', 'timestamp'),)

class Alert(db.Model):
    """Trading alerts and notifications"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'signal', 'backtest', 'ml_prediction', 'error'
    
    # Alert conditions
    symbol = db.Column(db.String(20))
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))
    ml_model_id = db.Column(db.Integer, db.ForeignKey('ml_model.id'))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Portfolio(db.Model):
    """Portfolio management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Portfolio configuration
    initial_capital = db.Column(db.Float, default=100000)
    current_value = db.Column(db.Float, default=100000)
    
    # Risk management
    max_position_size = db.Column(db.Float, default=0.1)  # 10% max per position
    stop_loss_pct = db.Column(db.Float, default=0.02)  # 2% stop loss
    take_profit_pct = db.Column(db.Float, default=0.06)  # 6% take profit
    
    # Strategies in this portfolio (JSON array of strategy IDs)
    strategies = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)