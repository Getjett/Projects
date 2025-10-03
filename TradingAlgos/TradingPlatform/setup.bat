@echo off
REM Windows Batch Script for Trading Platform Setup

echo ========================================
echo 🚀 Trading Platform Setup (Windows)
echo ========================================
echo.

REM Check if Python is installed
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://python.org
    pause
    exit /b 1
)
echo [SUCCESS] Python found

REM Check if Node.js is installed
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher from https://nodejs.org
    pause
    exit /b 1
)
echo [SUCCESS] Node.js found

REM Setup Backend
echo.
echo [INFO] Setting up backend...
cd backend

REM Create virtual environment
echo [INFO] Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Setup database
echo [INFO] Setting up database...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created!')"

echo [SUCCESS] Backend setup completed!
cd ..

REM Setup Frontend
echo.
echo [INFO] Setting up frontend...
cd frontend

REM Install npm dependencies
echo [INFO] Installing Node.js dependencies...
npm install

REM Create environment file
echo [INFO] Creating environment file...
if not exist .env (
    echo REACT_APP_API_URL=http://localhost:5000/api > .env
    echo REACT_APP_WS_URL=http://localhost:5000 >> .env
    echo REACT_APP_APP_NAME=Trading Platform >> .env
    echo REACT_APP_VERSION=1.0.0 >> .env
    echo [SUCCESS] Environment file created
)

echo [SUCCESS] Frontend setup completed!
cd ..

REM Create startup scripts
echo.
echo [INFO] Creating startup scripts...

REM Backend startup script
echo @echo off > start_backend.bat
echo echo 🚀 Starting Trading Platform Backend... >> start_backend.bat
echo cd backend >> start_backend.bat
echo call venv\Scripts\activate.bat >> start_backend.bat
echo python app.py >> start_backend.bat

REM Frontend startup script
echo @echo off > start_frontend.bat
echo echo 🎨 Starting Trading Platform Frontend... >> start_frontend.bat
echo cd frontend >> start_frontend.bat
echo npm start >> start_frontend.bat

REM Combined startup script
echo @echo off > start_platform.bat
echo echo 🚀 Starting Complete Trading Platform... >> start_platform.bat
echo echo Backend will start on http://localhost:5000 >> start_platform.bat
echo echo Frontend will start on http://localhost:3000 >> start_platform.bat
echo echo. >> start_platform.bat
echo start /b start_backend.bat >> start_platform.bat
echo timeout /t 5 /nobreak ^>nul >> start_platform.bat
echo start start_frontend.bat >> start_platform.bat

echo [SUCCESS] Startup scripts created!

REM Final message
echo.
echo ========================================
echo [SUCCESS] 🎉 Trading Platform setup completed!
echo ========================================
echo.
echo 📋 Next steps:
echo 1. Configure your Kite API credentials in backend\config.py
echo 2. Start the platform with: start_platform.bat
echo 3. Open http://localhost:3000 in your browser
echo.
echo 🔧 Individual services:
echo • Backend only: start_backend.bat
echo • Frontend only: start_frontend.bat
echo.
echo 📚 Features available:
echo • 📊 Interactive Dashboard
echo • ⚙️ Visual Strategy Builder  
echo • 🤖 Machine Learning Models
echo • 📈 Advanced Backtesting
echo • 💼 Portfolio Management
echo • 🔔 Real-time Alerts
echo.
echo [SUCCESS] Happy Trading! 🚀
echo.
pause