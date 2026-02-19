# AI-Driven Personal Finance Intelligence Platform

A comprehensive full-stack web application for tracking expenses, analyzing spending patterns, forecasting budgets, and generating AI-powered financial insights.

![Finance Intelligence](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Module 1: Expense and Income Data Management
- ✅ Complete CRUD operations for transactions
- ✅ Budget management with monthly tracking
- ✅ Django Admin interface for easy data management
- ✅ Transaction filtering and sorting

### Module 2: Spending Category Classification
- ✅ Auto-suggest categories based on transaction descriptions
- ✅ 8 pre-defined categories (Food, Transport, Utilities, Entertainment, Health, Salary, Shopping, Education)
- ✅ Keyword-based intelligent categorization

### Module 3: AI-Based Expense Pattern Analysis
- ✅ Average spending by day of week
- ✅ Top spending categories identification
- ✅ Recurring expense detection (subscriptions)
- ✅ 6-month spending trend analysis

### Module 4: Budget Forecasting and Prediction
- ✅ Simple moving average forecasting
- ✅ Budget projection alerts
- ✅ Overspending prediction
- ✅ Real-time budget utilization tracking

### Module 5: Financial Behavior Insights
- ✅ Dynamic insight generation
- ✅ Week-over-week spending comparisons
- ✅ Category-specific insights
- ✅ Alert system for budget anomalies

### Module 6: Savings Optimization Engine
- ✅ Identify non-essential spending
- ✅ Suggest specific reduction amounts
- ✅ Calculate potential annual savings
- ✅ Duplicate transaction detection

### Module 7: Interactive Analytics Dashboard
- ✅ Pie chart: Expense breakdown by category
- ✅ Line chart: Income vs Expenses (6 months)
- ✅ Bar chart: Budget vs Actual spending
- ✅ Real-time summary statistics

### Module 8: Monthly Financial Reports
- ✅ Monthly summaries with totals
- ✅ Top 3 expense categories
- ✅ Budget performance analysis
- ✅ Printable transaction lists

## 📋 Tech Stack

- **Backend**: Python 3.9+, Django 4.2
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite (default, easily upgradable to PostgreSQL)
- **Data Analysis**: Pandas, NumPy
- **Charts**: Chart.js
- **Styling**: Bootstrap 5, Bootstrap Icons

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project

```bash
cd "FinTech & Digital Finance Systems\Project3"
```

### Step 2: Create Virtual Environment (Recommended)

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

### Step 4: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional, for Admin access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Run the Development Server

```bash
python manage.py runserver
```

### Step 7: Access the Application

Open your browser and navigate to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
Project3/
├── finance_project/          # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI config
├── finance/                  # Finance app
│   ├── models.py            # Transaction, Budget models
│   ├── views.py             # All view functions
│   ├── forms.py             # Django forms
│   ├── services.py          # AI/ML analysis logic
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin configuration
│   └── templatetags/        # Custom template filters
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── dashboard.html       # Dashboard view
│   ├── transactions.html    # Transactions list
│   ├── budgets.html         # Budgets view
│   └── reports.html         # Monthly reports
├── static/                   # Static files
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # JavaScript functionality
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Usage Guide

### 1. Adding Transactions

1. Navigate to **Transactions** → **Add Transaction**
2. Enter amount, date, type (income/expense), category, and description
3. The system will auto-suggest a category based on the description keywords

### 2. Setting Budgets

1. Navigate to **Budgets** → **Add Budget**
2. Select a category and set the monthly limit
3. View budget utilization in real-time

### 3. Viewing Analytics

1. **Dashboard** shows:
   - Summary cards (Income, Expenses, Savings, Savings Rate)
   - Interactive charts (Pie, Line, Bar)
   - AI-generated insights
   - Savings optimization opportunities
   - Recent transactions

### 4. Generating Reports

1. Navigate to **Reports**
2. Select month and year
3. View comprehensive financial summary
4. Print or export data

### 5. Using Django Admin

1. Access http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Manage transactions and budgets in bulk
4. View generated insights

## 🔧 Key Components

### Models

- **Transaction**: Stores all financial transactions
- **Budget**: Monthly budget limits per category
- **FinancialInsight**: Generated insights and recommendations

### Services (AI/ML Logic)

Located in [finance/services.py](finance/services.py):

- `CategoryClassifier`: Auto-categorizes transactions
- `ExpensePatternAnalyzer`: Analyzes spending patterns using Pandas
- `BudgetForecaster`: Predicts future spending
- `InsightGenerator`: Creates dynamic insights
- `SavingsOptimizer`: Identifies savings opportunities
- `MonthlyReportGenerator`: Creates monthly summaries

### API Endpoints

- `/api/suggestions/` - Category suggestions
- `/api/patterns/` - Spending pattern analysis
- `/api/forecast/` - Budget forecasting
- `/api/savings/` - Savings opportunities
- `/api/insights/` - Financial insights
- `/api/summary/` - Quick summary stats

## 🎨 Customization

### Adding New Categories

Edit [finance/models.py](finance/models.py):

```python
class Category(models.TextChoices):
    YOUR_NEW_CATEGORY = 'YourCategory', 'Your Category Display Name'
```

### Modifying Analysis Logic

All AI/ML logic is in [finance/services.py](finance/services.py). You can modify:
- Classification keywords in `CategoryClassifier.CATEGORY_KEYWORDS`
- Forecasting algorithms in `BudgetForecaster`
- Insight generation in `InsightGenerator`

### Styling

Custom styles are in [static/css/style.css](static/css/style.css). Modify CSS variables in `:root` for quick color changes.

## 📊 Sample Data

To add sample data for testing:

1. Use Django Admin to add transactions manually
2. Or use the Django shell:

```bash
python manage.py shell
```

```python
from finance.models import Transaction, Budget, Category
from datetime import date
from django.utils import timezone

# Add sample transactions
Transaction.objects.create(
    amount=50.00,
    date=date.today(),
    transaction_type='expense',
    category=Category.FOOD,
    description='Lunch at restaurant'
)

# Add sample budget
Budget.objects.create(
    category=Category.FOOD,
    limit_amount=500.00,
    month=date.today().month,
    year=date.today().year
)
```

## 🐛 Troubleshooting

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic
```

### Issue: Database errors

**Solution:**
```bash
python manage.py migrate --run-syncdb
```

### Issue: Port already in use

**Solution:** Use a different port:
```bash
python manage.py runserver 8001
```

## 🚀 Deployment

### For Production:

1. **Update settings.py**:
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS`
   - Change `SECRET_KEY`

2. **Use PostgreSQL** (recommended):
   - Install `psycopg2-binary`
   - Update `DATABASES` configuration

3. **Serve static files**:
   - Use WhiteNoise or configure nginx/Apache

4. **Use WSGI server**:
   - Install Gunicorn: `pip install gunicorn`
   - Run: `gunicorn finance_project.wsgi:application`

## 📝 License

This project is open source and available under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue in the repository.

---

**Built with ❤️ using Django and Python**
