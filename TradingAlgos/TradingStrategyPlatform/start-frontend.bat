@echo off
REM AstraCharts Frontend Startup Script for Windows

echo 🎨 Starting AstraCharts Frontend...

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo ❌ Node modules not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Killing any existing frontend processes...
taskkill /f /im node.exe /fi "WINDOWTITLE eq *npm*" >nul 2>&1

echo Starting React development server...
set BROWSER=none
npm start