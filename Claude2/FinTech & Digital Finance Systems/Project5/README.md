# FinRisk AI - Financial Behavior and Risk Profiling System

A comprehensive Django-based web application for analyzing financial behavior, calculating risk tolerance, and providing personalized investment insights using AI-driven algorithms.

## 🌟 Features

### 8 Complete Modules:

1. **Financial Behavior Data Collection**
   - User profile management (age, income, employment, dependents)
   - Transaction tracking (income and expenses by category)
   - Comprehensive data entry forms

2. **Spending and Investment Pattern Analysis**
   - Automatic savings rate calculation
   - Essential vs. discretionary spending categorization
   - Spending pattern classification

3. **AI-Based Risk Profiling Engine**
   - Multi-factor risk scoring algorithm
   - Age, savings rate, income stability, and experience analysis
   - Component-based scoring (0-100 scale)

4. **Risk Tolerance Classification System**
   - Three risk categories: Conservative, Moderate, Aggressive
   - Evidence-based classification thresholds
   - Detailed score breakdown

5. **Personalized Financial Planning Insights**
   - Tailored investment recommendations
   - Risk-appropriate asset allocation guidance
   - Actionable financial advice

6. **Risk vs. Return Visualization Dashboard**
   - Interactive scatter plots (Chart.js)
   - Portfolio allocation charts
   - Asset class comparison tables

7. **Scenario-Based Financial Analysis**
   - What-if calculator
   - Market change projections
   - Compound interest modeling (5, 10, 20, 30 years)
   - Quick scenario presets (Bull/Bear/Recession)

8. **Financial Risk Profiling Reports**
   - Printable comprehensive reports
   - Financial Health Card
   - Transaction history
   - Investment recommendations

## 🛠️ Tech Stack

- **Backend:** Python 3.8+ / Django 4.2
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** SQLite (default)
- **Visualization:** Chart.js 4.4.0 (CDN)
- **Architecture:** Django REST patterns with JSON handling

## 📁 Project Structure

```
finrisk_ai/
├── finrisk_ai/           # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                  # Core Django app
│   ├── __init__.py
│   ├── admin.py          # Admin configuration
│   ├── apps.py           # App configuration
│   ├── forms.py          # Django forms
│   ├── models.py         # Database models
│   ├── risk_engine.py    # Risk calculation algorithms
│   ├── urls.py           # App URL routing
│   └── views.py          # View functions
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Professional financial styles
│   └── js/
│       └── main.js       # JavaScript functionality
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── core/             # App templates
│       ├── home.html
│       ├── profile_form.html
│       ├── profile_detail.html
│       ├── transaction_form.html
│       ├── transaction_list.html
│       ├── risk_analysis.html
│       ├── dashboard.html
│       ├── scenario_calculator.html
│       └── financial_report.html
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Navigate to Project Directory

```bash
cd "c:\Users\Dell\OneDrive\Desktop\Claude2\FinTech & Digital Finance Systems\Project5"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for Admin Access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## 📖 Usage Guide

### 1. Create a User Profile

1. Click "New Profile" on the home page
2. Fill in personal and financial information:
   - Name, age, annual income
   - Employment status and income stability
   - Number of dependents
   - Investment experience (years)

### 2. Add Transactions

1. From the profile detail page, click "Add Transaction"
2. Select transaction type (Income/Expense)
3. Choose category and enter amount
4. Add date and optional description
5. Add multiple transactions for better analysis

### 3. Analyze Risk Profile

1. After adding transactions, click "Analyze Profile"
2. The system calculates:
   - Risk score (0-100)
   - Risk classification
   - Savings rate
   - Spending patterns

### 4. View Dashboard

1. Access the dashboard from profile detail page
2. View interactive charts:
   - Risk vs. Return scatter plot
   - Portfolio allocation doughnut chart
   - Asset class details table

### 5. Try Scenario Calculator

