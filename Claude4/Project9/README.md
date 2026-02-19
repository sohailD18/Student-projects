# AgriSense - AI-Based Soil Health Analysis and Crop Advisory System

A full-stack web application where farmers can input soil parameters (N, P, K, pH, moisture) to get AI-based crop recommendations and fertilizer advice.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS3, JavaScript (Django Templates)
- **Database:** SQLite
- **AI/Logic:** Scikit-Learn (Decision Tree Classifier)
- **Styling:** Custom CSS with Green & Earthy theme
- **Icons:** Emoji-based (no external dependencies)

## Project Structure

```
Project9/
├── manage.py                      # Django management script
├── requirements.txt                # Python dependencies
├── agrisense/                     # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                          # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── ml_logic.py               # AI recommendation engine
│   ├── models.py                 # Database models
│   └── views.py                  # Controllers
├── static/                       # Static files
│   └── css/
│       └── style.css            # Main stylesheet
│   └── js/
│       └── main.js               # Interactive JavaScript
└── templates/                    # HTML templates
    ├── analyze.html             # Soil analysis form
    ├── base.html                # Base layout
    ├── contact.html             # Contact page
    ├── home.html                # Landing page
    ├── history.html             # Analysis history
    └── result.html              # Results display
```

## Database Models

### SoilData
- Nitrogen (N) - Integer
- Phosphorus (P) - Integer
- Potassium (K) - Integer
- pH Level - Float
- Moisture - Float
- Recommended Crop - String
- Fertilizer Suggestion - Text
- Timestamp - DateTime (auto)

### ContactMessage
- Name - String
- Email - Email
- Message - Text
- Timestamp - DateTime (auto)
- Is Read - Boolean

## Features

### 1. AI-Powered Crop Recommendation
- Uses Decision Tree Classifier trained on synthetic agricultural data
- Analyzes N, P, K, pH, and moisture levels
- Recommends from 15 different crops (Rice, Wheat, Maize, Cotton, etc.)

### 2. Fertilizer Advisory
- Rule-based recommendations for N, P, K levels
- Crop-specific fertilizer advice
- Detailed nutrient status analysis

### 3. User Interface
- Responsive green & earthy theme
- Mobile-friendly design
- Form validation
- Animated transitions
- Clean navigation

### 4. Data Persistence
- SQLite database
- Analysis history
- Contact form submissions
- Admin panel for data management

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Django>=4.0
- pandas
- scikit-learn
- numpy

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 4: Run Development Server
```bash
python manage.py runserver
```

### Step 5: Access Application
Open your browser and navigate to:
- **Home Page:** http://127.0.0.1:8000/
- **Analyze Soil:** http://127.0.0.1:8000/analyze
- **History:** http://127.0.0.1:8000/history
- **Contact:** http://127.0.0.1:8000/contact
- **Admin Panel:** http://127.0.0.1:8000/admin

## Usage Guide

### Analyzing Soil

1. Navigate to the **Analyze** page
2. Enter your soil parameters:
   - **Nitrogen (N):** 0-200 mg/kg (Ideal: 50-90)
   - **Phosphorus (P):** 0-150 mg/kg (Ideal: 20-50)
   - **Potassium (K):** 0-200 mg/kg (Ideal: 30-80)
   - **pH Level:** 0-14 (Ideal: 6.0-7.0)
   - **Moisture:** 0-100% (Ideal: 40-80%)
3. Click **"Analyze Soil"**
4. View your crop recommendation and fertilizer advice
5. Results are automatically saved to history

### Viewing History

1. Navigate to the **History** page
2. View your last 10 soil analyses
3. Click **"View Details"** to see full results
4. Use pagination for older analyses

### Contact Form

1. Navigate to the **Contact** page
2. Fill in your name, email, and message
3. Submit the form

## AI Model Details

### Training Data
The Decision Tree classifier is trained on 3000+ synthetic samples based on agricultural research:

**Crop Requirements Used:**
- Rice: High N, water-loving (60-100% moisture)
- Wheat: Moderate N, balanced nutrients
- Maize: High N, P, K requirements
- Cotton: Balanced nutrients, tolerates high pH
- Millet: Drought-resistant, low nutrient requirements
- And 10 more crops...

### Features
- **Input Features:** N, P, K, pH, moisture (normalized)
- **Model:** Decision Tree Classifier
- **Max Depth:** 15
- **Training Approach:** On-the-fly training at startup

## Customization

### Adding New Crops
Edit `core/ml_logic.py` and modify the `crop_requirements` list in the `_generate_training_data` method.

### Adjusting Nutrient Thresholds
Edit `core/ml_logic.py` and modify the threshold constants in `FertilizerAdvisor` class:
```python
N_LOW = 40      # Nitrogen low threshold
P_LOW = 20      # Phosphorus low threshold
K_LOW = 30      # Potassium low threshold
```

### Changing Theme Colors
Edit `static/css/style.css` and modify the CSS variables:
```css
:root {
    --primary-green: #2E7D32;
    --earth-brown: #795548;
    --cream: #F5F5DC;
}
```

## Screenshots Reference

The application includes:
1. **Hero Section** - Eye-catching landing page with animated elements
2. **Feature Cards** - Highlights AI capabilities
3. **Soil Parameters Info** - Educational content about N, P, K, pH, moisture
4. **Analysis Form** - Clean input form with validation
5. **Results Display** - Comprehensive recommendation dashboard
6. **History Table** - Paginated list of past analyses

## Security Notes

- This is a development/demo application
- For production:
  - Change `SECRET_KEY` in `settings.py`
  - Set `DEBUG = False`
  - Configure `ALLOWED_HOSTS`
  - Use a production database (PostgreSQL)
  - Set up HTTPS
  - Configure email backend for contact form

## License

This is a demonstration project for educational purposes.

## Support

For issues, questions, or suggestions, please use the Contact form in the application or create an issue in the repository.

---

**Built with ❤️ for Smart Agriculture**
