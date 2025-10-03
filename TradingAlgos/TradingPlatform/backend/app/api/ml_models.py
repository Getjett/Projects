"""
ML Models API
REST endpoints for machine learning model management
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import traceback

# Import your existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from app.models import MLModel, db
    from app.ml.ml_engine import MLModelEngine, FeatureEngineering
except ImportError:
    # Fallback for development
    pass

bp = Blueprint('ml_models', __name__)

# Global ML engine instance
ml_engine = MLModelEngine()

@bp.route('/models', methods=['GET'])
def get_models():
    """Get all ML models for user"""
    try:
        # In production, filter by user_id
        models = MLModel.query.all()
        
        models_data = []
        for model in models:
            models_data.append({
                'id': model.id,
                'name': model.name,
                'model_type': model.model_type,
                'symbol': model.symbol,
                'timeframe': model.timeframe,
                'status': model.status,
                'accuracy': model.accuracy,
                'created_at': model.created_at.isoformat() if model.created_at else None,
                'trained_at': model.trained_at.isoformat() if model.trained_at else None
            })
        
        return jsonify({'models': models_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/models', methods=['POST'])
def create_model():
    """Create new ML model"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'model_type', 'symbol', 'timeframe']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create model record
        ml_model = MLModel(
            name=data['name'],
            model_type=data['model_type'],
            symbol=data['symbol'],
            timeframe=data['timeframe'],
            config=data.get('config', '{}'),
            features=data.get('features', '[]'),
            target=data.get('target', 'price_direction'),
            user_id=1  # In production, get from session
        )
        
        db.session.add(ml_model)
        db.session.commit()
        
        return jsonify({
            'message': 'Model created successfully',
            'model_id': ml_model.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/models/<int:model_id>/train', methods=['POST'])
def train_model(model_id):
    """Train ML model in background"""
    try:
        ml_model = MLModel.query.get_or_404(model_id)
        data = request.get_json()
        
        # Start training in background thread
        thread = threading.Thread(
            target=_train_model_background,
            args=(model_id, data)
        )
        thread.daemon = True
        thread.start()
        
        # Update status to training
        ml_model.status = 'training'
        ml_model.training_progress = 0.0
        db.session.commit()
        
        return jsonify({
            'message': 'Model training started',
            'model_id': model_id,
            'status': 'training'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _train_model_background(model_id, config):
    """Background function to train ML model"""
    try:
        with db.app.app_context():
            ml_model = MLModel.query.get(model_id)
            
            # Simulate getting training data (replace with actual data fetching)
            # In production, fetch from your Kite API or database
            sample_data = _generate_sample_data()
            
            # Create target variable (price direction)
            sample_data['target'] = (sample_data['close'].shift(-1) > sample_data['close']).astype(int)
            sample_data = sample_data.dropna()
            
            # Prepare data
            X_train, X_test, y_train, y_test, feature_cols = ml_engine.prepare_data(
                sample_data, target_column='target'
            )
            
            # Update progress
            ml_model.training_progress = 0.3
            db.session.commit()
            
            # Train model based on type
            if ml_model.model_type == 'random_forest':
                model = ml_engine.train_random_forest(
                    X_train, y_train, 
                    task_type=config.get('task_type', 'classification')
                )
            elif ml_model.model_type == 'xgboost':
                model = ml_engine.train_xgboost(
                    X_train, y_train,
                    task_type=config.get('task_type', 'classification')
                )
            elif ml_model.model_type == 'svm':
                model = ml_engine.train_svm(
                    X_train, y_train,
                    task_type=config.get('task_type', 'classification')
                )
            elif ml_model.model_type == 'lstm':
                model, history = ml_engine.train_lstm(X_train, y_train)
            else:
                raise ValueError(f"Unsupported model type: {ml_model.model_type}")
            
            # Update progress
            ml_model.training_progress = 0.7
            db.session.commit()
            
            # Evaluate model
            metrics, predictions = ml_engine.evaluate_model(
                model, X_test, y_test,
                task_type=config.get('task_type', 'classification')
            )
            
            # Save model
            model_path = ml_engine.save_model(
                model, f"model_{model_id}",
                model_type='tensorflow' if ml_model.model_type == 'lstm' else 'sklearn'
            )
            
            # Update model record with results
            ml_model.status = 'trained'
            ml_model.training_progress = 1.0
            ml_model.model_path = model_path
            ml_model.trained_at = datetime.utcnow()
            
            # Update metrics
            if 'accuracy' in metrics:
                ml_model.accuracy = metrics['accuracy']
                ml_model.precision = metrics.get('precision')
                ml_model.recall = metrics.get('recall')
                ml_model.f1_score = metrics.get('f1_score')
            else:
                ml_model.mse = metrics.get('mse')
                ml_model.mae = metrics.get('mae')
            
            db.session.commit()
            
            # Emit WebSocket event for real-time updates
            # socketio.emit('model_training_complete', {
            #     'model_id': model_id,
            #     'status': 'trained',
            #     'metrics': metrics
            # })
            
    except Exception as e:
        with db.app.app_context():
            ml_model = MLModel.query.get(model_id)
            ml_model.status = 'failed'
            ml_model.error_message = str(e)
            db.session.commit()
            
        print(f"Error training model {model_id}: {str(e)}")
        print(traceback.format_exc())

@bp.route('/models/<int:model_id>/predict', methods=['POST'])
def predict_with_model(model_id):
    """Make predictions with trained model"""
    try:
        ml_model = MLModel.query.get_or_404(model_id)
        
        if ml_model.status != 'trained':
            return jsonify({'error': 'Model is not trained yet'}), 400
        
        data = request.get_json()
        
        # Load model
        model = ml_engine.load_model(
            f"model_{model_id}",
            model_type='tensorflow' if ml_model.model_type == 'lstm' else 'sklearn'
        )
        
        # Get prediction data (in production, this would come from real market data)
        prediction_data = _generate_sample_data(rows=1)
        
        # Add features
        prediction_data = FeatureEngineering.add_technical_indicators(prediction_data)
        prediction_data = FeatureEngineering.add_pattern_features(prediction_data)
        
        # Select same features used in training
        if ml_engine.feature_columns:
            prediction_data = prediction_data[ml_engine.feature_columns]
        
        # Make prediction
        prediction = ml_engine.predict(model, prediction_data)
        
        return jsonify({
            'model_id': model_id,
            'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.85  # In production, calculate actual confidence
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete ML model"""
    try:
        ml_model = MLModel.query.get_or_404(model_id)
        
        # Delete model files
        if ml_model.model_path and os.path.exists(ml_model.model_path):
            os.remove(ml_model.model_path)
        
        # Delete from database
        db.session.delete(ml_model)
        db.session.commit()
        
        return jsonify({'message': 'Model deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/feature-importance/<int:model_id>')
def get_feature_importance(model_id):
    """Get feature importance for trained model"""
    try:
        ml_model = MLModel.query.get_or_404(model_id)
        
        if ml_model.status != 'trained':
            return jsonify({'error': 'Model is not trained yet'}), 400
        
        # Load model
        model = ml_engine.load_model(f"model_{model_id}")
        
        # Get feature importance
        importance_df = ml_engine.get_feature_importance(model, ml_engine.feature_columns)
        
        if importance_df is not None:
            return jsonify({
                'feature_importance': importance_df.to_dict('records')
            })
        else:
            return jsonify({'message': 'Feature importance not available for this model type'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _generate_sample_data(rows=1000):
    """Generate sample market data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=rows, freq='5T')
    
    # Generate realistic OHLCV data
    base_price = 100
    data = []
    
    for i, date in enumerate(dates):
        if i == 0:
            open_price = base_price
        else:
            open_price = data[-1]['close']
        
        # Random walk with some trend
        change = np.random.normal(0, 0.02)
        close_price = open_price * (1 + change)
        
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(data)