# Setup Guide - AI-Based Demand Forecasting and Inventory Management System

## Prerequisites

Before starting, ensure you have:
- **Python 3.8 or higher** installed
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Edge, Safari)
- Basic command line knowledge

---

## Step-by-Step Installation

### Step 1: Navigate to Project Directory

Open your terminal/command prompt and navigate to the project folder:

```bash
cd c:\Users\Dell\OneDrive\Desktop\Claude2\E-commerce\Project2
```

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates your project dependencies:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You'll know it's activated when you see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- Django (Web Framework)
- Django REST Framework
- Pandas (Data manipulation)
- NumPy (Numerical computing)
- Scikit-Learn (Machine Learning)
- Statsmodels (Statistical models)
- Matplotlib (Visualization)

**Expected Output:**
```
Successfully installed Django-4.2.7 djangorestframework-3.14.0 ...
```

### Step 4: Run Database Migrations

Create the SQLite database and tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

**What this does:**
- `makemigrations`: Creates migration files based on your models
- `migrate`: Applies migrations to create database tables

**Expected Output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying inventory.0001_initial... OK
  ...
```

### Step 5: Create Superuser (Optional)

If you want to use Django Admin to manage data:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email (optional)
- Password

### Step 6: Generate Dummy Data

Populate the database with sample products and sales data:

```bash
python scripts/generate_dummy_data.py
```

**This creates:**
- 20 sample products across different categories
- 6 months of historical sales data
- Realistic sales patterns with trends and seasonality

**Expected Output:**
```
============================================================
DUMMY DATA GENERATOR
Inventory Management System
============================================================

Creating products...
  Created: Wireless Mouse (Electronics) - Stock: 25
  Created: Cotton T-Shirt (Clothing) - Stock: 5
  ...

Total Products: 20

============================================================
Dummy data generation complete!
============================================================
```

---

## Running the Application

### Start the Development Server

```bash
python manage.py runserver
```

**Expected Output:**
```
Django version 4.2.7, using settings 'inventory_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Access the Application

Open your web browser and navigate to:

**Main Dashboard:**
```
http://127.0.0.1:8000/
```

**Django Admin Panel:**
```
http://127.0.0.1:8000/admin/
```

---

## Application Features Overview

### 1. Dashboard (Main Page)

**URL:** `http://127.0.0.1:8000/`

**What you'll see:**
- **KPI Cards:** Total products, low stock alerts, inventory value, average daily sales
- **Category Distribution:** Products grouped by category
- **Sales vs Forecast Chart:** Interactive chart showing actual sales vs AI predictions
- **Inventory Status Chart:** Pie chart showing stock status distribution
- **Inventory Table:** Detailed list of all products with forecasts

### 2. Django Admin Panel

**URL:** `http://127.0.0.1:8000/admin/`

**Features:**
- Add/edit products manually
- View and manage sales data
- Configure system settings

**Login:** Use the superuser credentials created in Step 5

---

## Using the Application

### Viewing Product Forecasts

1. **On the main dashboard**, locate the "Sales vs Forecast" chart
2. **Use the dropdown** to select different products
3. **View the chart** showing:
   - Blue line: Historical actual sales
   - Green dashed line: AI forecast for next 30 days

### Checking Inventory Status

The inventory table shows each product's status:

- **Green (Good):** Stock level is healthy
- **Red (Low Stock):** Need to reorder soon
- **Dark Red (Critical):** Below safety stock level
- **Orange (Over-stock):** Excess inventory

### Viewing Product Details

1. **Click the eye icon** (👁️) in the Actions column
2. **A modal opens** with:
   - Detailed forecast chart
   - Current stock, predicted demand, safety stock
   - Suggested order quantity
   - Status information

### Filtering the Table

- **Search bar:** Type product name to filter
- **Status filter:** Select status (Low Stock, Good, etc.) to filter
- **Pagination:** Use pagination links at bottom for large datasets

---

## API Endpoints

The system provides RESTful API endpoints for integration:

### Forecasting APIs
```
GET /api/forecast/all/                    # Forecast for all products
GET /api/forecast/<product_id>/           # Forecast for specific product
```

### Chart Data APIs
```
GET /api/chart/<product_id>/              # Historical + forecast data
GET /api/sales/<product_id>/              # Historical sales only
```

### Dashboard APIs
```
GET /api/dashboard/stats/                 # KPI statistics
GET /api/inventory/summary/               # Inventory summary
GET /api/products/                        # Products list
GET /api/reports/replenishment/           # Replenishment report
```

**Example API Call:**
```bash
curl http://127.0.0.1:8000/api/forecast/1/
```

**Response:**
```json
{
  "success": true,
  "forecast": {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "current_stock": 25,
    "predicted_demand": 450,
    "suggested_order_quantity": 435,
    "status": "low",
    "daily_forecast": [...]
  }
}
```

---

## AI/ML Forecasting Explained

### How It Works

1. **Data Collection:**
   - Fetches historical sales data from database
   - Aggregates sales by date

2. **Feature Engineering:**
   - Creates temporal features (day of week, month)
   - Calculates rolling averages
   - Adds trend components

3. **Model Selection:**
   - **If sufficient data (>10 days):** Uses Linear Regression
   - **If limited data:** Uses Moving Average

