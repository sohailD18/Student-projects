# API Documentation
# AI-Based Demand Forecasting & Inventory Management System

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
Currently, the API does not require authentication for development purposes.

---

## Response Format

All API responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message description"
}
```

---

## Forecasting Endpoints

### 1. Get All Products Forecast
Get forecast data for all products in the system.

**Endpoint:** `GET /api/forecast/all/`

**Response:**
```json
{
  "success": true,
  "forecasts": [
    {
      "product_id": 1,
      "product_name": "Wireless Mouse",
      "current_stock": 25,
      "safety_stock": 8,
      "total_predicted_demand": 450,
      "average_daily_demand": 15.0,
      "max_daily_demand": 25,
      "min_daily_demand": 5,
      "suggested_order_quantity": 433,
      "status": "low",
      "status_display": "Low Stock",
      "forecast_days": 30,
      "daily_forecast": [...],
      "historical_data_points": 180,
      "model_used": "Linear Regression"
    }
  ],
  "total": 20
}
```

---

### 2. Get Single Product Forecast
Get forecast data for a specific product.

**Endpoint:** `GET /api/forecast/{product_id}/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Response:**
```json
{
  "success": true,
  "forecast": {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "current_stock": 25,
    "safety_stock": 8,
    "total_predicted_demand": 450,
    "average_daily_demand": 15.0,
    "suggested_order_quantity": 433,
    "status": "low",
    "status_display": "Low Stock",
    "daily_forecast": [
      {
        "date": "2024-01-15",
        "predicted_quantity": 15
      }
    ]
  }
}
```

---

### 3. Get Forecast with Confidence Intervals
Get forecast with upper and lower bounds (95% confidence).

**Endpoint:** `GET /api/forecast/{product_id}/confidence/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Query Parameters:**
- `days` (integer, optional) - Number of days to forecast (default: 30)

**Example:**
```
GET /api/forecast/1/confidence/?days=60
```

**Response:**
```json
{
  "success": true,
  "product_id": 1,
  "forecast": {
    "product_id": 1,
    "total_predicted_demand": 450,
    "has_confidence_intervals": true,
    "confidence_level": 95,
    "average_uncertainty": 5.2,
    "daily_forecast": [
      {
        "date": "2024-01-15",
        "predicted_quantity": 15,
        "lower_bound": 10,
        "upper_bound": 20,
        "range": 10
      }
    ]
  }
}
```

---

## Trend Analysis Endpoints

### 4. Get Product Trend Analysis
Get detailed trend analysis for a specific product.

**Endpoint:** `GET /api/trend/{product_id}/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Query Parameters:**
- `days` (integer, optional) - Analysis period in days (default: 90)

**Example:**
```
GET /api/trend/1/?days=60
```

**Response:**
```json
{
  "success": true,
  "product_id": 1,
  "analysis": {
    "analysis_period_days": 90,
    "growth_rate": 12.5,
    "trend_direction": "increasing",
    "trend_display": "Rising Trend",
    "volatility": 15.3,
    "momentum": 8.2,
    "peak_sales_day": "Saturday",
    "current_7day_avg": 16.5,
    "current_30day_avg": 15.2,
    "overall_average": 14.8,
    "max_sales": 35,
    "min_sales": 5,
    "total_sales_in_period": 1332
  }
}
```

---

### 5. Get All Products Trends
Get trend analysis summary for all products.

**Endpoint:** `GET /api/trends/all/`

**Response:**
```json
{
  "success": true,
  "trends": [
    {
      "product_id": 1,
      "product_name": "Wireless Mouse",
      "category": "Electronics",
      "trend_direction": "increasing",
      "trend_display": "Rising Trend",
      "growth_rate": 12.5,
      "volatility": 15.3,
      "momentum": 8.2
    }
  ],
  "total": 20
}
```

---

## Model Accuracy Endpoints

### 6. Get Model Accuracy Metrics
Get accuracy metrics for the forecasting model.

**Endpoint:** `GET /api/accuracy/{product_id}/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Response:**
```json
{
  "success": true,
  "product_id": 1,
  "accuracy": {
    "test_samples": 36,
    "mape": 8.5,
    "rmse": 3.2,
    "mae": 2.5,
    "r_squared": 0.89,
    "accuracy_level": "Excellent",
    "model_confidence": "high",
    "actual_avg": 15.2,
    "predicted_avg": 15.8
  }
}
```

**Accuracy Metrics Explained:**
- **MAPE**: Mean Absolute Percentage Error (lower is better, <10% is excellent)
- **RMSE**: Root Mean Square Error (lower is better)
- **MAE**: Mean Absolute Error (lower is better)
- **R²**: R-squared score (0-1, higher is better, >0.8 is good)
- **accuracy_level**: Excellent (<10%), Good (<20%), Fair (<30%), Poor (>30%)

---

## Chart Data Endpoints

### 7. Get Product Chart Data
Get combined historical and forecast data for visualization.

**Endpoint:** `GET /api/chart/{product_id}/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Response:**
```json
{
  "success": true,
  "product_name": "Wireless Mouse",
  "historical": {
    "labels": ["2024-01-01", "2024-01-02", ...],
    "values": [15, 18, 12, ...]
  },
  "forecast": {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "daily_forecast": [
      {
        "date": "2024-02-01",
        "predicted_quantity": 16
      }
    ]
  }
}
```

---

### 8. Get Historical Sales Data
Get historical sales data for a product.

