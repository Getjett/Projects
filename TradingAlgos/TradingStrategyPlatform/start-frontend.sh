#!/bin/bash

# AstraCharts Frontend Startup Script

set -e

echo "🎨 Starting AstraCharts Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run setup.sh first."
    exit 1
fi

# Check if React scripts are available
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo "❌ React scripts not installed. Please run setup.sh first."
    exit 1
fi

echo "✅ Dependencies found"
echo "🚀 Starting React development server..."
echo ""
echo "🌐 Frontend will be available at:"
echo "   - Application: http://localhost:3000"
echo ""
echo "📝 Note: The development server will automatically open your browser"
echo "Press Ctrl+C to stop the server"
echo ""

# Set environment variable to prevent automatic browser opening in headless environments
export BROWSER=none

# Start the React development server
npm start