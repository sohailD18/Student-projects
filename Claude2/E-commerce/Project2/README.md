# AI-Based Demand Forecasting and Inventory Management System

## 🎯 Project Overview
A comprehensive web application that leverages machine learning to predict product demand and optimize inventory management for retail businesses.

## ✨ Key Features

### 1. **AI-Powered Demand Forecasting**
- Uses historical sales data to predict future demand
- Implements Linear Regression and Time Series analysis
- 30-day forecast with confidence intervals
- Automatic model training for each product

### 2. **Smart Inventory Management**
- Real-time stock monitoring
- Automated replenishment suggestions
- Safety stock calculations
- Multi-status alerts (Low Stock, Good, Over-stock)

### 3. **Visual Dashboard**
- Interactive charts using Chart.js
- Sales trend visualization
- Forecast comparison
- Inventory health metrics

### 4. **Data Management**
- Easy product entry
- Historical sales data input
- Bulk data import capability
- Automatic dummy data generation

## 🏗️ Architecture

### Data Flow
```
User Input → Database → AI Model → Forecast → Dashboard
   ↓           ↓          ↓          ↓          ↓
Products    SQLite   Scikit-Learn  JSON    Chart.js
Sales Data  Django    Pandas       API     Visualization
```

### Component Breakdown

**Backend (Django)**
- **Models**: Product, SalesData
- **Views**: Dashboard, Forecasting API
- **Utils**: AI/ML forecasting logic

**Frontend (HTML/CSS/JS)**
- **Templates**: Dashboard layout
- **CSS**: Responsive design
- **JavaScript**: Chart.js integration, AJAX calls

**AI/ML Layer**
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **Scikit-Learn**: Machine learning models

## 📊 Database Schema

### Product Model
```python
- id: AutoField
- name: CharField (max_length=200)
- category: CharField (max_length=100)
- current_stock: IntegerField
- price: DecimalField (max_digits=10, decimal_places=2)
- safety_stock: IntegerField (default=10)
- created_at: DateTimeField
- updated_at: DateTimeField
```

### SalesData Model
```python
- id: AutoField
- product: ForeignKey (Product)
- date: DateField
- quantity_sold: IntegerField
- revenue: DecimalField (calculated field)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone/Create Project Directory**
```bash
mkdir inventory_forecast_system
cd inventory_forecast_system
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Generate Dummy Data** (Optional)
```bash
python scripts/generate_dummy_data.py
```

5. **Run Development Server**
```bash
python manage.py runserver
```

6. **Access Application**
```
http://127.0.0.1:8000/
```

## 📁 Project Structure

```
inventory_forecast_system/
├── inventory_project/          # Django Project Settings
├── inventory/                  # Main Django App
│   ├── models.py              # Database Models
│   ├── views.py               # View Functions
│   ├── urls.py                # URL Routing
│   └── utils.py               # AI/ML Logic
├── templates/                  # HTML Templates
├── static/                     # CSS & JavaScript
├── scripts/                    # Utility Scripts
└── manage.py                   # Django Management
```

## 🎨 Dashboard Features

### KPI Cards
- Total Products
- Low Stock Alerts
- Total Inventory Value
- Average Daily Sales

### Charts
- **Sales vs Forecast**: Line chart comparing actual sales with predicted demand
- **Inventory Status**: Bar chart showing stock levels across products
- **Category Distribution**: Pie chart of products by category

### Inventory Table
- Product name and category
- Current stock level
- Predicted demand (30 days)
- Status indicators
- Reorder suggestions

## 🔬 AI/ML Implementation

### Forecasting Algorithm

The system uses a hybrid approach:

1. **Data Aggregation**
   - Group sales by date
   - Calculate daily totals
   - Handle missing dates

2. **Feature Engineering**
   - Day of week
   - Month
   - Trend component
   - Seasonal component

3. **Model Training**
   - Linear Regression for trend
   - Moving Average for baseline
   - Ensemble prediction

4. **Forecast Generation**
   - 30-day future prediction
   - Confidence intervals
   - Anomaly detection

### Replenishment Logic

```
IF current_stock < predicted_demand + safety_stock:
    order_quantity = (predicted_demand + safety_stock) - current_stock
    status = "Low Stock"
ELSE IF current_stock > predicted_demand * 2:
    status = "Over-stock"
ELSE:
    status = "Good"
```

## 📝 API Endpoints

### HTML Views
- `GET /` - Main dashboard

### JSON API
- `GET /api/forecast/<product_id>/` - Get forecast for specific product
- `GET /api/forecast/all/` - Get forecast for all products
- `POST /api/products/` - Create new product
- `POST /api/sales/` - Add sales data

## 🛠️ Customization

### Adjust Forecasting Period
Edit `inventory/utils.py`:
```python
FORECAST_DAYS = 30  # Change to desired days
```

### Modify Safety Stock Formula
Edit `inventory/models.py`:
```python
safety_stock = models.IntegerField(default=10)  # Adjust default
```

### Change Chart Colors
Edit `static/js/dashboard.js`:
```javascript
const CHART_COLORS = {
    primary: '#3498db',
    secondary: '#e74c3c',
    // Modify colors here
};
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Server won't start
**Solution**: Check port 8000 availability, or use `python manage.py runserver 8080`

**Issue**: No data in dashboard
**Solution**: Run dummy data generator: `python scripts/generate_dummy_data.py`

**Issue**: Charts not loading
**Solution**: Check browser console for errors, ensure Chart.js CDN is accessible

**Issue**: Import errors
**Solution**: Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Scikit-Learn Documentation](https://scikit-learn.org/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📄 License

This project is open source and available for educational purposes.

## 👥 Contributing

Contributions, issues, and feature requests are welcome!

## 📞 Support

For issues and questions, please open an issue in the repository.

---

**Built with ❤️ using Django, Scikit-Learn, and Chart.js**
