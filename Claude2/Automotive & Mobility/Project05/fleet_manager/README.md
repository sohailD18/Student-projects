# AI-Driven Fleet Management and Analytics System

A production-ready Django application for managing vehicle fleets with AI-powered predictive maintenance, cost optimization, and comprehensive analytics.

## Features

### 1. Fleet Data Management
- **Vehicle Models**: Complete vehicle information (VIN, plate, make, model, year, type, mileage)
- **Driver Management**: Driver profiles with license tracking
- **Trip Tracking**: Record trips with distance, fuel consumption, and routes
- **Maintenance History**: Comprehensive maintenance record tracking
- **Alert System**: Automated alerts for maintenance needs and safety concerns

### 2. Usage Analysis
- Total distance tracking per vehicle
- Fuel consumption analysis
- Operational hours calculation
- Performance metrics per vehicle

### 3. AI-Based Predictive Maintenance
- **Linear Regression Model**: Predicts next maintenance mileage based on:
  - Historical maintenance intervals
  - Mileage patterns
  - Cost trends
- **Failure Probability**: Analyzes risk factors including:
  - High mileage indicators
  - Low fuel efficiency patterns
  - Frequent repair history
  - Overdue maintenance

### 4. Cost Optimization
- Cost-per-mile calculation
- Fuel efficiency ratings (MPG)
- Maintenance cost analysis
- Vehicle efficiency ratings (0-100 scale)

### 5. KPI Dashboard
- **Visual Charts** (Chart.js):
  - Monthly maintenance costs (Bar chart)
  - Fuel efficiency trends (Line chart)
  - Vehicle status distribution (Doughnut chart)
- **KPI Cards**:
  - Total vehicles and active count
  - Total trips and distance
  - Average fuel efficiency
  - Active alerts
- **Predictive Flags**: Vehicles requiring immediate attention

### 6. Predictive Alerts
- Automatic alert generation based on AI predictions
- Severity levels: Info, Warning, Critical, Emergency
- Alert types:
  - Maintenance Due/Overdue
  - Low Efficiency
  - High Mileage
  - Safety Concerns
  - License Expiry

### 7. Reporting System
- Export to CSV formats:
  - Fleet Overview Report
  - Trips Report
  - Maintenance Report
  - AI Analytics Report

## Tech Stack

- **Backend**: Django 4.2 (Python 3.10+)
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: pandas (data manipulation), scikit-learn (Linear Regression)
- **Visualization**: Chart.js
- **Styling**: Bootstrap 5 (CDN)

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
cd fleet_manager
pip install -r requirements.txt
```

### Step 2: Run Migrations

```bash
python manage.py migrate
```

### Step 3: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 4: Collect Static Files (Optional for Production)

```bash
python manage.py collectstatic
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
fleet_manager/
├── core/                      # Main application
│   ├── migrations/            # Database migrations
│   ├── static/                # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── style.css      # Custom styles
│   │   └── js/
│   │       └── main.js        # Frontend JavaScript
│   ├── templates/             # HTML templates
│   │   └── core/
│   │       ├── base.html      # Base template
│   │       ├── dashboard.html # KPI Dashboard
│   │       ├── vehicle_list.html
│   │       ├── vehicle_detail.html
│   │       ├── analytics.html # AI predictions
│   │       └── report.html    # Report export
│   ├── admin.py               # Admin configuration
│   ├── models.py              # Data models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   └── utils.py               # AI/ML utilities
├── fleet_manager/             # Project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI config
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── db.sqlite3                 # SQLite database (created after migration)
```

## Usage Guide

### 1. Access the Dashboard
Navigate to `http://127.0.0.1:8000/dashboard/` to view the fleet dashboard with KPIs and charts.

### 2. Manage Vehicles
- Visit `/vehicles/` to view all vehicles
- Add vehicles through Django Admin at `/admin/core/vehicle/add/`
- Click on a vehicle to view detailed analytics

### 3. View AI Analytics
- Visit `/analytics/` to see:
  - AI predictions for all vehicles
  - Maintenance forecasts
  - Failure risk assessments
  - Efficiency rankings

### 4. Generate Reports
- Visit `/reports/` to export CSV reports
- Available reports:
  - Fleet Overview
  - Trip History
  - Maintenance Records
  - AI Analytics

### 5. Admin Panel
Access `/admin/` to:
- Add/edit vehicles
- Add/edit drivers
- Record trips
- Log maintenance
- Manage alerts

## AI Features Explained

### Predictive Maintenance (Linear Regression)
The system uses scikit-learn's Linear Regression to analyze:
- Past maintenance intervals
- Mileage accumulation patterns
- Maintenance costs

**Prediction Formula**:
```
Next Maintenance Mileage = Last Maintenance Mileage + Predicted Interval
```

The model considers:
- Previous service intervals
- Cost patterns
- Days since last service

### Failure Probability
Risk factors analyzed:
1. **High Mileage Risk**: Vehicles over 100,000 miles
2. **Low Efficiency**: MPG below 15
3. **High Maintenance Costs**: Average cost over $500 per service
4. **Overdue Maintenance**: No service in 90+ days

### Efficiency Rating (0-100)
Calculated based on:
- Fuel efficiency score (up to 50 points)
- Cost-per-mile score (up to 50 points)

**Rating Scale**:
- Excellent (80-100): High efficiency, low cost
- Good (60-79): Above average
- Fair (40-59): Average, improvement needed
- Poor (0-39): Low efficiency, high cost

## API Endpoints (AJAX)

### Refresh Alerts
```http
POST /api/alerts/refresh/
```
Triggers AI analysis to generate new alerts.

### Get Vehicle Stats
```http
GET /api/vehicles/<id>/stats/
```
Returns real-time statistics for a vehicle.

### Dismiss Alert
```http
POST /api/alerts/<id>/dismiss/
```
Marks an alert as resolved.

## Database Models

### Vehicle
- Fields: vin, plate, type, make, model, year, purchase_date, current_mileage, status, fuel_capacity
- Properties: total_distance, fuel_efficiency, cost_per_mile, total_maintenance_cost

### Driver
- Fields: name, email, phone, license_number, license_type, license_expiry, status, hire_date
- Properties: total_trips, total_distance_driven

### Trip
- Fields: vehicle, driver, start_date, end_date, distance, fuel_used, start_location, end_location, status
- Properties: duration_hours, average_speed, fuel_efficiency

### MaintenanceRecord
- Fields: vehicle, date, maintenance_type, mileage_at_service, cost, description, severity, performed_by

### Alert
- Fields: vehicle, alert_type, message, severity, is_active, resolved_date, created_at

## Development

### Adding New Features

1. **Add new model fields**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create custom management command**:
   ```bash
   python manage.py create_custom_command
   ```

3. **Run development server**:
   ```bash
   python manage.py runserver
   ```

### Testing

Add sample data via Django Admin or create a data import script.

## Production Deployment

### Security Checklist
- [ ] Set `DEBUG = False` in settings.py
- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up HTTPS
- [ ] Configure static files serving
- [ ] Set up database backups

### Static Files
```bash
python manage.py collectstatic --noinput
```

## Troubleshooting

### Import Errors
If you encounter `ModuleNotFoundError` for sklearn or pandas:
```bash
pip install -r requirements.txt
```

### Migration Errors
If migrations fail:
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
Run collectstatic:
```bash
python manage.py collectstatic
```

## License

This project is for educational and commercial use.

## Credits

- Built with Django
- AI powered by scikit-learn
- Charts by Chart.js
- Styled with Bootstrap 5
