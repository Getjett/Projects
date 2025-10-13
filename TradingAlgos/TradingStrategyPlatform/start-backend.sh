#!/bin/bash

# AstraCharts Backend Startup Script

set -e

echo "🔧 Starting AstraCharts Backend..."

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" &> /dev/null; then
    echo "❌ Dependencies not installed. Please run setup.sh first."
    exit 1
fi

echo "✅ Virtual environment activated"
echo "🚀 Starting FastAPI server..."
echo ""
echo "📡 Backend will be available at:"
echo "   - API: http://localhost:8000"
echo "   - Documentation: http://localhost:8000/docs"
echo "   - Interactive API: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload