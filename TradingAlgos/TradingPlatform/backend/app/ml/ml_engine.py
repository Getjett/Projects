"""
Machine Learning Engine for Trading Platform
Comprehensive ML capabilities including LSTM, Random Forest, XGBoost, and more
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class FeatureEngineering:
    """Advanced feature engineering for trading data"""
    
    @staticmethod
    def add_technical_indicators(df):
        """Add comprehensive technical indicators"""
        df = df.copy()
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
            df[f'EMA_{period}'] = df['close'].ewm(span=period).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        df['BB_width'] = df['BB_upper'] - df['BB_lower']
        df['BB_position'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # Stochastic Oscillator
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        
        # Price-based features
        df['Price_change'] = df['close'].pct_change()
        df['Price_change_2'] = df['close'].pct_change(2)
        df['Price_change_5'] = df['close'].pct_change(5)
        
        # Volume indicators
        df['Volume_SMA'] = df['volume'].rolling(window=20).mean()
        df['Volume_ratio'] = df['volume'] / df['Volume_SMA']
        
        # Volatility
        df['Volatility'] = df['Price_change'].rolling(window=20).std()
        
        # High-Low spread
        df['HL_spread'] = (df['high'] - df['low']) / df['close']
        
        # Return features
        for period in [1, 2, 3, 5, 10]:
            df[f'Return_{period}d'] = df['close'].pct_change(period)
        
        return df
    
    @staticmethod
    def add_pattern_features(df):
        """Add candlestick pattern recognition features"""
        df = df.copy()
        
        # Basic patterns
        df['Doji'] = abs(df['close'] - df['open']) <= (df['high'] - df['low']) * 0.1
        df['Hammer'] = ((df['high'] - df[['open', 'close']].max(axis=1)) <= 
                       (df[['open', 'close']].max(axis=1) - df[['open', 'close']].min(axis=1)) * 0.1) & \
                      ((df[['open', 'close']].min(axis=1) - df['low']) >= 
                       (df[['open', 'close']].max(axis=1) - df[['open', 'close']].min(axis=1)) * 2)
        
        # Trend patterns
        df['Higher_high'] = (df['high'] > df['high'].shift(1)) & (df['high'].shift(1) > df['high'].shift(2))
        df['Lower_low'] = (df['low'] < df['low'].shift(1)) & (df['low'].shift(1) < df['low'].shift(2))
        
        return df
    
    @staticmethod
    def create_sequences(data, sequence_length=60, target_col='close'):
        """Create sequences for LSTM models"""
        X, y = [], []
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(data[i][target_col] if isinstance(data, pd.DataFrame) else data[i])
        return np.array(X), np.array(y)

class MLModelEngine:
    """Main ML engine for training and prediction"""
    
    def __init__(self, model_dir='ml_models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.scaler = None
        self.feature_columns = None
    
    def prepare_data(self, df, target_column='target', test_size=0.2):
        """Prepare data for ML training"""
        # Add features
        df = FeatureEngineering.add_technical_indicators(df)
        df = FeatureEngineering.add_pattern_features(df)
        
        # Remove NaN values
        df = df.dropna()
        
        # Separate features and target
        feature_cols = [col for col in df.columns if col not in ['date', 'timestamp', target_column]]
        X = df[feature_cols]
        y = df[target_column]
        
        # Store feature columns for later use
        self.feature_columns = feature_cols
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, shuffle=False
        )
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def train_random_forest(self, X_train, y_train, task_type='classification', **kwargs):
        """Train Random Forest model"""
        if task_type == 'classification':
            model = RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=42
            )
        else:
            model = RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=42
            )
        
        model.fit(X_train, y_train)
        return model
    
    def train_xgboost(self, X_train, y_train, task_type='classification', **kwargs):
        """Train XGBoost model"""
        if task_type == 'classification':
            model = xgb.XGBClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 6),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=42
            )
        else:
            model = xgb.XGBRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 6),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=42
            )
        
        model.fit(X_train, y_train)
        return model
    
    def train_svm(self, X_train, y_train, task_type='classification', **kwargs):
        """Train SVM model"""
        if task_type == 'classification':
            model = SVC(
                C=kwargs.get('C', 1.0),
                kernel=kwargs.get('kernel', 'rbf'),
                random_state=42
            )
        else:
            model = SVR(
                C=kwargs.get('C', 1.0),
                kernel=kwargs.get('kernel', 'rbf')
            )
        
        model.fit(X_train, y_train)
        return model
    
    def train_lstm(self, X_train, y_train, sequence_length=60, **kwargs):
        """Train LSTM model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models")
        
        # Reshape data for LSTM
        X_train_seq, y_train_seq = FeatureEngineering.create_sequences(
            X_train, sequence_length
        )
        
        # Build LSTM model
        model = Sequential([
            LSTM(kwargs.get('lstm_units', 50), return_sequences=True, 
                 input_shape=(sequence_length, X_train.shape[1])),
            Dropout(kwargs.get('dropout', 0.2)),
            LSTM(kwargs.get('lstm_units', 50), return_sequences=False),
            Dropout(kwargs.get('dropout', 0.2)),
            Dense(kwargs.get('dense_units', 25)),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=kwargs.get('learning_rate', 0.001)),
            loss='mse',
            metrics=['mae']
        )
        
        # Train model
        history = model.fit(
            X_train_seq, y_train_seq,
            batch_size=kwargs.get('batch_size', 32),
            epochs=kwargs.get('epochs', 100),
            validation_split=0.2,
            verbose=0
        )
        
        return model, history
    
    def evaluate_model(self, model, X_test, y_test, task_type='classification'):
        """Evaluate model performance"""
        predictions = model.predict(X_test)
        
        if task_type == 'classification':
            if hasattr(predictions, 'shape') and len(predictions.shape) > 1:
                predictions = np.argmax(predictions, axis=1)
            
            metrics = {
                'accuracy': accuracy_score(y_test, predictions),
                'precision': precision_score(y_test, predictions, average='weighted'),
                'recall': recall_score(y_test, predictions, average='weighted'),
                'f1_score': f1_score(y_test, predictions, average='weighted')
            }
        else:
            metrics = {
                'mse': mean_squared_error(y_test, predictions),
                'mae': mean_absolute_error(y_test, predictions),
                'rmse': np.sqrt(mean_squared_error(y_test, predictions))
            }
        
        return metrics, predictions
    
    def get_feature_importance(self, model, feature_names):
        """Get feature importance from trained model"""
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            return importance_df
        else:
            return None
    
    def save_model(self, model, model_name, model_type='sklearn'):
        """Save trained model"""
        model_path = os.path.join(self.model_dir, f"{model_name}.joblib")
        
        if model_type == 'tensorflow':
            model_path = os.path.join(self.model_dir, f"{model_name}.h5")
            model.save(model_path)
        else:
            joblib.dump(model, model_path)
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.joblib")
        joblib.dump(self.scaler, scaler_path)
        
        return model_path
    
    def load_model(self, model_name, model_type='sklearn'):
        """Load trained model"""
        if model_type == 'tensorflow':
            model_path = os.path.join(self.model_dir, f"{model_name}.h5")
            model = load_model(model_path)
        else:
            model_path = os.path.join(self.model_dir, f"{model_name}.joblib")
            model = joblib.load(model_path)
        
        # Load scaler
        scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.joblib")
        self.scaler = joblib.load(scaler_path)
        
        return model
    
    def predict(self, model, data, model_type='sklearn'):
        """Make predictions with trained model"""
        if self.scaler:
            data_scaled = self.scaler.transform(data)
        else:
            data_scaled = data
        
        predictions = model.predict(data_scaled)
        return predictions

class EnsembleEngine:
    """Ensemble learning for combining multiple models"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
    
    def add_model(self, name, model, weight=1.0):
        """Add model to ensemble"""
        self.models[name] = model
        self.weights[name] = weight
    
    def predict(self, data):
        """Make ensemble predictions"""
        predictions = []
        total_weight = sum(self.weights.values())
        
        for name, model in self.models.items():
            pred = model.predict(data)
            weight = self.weights[name] / total_weight
            predictions.append(pred * weight)
        
        return np.sum(predictions, axis=0)
    
    def update_weights(self, performance_scores):
        """Update model weights based on performance"""
        for name, score in performance_scores.items():
            if name in self.weights:
                self.weights[name] = score

# Example usage and testing
if __name__ == "__main__":
    print("🤖 ML Engine initialized")
    print("Available models: Random Forest, XGBoost, SVM")
    if TENSORFLOW_AVAILABLE:
        print("🧠 Deep Learning models: LSTM, GRU")
    print("📊 Feature engineering: Technical indicators, patterns")
    print("🎯 Ensemble learning: Model combination")