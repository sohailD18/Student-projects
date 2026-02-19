# 🚗 Driver Behavior Analysis Web Application

An AI-powered full-stack web application for analyzing driver behavior patterns and providing safety recommendations based on historical driving data.

## 📋 Project Overview

This application analyzes driving metrics such as speed, braking patterns, acceleration events, and cornering speeds to:
- Calculate a comprehensive **Risk Score (0-100)**
- Classify driver behavior as **Safe**, **Moderate**, or **Risky**
- Provide personalized **safety recommendations**
- Visualize trends with interactive **charts and dashboards**

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript (No frameworks)
- **Backend**: Python Django 6.0.2
- **Database**: SQLite (Default Django DB)
- **AI/Analysis**: Custom Python algorithms (ai_utils.py)
- **Visualization**: Chart.js 4.4.0

## 📁 Project Structure

```
Project3/
├── driver_behavior_env/          # Virtual Environment
├── driver_behavior_project/       # Django Project Settings
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI config
├── driver_app/                   # Main Django App
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── urls.py                   # App URL routing
│   ├── admin.py                  # Admin configuration
│   ├── ai_utils.py               # AI Analysis Engine
│   └── migrations/               # Database migrations
├── templates/                    # HTML Templates
│   ├── base.html                 # Base template
│   ├── dashboard.html            # Main dashboard
│   ├── add_trip.html             # Data entry form
│   ├── trip_detail.html          # Trip details view
│   └── driver_report.html        # Driver performance report
├── static/                       # Static Files
│   ├── css/
│   │   └── styles.css           # Custom CSS
│   └── js/
│       └── main.js              # Common JavaScript
├── manage.py                     # Django management script
├── db.sqlite3                    # SQLite Database
└── README.md                     # This file
```

## 🚀 Setup Instructions

### Phase 1: Environment Setup

```bash
# Navigate to project directory
cd c:\Users\Dell\OneDrive\Desktop\Claude2\E-commerce\Project3

# Activate virtual environment
# Windows:
driver_behavior_env\Scripts\activate
# Linux/Mac:
source driver_behavior_env/bin/activate

# Install dependencies (if needed)
pip install django
```

### Phase 2: Database Setup

```bash
# Run migrations (already done)
python manage.py makemigrations
python manage.py migrate
```

### Phase 3: Create Superuser

```bash
# Create admin user (already created)
# Username: admin
# Password: admin123

# To create a new superuser:
python manage.py createsuperuser
```

### Phase 4: Run Development Server

```bash
# Start the development server
python manage.py runserver

# Application will be available at: http://127.0.0.1:8000/
# Admin panel: http://127.0.0.1:8000/admin/
```

## 🎯 Features

### 1. **Dashboard ([首页](http://127.0.0.1:8000/))**
- Overview of all driving statistics
- Interactive charts showing:
  - Risk score trends over time
  - Speed analysis patterns
- Recent trips table with classifications
- Quick action buttons

### 2. **Add Trip Data ([/add/](http://127.0.0.1:8000/add/))**
- Form to input new driving data
- **Real-time AI risk assessment** preview
- Fields include:
  - Driver name
  - Trip date
  - Average speed
  - Maximum speed
  - Cornering speed
  - Harsh braking events
  - Rapid acceleration events

### 3. **AI Analysis Engine**

**Risk Score Calculation (0-100):**
- **Speed Risk** (0-35 points): Based on max and average speeds
- **Braking Risk** (0-25 points): Based on harsh braking events
- **Acceleration Risk** (0-25 points): Based on rapid acceleration events
- **Cornering Risk** (0-15 points): Based on cornering speed

**Classification:**
- **Safe**: Risk score < 30
- **Moderate**: Risk score 30-70
- **Risky**: Risk score > 70

**Recommendations:**
- Personalized suggestions based on weakest metrics
- Actionable safety improvements
- Targeted feedback for specific behaviors

### 4. **Trip Details ([/trip/<id>/](http://127.0.0.1:8000/trip/1/))**
- Detailed view of individual trips
- Full AI recommendations
- Visual safety gauge
- Performance metrics breakdown

### 5. **Driver Reports ([/report/<name>/](http://127.0.0.1:8000/report/John/))**
- Comprehensive driver performance analysis
- Behavior classification distribution
- Trip history with visual progress bars
- Aggregated statistics

