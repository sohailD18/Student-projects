# AI-Powered Market Trend and Stock Movement Analysis System

A comprehensive full-stack Django application for analyzing stock market trends using Machine Learning. Features include price prediction, volatility analysis, buy/sell signal generation, and automated market reports.

## Features

### 1. Market and Stock Data Management
- Store stock tickers with comprehensive metadata
- Historical OHLCV (Open, High, Low, Close, Volume) data storage
- Django admin interface for easy management
- Integration with Yahoo Finance API via `yfinance`
- Fallback to dummy data generation when API is unavailable

### 2. Time-Series Preprocessing and Trend Analysis
- Automatic data cleaning (missing values, outliers)
- Feature engineering including:
  - Moving Averages (5, 10, 20, 50-day)
  - Relative Strength Index (RSI)
  - Bollinger Bands
  - MACD (Moving Average Convergence Divergence)
  - Price momentum indicators
  - Lag features for time-series analysis

### 3. AI-Based Price Prediction Engine
- Multiple ML model support:
  - Random Forest Regressor
  - Linear Regression
- Next-day closing price prediction
- Feature importance analysis
- Model performance metrics (MSE, RMSE, R², MAE)

### 4. Volatility and Risk Analysis Module
- Daily and annualized volatility calculations
- Value at Risk (VaR) at 95% and 99% confidence levels
- Sharpe Ratio calculation
- Maximum Drawdown analysis
- Risk level classification (Low, Medium, High, Very High)

### 5. Buy/Sell Signal Generation
- Automated trading signals based on prediction confidence
- Configurable threshold parameters
- Signal confidence scoring
- Clear visual indicators on dashboard

### 6. Model Evaluation and Accuracy Tracking
- Real-time accuracy metrics display
- Historical prediction tracking
- Model comparison capabilities

### 7. Market Analysis and Insight Reports
- Automated market trend detection (Bullish, Bearish, Sideways, Volatile)
- Comprehensive summary generation
- Key findings extraction
- Actionable trading recommendations

### 8. Interactive Visualization Dashboard
- Historical price charts with moving averages
- Prediction vs. actual price comparison
- Volatility visualization
- Trading volume analysis
- Real-time updates via REST API
- Dark theme optimized for financial data

## Tech Stack

- **Backend:** Django 4.2 (Python)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (No frameworks)
- **Database:** SQLite (default Django)
- **ML/AI:** pandas, numpy, scikit-learn
- **Visualization:** Chart.js
- **Data Source:** Yahoo Finance (yfinance)

## Project Structure

