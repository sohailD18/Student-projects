# 🚗 Intelligent Route Planning & Optimization System

A full-stack web application for AI-powered route optimization with real-time traffic analysis, cost estimation, and comprehensive analytics.

## 🌟 Features

- **🗺️ Interactive Map**: Click-to-select origin and destination using Leaflet.js and OpenStreetMap
- **🤖 AI Route Optimization**: Heuristic algorithm simulating intelligent route planning
- **🚦 Traffic Simulation**: Time-based traffic patterns (rush hours, weekends, etc.)
- **💰 Cost Estimation**: Fuel cost and CO2 emission calculations
- **📊 Analytics Dashboard**: Traffic patterns, route distribution, and efficiency trends
- **📄 Export Reports**: Generate downloadable route summary reports
- **🌱 Multiple Route Types**: Fastest, Shortest, Scenic, and Eco-Friendly options

## 🛠️ Tech Stack

**Backend:**
- Django 4.2+ (Python)
- SQLite Database
- RESTful API endpoints

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Leaflet.js (Interactive Maps - No API Key Required!)
- Chart.js (Analytics Dashboard)
- OpenStreetMap (Free Map Tiles)

**No external API keys required!** Everything works out of the box.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional - for Admin Panel)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 4. Run the Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

Open your browser and navigate to:
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📖 How to Use

### Planning a Route

1. **Set Origin Location**: Click anywhere on the map to place a blue marker (origin)
2. **Set Destination**: Click again to place a red marker (destination)
3. **Name Your Locations** (optional): Enter location names in the input fields
4. **Calculate Routes**: Click the "🚀 Calculate Routes" button
5. **View Options**: See 4 different route options:
   - **Fastest Route** (Blue) - Optimized for travel time
   - **Shortest Route** (Green) - Minimal distance
   - **Most Scenic Route** (Purple) - Longer but enjoyable
   - **Eco-Friendly Route** (Emerald) - Best for fuel efficiency

### Understanding Route Cards

Each route card displays:
- **Distance**: Total distance in kilometers
- **Time**: Estimated travel time (considering traffic)
- **Fuel Cost**: Estimated fuel cost in USD
- **CO2 Emissions**: Environmental impact in kg

### Analytics Dashboard

The dashboard provides:
- **Hourly Traffic Pattern**: Traffic levels throughout the day
- **Weekly Comparison**: Average route metrics by day
- **Route Distribution**: Popularity of different route types
- **Efficiency Trend**: Optimization performance over time

### Exporting Reports

1. Calculate and select a route
2. Click "📄 Export Report"
3. A text file with comprehensive route details will be downloaded

## 🏗️ Project Structure

```
route_optimizer/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── db.sqlite3               # SQLite database (created after migration)
│
├── route_optimizer/         # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── route_planner/           # Main application
│   ├── __init__.py
│   ├── admin.py             # Admin panel configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── views.py             # View functions & API endpoints
│   ├── urls.py              # App URL routing
│   ├── api_urls.py          # API endpoint routing
│   ├── optimization_engine.py  # AI route optimization logic
│   │
│   └── migrations/          # Database migrations
│       └── __init__.py
│
├── templates/               # HTML templates
│   └── index.html           # Main application page
│
└── static/                  # Static files
    ├── css/
    │   └── style.css        # Main stylesheet
    └── js/
        └── app.js           # Frontend JavaScript
```

## 🗄️ Database Models

### Location
Geographic locations with coordinates

### TrafficData
Simulated traffic data for route optimization

### Route
Routes between locations with metadata

### RouteHistory
Historical record of route calculations

### OptimizationMetrics
Performance metrics for the AI engine

## 🔧 API Endpoints

### POST `/api/calculate-routes/`
Calculate routes between two locations

**Request:**
```json
{
  "origin_name": "New York",
  "origin_lat": 40.7128,
  "origin_lng": -74.0060,
  "destination_name": "Boston",
  "destination_lat": 42.3601,
  "destination_lng": -71.0589
}
```

**Response:**
```json
{
  "success": true,
  "routes": {
    "fastest": {...},
    "shortest": {...},
    "scenic": {...},
    "eco": {...}
  }
}
```

### GET `/api/analytics/`
Get analytics data for charts

### GET `/api/history/`
Get route calculation history

### POST `/api/export-report/`
Generate and export route report

### GET `/api/dashboard-stats/`
Get dashboard statistics

## 🤖 AI Optimization Engine

The optimization engine uses heuristic algorithms to:

1. **Calculate Distance**: Haversine formula for accurate distances
2. **Simulate Traffic**: Time-based traffic patterns
3. **Generate Routes**: Multiple route options with trade-offs
4. **Select Best Route**: Weighted scoring system
5. **Estimate Costs**: Fuel consumption and CO2 emissions

### Traffic Simulation

- **Rush Hours** (7-9 AM, 5-7 PM, weekdays): 1.8-2.5x traffic factor
- **Daytime** (10 AM-4 PM): 1.2-1.5x traffic factor
- **Evening** (8-10 PM): 1.1-1.3x traffic factor
- **Nights/Weekends**: 0.9-1.2x traffic factor

### Route Selection Algorithm

Routes are scored based on:
- **Time Efficiency** (50% weight)
- **Distance** (30% weight)
- **Environmental Impact** (20% weight)

## 🎨 Customization

### Adjusting Traffic Patterns

Edit `route_planner/optimization_engine.py`:

```python
def simulate_traffic_factor(self, distance_km, base_time_minutes):
    # Modify traffic patterns here
    if self.current_hour in [7, 8, 9, 17, 18, 19]:
        hour_factor = 2.0  # Peak traffic
    # ...
```

### Changing Fuel Prices

Edit the constants in `optimization_engine.py`:

```python
FUEL_PRICE_PER_LITER = 3.5  # USD
FUEL_CONSUMPTION_L_PER_100KM = 8.5  # Liters per 100km
```

### Modifying Route Colors

Edit `static/css/style.css`:

```css
.route-fastest { border-left: 4px solid #2563eb; }
.route-shortest { border-left: 4px solid #16a34a; }
/* ... */
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Use a different port
python manage.py runserver 8001
```

### Migration Errors

```bash
# Reset migrations
python manage.py makemigrations route_planner --empty
python manage.py migrate route_planner --zero
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading

Ensure `DEBUG = True` in `settings.py` during development.

## 🚀 Deployment

### For Production

1. Set `DEBUG = False` in `settings.py`
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production WSGI server (e.g., Gunicorn):

```bash
pip install gunicorn
gunicorn route_optimizer.wsgi:application
```

4. Collect static files:

```bash
python manage.py collectstatic
```

## 📝 License

This project is open source and available for educational purposes.

## 👥 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📧 Support

For questions or issues, please open an issue on the project repository.

---

**Built with ❤️ using Django, Python, and modern web technologies**