### 6. **Admin Panel ([/admin/](http://127.0.0.1:8000/admin/))**
- Full CRUD operations for driver data
- Filter and search capabilities
- Bulk editing support
- Data export options

## 🧪 Testing Guide

### Test Case 1: Safe Driver

1. Navigate to [Add Trip Data](http://127.0.0.1:8000/add/)
2. Enter the following data:
   - Driver Name: `Safe Driver`
   - Date: Today's date
   - Average Speed: `45` km/h
   - Max Speed: `60` km/h
   - Cornering Speed: `25` km/h
   - Harsh Braking: `0`
   - Rapid Acceleration: `0`
3. Click "Analyze & Save Trip Data"
4. **Expected Result**: Risk Score < 30, Classification: "Safe"

### Test Case 2: Risky Driver

1. Navigate to [Add Trip Data](http://127.0.0.1:8000/add/)
2. Enter the following data:
   - Driver Name: `Risky Driver`
   - Date: Today's date
   - Average Speed: `110` km/h
   - Max Speed: `150` km/h
   - Cornering Speed: `75` km/h
   - Harsh Braking: `6`
   - Rapid Acceleration: `5`
3. Click "Analyze & Save Trip Data"
4. **Expected Result**: Risk Score > 70, Classification: "Risky"

### Test Case 3: View Dashboard

1. Navigate to [Dashboard](http://127.0.0.1:8000/)
2. **Verify**:
   - Statistics cards show correct counts
   - Charts display data properly
   - Recent trips table populates
   - Links work correctly

### Test Case 4: Generate Driver Report

1. Click on a driver's name in the dashboard
2. **Verify**:
   - All trips for that driver display
   - Aggregated statistics are accurate
   - Behavior distribution percentages are correct

## 📊 Sample Data

Use the Python shell to add sample data:

```python
from driver_app.models import DriverData
from datetime import date

# Create sample trips
DriverData.objects.create(
    driver_name="John Doe",
    trip_date=date.today(),
    average_speed=65.5,
    max_speed=95.0,
    cornering_speed=40.0,
    harsh_braking_events=2,
    rapid_acceleration_events=1,
    risk_score=35.0,
    behavior_class="Moderate",
    recommendations="Reduce speed in residential areas..."
)
```

## 🔧 Configuration

### Modify Risk Thresholds

Edit [driver_app/ai_utils.py](driver_app/ai_utils.py:98):

```python
def classify_behavior(risk_score: float) -> str:
    if risk_score < 30:      # Adjust Safe threshold
        return 'Safe'
    elif risk_score < 70:    # Adjust Moderate threshold
        return 'Moderate'
    else:
        return 'Risky'
```

### Adjust Risk Scoring

Edit [driver_app/ai_utils.py](driver_app/ai_utils.py:14):

```python
def calculate_risk_score(...):
    # Modify scoring weights and thresholds
    # to customize risk assessment algorithm
```

## 🐛 Troubleshooting

### Issue: Static files not loading

**Solution:**
```bash
# Collect static files
python manage.py collectstatic
```

### Issue: "No module named 'driver_app'"

**Solution:**
- Ensure virtual environment is activated
- Verify `driver_app` is in `INSTALLED_APPS` in settings.py
- Restart the development server

### Issue: Database locked

**Solution:**
```bash
# Delete the database and re-run migrations
del db.sqlite3
python manage.py migrate
```

## 📚 API Endpoints

### Web Interface
- `GET /` - Dashboard
- `GET /add/` - Add trip form
- `POST /add/` - Submit trip data
- `GET /trip/<id>/` - Trip details
- `GET /report/<name>/` - Driver report
- `GET /admin/` - Admin panel

### JSON API
- `GET /api/chart-data/` - Get chart data (JSON)
- `POST /analyze/` - Analyze driving data (JSON)

## 🔐 Security Notes

- **CSRF Protection**: Enabled for all forms
- **SQL Injection**: Protected by Django ORM
- **XSS Protection**: Auto-escaping in templates
- **Input Validation**: Server-side validation on all inputs

## 🚀 Deployment

### For Production:

1. **Update settings.py:**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn driver_behavior_project.wsgi:application
   ```

4. **Set up a database (PostgreSQL recommended):**

## 📝 License

This project is for educational and demonstration purposes.

## 👥 Credits

- **Developer**: Claude AI
- **Framework**: Django
- **Charts**: Chart.js
- **Icons**: Emoji

---

**Happy Coding! 🚗💨**
