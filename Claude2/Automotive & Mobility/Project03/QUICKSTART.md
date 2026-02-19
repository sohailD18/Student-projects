# 🚀 Quick Start Guide - Driver Behavior Analysis System

## Running the Application

### Step 1: Activate Virtual Environment

**Windows:**
```bash
cd c:\Users\Dell\OneDrive\Desktop\Claude2\E-commerce\Project3
driver_behavior_env\Scripts\activate
```

**Linux/Mac:**
```bash
cd /path/to/Project3
source driver_behavior_env/bin/activate
```

### Step 2: Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **Login Page**: http://127.0.0.1:8000/login/
- **Dashboard**: http://127.0.0.1:8000/ (requires login)
- **Admin Panel**: http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `admin1234`

## 🔐 Demo Credentials

### Admin Account
```
Username: admin
Password: admin1234
```

### Demo Users (All with password: user123)
- **john** - Mostly Safe Driver (12 trips)
- **sarah** - Mixed Driver (12 trips)
- **mike** - Moderate Driver (12 trips)
- **emma** - Very Safe Driver (12 trips)
- **david** - Risky Driver (12 trips)

**Total**: 60 pre-loaded trip records!

### Step 3: Add Test Data

**Option A: Using the Web Form**
1. Go to http://127.0.0.1:8000/add/
2. Fill in the form with driving data
3. Click "Analyze & Save Trip Data"
4. View results on the dashboard

**Option B: Using Django Admin**
1. Go to http://127.0.0.1:8000/admin/
2. Log in with admin/admin123
3. Click "Driver Data Records"
4. Click "Add Driver Data"
5. Fill in the fields (risk score will be calculated automatically)

**Option C: Using Python Shell**
```bash
python manage.py shell
```

```python
from driver_app.models import DriverData
from datetime import date
from driver_app.ai_utils import analyze_driver_behavior

# Create a new trip
trip = DriverData.objects.create(
    driver_name="John Doe",
    trip_date=date.today(),
    average_speed=65.5,
    max_speed=95.0,
    cornering_speed=40.0,
    harsh_braking_events=2,
    rapid_acceleration_events=1,
)

# Analyze the trip
result = analyze_driver_behavior({
    'average_speed': trip.average_speed,
    'max_speed': trip.max_speed,
    'harsh_braking_events': trip.harsh_braking_events,
    'rapid_acceleration_events': trip.rapid_acceleration_events,
    'cornering_speed': trip.cornering_speed,
})

# Save the analysis results
trip.risk_score = result['risk_score']
trip.behavior_class = result['behavior_class']
trip.recommendations = result['recommendations']
trip.save()

print(f"Risk Score: {trip.risk_score}")
print(f"Classification: {trip.behavior_class}")
```

## Sample Data to Test

### Safe Driver Example
```
Driver Name: Safe Driver
Date: [Today]
Average Speed: 45 km/h
Max Speed: 60 km/h
Cornering Speed: 25 km/h
Harsh Braking: 0
Rapid Acceleration: 0
```
**Expected**: Risk Score < 30, Classification: "Safe"

### Moderate Driver Example
```
Driver Name: Moderate Driver
Date: [Today]
Average Speed: 75 km/h
Max Speed: 100 km/h
Cornering Speed: 50 km/h
Harsh Braking: 2
Rapid Acceleration: 2
```
**Expected**: Risk Score 30-70, Classification: "Moderate"

### Risky Driver Example
```
Driver Name: Risky Driver
Date: [Today]
Average Speed: 110 km/h
Max Speed: 150 km/h
Cornering Speed: 75 km/h
Harsh Braking: 6
Rapid Acceleration: 5
```
**Expected**: Risk Score > 70, Classification: "Risky"

## Key Features to Test

1. **Dashboard Charts**
   - Risk Score Trends (Last 30 Days)
   - Speed Analysis (Last 30 Days)
   - Real-time updates when adding new data

2. **Real-Time AI Preview**
   - On the "Add Trip" page
   - Risk score updates as you type
   - Immediate classification feedback

3. **Driver Reports**
   - Click on any driver name in the dashboard
   - See aggregated statistics
   - View behavior distribution

4. **Trip Details**
   - Click "View Details" on any trip
   - See full AI recommendations
   - Visual safety gauge

## Troubleshooting

### "No module named 'driver_app'"
```bash
# Ensure virtual environment is activated
# Windows:
driver_behavior_env\Scripts\activate

# Restart the server
python manage.py runserver
```

### Database Issues
```bash
# Reset the database
del db.sqlite3
python manage.py migrate

# Create superuser again
python manage.py createsuperuser
```

### Port 8000 Already in Use
```bash
# Use a different port
python manage.py runserver 8080
```

### Templates Not Loading
```bash
# Check if templates directory exists
ls templates/

# Verify Django settings
python manage.py check
```

## Project File Structure

```
Project3/
├── driver_app/                  # Main application
│   ├── ai_utils.py             # AI analysis engine
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   └── urls.py                 # URL routing
├── templates/                   # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── add_trip.html
│   ├── trip_detail.html
│   └── driver_report.html
├── static/                      # CSS and JS files
│   ├── css/styles.css
│   └── js/main.js
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database
└── README.md                    # Full documentation
```

## Next Steps

1. **Add Real Data**: Start tracking real driving metrics
2. **Customize Risk Thresholds**: Edit `driver_app/ai_utils.py`
3. **Add More Metrics**: Extend the `DriverData` model
4. **Export Reports**: Add PDF export functionality
5. **Deploy**: Use Gunicorn + Nginx for production

## Support

For detailed documentation, see [README.md](README.md)

---

**Built with Django 6.0, Python 3.13, and Chart.js**
