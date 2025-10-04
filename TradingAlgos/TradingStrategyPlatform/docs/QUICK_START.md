# Universal Trading Strategy Platform - Quick Start Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **PostgreSQL 14+** (Database)
- **Redis 7+** (Caching & Background Jobs)
- **Git** (Version Control)

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
cd "d:\New folder\Projects\TradingStrategyPlatform"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv
```

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

#### Install Requirements

```bash
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy example env file
Copy-Item .env.example -Destination .env

# Edit .env file with your settings
notepad .env
```

**Update these critical settings:**
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: Generate a secure random key
- `KITE_API_KEY`: Your Zerodha Kite API key
- `KITE_API_SECRET`: Your Zerodha Kite API secret

### 3. Database Setup

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE trading_platform;

# Exit psql
\q
```

#### Run Schema

```bash
cd ..\database
psql -U postgres -d trading_platform -f schema.sql
```

### 4. Redis Setup

#### Install Redis (Windows)

Download from: https://github.com/microsoftarchive/redis/releases

Or use WSL/Docker:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### Verify Redis

```bash
redis-cli ping
# Should return: PONG
```

### 5. Frontend Setup

```bash
cd ..\frontend
npm install
```

### 6. Run the Application

#### Start Backend (Terminal 1)

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python app.py
```

Backend will run on: http://localhost:8000

#### Start Frontend (Terminal 2)

```bash
cd frontend
npm start
```

Frontend will run on: http://localhost:3000

#### Start Celery Worker (Terminal 3) - For Background Jobs

```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A tasks.celery worker --loglevel=info --pool=solo
```

## 🎯 First Steps

### 1. Access the Application

Open your browser and navigate to: http://localhost:3000

### 2. Login with Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change the admin password immediately after first login!

### 3. Configure Kite Connect API

1. Go to **Settings** → **API Configuration**
2. Enter your Kite API credentials
3. Click **Connect to Kite**
4. Authorize the application

### 4. Create Your First Strategy

1. Navigate to **Strategy Builder**
2. Select **Instrument** (e.g., BANKNIFTY Options)
3. Configure **Entry Logic** (e.g., Second Bar Breakout)
4. Set **Risk Management** (Stop Loss, Target)
5. Click **Save Strategy**

### 5. Run Your First Backtest

1. Open your saved strategy
2. Click **Run Backtest**
3. Select **Date Range** (e.g., Last 3 Months)
4. Click **Start Backtest**
5. View results and analytics

## 📊 Testing the System

### Test Database Connection

```bash
cd backend
python -c "from config.settings import settings; print(settings.DATABASE_URL)"
```

### Test API Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### Test Frontend

Navigate to: http://localhost:3000

You should see the login page.

## 🔧 Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Database Connection Error

**Issue**: `psycopg2.OperationalError: connection refused`

**Solution**:
1. Ensure PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Verify database exists: `psql -U postgres -l`

### Redis Connection Error

**Issue**: `redis.exceptions.ConnectionError`

**Solution**:
1. Ensure Redis is running: `redis-cli ping`
2. Check `REDIS_HOST` and `REDIS_PORT` in `.env`

### Frontend Build Error

**Issue**: `npm ERR! missing script: start`

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

### Port Already in Use

**Issue**: `Error: listen EADDRINUSE: address already in use :::8000`

**Solution**:

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

## 📚 Next Steps

1. **Read Documentation**
   - [Web Interface Specification](docs/WEB_INTERFACE_SPECIFICATION.md)
   - [API Documentation](docs/API_DOCUMENTATION.md)
   - [User Guide](docs/USER_GUIDE.md)

2. **Explore Features**
   - Create strategies for different instruments
   - Test with various parameters
   - Analyze backtest results
   - Create custom patterns (coming soon)

3. **Join Community**
   - Report bugs on GitHub
   - Request features
   - Share your strategies

## 🎓 Learning Resources

### Understanding the Platform

- **Strategy Builder**: Configure custom trading strategies
- **Backtesting**: Test strategies on historical data
- **Pattern Creator**: Build custom candlestick patterns (future)
- **Analytics**: View comprehensive performance metrics

### Supported Instruments

- **Index Options**: Nifty, Bank Nifty, Fin Nifty
- **Equity**: All NSE/BSE stocks
- **Commodities**: Gold, Silver, Crude Oil, etc.
- **Currency**: USD/INR, EUR/INR, etc.
- **Futures**: Index and Stock Futures

## 🔒 Security Best Practices

1. **Change Default Passwords**
   - Update admin password immediately
   - Use strong, unique passwords

2. **Secure API Keys**
   - Never commit `.env` file
   - Rotate API keys regularly
   - Use environment variables in production

3. **Database Security**
   - Use strong PostgreSQL passwords
   - Enable SSL connections in production
   - Regular backups

4. **HTTPS in Production**
   - Use SSL certificates
   - Enable HTTPS only
   - Update CORS settings

## 📞 Support

### Get Help

- **Email**: support@tradingstrategy.com
- **Documentation**: Check docs folder
- **GitHub Issues**: Report bugs
- **Community Forum**: Ask questions

### Report Issues

When reporting issues, include:
- Error message
- Steps to reproduce
- System information
- Screenshots (if applicable)

---

**Happy Trading! 🚀📈**

*Last Updated: October 4, 2025*
