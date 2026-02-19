# ⚡ EV Trip Planner & AI-Enabled Charging Assistant System

A complete, production-ready Django web application for electric vehicle trip planning and charging station management. Features include an interactive map view, intelligent route planning with charging stops, and an AI-powered chat assistant.

## 🌟 Features

### 1. Trip Planner
- **Route Planning**: Input start location, destination, and vehicle details to calculate optimal routes
- **Battery Consumption Estimation**: Smart algorithms estimate battery usage based on distance and vehicle specs
- **Charging Stop Recommendations**: Automatically suggests charging stations along your route when needed
- **Trip History**: Save and review past trips with detailed information

### 2. Charging Station Finder
- **Interactive Map**: Leaflet.js-powered map with OpenStreetMap showing all charging stations
- **List View**: Searchable and filterable list of stations
- **Real-time Information**: View connector types, power output, pricing, and availability
- **Advanced Filtering**: Filter by connector type, fast charging availability, and price

### 3. AI Charging Assistant
- **Intelligent Chat**: Rule-based AI assistant answering EV-related questions
- **24/7 Availability**: Always ready to help with EV questions
- **Knowledge Base**: Covers battery maintenance, charging tips, range optimization, cost comparisons, and more
- **Floating Widget**: Quick access from any page when logged in

### 4. User Dashboard
- **Vehicle Management**: Add and manage multiple EVs with specifications
- **Trip History**: View all planned trips with status tracking
- **Profile Management**: Update personal information and preferences

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Django 4.2 |
| **Database** | SQLite (default) |
| **Frontend** | HTML5, CSS3 (Flexbox/Grid), Vanilla JavaScript |
| **Mapping** | Leaflet.js with OpenStreetMap |
| **Icons** | Emoji-based (no external icon libraries needed) |

## 📁 Project Structure

```
ev_trip_planner/
├── ev_trip_planner/          # Main project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI deployment
│
├── core/                     # Core application
│   ├── models.py             # User, Vehicle, ChargingStation models
│   ├── views.py              # Authentication, dashboard, stations views
│   ├── urls.py               # Core URL routing
│   ├── forms.py              # User, Vehicle, Station forms
│   ├── admin.py              # Admin configuration
│   └── migrations/           # Database migrations
│
├── planner/                  # Trip planning application
│   ├── models.py             # Trip, ChargingStop models
│   ├── views.py              # Trip planning views
│   ├── urls.py               # Planner URL routing
│   ├── forms.py              # Trip planning forms
│   └── utils.py              # Trip calculation algorithms
│
├── chat/                     # AI Assistant application
│   ├── models.py             # ChatConversation, ChatMessage models
│   ├── views.py              # Chat interface and API
│   ├── urls.py               # Chat URL routing
│   └── ai_responses.py       # Rule-based AI response system
│
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   ├── core/                 # Core app templates
│   ├── planner/              # Planner app templates
│   └── chat/                 # Chat app templates
│
├── static/                   # Static files
│   ├── css/
│   │   └── style.css         # Main stylesheet (eco-friendly theme)
│   └── js/
│       └── main.js           # Main JavaScript
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Extract the Project

```bash
cd ev_trip_planner
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Load Dummy Data (Optional)

The charging station migration includes 20 dummy stations across major US cities:

```bash
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

### Step 8: Access the Application

Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/login/

## 📱 Usage Guide

### 1. Register & Login
- Click "Sign Up" to create a new account
- Fill in your details and submit
- Log in with your credentials

### 2. Add Your Vehicle
- Go to "Dashboard" → "My Vehicles" → "Add Vehicle"
- Enter your EV details (make, model, battery capacity, range)
- This enables personalized trip planning

### 3. Plan a Trip
- Navigate to "Trip Planner"
- Enter start location and destination
- Select your vehicle and current battery level
- Click "Plan My Trip"
- Review the route with charging stops

### 4. Find Charging Stations
- Visit "Charging Stations"
- Use the map to find stations
- Filter by connector type, speed, or price
- Click on stations for details

### 5. Chat with AI Assistant
- Click the floating chat widget (bottom-right)
- Or visit the dedicated "AI Assistant" page
- Ask questions about EVs, charging, batteries, etc.

## 🎨 Design Features

- **Eco-friendly Theme**: Green color palette emphasizing sustainability
- **Responsive Design**: Mobile-first approach with Flexbox/Grid layouts
- **Modern UI**: Clean cards, smooth transitions, and intuitive navigation
- **Accessibility**: Semantic HTML with proper labels and ARIA attributes
- **No External CSS/JS Dependencies**: All styling and scripts are custom-built

## 🔧 Configuration

### Settings (settings.py)

Key configuration options:

```python
# Debug mode (set False in production)
DEBUG = True

# Allowed hosts (add your domain in production)
ALLOWED_HOSTS = ['*']

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Session timeout (24 hours)
SESSION_COOKIE_AGE = 86400
```

### Customization

1. **Update AI Responses**: Edit `chat/ai_responses.py` to modify AI behavior
2. **Add More Stations**: Add entries in `core/migrations/0002_populate_charging_stations.py`
3. **Adjust Trip Calculations**: Modify algorithms in `planner/utils.py`
4. **Change Theme**: Update CSS variables in `static/css/style.css`

## 🚀 Deployment

### Production Checklist

1. **Set DEBUG = False** in settings.py
2. **Configure ALLOWED_HOSTS** with your domain
3. **Set up a production database** (PostgreSQL recommended)
4. **Configure static files serving**
5. **Set up HTTPS** with a valid SSL certificate
6. **Use a production WSGI server** (Gunicorn recommended)

### Quick Deploy (Heroku Example)

```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set DEBUG=False
heroku buildpacks:set heroku/python

# Push to Heroku
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

## 📊 Database Models

### Core Models
- **UserProfile**: Extended user information
- **Vehicle**: User's electric vehicles
- **ChargingStation**: EV charging station data

### Planner Models
- **Trip**: Planned trips with route information
- **ChargingStop**: Charging stops along a trip

### Chat Models
- **ChatConversation**: Chat sessions
- **ChatMessage**: Individual chat messages

## 🤖 AI Assistant Knowledge Base

The AI assistant covers:
- Battery maintenance and health
- Charging times and costs
- Range and efficiency tips
- Cold weather driving
- Safety information
- Vehicle recommendations
- Trip planning guidance

## 🧪 Testing

Run the development server and test:

1. **Registration & Login Flow**
2. **Add Vehicle Functionality**
3. **Trip Planning with Charging Stops**
4. **Station Map and Filtering**
5. **AI Chat Responses**
6. **Dashboard and Profile Management**

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Feel free to extend and customize this project for your needs!

## 📧 Support

For issues or questions, please refer to the code documentation or Django's official documentation.

## 🌱 Environmental Impact

This application promotes:
- Zero-emission vehicle adoption
- Optimized route planning for energy efficiency
- Access to clean energy transportation
- Reduced carbon footprint through informed EV usage

---

**Built with 💚 for a sustainable future**
