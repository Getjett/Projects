# AstraCharts Trading Platform

A comprehensive algorithmic trading platform with advanced charting, backtesting, and strategy optimization capabilities.

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - [Download Python](https://python.org)
- **Node.js 16+** - [Download Node.js](https://nodejs.org)
- **npm** (comes with Node.js)

### Setup & Launch

#### Linux/macOS
```bash
# Clone or extract the project
cd TradingStrategyPlatform

# Setup (run once)
./setup.sh

# Start application
./start.sh
```

#### Windows
```cmd
# Clone or extract the project
cd TradingStrategyPlatform

# Setup (run once)
setup.bat

# Start application
start.bat
```

### Manual Startup (if needed)

#### Backend Only
```bash
# Linux/macOS
./start-backend.sh

# Windows
start-backend.bat
```

#### Frontend Only
```bash
# Linux/macOS
./start-frontend.sh

# Windows
start-frontend.bat
```

## 📡 Access Points

Once running, access the application at:

- **🎨 Frontend Application**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

### Backend (FastAPI + Python)
- RESTful API with automatic documentation
- Advanced chart visualization with Plotly.js
- Asynchronous backtesting with Celery
- Comprehensive strategy management
- Real-time data processing

### Frontend (React + TypeScript)
- Modern React with TypeScript
- Interactive charts with Plotly.js
- Responsive design
- Real-time updates
- Strategy configuration interface

## 🔧 Troubleshooting

### Common Issues

**Port Already in Use**
- Backend (8000): The setup scripts automatically kill existing processes
- Frontend (3000): The setup scripts handle this automatically

**Dependencies Issues**
- Run setup script again: `./setup.sh` (Linux/macOS) or `setup.bat` (Windows)
- For Node.js issues, delete `frontend/node_modules` and run setup again

**Permission Issues (Linux/macOS)**
```bash
chmod +x *.sh
```

**Python Virtual Environment Issues**
```bash
# Delete and recreate
rm -rf backend/venv
./setup.sh
```

## 📁 Project Structure

```
TradingStrategyPlatform/
├── backend/              # FastAPI backend
│   ├── main.py          # API entry point
│   ├── chart_visualization.py  # Plotly chart generation
│   ├── async_processing.py    # Celery async tasks
│   ├── requirements.txt # Python dependencies
│   └── venv/           # Virtual environment
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── package.json    # Node.js dependencies
│   └── node_modules/   # Installed packages
├── setup.sh/.bat       # Automated setup
├── start.sh/.bat       # Complete application launcher
├── start-backend.sh/.bat   # Backend launcher
└── start-frontend.sh/.bat  # Frontend launcher
```

## 🎯 Features

- **📊 Advanced Charting**: Interactive candlestick charts with technical indicators
- **🔄 Backtesting**: Historical strategy testing with performance metrics
- **⚡ Async Processing**: Non-blocking strategy execution with Celery
- **🎨 Modern UI**: Responsive React interface with TypeScript
- **📈 Strategy Management**: Create, test, and optimize trading strategies
- **📱 Real-time Updates**: Live chart updates and trade execution
- **🔧 API Documentation**: Automatic OpenAPI/Swagger documentation

## 💡 Usage Tips

1. **First Time Setup**: Always run the setup script before starting
2. **Regular Use**: Just use `start.sh` or `start.bat` to launch everything
3. **Development**: Use individual service scripts for backend-only or frontend-only work
4. **Stopping**: Press Ctrl+C in the terminal (Linux/macOS) or close windows (Windows)

## 🆘 Support

If you encounter issues:

1. Check that all prerequisites are installed
2. Run the setup script again
3. Check the terminal/command prompt for error messages
4. Ensure ports 3000 and 8000 are available
5. For Windows users, run Command Prompt as Administrator if needed