#!/bin/bash

# AstraCharts Complete Application Startup Script
# Starts both backend and frontend simultaneously

set -e

echo "🚀 Starting AstraCharts Trading Platform"
echo "========================================"

# Check if setup has been run
if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
    echo "❌ Setup not completed. Running setup first..."
    ./setup.sh
fi

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM EXIT

echo "🔧 Starting Backend Service..."
# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend started successfully (PID: $BACKEND_PID)"

echo "🎨 Starting Frontend Service..."
# Start frontend in background
./start-frontend.sh &
FRONTEND_PID=$!

echo "⏳ Waiting for frontend to initialize..."
sleep 10

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
echo ""
echo "🎉 AstraCharts Trading Platform is now running!"
echo "=============================================="
echo ""
echo "📡 Services Available:"
echo "   🔧 Backend API:        http://localhost:8000"
echo "   📚 API Documentation:  http://localhost:8000/docs"
echo "   🎨 Frontend App:       http://localhost:3000"
echo ""
echo "🔍 Service Status:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interruption
wait