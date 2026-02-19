# Dynamic Pricing System

An AI-enabled dynamic pricing system built with Django that helps optimize product prices based on sales trends, competitor pricing, and inventory levels.

## Features

- **Dashboard**: Real-time KPIs and revenue/cost/profit charts
- **Product Management**: View and manage your product inventory
- **AI-Powered Pricing Engine**: Intelligent price recommendations based on:
  - Sales trend analysis (increasing/decreasing/stable)
  - Competitor price monitoring
  - Stock level optimization
  - Price elasticity calculations
- **Simulation Tool**: Test hypothetical pricing scenarios
- **Interactive Charts**: Beautiful visualizations using Chart.js
- **Price History**: Track all price changes with reasons

## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Database with Sample Data

```bash
python manage.py seed_db
```

This will create:
- 15 sample products across various categories
- Sales history for the last 90 days
- Competitor price data
- Price change history

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and navigate to:
- **Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Products**: http://127.0.0.1:8000/products/
- **Simulation**: http://127.0.0.1:8000/simulation/

## Usage Guide

### Dashboard

- View KPIs: Total Revenue, Total Sales, Average Margin, Total Products
- Analyze 90-day revenue vs cost vs profit trends
- Quick access to Products and Simulation tools

### Product List

- View all products with key metrics
- See margin percentages (color-coded: green ≥20%, yellow ≥10%, red <10%)
- Check stock levels (color-coded: green >100, blue 10-100, red <10)
- Click "View" to see product details
- Click "Analyze" to run AI analysis

### Product Detail

- View comprehensive product information
- Get AI-powered price recommendations
- See sales history charts (quantity and price trends)
- View competitor price comparisons
- Track price change history

**To use AI recommendations:**
1. Click "Get AI Suggestion" button
2. Review the suggested price and explanation
3. Click "Apply Suggested Price" to update the price

### Simulation

Test hypothetical pricing scenarios:
1. Select a product
2. Enter a hypothetical price
3. Enter expected demand (units to sell)
4. Click "Run Simulation"
5. View comparison of current vs hypothetical profitability

## AI Pricing Algorithm

The Dynamic Pricing Engine uses multiple factors:

1. **Sales Trends**: Analyzes if sales are increasing, decreasing, or stable
2. **Stock Levels**: Considers inventory (low stock → price increase, high stock → price decrease)
3. **Competitor Pricing**: Monitors competitor prices and adjusts accordingly
4. **Price Elasticity**: Calculates demand sensitivity to price changes
5. **Profit Margins**: Ensures minimum viable margins (10% above cost)

### Pricing Rules

- **Decreasing Sales + High Stock**: Lower price to stimulate demand
- **Below Competitor Prices**: Increase price (cap at competitor min - 5%)
- **Low Stock (<10 units)**: Increase price (scarcity principle)
- **Increasing Sales**: Gradual price increase to optimize margins
- **Minimum Margin**: Always maintain at least 10% profit margin

## Project Structure

```
dynamic_pricing/
├── dynamic_pricing/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── pricing_engine/
│   ├── models.py            # Product, SalesHistory, CompetitorPrice, PriceHistory
│   ├── views.py             # All views (dashboard, products, simulation, API)
│   ├── urls.py              # App URL configuration
│   ├── services/
│   │   └── pricing_algorithm.py  # DynamicPricingEngine class
│   ├── templates/pricing_engine/
│   │   ├── base.html        # Base template with navigation
│   │   ├── dashboard.html   # Dashboard with charts
│   │   ├── product_list.html # Product list table
│   │   ├── product_detail.html # Product detail with AI
│   │   └── simulation.html  # Pricing simulation tool
│   └── management/commands/
│       └── seed_db.py       # Database seeding command
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

- `POST /api/products/<id>/update-price/` - Apply AI suggested price
- `POST /api/simulate/` - Run pricing simulation
- `GET /api/products/<id>/suggestion/` - Get AI price suggestion

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite (development)
- **Python**: 3.8+

## Customization

### Adjust Pricing Algorithm

Edit [`pricing_engine/services/pricing_algorithm.py`](pricing_engine/services/pricing_algorithm.py) to modify:
- Lookback period for sales analysis
- Price adjustment percentages
- Minimum margin requirements
- Elasticity calculations

### Add More Products

Edit [`pricing_engine/management/commands/seed_db.py`](pricing_engine/management/commands/seed_db.py) and add to the `products_data` list, then run:
```bash
python manage.py seed_db
```

### Customize Templates

All templates are in `pricing_engine/templates/pricing_engine/`

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check the Django documentation: https://docs.djangoproject.com/
