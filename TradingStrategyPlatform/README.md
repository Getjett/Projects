# 📊 Universal Trading Strategy Platform

A comprehensive web-based trading strategy platform supporting multiple asset classes including Index Options, Equity, Commodities, Currency, and Futures.

## 🎯 Features

- **Multi-Asset Support**: Trade strategies for Options, Equity, Commodities, Currency, and Futures
- **Strategy Builder**: Create custom strategies with 70+ parameters
- **Backtesting Engine**: Test strategies on historical data
- **Pattern Creator**: Build and test candlestick patterns
- **Real-time Analytics**: Comprehensive performance metrics and visualizations
- **Multi-Instrument Portfolio**: Manage strategies across different instruments

## 📁 Project Structure

```
TradingStrategyPlatform/
├── backend/                 # Backend API (Flask/FastAPI)
│   ├── api/                # API endpoints
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── strategies/         # Strategy execution engine
│   ├── backtesting/        # Backtesting engine
│   ├── data/               # Data fetching and processing
│   └── config/             # Configuration files
│
├── frontend/               # Frontend UI (React/Vue)
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # State management
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
│
├── database/               # Database scripts
│   ├── schema.sql          # Database schema
│   ├── migrations/         # Migration scripts
│   └── seeds/              # Seed data
│
├── docs/                   # Documentation
│   ├── WEB_INTERFACE_SPECIFICATION.md
│   ├── API_DOCUMENTATION.md
│   └── USER_GUIDE.md
│
└── docker/                 # Docker configuration
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Database Setup

```bash
cd database
psql -U postgres -f schema.sql
```

## 📚 Documentation

- [Web Interface Specification](docs/WEB_INTERFACE_SPECIFICATION.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [User Guide](docs/USER_GUIDE.md)

## 🛠 Technology Stack

### Frontend
- React.js 18+ with TypeScript
- Material-UI (MUI)
- Chart.js / TradingView Widgets
- Redux Toolkit
- Axios

### Backend
- FastAPI (Python 3.10+)
- PostgreSQL 14+ with TimescaleDB
- Redis for caching
- Celery for background jobs
- Kite Connect API integration

### DevOps
- Docker & Docker Compose
- GitHub Actions for CI/CD
- AWS/DigitalOcean for deployment

## 📊 Supported Instruments

### Index Options
- NIFTY (Nifty 50)
- BANKNIFTY (Bank Nifty)
- FINNIFTY (Fin Nifty)
- MIDCPNIFTY (Midcap Nifty)

### Equity (NSE/BSE)
- All NSE/BSE listed stocks
- Sector-wise filtering
- Custom watchlists

### Commodities (MCX)
- **Bullion**: Gold, Silver
- **Energy**: Crude Oil, Natural Gas
- **Agriculture**: Cardamom, Cotton, Mentha Oil
- **Base Metals**: Copper, Zinc, Nickel, Lead, Aluminium

### Currency (CDS)
- USD/INR, EUR/INR, GBP/INR, JPY/INR

### Futures
- Index Futures (Nifty, Bank Nifty)
- Stock Futures

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- API rate limiting
- HTTPS only
- Input sanitization
- SQL injection prevention

## 📈 Development Roadmap

### Phase 1 (MVP) - Completed ✅
- User authentication
- Basic strategy builder
- Backtesting engine
- Results visualization

### Phase 2 (In Progress) 🚧
- Advanced filters
- Pattern creator
- Multi-instrument support
- Real-time data integration

### Phase 3 (Planned) 📋
- Paper trading
- Live trading integration
- Alerts & notifications
- Portfolio management

## 👥 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📝 License

This project is licensed under the MIT License.

## 📞 Support

For support, email support@tradingstrategy.com or join our community forum.

---

**Version**: 1.0.0  
**Last Updated**: October 4, 2025  
**Status**: Active Development
