# Quick Start Guide

Get the AI-Based Financial Transaction Fraud Detection System up and running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Step-by-Step Setup

### 1. Navigate to Project Directory
```bash
cd "c:\Users\Dell\OneDrive\Desktop\Claude2\FinTech & Digital Finance Systems\Project1"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Generate Sample Data (1000 transactions)
```bash
python manage.py generate_transactions --count 1000
```

### 7. Train the AI Model
```bash
python manage.py train_model --save-model
```

### 8. Start the Server
```bash
python manage.py runserver
```

### 9. Access the Application

Open your browser and go to: **http://127.0.0.1:8000/**

## What You'll See

1. **Dashboard** - Overview with statistics and charts
2. **Transactions** - List of all transactions with fraud highlighting
3. **Performance** - Model metrics and accuracy
4. **Analysis** - Detailed fraud analysis and reports

## Common Issues

### "Module not found" error
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "No such table" error
- Run migrations: `python manage.py migrate`

### "Model not trained" message
- Run: `python manage.py train_model --save-model`

### Port 8000 already in use
- Use a different port: `python manage.py runserver 8080`

## Next Steps

1. **Explore the Dashboard** - View charts and statistics
2. **Browse Transactions** - Filter and search for fraud
3. **Check Performance** - See how well the AI is working
4. **Download Reports** - Export fraud analysis as CSV

## Advanced Usage

### Generate more data
```bash
python manage.py generate_transactions --count 5000 --fraud-ratio 0.15
```

### Use Isolation Forest (unsupervised learning)
```bash
python manage.py train_model --model-type isolation_forest --save-model
```

### Access Django Admin
First, create a superuser:
```bash
python manage.py createsuperuser
```

Then visit: http://127.0.0.1:8000/admin/

## Project Structure Overview

```
Project1/
├── fraud_detection/         # Main Django project
├── transactions/            # Core app
│   ├── models.py           # Database models
│   ├── views.py            # Page views
│   ├── ml_engine.py        # AI/ML engine
│   └── utils.py            # Data utilities
├── templates/               # HTML templates
├── static/                  # CSS files
├── manage.py               # Django management
└── requirements.txt        # Python dependencies
```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review Django docs: https://docs.djangoproject.com/
- Review Scikit-Learn docs: https://scikit-learn.org/

---

**Happy fraud hunting! 🎯**
