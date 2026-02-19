# 🤖 AI-Based Inventory Demand Analysis & Stock Level Prediction System

A full-stack Django application that uses machine learning to predict product demand and optimize inventory levels. Built with Django, Python, Pandas, Scikit-Learn, and Chart.js.

## 📋 Features

### Core Functionality
- **AI-Powered Demand Prediction** using Linear Regression and Random Forest
- **Automated Stock Recommendations** with safety margin calculations
- **Interactive Analytics Dashboard** with real-time visualizations
- **Smart Status Classification**: Low Stock, Optimal, or Overstock
- **Comprehensive Reporting** for reordering needs
- **Historical Sales Tracking** and trend analysis

### Technical Highlights
- Ensemble ML models (Linear Regression + Random Forest) for robust predictions
- Feature engineering including seasonality, day-of-week patterns, and rolling averages
- Confidence scoring for prediction reliability
- Responsive web interface with modern design
- Django Admin panel for manual data management

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 4.2+ (Python) |
| **Database** | SQLite (default Django) |
| **AI/ML** | Pandas, Scikit-Learn, NumPy |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Visualization** | Chart.js (via CDN) |

## 📦 Project Structure

```
Project5/
├── inventory_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory_system/           # Main app
│   ├── models.py               # Database models
│   ├── views.py                # View logic
│   ├── urls.py                 # App URLs
│   ├── admin.py                # Admin configuration
│   ├── services/               # AI/ML services
│   │   └── predictor.py        # Demand prediction engine
│   ├── management/commands/    # Django management commands
│   │   ├── seed_data.py        # Populate dummy data
│   │   └── run_predictions.py # Generate predictions
│   └── templatetags/           # Custom template filters
├── templates/                  # HTML templates
│   ├── base.html
│   └── inventory_system/
│       ├── dashboard.html
│       ├── analytics.html
│       ├── reports.html
│       └── product_detail.html
├── static/                     # Static files
│   ├── css/style.css
│   └── js/main.js
├── manage.py
├── requirements.txt
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd c:\Users\Dell\OneDrive\Desktop\Claude3\Project5
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser for the admin panel**
   ```bash
   python manage.py createsuperuser
   ```

5. **Seed the database with dummy data**
   ```bash
   python manage.py seed_data --months 12
   ```
   This creates 15 sample products with 12 months of historical sales data.

6. **Generate AI predictions**
   ```bash
   python manage.py run_predictions
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Dashboard: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## 📊 Usage Guide

### 1. **Dashboard**
- View all products with current stock levels
- See AI predictions at a glance
- Color-coded status indicators:
  - 🟢 Green = Optimal
  - 🔴 Red = Low Stock
  - 🟡 Yellow = Overstock

### 2. **Analytics**
- Select products to view demand charts
- Compare historical sales vs. AI predictions
- 90-day historical data + 30-day forecast

### 3. **Reports**
- **Low Stock Report**: Products needing immediate reordering
- **Overstock Report**: Products with excess inventory
- **Order Value**: Total estimated investment needed
- **Priority Ranking**: Most critical items first

### 4. **Product Detail**
- Complete product information
- Sales history (last 50 transactions)
- Individual AI predictions with recommendations

### 5. **Run AI Predictions**
- Generate new predictions for all products
- Updates based on latest sales data
- Takes 5-30 seconds depending on data volume

## 🤖 AI/ML Details

### Prediction Algorithm

The system uses an **ensemble approach** combining:

1. **Linear Regression**: Captures linear trends
2. **Random Forest**: Detects complex, non-linear patterns

### Features Used

| Feature | Description |
|---------|-------------|
| Day of Week | Captures weekly patterns |
| Month | Seasonal trends |
| Rolling 7-Day Average | Short-term trends |
| Rolling 30-Day Average | Long-term trends |
| Lag Features (7, 30 days) | Autocorrelation |
| Date Index | Trend over time |

### Safety Margin

- **Default**: 20% above predicted demand
- **Purpose**: Buffer against uncertainty
- **Customizable**: Via `--safety-margin` flag

### Status Calculation

- **Low Stock**: Current < Recommended
- **Optimal**: Recommended ≤ Current ≤ Recommended × 1.5
- **Overstock**: Current > Recommended × 1.5

## 🔧 Management Commands

### seed_data
Populate database with dummy products and sales data.

```bash
python manage.py seed_data --months 12
```

Options:
- `--months`: Number of months of historical data (default: 12)

### run_predictions
Generate AI predictions for all products.

```bash
python manage.py run_predictions --safety-margin 0.20
```

Options:
- `--safety-margin`: Safety margin percentage (default: 0.20 = 20%)

## 📈 API Endpoints

### Chart Data API
Fetch historical and predicted data for a product.

```
GET /api/chart-data/<product_id>/
```

Response:
```json
{
  "labels": ["2024-01-01", "2024-01-02", ...],
  "historical": [45, 52, ...],
  "predicted": [null, null, ..., 48, 50, ...]
}
```

## 🎨 Customization

### Adjust Safety Margin

Edit [services/predictor.py](inventory_system/services/predictor.py):
```python
def __init__(self, safety_margin=0.30, prediction_days=30):
    self.safety_margin = safety_margin  # Change from 0.20 to 0.30
```

### Change Prediction Period

```python
def __init__(self, safety_margin=0.20, prediction_days=60):
    self.prediction_days = prediction_days  # Change from 30 to 60 days
```

### Add New Product Categories

Edit [models.py](inventory_system/models.py):
```python
CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('clothing', 'Clothing'),
    # Add your categories here
]
```

## 🐛 Troubleshooting

### Issue: No predictions appear
**Solution**: Run `python manage.py run_predictions`

### Issue: Chart doesn't load
**Solution**: Ensure Chart.js CDN is accessible. Check browser console for errors.

### Issue: Import errors for sklearn/pandas
**Solution**: Run `pip install -r requirements.txt` again

### Issue: Database locked
**Solution**: Stop the server and run `python manage.py migrate` again

## 📝 Future Enhancements

Potential improvements for the system:

1. **Additional ML Models**: XGBoost, LSTM for time series
2. **Multi-warehouse Support**: Track inventory across locations
3. **Supplier Management**: Lead time predictions
4. **Email Alerts**: Automatic notifications for low stock
5. **Export Reports**: PDF/Excel generation
6. **User Authentication**: Role-based access control
7. **API Integration**: Connect to POS systems
8. **Advanced Analytics**: ABC analysis, EOQ calculations

## 📄 License

This project is for educational purposes. Feel free to modify and use as needed.

## 👨‍💻 Author

Built as a demonstration of full-stack Django development with AI/ML integration.

---

**Happy Predicting! 🚀📊**
