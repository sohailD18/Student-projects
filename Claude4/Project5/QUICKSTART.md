# Quick Start Guide - AI Trip Planner

## Fastest Setup (Windows)

### Option 1: Automated Setup
1. Double-click `setup.bat`
2. Wait for completion
3. Run: `venv\Scripts\activate`
4. Run: `python manage.py runserver`
5. Open: http://127.0.0.1:8000/

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Seed locations
python manage.py seed_locations

# Train AI model
python manage.py train_model

# Run server
python manage.py runserver
```

## Access Points

| Page | URL |
|------|-----|
| Home | http://127.0.0.1:8000/ |
| Admin | http://127.0.0.1:8000/admin/ |
| About | http://127.0.0.1:8000/about/ |

## Default Locations (After Seeding)

- New Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow
- Landmarks: India Gate, Taj Mahal, Gateway of India, Connaught Place
- Airports: Delhi, Mumbai, Bangalore

## Test Route Examples

1. **Delhi to Mumbai**: ~1,400 km, ~16-20 hours
2. **Delhi to Agra**: ~200 km, ~3-4 hours
3. **Bangalore to Chennai**: ~350 km, ~5-7 hours
4. **Mumbai to Pune**: ~150 km, ~2-3 hours

## Project Files Reference

| File | Purpose |
|------|---------|
| [core/models.py](core/models.py) | Database schema |
| [core/views.py](core/views.py) | Business logic & AI |
| [core/admin.py](core/admin.py) | Admin panel config |
| [core/management/commands/train_model.py](core/management/commands/train_model.py) | ML model training |
| [core/management/commands/seed_locations.py](core/management/commands/seed_locations.py) | Data seeding |
| [templates/index.html](templates/index.html) | Home page form |
| [templates/result.html](templates/result.html) | Results with map |
| [static/css/style.css](static/css/style.css) | Custom styles |
| [static/js/main.js](static/js/main.js) | Frontend scripts |

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `python manage.py runserver 8001` |
| Model not found | `python manage.py train_model` |
| No locations | `python manage.py seed_locations` |
| Migration errors | Delete `db.sqlite3` and run migrations again |

## AI Model Information

- **Algorithm**: RandomForestRegressor
- **Features**: Distance, Traffic Level, Weather, Transport Mode
- **Training Data**: 5,000 simulated trip records
- **Model Files**: `travel_model.pkl`, `model_features.pkl`
- **Retrain Command**: `python manage.py train_model`

## Technology Versions

- Django 5.0.1
- scikit-learn 1.4.0
- pandas 2.2.0
- numpy 1.26.3
- Bootstrap 5.3.2
- Leaflet 1.9.4

## For Presentation/Demo

1. **Start with setup.bat** - Shows automated setup
2. **Show Admin Panel** - Demonstrates Django admin
3. **Plan a Trip** - Delhi to Mumbai (classic example)
4. **Explain AI Features**:
   - Traffic impact (try levels 1 vs 10)
   - Weather effects (clear vs heavy rain)
   - Transport mode differences
5. **Show Code Highlights**:
   - ML model training command
   - AI prediction in views.py
   - Database models
6. **Demo Features**:
   - Multiple route options
   - Interactive map
   - Fuel cost estimation

## Academic Project Tips

### For Viva/Defense Preparation:

**Technical Questions:**
- **Why RandomForest?** - Handles non-linear relationships, robust to outliers
- **How does traffic affect predictions?** - 8% speed reduction per traffic level
- **What features matter most?** - Distance (65%), Traffic (20%), Transport (10%), Weather (5%)
- **Why Django?** - Built-in admin, ORM, security features, rapid development

**Enhancement Ideas:**
- Real-time traffic API integration
- User authentication with saved routes
- Mobile app (React Native)
- EV charging stations
- Carpooling feature
- Historical trip analytics dashboard

**Database Design:**
- **Location** - Geographic data
- **TripHistory** - ML training data
- **UserPreference** - Personalization
- **RouteSuggestion** - Caching for performance

## Contact & Support

For detailed documentation, see [README.md](README.md)