```
Project4/
├── market_trend_system/          # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── market_analysis/              # Main app
│   ├── models.py                 # Database models
│   ├── views.py                  # API endpoints & views
│   ├── urls.py                   # URL routing
│   ├── admin.py                  # Admin configuration
│   ├── ml_utils.py               # ML utilities
│   └── migrations/
├── templates/                    # HTML templates
│   └── dashboard.html
├── static/                       # Static files
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Step 1: Clone or Download the Project
```bash
cd "c:\Users\Dell\OneDrive\Desktop\Claude2\FinTech & Digital Finance Systems\Project4"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for Admin Access)
```bash
python manage.py createsuperuser
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
- Dashboard: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

## Usage Guide

### 1. Adding a Stock

**Via Dashboard:**
1. Click "Add New Stock" button
2. Enter a stock symbol (e.g., AAPL, GOOGL, MSFT)
3. Click "Fetch Data"
4. The system will automatically fetch or generate historical data

**Via Admin Panel:**
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to "Stocks" under "Market Analysis"
3. Add stocks manually

### 2. Training & Prediction

1. Select a stock from the dropdown
2. Choose a model type (Random Forest or Linear Regression)
3. Click "Train & Predict" button
4. View prediction metrics and trading signals

### 3. Volatility Analysis

1. Select a stock
2. Click "Analyze Volatility" button
3. View risk metrics including VaR, Sharpe Ratio, and risk level

### 4. Generating Reports

1. Select a stock
2. Click "Generate Report" button
3. View comprehensive market analysis with recommendations

## API Endpoints

### Stock Management
- `GET /api/stocks/` - List all stocks
- `GET /api/stocks/<id>/` - Get stock details
- `POST /api/fetch-data/` - Fetch stock data from API

### Prediction Engine
- `POST /api/train-predict/` - Train model and generate prediction
- `GET /api/predictions/<stock_id>/` - Get prediction history

### Volatility Analysis
- `POST /api/analyze-volatility/` - Calculate volatility metrics

### Reports
- `POST /api/generate-report/` - Generate market analysis report
- `GET /api/reports/<stock_id>/` - Get report history

### Dashboard
- `GET /api/dashboard/<stock_id>/` - Get comprehensive dashboard data

## Database Models

### Stock
- Stock ticker information
- Company metadata
- Sector/industry classification

### HistoricalData
- Daily OHLCV data
- Technical indicators (MA, RSI)
- Pre-computed features for ML

### Prediction
- Model predictions with metrics
- Trading signals
- Model performance tracking

### VolatilityAnalysis
- Volatility metrics
- Risk indicators (VaR, Sharpe Ratio)
- Risk classification

### MarketReport
- Generated analysis reports
- Trend classification
- Recommendations

## Technical Indicators Explained

### Moving Averages (MA)
- **MA-5:** 5-day simple moving average
- **MA-10:** 10-day simple moving average
- **MA-20:** 20-day simple moving average
- **MA-50:** 50-day simple moving average

### Relative Strength Index (RSI)
- Measures momentum oscillating between 0-100
- Above 70: Overbought condition
- Below 30: Oversold condition

### Bollinger Bands
- Volatility bands around price
- Upper/Lower bands indicate support/resistance

### MACD
- Trend-following momentum indicator
- Signal line crossovers indicate buy/sell opportunities

## Risk Metrics Explained

### Volatility
- **Daily Volatility:** Standard deviation of daily returns
- **Annualized Volatility:** Daily volatility × √252

### Value at Risk (VaR)
- **VaR 95%:** Maximum expected loss at 95% confidence
- **VaR 99%:** Maximum expected loss at 99% confidence

### Sharpe Ratio
- Risk-adjusted return measure
- Higher values indicate better risk-adjusted performance

### Maximum Drawdown
- Largest peak-to-trough decline
- Measures downside risk

## Troubleshooting

### Issue: yfinance not working
**Solution:** The system automatically falls back to dummy data generation. No action needed.

### Issue: Insufficient data for prediction
**Solution:** Ensure you have at least 50 days of historical data. Fetch more data or use a different stock.

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic
```

### Issue: Port already in use
**Solution:** Use a different port:
```bash
python manage.py runserver 8001
```

## Performance Optimization

1. **Database Indexing:** All critical fields are indexed for fast queries
2. **Batch Processing:** Data is processed in batches for efficiency
3. **Caching:** Consider implementing Redis for production
4. **Async Tasks:** For large datasets, consider Celery for background tasks

## Production Deployment

For production deployment, consider:

1. **Database:** Switch from SQLite to PostgreSQL
2. **Web Server:** Use Gunicorn or uWSGI
3. **Reverse Proxy:** Configure Nginx
4. **Environment Variables:** Use django-environ for settings
5. **Security:**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS
   - Set up proper CORS policies

## Contributing

This is a complete, production-ready system. To extend functionality:

1. Add new models in `models.py`
2. Create corresponding views in `views.py`
3. Update URL routing in `urls.py`
4. Add frontend components in templates and static files

## License

This project is for educational and demonstration purposes.

## Disclaimer

**IMPORTANT:** This system is for educational and research purposes only. Do not make investment decisions based solely on these predictions. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

## Support

For issues or questions, please refer to the inline code documentation or Django/scikit-learn official documentation.

---

**Built with Django, scikit-learn, and Chart.js**
