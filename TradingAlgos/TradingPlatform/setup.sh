#!/bin/bash

# Advanced Trading Platform Setup Script
# This script sets up the complete trading platform with ML capabilities

echo "🚀 Setting up Advanced Trading Platform..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create database
    print_status "Setting up database..."
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
    
    print_success "Backend setup completed!"
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cat > .env << EOL
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=http://localhost:5000
REACT_APP_APP_NAME=Trading Platform
REACT_APP_VERSION=1.0.0
EOL
        print_success "Environment file created"
    fi
    
    print_success "Frontend setup completed!"
    cd ..
}

# Create sample data
create_sample_data() {
    print_status "Creating sample data..."
    
    cd backend
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    python -c "
import sys
sys.path.append('.')
from app.models import *
from app import app
import json
from datetime import datetime

with app.app_context():
    # Create sample user
    user = User(
        username='demo_user',
        email='demo@example.com',
        password_hash='demo_hash'
    )
    db.session.add(user)
    db.session.commit()
    
    # Create sample strategies
    strategies = [
        {
            'name': 'MA Crossover Strategy',
            'description': 'Simple moving average crossover strategy',
            'strategy_type': 'technical',
            'config': json.dumps({
                'short_ma': 5,
                'long_ma': 20,
                'timeframe': '5minute'
            }),
            'user_id': user.id
        },
        {
            'name': 'RSI Mean Reversion',
            'description': 'RSI-based mean reversion strategy',
            'strategy_type': 'technical',
            'config': json.dumps({
                'rsi_period': 14,
                'oversold': 30,
                'overbought': 70,
                'timeframe': '5minute'
            }),
            'user_id': user.id
        },
        {
            'name': 'ML Price Prediction',
            'description': 'Machine learning price prediction model',
            'strategy_type': 'ml',
            'config': json.dumps({
                'model_type': 'random_forest',
                'features': ['SMA_20', 'RSI', 'MACD'],
                'target': 'price_direction'
            }),
            'user_id': user.id
        }
    ]
    
    for strategy_data in strategies:
        strategy = Strategy(**strategy_data)
        db.session.add(strategy)
    
    db.session.commit()
    print('Sample data created successfully!')
"
    
    print_success "Sample data created!"
    cd ..
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend startup script
    cat > start_backend.sh << 'EOL'
#!/bin/bash
echo "🚀 Starting Trading Platform Backend..."
cd backend
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
python app.py
EOL
    chmod +x start_backend.sh
    
    # Frontend startup script
    cat > start_frontend.sh << 'EOL'
#!/bin/bash
echo "🎨 Starting Trading Platform Frontend..."
cd frontend
npm start
EOL
    chmod +x start_frontend.sh
    
    # Combined startup script
    cat > start_platform.sh << 'EOL'
#!/bin/bash
echo "🚀 Starting Complete Trading Platform..."
echo "Backend will start on http://localhost:5000"
echo "Frontend will start on http://localhost:3000"
echo ""

# Start backend in background
./start_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
./start_frontend.sh &
FRONTEND_PID=$!

echo "Platform started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOL
    chmod +x start_platform.sh
    
    print_success "Startup scripts created!"
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    check_python
    check_node
    setup_backend
    setup_frontend
    create_sample_data
    create_startup_scripts
    
    echo ""
    echo "================================================"
    print_success "🎉 Trading Platform setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure your Kite API credentials in backend/config.py"
    echo "2. Start the platform with: ./start_platform.sh"
    echo "3. Open http://localhost:3000 in your browser"
    echo ""
    echo "🔧 Individual services:"
    echo "• Backend only: ./start_backend.sh"
    echo "• Frontend only: ./start_frontend.sh"
    echo ""
    echo "📚 Features available:"
    echo "• 📊 Interactive Dashboard"
    echo "• ⚙️ Visual Strategy Builder"
    echo "• 🤖 Machine Learning Models"
    echo "• 📈 Advanced Backtesting"
    echo "• 💼 Portfolio Management"
    echo "• 🔔 Real-time Alerts"
    echo ""
    print_success "Happy Trading! 🚀"
}

# Run main function
main