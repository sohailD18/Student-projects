# Credit Risk Assessment & Loan Eligibility Prediction System

An AI-powered web application that evaluates loan applicants by analyzing financial history using machine learning models to predict credit risk and determine loan eligibility.

## 🌟 Features

- **AI-Powered Analysis**: Uses RandomForestClassifier trained on synthetic data
- **Instant Predictions**: Real-time credit risk assessment in under 2 seconds
- **Comprehensive Dashboard**: Interactive analytics with Chart.js visualizations
- **Detailed Reports**: Generate and download printable PDF reports
- **Risk Categorization**: Automatic classification into Low/Medium/High risk
- **Smart Recommendations**: Eligibility decisions with bonus logic for high credit scores
- **Responsive Design**: Beautiful UI built with Bootstrap 5
- **Data Management**: Complete CRUD operations for applicant records

## 🛠️ Tech Stack

- **Backend**: Django 4.2 (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **UI Framework**: Bootstrap 5.3.2
- **Charts**: Chart.js 4.4.0
- **Machine Learning**: Scikit-Learn 1.3.0
- **PDF Generation**: WeasyPrint (optional)

## 📋 Requirements

- Python 3.9 or higher
- pip (Python package manager)
- Modern web browser

## 🚀 Installation & Setup

### Step 1: Navigate to Project Directory

```bash
cd credit_risk_system
```

### Step 2: Create Virtual Environment (Recommended)

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

### Step 4: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional, for Admin Access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Train the ML Model

The ML model will be automatically trained when you first run the application. It generates 1000 synthetic samples and trains a RandomForestClassifier.

### Step 7: Run Development Server

```bash
python manage.py runserver
```

### Step 8: Access the Application

- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
credit_risk_system/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
│
├── credit_risk_system/               # Main project configuration
│   ├── settings.py                   # Project settings
│   ├── urls.py                       # Main URL configuration
│   └── wsgi.py                       # WSGI application
│
└── assessment/                       # Assessment app
    ├── models.py                     # Database models
    ├── views.py                      # View logic
    ├── forms.py                      # Django forms
    ├── urls.py                       # App URL routing
    ├── admin.py                      # Admin configuration
    ├── utils.py                      # Utility functions
    │
    ├── ml_model/                     # Machine Learning Module
    │   ├── predictor.py              # ML prediction engine
    │   ├── model.pkl                 # Trained model (auto-generated)
    │   ├── scaler.pkl                # Feature scaler (auto-generated)
    │   └── encoder.pkl               # Label encoders (auto-generated)
    │
    ├── templates/assessment/         # HTML Templates
    │   ├── base.html                 # Base template
    │   ├── home.html                 # Home page
    │   ├── assessment_form.html      # Assessment form
    │   ├── assessment_result.html    # Results page
    │   ├── dashboard.html            # Analytics dashboard
    │   ├── report.html               # Printable report
    │   ├── report_pdf.html           # PDF report template
    │   ├── applicant_list.html       # Applicant list
    │   └── applicant_detail.html     # Applicant details
    │
    └── static/assessment/css/        # Static CSS Files
        └── styles.css                # Custom styles
```

## 🎯 Usage Guide

### 1. Create a New Assessment

1. Click "New Assessment" in the navigation bar
2. Fill in the applicant's personal information
3. Enter financial details (income, employment, DTI ratio)
4. Provide credit history (credit score, late payments, etc.)
5. Click "Run Assessment"

### 2. View Results

After submission, you'll see:
- **Eligibility Status**: Approved, Manual Review, or Rejected
- **Risk Category**: Low, Medium, or High Risk
- **Default Probability**: Percentage chance of default
- **Detailed Analysis**: Breakdown of all factors

### 3. Generate Reports

- Click "Generate Report" on any result page
- View the report in the browser
- Print or download as PDF

### 4. Analytics Dashboard

- View overall statistics
- Risk distribution pie charts
- Income vs. approval status bar charts
- Approval rate trends

### 5. Manage Applicants

- View all assessments in the applicant list
- Filter by status or risk category
- Search by name or email
- View detailed information
- Delete records

## 🧠 ML Model Details

### Algorithm
- **RandomForestClassifier** with 100 estimators
- Maximum depth: 10
- Balanced class weights

### Features Used
1. Annual Income
2. Employment Status (encoded)
3. Years Employed
4. Debt-to-Income Ratio
5. Credit Score
6. Number of Open Loans
7. Number of Credit Lines
8. Late Payments (2 years)
9. Bankruptcies (binary)
10. Home Ownership Status (encoded)

### Data Preprocessing
- One-Hot Encoding for categorical variables
- StandardScaler for numerical features
- Synthetic data generation (1000 samples)

### Prediction Rules
- **Default Probability < 30%**: Approved
- **Default Probability 30-60%**: Manual Review
- **Default Probability > 60%**: Rejected
- **Bonus**: Credit Score > 750 reduces risk by 10%

## 🔧 Configuration

### Modify Risk Thresholds

Edit `assessment/utils.py`:

```python
def calculate_eligibility(prediction_probability: float, applicant_profile: Dict):
    # Adjust these thresholds as needed
    if adjusted_probability < 0.3:  # Low risk threshold
        eligibility_status = 'approved'
    elif adjusted_probability < 0.6:  # Medium risk threshold
        eligibility_status = 'manual_review'
    else:
        eligibility_status = 'rejected'
```

### Modify ML Model Parameters

Edit `assessment/ml_model/predictor.py`:

```python
self.model = RandomForestClassifier(
    n_estimators=100,  # Number of trees
    max_depth=10,      # Maximum tree depth
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'
)
```

### Change Synthetic Data Size

In `assessment/ml_model/predictor.py`:

```python
df = self._generate_synthetic_data(n_samples=1000)  # Change this value
```

## 🐛 Troubleshooting

### Model Not Training

If the model doesn't train automatically:

```bash
cd assessment/ml_model
python predictor.py
```

### Migration Errors

```bash
# Delete existing database
rm db.sqlite3

# Re-run migrations
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading

```bash
python manage.py collectstatic
```

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## 🔒 Security Notes

⚠️ **Important**: This is a demonstration project. For production use:

1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False` in production
3. Use environment variables for sensitive data
4. Implement proper authentication
5. Add HTTPS/SSL certificates
6. Use a production database (PostgreSQL)
7. Implement proper logging and monitoring
8. Add rate limiting and CSRF protection

## 📊 API Endpoints

### Get Statistics
```
GET /api/stats/
```

Returns JSON data for charts:
- Risk distribution
- Status distribution
- Average income by status
- Approval rate timeline

## 🤝 Contributing

This is a project for educational purposes. Feel free to:
- Add new features
- Improve the ML model
- Enhance the UI
- Fix bugs
- Add tests

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 👥 Credits

Built with:
- Django Framework
- Scikit-Learn
- Bootstrap 5
- Chart.js

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check Django documentation
4. Review Scikit-Learn documentation

---

**Note**: This system uses synthetic data for demonstration. In a real-world scenario, you would train the model on historical loan data with actual outcomes.
