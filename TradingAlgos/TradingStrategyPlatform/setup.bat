@echo off
REM AstraCharts Trading Platform Setup Script for Windows
REM This script sets up all dependencies for the AstraCharts Trading Platform

echo 🔧 AstraCharts Trading Platform Setup
echo ====================================

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    exit /b 1
)

echo ✅ Python found

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    exit /b 1
)

echo ✅ Node.js found

REM Check npm installation
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed or not in PATH
    echo Please install Node.js with npm from https://nodejs.org
    exit /b 1
)

echo ✅ npm found

REM Setup Backend
echo 🐍 Setting up Backend Environment...
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

cd ..

REM Setup Frontend
echo 📦 Setting up Frontend Environment...
cd frontend

echo Installing Node.js dependencies...
npm install --legacy-peer-deps

echo Installing additional dependencies...
npm install ajv@^8.0.0 --legacy-peer-deps

cd ..

echo ✅ Setup completed successfully!
echo ==================================
echo
echo 🚀 To start the application, run:
echo    start.bat
echo
echo 🔧 To start individual services:
echo    start-backend.bat
echo    start-frontend.bat