**Endpoint:** `GET /api/sales/{product_id}/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Query Parameters:**
- `days` (integer, optional) - Number of days of data (default: 90)

**Example:**
```
GET /api/sales/1/?days=180
```

**Response:**
```json
{
  "success": true,
  "product_id": 1,
  "data": {
    "labels": ["2024-01-01", "2024-01-02", ...],
    "values": [15, 18, 12, ...]
  }
}
```

---

## Dashboard Endpoints

### 9. Get Dashboard Statistics
Get aggregate statistics for dashboard KPIs.

**Endpoint:** `GET /api/dashboard/stats/`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_products": 20,
    "total_inventory_value": 15420.50,
    "low_stock_count": 5,
    "total_recent_sales": 450,
    "average_daily_sales": 15.0,
    "category_counts": {
      "Electronics": 5,
      "Clothing": 5,
      "Food & Beverages": 5,
      "Home & Garden": 5
    }
  }
}
```

---

### 10. Get Inventory Summary
Get comprehensive inventory summary.

**Endpoint:** `GET /api/inventory/summary/`

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_inventory_value": 15420.50,
    "total_products": 20,
    "status_counts": {
      "low": 3,
      "good": 12,
      "overstock": 3,
      "critical": 1,
      "out_of_stock": 1
    },
    "category_distribution": {
      "Electronics": 5,
      "Clothing": 5,
      "Food & Beverages": 5,
      "Home & Garden": 5
    },
    "low_stock_items": [...]
  }
}
```

---

## Product Management Endpoints

### 11. Get Products List
Get paginated list of all products.

**Endpoint:** `GET /api/products/`

**Query Parameters:**
- `page` (integer, optional) - Page number (default: 1)
- `category` (string, optional) - Filter by category
- `search` (string, optional) - Search by name

**Examples:**
```
GET /api/products/?page=2
GET /api/products/?category=electronics
GET /api/products/?search=mouse
```

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": 1,
      "name": "Wireless Mouse",
      "category": "Electronics",
      "current_stock": 25,
      "price": 29.99,
      "safety_stock": 8
    }
  ],
  "page": 1,
  "total_pages": 2,
  "total_count": 20
}
```

---

## Report Endpoints

### 12. Get Replenishment Report
Get report of items needing reorder.

**Endpoint:** `GET /api/reports/replenishment/`

**Response:**
```json
{
  "success": true,
  "report": [
    {
      "product_id": 1,
      "product_name": "Wireless Mouse",
      "suggested_order_quantity": 433,
      "current_stock": 25,
      "total_predicted_demand": 450
    }
  ],
  "summary": {
    "total_items_to_reorder": 5,
    "total_units_needed": 1250,
    "estimated_cost": 31250.0
  }
}
```

---

### 13. Get Comprehensive Product Report
Get complete report for a single product.

**Endpoint:** `GET /api/report/{product_id}/comprehensive/`

**URL Parameters:**
- `product_id` (integer, required) - Product ID

**Response:**
```json
{
  "success": true,
  "report": {
    "product_info": {
      "id": 1,
      "name": "Wireless Mouse",
      "category": "Electronics",
      "current_stock": 25,
      "safety_stock": 8,
      "price": 29.99
    },
    "forecast": { ... },
    "trend_analysis": { ... },
    "model_accuracy": { ... },
    "historical_data": { ... },
    "report_generated_at": "2024-01-15T10:30:00"
  }
}
```

---

## System Endpoints

### 14. Health Check
Check system health status.

**Endpoint:** `GET /health/`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected"
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 404 | Resource not found (e.g., invalid product_id) |
| 500 | Internal server error |

---

## Usage Examples

### Python
```python
import requests

# Get all forecasts
response = requests.get('http://127.0.0.1:8000/api/forecast/all/')
data = response.json()

# Get specific product forecast
product_id = 1
response = requests.get(f'http://127.0.0.1:8000/api/forecast/{product_id}/')
forecast = response.json()
print(f"Predicted demand: {forecast['forecast']['total_predicted_demand']}")

# Get trend analysis
response = requests.get(f'http://127.0.0.1:8000/api/trend/{product_id}/')
trend = response.json()
print(f"Growth rate: {trend['analysis']['growth_rate']}%")

# Get replenishment report
response = requests.get('http://127.0.0.1:8000/api/reports/replenishment/')
report = response.json()
print(f"Items to reorder: {report['summary']['total_items_to_reorder']}")
```

### JavaScript (Fetch)
```javascript
// Get all forecasts
fetch('http://127.0.0.1:8000/api/forecast/all/')
  .then(response => response.json())
  .then(data => console.log(data));

// Get specific product forecast
const productId = 1;
fetch(`http://127.0.0.1:8000/api/forecast/${productId}/`)
  .then(response => response.json())
  .then(data => {
    console.log('Predicted demand:', data.forecast.total_predicted_demand);
  });

// Get trend analysis
fetch(`http://127.0.0.1:8000/api/trend/${productId}/`)
  .then(response => response.json())
  .then(data => {
    console.log('Growth rate:', data.analysis.growth_rate + '%');
  });
```

### cURL
```bash
# Get all forecasts
curl http://127.0.0.1:8000/api/forecast/all/

# Get specific product forecast
curl http://127.0.0.1:8000/api/forecast/1/

# Get forecast with confidence intervals
curl http://127.0.0.1:8000/api/forecast/1/confidence/?days=60

# Get trend analysis
curl http://127.0.0.1:8000/api/trend/1/

# Get model accuracy
curl http://127.0.0.1:8000/api/accuracy/1/

# Get replenishment report
curl http://127.0.0.1:8000/api/reports/replenishment/
```

---

## Rate Limiting

Currently, there are no rate limits in development. For production, implement rate limiting based on your requirements.

---

## Versioning

API Version: 1.0

Future versions will be indicated in the URL path (e.g., `/api/v2/forecast/`).

---

## Support

For issues or questions, refer to the main documentation or create an issue in the project repository.