1. Open "Scenario Calculator"
2. Adjust parameters:
   - Current portfolio value
   - Monthly contributions
   - Savings increase/decrease
   - Market changes
3. View projections for 5, 10, 20, and 30 years
4. Use quick presets (Bull Market, Bear Market, etc.)

### 6. Generate Financial Report

1. Click "Financial Report"
2. View comprehensive analysis
3. Print or save as PDF

## 🧠 Risk Scoring Algorithm

The risk score is calculated using a weighted multi-factor algorithm:

| Component | Weight | Scoring Logic |
|-----------|--------|---------------|
| **Age Factor** | 30% | Younger = higher risk capacity (18-25: 100pts, 65+: 10pts) |
| **Savings Rate** | 30% | Higher savings = better financial health (0%: 20pts, 20%+: 100pts) |
| **Income Stability** | 25% | Very Stable: 100pts, Unstable: 25pts |
| **Investment Experience** | 15% | 0yrs: 30pts, 10+yrs: 100pts |
| **Dependents Adjustment** | -5 to -15 points | Reduces risk capacity based on financial obligations |

**Classification Thresholds:**
- **Conservative:** 0-40 points
- **Moderate:** 41-70 points
- **Aggressive:** 71-100 points

## 🎨 Customization

### Modify Risk Parameters

Edit `core/risk_engine.py` to adjust:
- Age factor scoring
- Savings rate thresholds
- Income stability weights
- Classification boundaries

### Add New Asset Classes

Edit `_prepare_chart_data()` function in `core/views.py`:
```python
asset_classes = [
    {'name': 'Your Asset', 'risk': 15, 'return': 8, 'allocation': 10},
    # Add more assets...
]
```

### Customize Styles

Edit `static/css/style.css` to modify:
- Color scheme (CSS variables at top)
- Layout and spacing
- Typography
- Component styles

## 📊 Database Models

### UserProfile
- Personal demographics
- Financial information
- Employment details

### Transaction
- Transaction date
- Category (income/expense types)
- Amount and type
- User profile link

### RiskProfile
- Calculated risk score
- Classification
- Component scores
- Spending patterns
- AI-generated insights

## 🔒 Security Notes

- **Development Mode:** `DEBUG = True` in settings.py
- **Production:** Set `DEBUG = False` and update `SECRET_KEY`
- **CSRF Protection:** Enabled by default
- **SQL Injection:** Protected by Django ORM

## 🌐 Deployment

### For Production Deployment:

1. **Set environment variables:**
   ```bash
   export DEBUG=False
   export SECRET_KEY='your-secure-secret-key'
   export ALLOWED_HOSTS='yourdomain.com'
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

3. **Use a production WSGI server:**
   - Gunicorn (recommended)
   - uWSGI
   - Waitress (Windows)

4. **Database:** Switch from SQLite to PostgreSQL for production

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python manage.py runserver 8001
```

### Migration Issues
```bash
# Reset migrations (WARNING: deletes data)
python manage.py flush
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

## 📝 API Endpoints

- `GET /` - Home page
- `GET /profiles/` - List all profiles
- `POST /profiles/create/` - Create new profile
- `GET /profiles/<id>/` - View profile details
- `POST /profiles/<id>/transactions/add/` - Add transaction
- `GET /profiles/<id>/analyze/` - Analyze risk profile
- `GET /profiles/<id>/dashboard/` - View dashboard
- `POST /api/calculate-scenario/` - Calculate scenarios
- `GET /profiles/<id>/report/` - Generate financial report

## 👥 Admin Panel

Access at: `http://127.0.0.1:8000/admin/`

Features:
- Manage user profiles
- View/edit transactions
- Review risk profiles
- Export data

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Support

For issues, questions, or contributions, please refer to the project documentation.

---

**Built with ❤️ using Django and Vanilla JavaScript**

**Version:** 1.0.0
**Last Updated:** 2024
