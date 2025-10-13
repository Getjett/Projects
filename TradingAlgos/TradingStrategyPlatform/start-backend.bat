@echo off
REM AstraCharts Backend Startup Script for Windows

echo 🐍 Starting AstraCharts Backend...

cd backend

REM Check if virtual environment exists
if not exist venv (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Killing any existing backend processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *uvicorn*" >nul 2>&1

echo Starting FastAPI server...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload