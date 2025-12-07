# Alpha Research

**AI-Powered Investment Research & Quantitative Analysis Platform**

Combining cutting-edge AI research insights with quantitative investment strategies and market data analysis.

---

## 🎯 Project Vision

Alpha Research integrates:
- 📄 **AI Research Papers** - Daily curated summaries from `research-tracker`
- 📊 **Stock Market Data** - Real-time & historical data from multiple sources
- 🧮 **Quantitative Strategies** - Backtesting framework for algorithmic trading
- 💰 **Value Investing** - Fundamental analysis & valuation models
- 📈 **Interactive Dashboard** - Beautiful data visualizations & analytics

---

## 🏗️ Project Structure

```
alpha-research/
├── research/          # AI paper insights & integration
│   ├── sync.py        # Sync from research-tracker database
│   └── analyzer.py    # Extract investment signals from papers
│
├── market/            # Market data fetching & storage
│   ├── fetchers/      # Data sources (Yahoo, Alpha Vantage, etc.)
│   ├── database/      # Market data storage
│   └── models.py      # Data models
│
├── strategies/        # Investment strategies
│   ├── quant/         # Quantitative strategies
│   ├── value/         # Value investing models
│   └── backtest/      # Backtesting engine
│
├── dashboard/         # Web UI
│   ├── frontend/      # React/Vue dashboard
│   └── backend/       # API server
│
├── api/               # REST API
│   ├── routes/        # API endpoints
│   └── middleware/    # Authentication, rate limiting
│
├── data/              # Data storage
│   ├── market/        # Stock data
│   ├── research/      # Synced research papers
│   └── backtest/      # Strategy results
│
├── scripts/           # Utility scripts
│   └── init_db.py     # Database initialization
│
└── tests/             # Unit tests
```

---

## 🚀 Features (Planned)

### Phase 1: Foundation (Current)
- [x] Project structure setup
- [ ] Database design (PostgreSQL/TimescaleDB)
- [ ] Market data fetcher (Yahoo Finance)
- [ ] Basic API endpoints

### Phase 2: Research Integration
- [ ] Sync AI papers from research-tracker
- [ ] Display papers in dashboard
- [ ] Extract investment themes from summaries
- [ ] Link papers to relevant stocks/sectors

### Phase 3: Quantitative Strategies
- [ ] Backtesting framework
- [ ] Momentum strategies
- [ ] Mean reversion strategies
- [ ] Factor models (Fama-French)

### Phase 4: Value Investing
- [ ] Fundamental data integration
- [ ] DCF calculator
- [ ] Graham's value metrics
- [ ] Buffett-style analysis

### Phase 5: Dashboard
- [ ] Stock screener
- [ ] Portfolio tracker
- [ ] Strategy performance charts
- [ ] Research paper feed

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (API server)
- PostgreSQL / SQLite (time-series data)
- SQLAlchemy (ORM)
- Pandas, NumPy (data analysis)

**Market Data:**
- yfinance (Yahoo Finance)
- Alpha Vantage API (optional)
- Akshare (China A-shares)

**Frontend:**
- React + TypeScript
- Recharts / Plotly (charts)
- TailwindCSS (styling)

**Deployment:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)

---

## 📦 Installation

```bash
# Clone repository
git clone git@github.com:shuorenyuyu/alpha-research.git
cd alpha-research

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run API server
python api/main.py
```

---

## 🔗 Related Projects

- [research-tracker](https://github.com/shuorenyuyu/research-tracker) - AI paper curation & summarization

---

## 📝 License

MIT License - See LICENSE file for details

---

**Last Updated:** December 8, 2025
