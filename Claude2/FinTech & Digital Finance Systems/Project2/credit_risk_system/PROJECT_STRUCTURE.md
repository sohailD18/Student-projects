# Credit Risk Assessment System - Project Structure

## Directory Structure
```
credit_risk_system/
├── manage.py                           # Django management script
├── requirements.txt                    # Python dependencies
├── db.sqlite3                         # SQLite database (created after migration)
│
├── credit_risk_system/                # Main project configuration
│   ├── __init__.py
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # Main URL configuration
│   └── wsgi.py                        # WSGI application
│
└── assessment/                        # Assessment app
    ├── __init__.py
    ├── admin.py                       # Admin configuration
    ├── apps.py                        # App configuration
    ├── models.py                      # Database models (COMPLETED)
    ├── forms.py                       # Django forms (PENDING)
    ├── views.py                       # View logic (PENDING)
    ├── urls.py                        # App URL routing (PENDING)
    ├── utils.py                       # Utility functions (PENDING)
    │
    ├── ml_model/                      # Machine Learning Module
    │   ├── __init__.py
    │   ├── predictor.py               # ML prediction engine (PENDING)
    │   └── model.pkl                  # Trained model (auto-generated)
    │
    ├── templates/assessment/          # HTML Templates
    │   ├── base.html                  # Base template (PENDING)
    │   ├── home.html                  # Home page (PENDING)
    │   ├── assessment_form.html       # Assessment form (PENDING)
    │   ├── assessment_result.html     # Results page (PENDING)
    │   ├── dashboard.html             # Analytics dashboard (PENDING)
    │   └── report.html                # Printable report (PENDING)
    │
    └── static/assessment/css/         # Static CSS Files
        └── styles.css                 # Custom styles (PENDING)
```

## Models Created

### 1. Applicant Model
**Fields:**
- `id` (UUID, Primary Key)
- `name` (CharField)
- `email` (EmailField)
- `phone` (CharField)
- `annual_income` (DecimalField)
- `employment_status` (CharField with choices: employed, self_employed, unemployed, retired, student)
- `years_employed` (IntegerField)
- `debt_to_income_ratio` (DecimalField)
- `risk_probability` (DecimalField, computed)
- `risk_category` (CharField: low/medium/high)
- `eligibility_status` (CharField: approved/manual_review/rejected)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Methods:**
- `approved` (property): Returns True if status is 'approved'

### 2. FinancialData Model
**Fields:**
- `applicant` (OneToOneField to Applicant)
- `credit_score` (IntegerField, 300-850)
- `num_open_loans` (IntegerField)
- `num_credit_lines` (IntegerField)
- `late_payments` (IntegerField, last 2 years)
- `bankruptcies` (BooleanField)
- `home_ownership_status` (CharField: rent/mortgage/own/other)
- `total_credit_limit` (DecimalField, optional)
- `credit_utilization` (DecimalField, optional)
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

**Methods:**
- `is_high_risk_credit` (property): Returns True if credit profile indicates high risk

## Next Steps

To continue with the implementation, type **"Continue"** or **"Next"** and I will create:

1. ✅ Project structure and settings
2. ✅ Models (Applicant and FinancialData)
3. ⏳ ML Prediction Engine with synthetic data generator
4. ⏳ Forms for data input
5. ⏳ Views for application logic
6. ⏳ URL routing configuration
7. ⏳ HTML templates with Bootstrap 5
8. ⏳ Dashboard with Chart.js visualizations
9. ⏳ Static CSS files

## Setup Instructions

After completing all files:

```bash
# Navigate to project directory
cd credit_risk_system

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access the application at: http://127.0.0.1:8000/
# Access admin at: http://127.0.0.1:8000/admin/
```

## SQL Migration Commands Preview

The models will create the following SQL structure:

```sql
-- Applicant Table
CREATE TABLE assessment_applicant (
    id CHAR(32) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    annual_income DECIMAL(12,2) NOT NULL,
    employment_status VARCHAR(20) NOT NULL,
    years_employed INTEGER NOT NULL,
    debt_to_income_ratio DECIMAL(5,2) NOT NULL,
    risk_probability DECIMAL(5,4) NULL,
    risk_category VARCHAR(20) NULL,
    eligibility_status VARCHAR(20) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- FinancialData Table
CREATE TABLE assessment_financialdata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_id CHAR(32) NOT NULL UNIQUE REFERENCES assessment_applicant(id),
    credit_score INTEGER NOT NULL,
    num_open_loans INTEGER NOT NULL,
    num_credit_lines INTEGER NOT NULL,
    late_payments INTEGER NOT NULL,
    bankruptcies BOOLEAN NOT NULL,
    home_ownership_status VARCHAR(20) NOT NULL,
    total_credit_limit DECIMAL(12,2) NULL,
    credit_utilization DECIMAL(5,2) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```