4. **Forecast Generation:**
   - Predicts demand for next 30 days
   - Calculates confidence metrics
   - Generates replenishment suggestions

5. **Status Determination:**
   ```
   IF current_stock < predicted_demand + safety_stock:
       status = "Low Stock"
       order_quantity = (predicted_demand + safety_stock) - current_stock
   ```

### Model Accuracy

The system uses multiple indicators:
- **Historical trends:** Captured by Linear Regression
- **Seasonality:** Day of week, month features
- **Recent patterns:** Rolling averages
- **Safety buffer:** Configurable safety stock

---

## Customization

### Change Forecast Period

Edit [inventory/utils.py](inventory/utils.py):
```python
FORECAST_DAYS = 30  # Change to 60 for 60-day forecast
```

### Adjust Safety Stock Formula

Edit [inventory/models.py](inventory/models.py):
```python
safety_stock = models.IntegerField(default=10)  # Change default value
```

### Modify Chart Colors

Edit [static/js/dashboard.js](static/js/dashboard.js):
```javascript
const CHART_COLORS = {
    primary: 'rgb(52, 152, 219)',     // Change this color
    secondary: 'rgb(46, 204, 113)',   // Change this color
    // ...
};
```

---

## Troubleshooting

### Issue: Server won't start

**Error:** `Error: That port is already in use.`

**Solution:** Use a different port:
```bash
python manage.py runserver 8080
```
Then access at `http://127.0.0.1:8080/`

### Issue: No data showing in dashboard

**Cause:** Database is empty

**Solution:** Generate dummy data:
```bash
python scripts/generate_dummy_data.py
```

### Issue: Charts not loading

**Cause:** JavaScript errors or CDN issues

**Solutions:**
1. Open browser console (F12) and check for errors
2. Verify internet connection (Chart.js loads from CDN)
3. Try clearing browser cache

### Issue: Import errors

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Migration errors

**Solution:** Reset database:
```bash
# Delete database file
rm db.sqlite3  # Mac/Linux
del db.sqlite3  # Windows

# Re-run migrations
python manage.py migrate
```

---

## Project Structure Reference

```
Project2/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── db.sqlite3                         # Database (created after migration)
│
├── inventory_project/                 # Django project settings
│   ├── settings.py                   # Project configuration
│   ├── urls.py                       # Main URL routing
│   └── wsgi.py                       # WSGI configuration
│
├── inventory/                         # Main application
│   ├── models.py                     # Database models
│   ├── views.py                      # View functions
│   ├── urls.py                       # App URL routing
│   ├── utils.py                      # AI/ML forecasting logic
│   └── admin.py                      # Admin configuration
│
├── templates/                         # HTML templates
│   ├── base.html                     # Base template
│   └── dashboard.html                # Dashboard page
│
├── static/                            # Static files
│   ├── css/
│   │   └── style.css                 # Styles
│   └── js/
│       └── dashboard.js              # JavaScript & Chart.js
│
└── scripts/                           # Utility scripts
    └── generate_dummy_data.py        # Dummy data generator
```

---

## Next Steps

### Adding Your Own Data

**Option 1: Via Django Admin**
1. Go to `http://127.0.0.1:8000/admin/`
2. Add products under "Products"
3. Add sales data under "Sales Data"

**Option 2: Via API**
```bash
# Add product
curl -X POST http://127.0.0.1:8000/api/products/ \
  -d "name=New Product&category=electronics&current_stock=100&price=29.99"

# Add sales data
curl -X POST http://127.0.0.1:8000/api/sales/ \
  -d "product_id=1&date=2024-01-01&quantity_sold=10"
```

### Exporting Forecast Data

The system can provide CSV exports via the API:

```python
import requests

response = requests.get('http://127.0.0.1:8000/api/forecast/all/')
data = response.json()

# Convert to CSV
import pandas as pd
df = pd.DataFrame(data['forecasts'])
df.to_csv('forecasts.csv', index=False)
```

---

## Performance Tips

1. **Database Optimization:**
   - Run `python manage.py migrate` after model changes
   - Use Django Admin for bulk operations

2. **Large Datasets:**
   - Add indexes to models for faster queries
   - Use pagination for tables (already implemented)

3. **Forecasting:**
   - Cache forecast results for frequently accessed products
   - Run forecasts as background tasks for large datasets

---

## Security Considerations

**For Development:**
- DEBUG = True (OK for development)
- SECRET_KEY is exposed (OK for development)

**For Production:**
1. Set `DEBUG = False` in settings.py
2. Change `SECRET_KEY` to a random secure key
3. Use environment variables for sensitive data
4. Implement user authentication
5. Set up proper CORS policies
6. Use a production database (PostgreSQL)

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Scikit-Learn Documentation](https://scikit-learn.org/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the terminal
3. Check browser console for JavaScript errors
4. Verify all dependencies are installed correctly

---

**System Successfully Built!**

You now have a complete AI-based demand forecasting and inventory management system. The forecasting model uses Linear Regression to predict future demand based on historical sales patterns, seasonal trends, and temporal features.

**Key Features Implemented:**
- ✅ Product and sales data management
- ✅ AI-powered demand forecasting
- ✅ Interactive dashboard with visualizations
- ✅ Replenishment suggestions
- ✅ Status-based alerts
- ✅ RESTful API endpoints
- ✅ Responsive design

Happy forecasting! 🚀
