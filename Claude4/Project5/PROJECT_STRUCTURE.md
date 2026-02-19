# AI Trip Planner - Project Structure

## Complete File Tree

```
Project5/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── setup.bat                          # Windows automated setup script
├── README.md                          # Full documentation
├── QUICKSTART.md                      # Quick start guide
├── .gitignore                         # Git ignore rules
│
├── trip_planner_ai/                   # Django project configuration
│   ├── __init__.py
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # Root URL configuration
│   └── wsgi.py                        # WSGI config
│
├── core/                              # Main application
│   ├── __init__.py
│   ├── apps.py                        # App configuration
│   ├── models.py                      # Database models (4 tables)
│   ├── views.py                       # Business logic & AI predictions
│   ├── urls.py                        # App URL routes
│   ├── admin.py                       # Admin panel configuration
│   │
│   └── management/                    # Django management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           ├── train_model.py         # ML model training (5000 samples)
│           └── seed_locations.py      # Seed sample locations (18 locations)
│
├── templates/                         # HTML templates
│   ├── base.html                      # Base template with Bootstrap 5
│   ├── index.html                     # Home page with trip form
│   ├── result.html                    # Results page with map
│   └── about.html                     # About project page
│
├── static/                            # Static files (CSS, JS, Images)
│   ├── css/
│   │   └── style.css                  # Custom styles (~400 lines)
│   └── js/
│       └── main.js                    # Frontend JavaScript (~300 lines)
│
├── db.sqlite3                         # SQLite database (created after migrations)
├── travel_model.pkl                   # Trained ML model (created after training)
├── model_features.pkl                 # Feature names for prediction
└── training_data.csv                  # Sample training data (5000 records)
```

## Code Statistics

| Component | Files | Lines of Code | Description |
|-----------|-------|---------------|-------------|
| **Python Backend** | 6 | ~1,500 | Django views, models, admin, commands |
| **HTML Templates** | 4 | ~900 | Jinja2 templates with Bootstrap 5 |
| **CSS Styles** | 1 | ~400 | Custom responsive styles |
| **JavaScript** | 1 | ~300 | Frontend interactivity |
| **Configuration** | 4 | ~200 | Django settings, URLs, requirements |
| **Documentation** | 3 | ~600 | README, quick start, project structure |
| **TOTAL** | **19** | **~3,900** | Complete project |

## Key Code Files

### 1. [core/models.py](core/models.py) - 285 lines
**4 Database Models:**
- `Location` - Geographic locations with coordinates
- `TripHistory` - Historical trip data for ML training
- `UserPreference` - User settings and personalization
- `RouteSuggestion` - Cached route recommendations

### 2. [core/views.py](core/views.py) - 430 lines
**Key Functions:**
- `load_ai_model()` - Load trained ML model
- `predict_travel_time()` - AI prediction with fallback
- `haversine_distance()` - Distance calculation
- `generate_routes()` - 3 route options (fastest, shortest, scenic)
- `home()` - Home page with form
- `plan_trip()` - Process trip request
- `location_search()` - API for autocomplete

### 3. [core/management/commands/train_model.py](core/management/commands/train_model.py) - 230 lines
**ML Pipeline:**
1. Generate 5,000 dummy trip records
2. Encode features (distance, traffic, weather, transport)
3. Train RandomForestRegressor (100 trees, depth 15)
4. Save model and feature names
5. Display performance metrics

### 4. [templates/index.html](templates/index.html) - 180 lines
**Features:**
- Hero section with gradient background
- Source/destination dropdowns
- Transport mode selection (buttons)
- Traffic level slider (1-10)
- Weather condition dropdown
- Feature cards showcase

### 5. [templates/result.html](templates/result.html) - 290 lines
**Features:**
- Interactive map with Leaflet.js
- 3 route cards with details
- Route polylines on map
- AI insights section
- Traffic/weather impact analysis

### 6. [static/css/style.css](static/css/style.css) - 400 lines
**Styling:**
- Gradient backgrounds
- Card hover effects
- Responsive design
- Dark mode support (optional)
- Print styles
- Accessibility features

### 7. [static/js/main.js](static/js/main.js) - 300 lines
**Features:**
- Location search with debounce
- Form validation
- Toast notifications
- Map initialization helpers
- Loading states
- Event tracking

