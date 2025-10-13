@echo off
REM AstraCharts Complete Application Startup Script for Windows
REM Starts both backend and frontend simultaneously

echo 🚀 Starting AstraCharts Trading Platform
echo ========================================

REM Check if setup has been run
if not exist backend\venv (
    echo ❌ Backend setup not completed. Running setup first...
    call setup.bat
)

if not exist frontend\node_modules (
    echo ❌ Frontend setup not completed. Running setup first...
    call setup.bat
)

echo 🔧 Starting Backend Service...
start "AstraCharts Backend" /min start-backend.bat

echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo 🎨 Starting Frontend Service...
start "AstraCharts Frontend" /min start-frontend.bat

echo ⏳ Waiting for frontend to initialize...
timeout /t 10 /nobreak >nul

echo ✅ Services started successfully!
echo ================================
echo
echo 🎉 AstraCharts Trading Platform is now running!
echo ==============================================
echo
echo 📡 Services Available:
echo    🔧 Backend API:        http://localhost:8000
echo    📚 API Documentation:  http://localhost:8000/docs
echo    🎨 Frontend App:       http://localhost:3000
echo
echo 🔍 Check the opened windows for service status
echo 🛑 Close the service windows to stop the application
echo
echo Press any key to open the application in your browser...
pause >nul

REM Open browser to frontend
start http://localhost:3000