# AI-Based Carbon Credit Analysis and Trading Support System

A production-ready Django web application that enables industries to track carbon emissions, analyze trends using AI/ML, and receive intelligent trading recommendations for carbon credits.

## Features

- **Data Management**: Store industry details and historical emission data
- **AI Trend Analysis**: Predict future emissions using Linear Regression
- **Trading Insights**: Get Buy/Sell/Hold recommendations based on predictions
- **Interactive Dashboard**: Visualize data with Chart.js
- **Price Analysis**: Track carbon credit price trends
- **Performance Comparison**: Compare efficiency across industries
- **Printable Reports**: Generate comprehensive analysis reports

## Tech Stack

- **Backend**: Python (Django 5.0+)
- **Database**: SQLite
- **AI/ML**: scikit-learn, pandas, numpy
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5
- **Visualization**: Chart.js

## Project Structure

```
Project6/
├── carbon_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tracker/                 # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL patterns
│   ├── admin.py            # Admin configuration
│   ├── services.py         # AI/ML services
│   └── management/commands/
│       └── seed_data.py    # Database seeding command
├── templates/              # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── analysis.html
│   └── report.html
├── static/                 # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── requirements.txt        # Python dependencies
```

## Installation & Setup

### Step 1: Open Terminal

Navigate to the project directory:
```bash
cd c:\Users\Dell\OneDrive\Desktop\Claude3\Project6
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
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

Follow the prompts to create an admin account.

### Step 6: Seed the Database

```bash
python manage.py seed_data
```

This will populate the database with:
- 5 sample industries
- 2 years of historical emission data
- 1 year of carbon price history

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Application Usage

### Dashboard (Home Page)

- View overview of all industries
- Check total emissions and active credits
- Monitor current carbon prices
- See AI trading insights for all industries

### Industry Analysis

Click on any industry card to view:
- Historical emission trends
- AI predictions for next 6 months
- Trading recommendations (Buy/Sell/Hold)
- Detailed performance metrics

### Reports

Navigate to Reports for:
- Executive summary
- Industry performance comparison
- Printable PDF-style reports

### Admin Panel

Access the admin panel at **http://127.0.0.1:8000/admin/**
- Manage industries
- Add/edit emission records
- Update carbon prices
- View prediction logs

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/emission_data/` | Get emission data for charts |
| `/api/predictions/<id>/` | Get AI predictions for an industry |
| `/api/carbon_prices/` | Get carbon price history |
| `/api/price_analysis/` | Get price trend analysis |
| `/api/industry_comparison/` | Compare industry performance |
| `/api/all_predictions/` | Get all industry predictions |

## Database Models

### Industry
- Name
- Industry Type
- Emission Limit (annual)
- Description

### EmissionRecord
- Industry (Foreign Key)
- Year
- Month
- Emission Amount

### CarbonPrice
- Date
- Price Per Ton (USD)

### PredictionLog
- Industry (Foreign Key)
- Predicted Emission
- Trading Suggestion
- Confidence Score

## AI/ML Features

### Predictive Analytics
- Uses **Linear Regression** from scikit-learn
- Predicts emissions for next 3-6 months
- Provides confidence scores
- Considers seasonality and trends

### Trading Recommendations
- **SELL**: When projected surplus > 10% of limit
- **BUY**: When projected deficit occurs
- **HOLD**: When emissions are near limit

### Price Analysis
- 30-day trend analysis
- Market advice based on price movements
- Volatility calculations

## Troubleshooting

### Port Already in Use

If port 8000 is busy, use a different port:
```bash
python manage.py runserver 8080
```

### Database Issues

To reset the database:
```bash
del db.sqlite3
python manage.py migrate
python manage.py seed_data
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install --upgrade -r requirements.txt
```

## Development Notes

- The system uses SQLite for simplicity (can be upgraded to PostgreSQL)
- All predictions are logged for audit purposes
- Charts are responsive and work on mobile devices
- Print-friendly report layouts

## Future Enhancements

- User authentication and authorization
- Real-time price feeds from carbon markets
- Export to PDF/Excel
- Email notifications for trading alerts
- More advanced ML models (LSTM, Prophet)
- Integration with carbon credit exchanges

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check the Django documentation at:
https://docs.djangoproject.com/en/5.0/