## Database Schema

### Location Table
```sql
- id (UUID, PK)
- name (VARCHAR 255)
- address (TEXT)
- city (VARCHAR 100)
- state (VARCHAR 100)
- latitude (DECIMAL 9,6)
- longitude (DECIMAL 9,6)
- location_type (VARCHAR 20)
- is_popular (BOOLEAN)
```

### TripHistory Table
```sql
- id (UUID, PK)
- source (FK → Location)
- destination (FK → Location)
- distance (FLOAT)
- traffic_level (INT 1-10)
- travel_time (FLOAT)
- weather_condition (VARCHAR 20)
- transport_mode (VARCHAR 20)
- route_type (VARCHAR 50)
- fuel_cost (FLOAT)
- date_of_travel (DATETIME)
```

### UserPreference Table
```sql
- id (UUID, PK)
- user (FK → User, nullable)
- session_id (VARCHAR 100)
- preferred_transport_mode (VARCHAR 20)
- route_priority (VARCHAR 20)
- avoid_tolls (BOOLEAN)
- avoid_highways (BOOLEAN)
- default_home_location (FK → Location)
- default_work_location (FK → Location)
```

## ML Model Details

### Training Command
```bash
python manage.py train_model
```

### Model Architecture
- **Algorithm**: RandomForestRegressor
- **Estimators**: 100 trees
- **Max Depth**: 15
- **Features**: 4 (distance, traffic, weather, transport)
- **Target**: travel_time (minutes)

### Feature Encoding
| Feature | Type | Encoding | Values |
|---------|------|----------|--------|
| Distance | Continuous | None | km |
| Traffic Level | Ordinal | None | 1-10 |
| Weather | Categorical | Label Encoding | 0-4 |
| Transport Mode | Categorical | Label Encoding | 0-2 |

### Performance Metrics
- **MAE**: ~5-8 minutes
- **RMSE**: ~8-12 minutes
- **R²**: ~0.85-0.92
- **Training Samples**: 5,000

## URL Routes

| Pattern | View | Purpose |
|---------|------|---------|
| `/` | `home` | Home page with form |
| `/plan-trip/` | `plan_trip` | Process trip request |
| `/api/search-locations/` | `location_search` | Autocomplete API |
| `/about/` | `about` | Project information |
| `/admin/` | Django Admin | Database management |

## Frontend Technologies

### CDN Links Used
```html
<!-- Bootstrap 5 CSS -->
https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/

<!-- Bootstrap Icons -->
https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/

<!-- Leaflet CSS -->
https://unpkg.com/leaflet@1.9.4/

<!-- Leaflet JS -->
https://unpkg.com/leaflet@1.9.4/

<!-- OpenStreetMap Tiles -->
https://{s}.tile.openstreetmap.org/
```

## Setup Commands Reference

```bash
# Virtual Environment
python -m venv venv
venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate

# Seed Data
python manage.py seed_locations

# Train AI
python manage.py train_model

# Create Admin User
python manage.py createsuperuser

# Run Server
python manage.py runserver
```

## File Size Estimates

| File | Size |
|------|------|
| db.sqlite3 (initial) | ~100 KB |
| travel_model.pkl | ~2-5 MB |
| model_features.pkl | ~1 KB |
| training_data.csv | ~500 KB |

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive design)

## Academic Documentation

### Project Report Sections
1. **Introduction** - Problem statement, objectives
2. **System Analysis** - Requirements, feasibility
3. **System Design** - Architecture, database, UI
4. **Implementation** - Code organization, algorithms
5. **Testing** - Test cases, screenshots
6. **ML Model** - Algorithm selection, training, evaluation
7. **Conclusion** - Results, future scope
8. **Bibliography** - References

### Screenshot Locations
- Home page: `index.html`
- Form submission: Browser dev tools
- Results page: `result.html` (after planning a trip)
- Admin panel: http://127.0.0.1:8000/admin/
- Model training: Command prompt after `train_model`
- Database tables: Admin panel or Django shell

---

**Project Completed: January 2024**
**Total Development Time: ~10-15 hours**
**Academic Value: Final Year BCA Project**
