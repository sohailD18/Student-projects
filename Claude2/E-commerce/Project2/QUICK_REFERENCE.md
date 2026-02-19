# Quick Reference Card
# AI-Based Demand Forecasting & Inventory Management System

## Essential Commands

### Initial Setup
```bash
# Navigate to project
cd c:\Users\Dell\OneDrive\Desktop\Claude2\E-commerce\Project2

# Install dependencies
pip install -r requirements.txt

# Create database
python manage.py makemigrations
python manage.py migrate

# Generate test data
python scripts/generate_dummy_data.py
```

### Running the Server
```bash
# Start server
python manage.py runserver

# Use different port
python manage.py runserver 8080
```

### Django Admin
```bash
# Create superuser
python manage.py createsuperuser

# Access admin panel
http://127.0.0.1:8000/admin/
```

### Database Management
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: deletes all data)
# Delete db.sqlite3 file, then run migrate
```

---

## Important URLs

| Page | URL |
|------|-----|
| **Main Dashboard** | http://127.0.0.1:8000/ |
| **Django Admin** | http://127.0.0.1:8000/admin/ |
| **API - All Forecasts** | http://127.0.0.1:8000/api/forecast/all/ |
| **API - Product Forecast** | http://127.0.0.1:8000/api/forecast/1/ |
| **API - Dashboard Stats** | http://127.0.0.1:8000/api/dashboard/stats/ |
| **API - Products List** | http://127.0.0.1:8000/api/products/ |

---

## File Structure Reference

```
inventory_project/
├── manage.py                    # Django management script
├── requirements.txt             # Dependencies
├── db.sqlite3                   # Database (auto-created)
│
├── inventory_project/           # Project settings
│   └── settings.py             # Configuration
│
├── inventory/                   # Main app
│   ├── models.py               # Product, SalesData models
│   ├── views.py                # Dashboard & API views
│   ├── urls.py                 # URL routing
│   └── utils.py                # AI/ML forecasting logic
│
├── templates/                   # HTML files
│   ├── base.html               # Base template
│   └── dashboard.html          # Dashboard page
│
├── static/                      # CSS & JS
│   ├── css/style.css           # Styles
│   └── js/dashboard.js         # Charts & interactivity
│
└── scripts/
    └── generate_dummy_data.py  # Test data generator
```

---

## Common Tasks

### Add New Product (via Admin)
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Click "Products" → "Add Product"
4. Fill in details and save

### Add Sales Data (via Admin)
1. Go to http://127.0.0.1:8000/admin/
2. Click "Sales Data" → "Add Sales Data"
3. Select product, date, and quantity sold
4. Save

### View Product Forecast
1. On dashboard, use the dropdown in "Sales vs Forecast" chart
2. Click the eye icon (👁️) in the Actions column
3. View detailed forecast in modal

### Filter Inventory Table
- **Search:** Type in the search box
- **Status Filter:** Select status from dropdown
- **Pagination:** Use links at bottom

---

## Forecasting Logic Quick Guide

### Model Selection
- **Linear Regression:** Used when ≥10 days of historical data
- **Moving Average:** Used when <10 days of data

### Features Used
- Day of week
- Month
- Rolling averages (7-day, 30-day)
- Trend component
- Lag features

### Status Calculation
```
Current Stock < Safety Stock → CRITICAL
Current Stock < Predicted Demand + Safety Stock → LOW STOCK
Current Stock > Predicted Demand × 2 → OVER-STOCK
Otherwise → GOOD
```

### Order Quantity Formula
```
Order Qty = max(0, (Predicted Demand + Safety Stock) - Current Stock)
```

---

## Customization

### Change Forecast Period
Edit [inventory/utils.py]:
```python
FORECAST_DAYS = 30  # Change to desired days
```

### Modify Safety Stock
Edit [inventory/models.py]:
```python
safety_stock = models.IntegerField(default=10)
```

### Change Chart Colors
Edit [static/js/dashboard.js]:
```javascript
const CHART_COLORS = {
    primary: 'rgb(52, 152, 219)',
    secondary: 'rgb(46, 204, 113)',
    // ... etc
};
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ESC | Close modal |
| Ctrl+R | Refresh dashboard |

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Server won't start | Use different port: `python manage.py runserver 8080` |
| No data showing | Run: `python scripts/generate_dummy_data.py` |
| Charts not loading | Check browser console (F12) for errors |
| Import errors | Reinstall: `pip install -r requirements.txt --force-reinstall` |
| Migration errors | Delete db.sqlite3 and run `python manage.py migrate` |

---

## API Quick Examples

### Get All Forecasts
```bash
curl http://127.0.0.1:8000/api/forecast/all/
```

### Get Specific Product Forecast
```bash
curl http://127.0.0.1:8000/api/forecast/1/
```

### Get Dashboard Statistics
```bash
curl http://127.0.0.1:8000/api/dashboard/stats/
```

### Python Example
```python
import requests

# Get forecast for product ID 1
response = requests.get('http://127.0.0.1:8000/api/forecast/1/')
data = response.json()

print(f"Product: {data['forecast']['product_name']}")
print(f"Predicted Demand: {data['forecast']['total_predicted_demand']}")
print(f"Suggested Order: {data['forecast']['suggested_order_quantity']}")
```

---

## Status Colors Reference

| Status | Color | Meaning |
|--------|-------|---------|
| Good | 🟢 Green | Stock level is healthy |
| Low Stock | 🔴 Red | Need to reorder soon |
| Critical | 🔴 Dark Red | Below safety stock |
| Over-stock | 🟠 Orange | Excess inventory |
| Out of Stock | ⚫ Dark Red | Zero stock |

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python, Django, Django REST Framework |
| **Database** | SQLite |
| **AI/ML** | Pandas, NumPy, Scikit-Learn, Statsmodels |
| **Visualization** | Chart.js |

---

## Tips for Best Results

1. **Data Quality:** More historical data = better forecasts
2. **Regular Updates:** Add sales data daily for accuracy
3. **Review Forecasts:** Check predictions weekly
4. **Adjust Safety Stock:** Based on supplier lead times
5. **Monitor Trends:** Use charts to identify patterns

---

## Version Info

- **System Version:** 1.0
- **Django Version:** 4.2.7
- **Python Required:** 3.8+

---

**For detailed documentation, see [README.md](README.md) and [SETUP.md](SETUP.md)**
