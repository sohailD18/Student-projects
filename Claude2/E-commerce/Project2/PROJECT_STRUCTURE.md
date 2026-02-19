# AI-Based Demand Forecasting and Inventory Management System

## Project Overview
A comprehensive web application that uses historical sales data to predict future product demand using AI/ML forecasting and helps retailers manage inventory levels.

## Tech Stack
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python with Django
- **Database**: SQLite
- **AI/Data Libraries**: Pandas, NumPy, Scikit-Learn
- **Visualization**: Chart.js

## Folder Structure

```
inventory_forecast_system/
├── inventory_project/          # Django Project Settings
│   ├── __init__.py
│   ├── settings.py            # Project configuration
│   ├── urls.py                # Main URL routing
│   └── wsgi.py
│
├── inventory/                  # Main Django App
│   ├── __init__.py
│   ├── admin.py               # Django Admin configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # Database Models
│   ├── views.py               # View Functions
│   ├── urls.py                # App URL Routing
│   ├── utils.py               # AI/ML Forecasting Logic
│   └── migrations/            # Database Migrations
│
├── templates/                  # HTML Templates
│   ├── base.html              # Base Template
│   ├── dashboard.html         # Main Dashboard
│   └── inventory_table.html   # Inventory Table Component
│
├── static/                     # Static Files
│   ├── css/
│   │   └── style.css          # Custom Styles
│   └── js/
│       └── dashboard.js       # Dashboard JavaScript
│
├── scripts/                    # Utility Scripts
│   └── generate_dummy_data.py # Dummy Data Generator
│
├── manage.py                   # Django Management Script
├── requirements.txt            # Python Dependencies
└── README.md                   # This File
```

## Architecture Flow

```
User Browser
    ↓
Django View (views.py)
    ↓
AI/ML Service (utils.py)
    ↓
Database (SQLite)
    ↓
Historical Sales Data Processing
    ↓
Model Training (Scikit-Learn)
    ↓
Forecast Generation
    ↓
JSON Response + HTML Template
    ↓
Frontend Visualization (Chart.js)
```

## Key Features
1. **Data Management**: Add/view Products and Historical Sales Data
2. **AI Forecasting**: Predict demand using Linear Regression/Time Series
3. **Dashboard**: Visual comparison of stock vs predicted demand
4. **Replenishment**: Smart order quantity suggestions
5. **Visual Reports**: Charts showing sales vs forecast
6. **Alerts**: Low stock (Red) and Over-stock (Orange) indicators

## Setup Instructions
See SETUP.md for detailed installation and running instructions.
