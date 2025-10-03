"""
Simplified Trading Platform Backend
Basic Flask application for quick start
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys

# Add the parent directory to the path to access TradingAlgos modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from simple_kite import connect_to_kite
    from config import *
    KITE_AVAILABLE = True
    
    # Test actual connection
    def test_kite_connection():
        try:
            kite = connect_to_kite()
            if kite:
                profile = kite.profile()
                return True, f"Connected as {profile.get('user_name', 'Unknown')}"
        except Exception as e:
            return False, str(e)
        return False, "Connection failed"
    
except ImportError:
    KITE_AVAILABLE = False
    def test_kite_connection():
        return False, "Kite modules not available"
    print("Warning: Kite modules not available. Using simulation mode.")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading-platform-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Simple database models
class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    strategy_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Backtest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(20), nullable=False)
    return_percentage = db.Column(db.Float)
    total_trades = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    kite_connected, kite_status = test_kite_connection()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'kite_available': KITE_AVAILABLE,
        'kite_connected': kite_connected,
        'kite_status': kite_status
    })

@app.route('/api/dashboard')
def dashboard():
    """Main dashboard data"""
    try:
        total_strategies = Strategy.query.count()
        total_backtests = Backtest.query.count()
        
        # Test Kite connection status
        kite_connected, kite_status = test_kite_connection()
        
        # Get recent backtests
        recent_backtests = Backtest.query.order_by(Backtest.created_at.desc()).limit(5).all()
        
        return jsonify({
            'summary': {
                'total_strategies': total_strategies,
                'total_backtests': total_backtests,
                'kite_connected': kite_connected,
                'kite_status': kite_status,
                'last_updated': datetime.now().isoformat()
            },
            'recent_backtests': [
                {
                    'id': bt.id,
                    'name': bt.name,
                    'symbol': bt.symbol,
                    'return_pct': bt.return_percentage or 0,
                    'created_at': bt.created_at.isoformat()
                } for bt in recent_backtests
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all strategies"""
    try:
        strategies = Strategy.query.all()
        return jsonify({
            'strategies': [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'strategy_type': s.strategy_type,
                    'created_at': s.created_at.isoformat(),
                    'is_active': s.is_active
                } for s in strategies
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    """Create new strategy"""
    try:
        data = request.get_json()
        
        strategy = Strategy(
            name=data['name'],
            description=data.get('description', ''),
            strategy_type=data.get('strategy_type', 'technical'),
            config=data.get('config', '{}')
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify({
            'message': 'Strategy created successfully',
            'strategy_id': strategy.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run a simple backtest"""
    try:
        data = request.get_json()
        
        # Create sample backtest result
        result = {
            'return_percentage': np.random.uniform(-5, 15),  # Random return between -5% and 15%
            'total_trades': np.random.randint(10, 100),
            'winning_trades': np.random.randint(5, 70),
            'max_drawdown': np.random.uniform(1, 8)
        }
        
        # Save backtest result
        backtest = Backtest(
            name=data.get('name', 'Test Backtest'),
            symbol=data.get('symbol', 'RELIANCE'),
            timeframe=data.get('timeframe', '5minute'),
            return_percentage=result['return_percentage'],
            total_trades=result['total_trades'],
            strategy_id=data.get('strategy_id')
        )
        
        db.session.add(backtest)
        db.session.commit()
        
        return jsonify({
            'message': 'Backtest completed',
            'backtest_id': backtest.id,
            'results': result
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/kite/status')
def kite_status():
    """Get Kite API connection status"""
    try:
        kite_connected, status_message = test_kite_connection()
        return jsonify({
            'connected': kite_connected,
            'status': status_message,
            'available': KITE_AVAILABLE,
            'last_checked': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'status': f'Error: {str(e)}',
            'available': KITE_AVAILABLE,
            'last_checked': datetime.now().isoformat()
        }), 500

@app.route('/api/kite/refresh', methods=['POST'])
def refresh_kite_connection():
    """Refresh Kite API connection"""
    try:
        if not KITE_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'Kite modules not available'
            }), 400
        
        # Test connection
        kite_connected, status_message = test_kite_connection()
        
        return jsonify({
            'success': kite_connected,
            'message': status_message,
            'connected': kite_connected,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing connection: {str(e)}',
            'connected': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/data/symbols')
def get_symbols():
    """Get available symbols"""
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'HINDUNILVR', 'ITC', 'LT', 'KOTAKBANK']
    return jsonify({'symbols': symbols})

@app.route('/api/data/historical/<symbol>')
def get_historical_data(symbol):
    """Get historical data for symbol"""
    try:
        timeframe = request.args.get('timeframe', '5minute')
        days = int(request.args.get('days', 30))
        
        print(f"📊 Fetching {days} days of {timeframe} data for {symbol}")
        
        # Try to get real data from Kite API
        real_data = None
        if KITE_AVAILABLE:
            try:
                kite = connect_to_kite()
                if kite:
                    from datetime import datetime, timedelta
                    import pandas as pd
                    
                    # Convert timeframe to Kite format
                    kite_timeframe = {
                        '1minute': 'minute',
                        '5minute': '5minute', 
                        '15minute': '15minute',
                        'day': 'day'
                    }.get(timeframe, '5minute')
                    
                    # Calculate date range
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=days)
                    
                    # Get instrument token for the symbol
                    # Note: This is a simplified approach - in production you'd have a proper instrument mapping
                    try:
                        # Try to fetch data (this will work if symbol format is correct)
                        historical_data = kite.historical_data(
                            instrument_token=f"NSE:{symbol}",  # Simplified - should be actual token
                            from_date=from_date,
                            to_date=to_date,
                            interval=kite_timeframe
                        )
                        
                        real_data = [
                            {
                                'date': candle['date'].isoformat(),
                                'open': candle['open'],
                                'high': candle['high'], 
                                'low': candle['low'],
                                'close': candle['close'],
                                'volume': candle['volume']
                            } for candle in historical_data
                        ]
                        print(f"✅ Retrieved {len(real_data)} real data points from Kite API")
                        
                    except Exception as e:
                        print(f"⚠️ Error fetching real data: {e}")
                        
            except Exception as e:
                print(f"⚠️ Kite API error: {e}")
        
        # If real data available, return it
        if real_data:
            return jsonify({
                'symbol': symbol,
                'timeframe': timeframe,
                'data': real_data,
                'source': 'kite_api',
                'message': f'Real data from Kite API ({len(real_data)} records)'
            })
        
        # Generate sample data for demo
        print(f"📝 Generating sample data for demo")
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='5T')
        
        data = []
        base_price = 100 + np.random.randint(0, 1000)
        
        for i, date in enumerate(dates):
            if i == 0:
                open_price = base_price
            else:
                open_price = data[-1]['close']
            
            change = np.random.normal(0, 0.02)
            close_price = open_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'date': date.isoformat(),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
        
        return jsonify({
            'symbol': symbol,
            'timeframe': timeframe,
            'data': data[-200:],  # Return last 200 points
            'source': 'sample_data',
            'message': f'Sample data for demo ({len(data[-200:])} records)'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    print('Client connected')
    emit('status', {'msg': 'Connected to trading platform'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample data if empty
        if Strategy.query.count() == 0:
            sample_strategies = [
                Strategy(name='MA Crossover', description='5/20 MA crossover strategy', strategy_type='technical'),
                Strategy(name='RSI Strategy', description='RSI mean reversion', strategy_type='technical'),
                Strategy(name='ML Predictor', description='Random Forest price prediction', strategy_type='ml')
            ]
            
            for strategy in sample_strategies:
                db.session.add(strategy)
            
            db.session.commit()
            print("Sample strategies created!")
    
    print("🚀 Starting Trading Platform Backend...")
    print("📊 Backend running on http://localhost:5000")
    print("🔌 WebSocket ready for real-time updates")
    print("💾 Database initialized with sample data")
    
    if KITE_AVAILABLE:
        print("📈 Kite API integration available")
    else:
        print("⚠️  Kite API not available - running in demo mode")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)