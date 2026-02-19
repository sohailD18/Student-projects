# System Architecture

## Overview

The AI-Based Financial Transaction Fraud Detection System is a full-stack web application built with Django and Scikit-Learn. It provides real-time fraud detection, visualization, and reporting capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Dashboard│  │  Trans   │  │  Perf    │  │ Analysis │  │
│  │   View   │  │   List   │  │  View    │  │   View   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│         │             │             │             │         │
│         └─────────────┴─────────────┴─────────────┘         │
│                           │                                 │
│              ┌────────────▼─────────────┐                  │
│              │    Chart.js Visuals      │                  │
│              │    AJAX API Calls        │                  │
│              └────────────┬─────────────┘                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Backend Layer (Django)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    URLs (urls.py)                    │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │                   Views (views.py)                   │  │
│  │  • dashboard()    • transaction_list()               │  │
│  │  • model_performance() • fraud_analysis()            │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐  │
│  │              Business Logic Layer                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  ML Engine  │  │  Utils      │  │  Commands   │  │  │
│  │  │(ml_engine.py)│  │ (utils.py)  │  │(management/) │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────┬───────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Data Layer (Django ORM)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Transaction │  │ModelMetrics │  │ FraudAlert  │        │
│  │    Model    │  │   Model     │  │   Model     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                           │                                 │
│  ┌───────────────────────▼───────────────────────┐        │
│  │              SQLite Database                  │        │
│  │         • db.sqlite3 (default)               │        │
│  └───────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  ML/AI Layer (Scikit-Learn)                 │
│  ┌───────────────────────────────────────────────────┐     │
│  │          FraudDetectionEngine                     │     │
│  │  • RandomForestClassifier (Supervised)            │     │
│  │  • IsolationForest (Unsupervised)                 │     │
│  │  • DataPreprocessor (StandardScaler, LabelEncode) │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Frontend Layer

**Templates:**
- `base.html` - Base template with navigation
- `dashboard.html` - Main dashboard with charts
- `transaction_list.html` - Transaction browser
- `transaction_detail.html` - Single transaction view
- `model_performance.html` - Model metrics
- `fraud_analysis.html` - Fraud reports

**Static Assets:**
- `css/style.css` - Main stylesheet (dark theme)
- `css/chart-custom.css` - Chart.js customization

**JavaScript:**
- Chart.js for visualizations
- AJAX for API calls
- Dynamic filtering and search

### 2. Backend Layer (Django)

**URL Configuration (`urls.py`):**
```python
/                    → Dashboard
/transactions/        → Transaction list
/transactions/<id>/   → Transaction detail
/performance/         → Model performance
/analysis/            → Fraud analysis
/api/dashboard-data/  → Dashboard data API
/api/predict/         → Prediction API
```

**Views (`views.py`):**
- Render HTML templates
- Handle business logic
- Query database
- Calculate statistics
- Return JSON for API endpoints

### 3. Business Logic Layer

**ML Engine (`ml_engine.py`):**
```python
FraudDetectionEngine
├── train()           # Train model on data
├── predict()         # Predict single transaction
├── predict_batch()   # Predict multiple transactions
├── evaluate()        # Calculate metrics
├── save()            # Save to disk
└── load()            # Load from disk
```

**Utils (`utils.py`):**
```python
DataPreprocessor
├── fit()             # Fit scaler/encoders
├── transform()       # Transform features
├── create_features() # Extract features
└── save/load()       # Persistence
```

**Management Commands:**
- `generate_transactions` - Create synthetic data
- `train_model` - Train AI model

### 4. Data Layer

**Models (`models.py`):**

**Transaction Model:**
```python
Fields:
- transaction_id, transaction_type, amount
- location, country, city, ip_address
- merchant, merchant_category
- account_id, card_number_last4
- timestamp
- is_fraud, risk_score, fraud_reason
- is_flagged, is_reviewed
- device_id, browser, os
- features (JSON)
```

**ModelMetrics Model:**
```python
Fields:
- model_name, model_version
- accuracy, precision, recall, f1_score
- Confusion matrix (TP, TN, FP, FN)
- Training/test sample counts
- parameters (JSON)
```

**FraudAlert Model:**
```python
Fields:
- transaction (FK)
- alert_type, status
- description, risk_score
- assigned_to, notes
- timestamps
```

### 5. ML/AI Layer

**Models:**
1. **Random Forest Classifier** (Supervised)
   - Ensemble of decision trees
   - Requires labeled training data
   - Provides probability estimates
   - Feature importance available

2. **Isolation Forest** (Unsupervised)
   - Anomaly detection
   - No labels required
   - Good for novel fraud patterns
   - Isolation score based

**Preprocessing Pipeline:**
```
Raw Data
    ↓
Temporal Features (hour, day)
    ↓
Categorical Encoding (LabelEncoder)
    ↓
Numerical Scaling (StandardScaler)
    ↓
Feature Vector
    ↓
Model Prediction
```

## Data Flow

### 1. Transaction Ingestion Flow

```
Synthetic Data Generation
    ↓
Transaction.objects.create()
    ↓
ML Engine Prediction (if trained)
    ↓
Update is_fraud, risk_score
    ↓
Create FraudAlert (if high risk)
    ↓
Create AuditLog
```

### 2. Fraud Detection Flow

```
New Transaction
    ↓
Extract Features
    ↓
Preprocess (scale/encode)
    ↓
Model Prediction
    ↓
Calculate Risk Score
    ↓
Generate Fraud Reason
    ↓
Flag if Risk > Threshold
    ↓
Store Results
```

### 3. Dashboard Data Flow

```
User Request
    ↓
View queries DB
    ↓
Calculate statistics
    ↓
Render template
    ↓
Load page
    ↓
JS fetches API data
    ↓
Update charts
```

## Security Considerations

1. **Input Validation**
   - Django forms and ORM prevent SQL injection
   - Type checking on API endpoints

2. **Authentication** (To be added)
   - User login required
   - Role-based access control
   - API token authentication

3. **Data Protection**
   - Sensitive data hashing
   - Secure secret key management
   - HTTPS in production

## Performance Optimizations

1. **Database Indexing**
   - Index on timestamp, is_fraud, risk_score
   - Composite indexes for common queries

2. **Query Optimization**
   - select_related() for foreign keys
   - only() for specific fields
   - Pagination for large lists

3. **Caching** (To be added)
   - Redis for session data
   - Cache dashboard statistics
   - Cache model predictions

## Scalability Options

1. **Horizontal Scaling**
   - Load balancer + multiple Django instances
   - Separate database server
   - Redis for session management

2. **Vertical Scaling**
   - More CPU cores for model training
   - More RAM for larger datasets
   - Fast storage (SSD)

3. **Microservices** (Advanced)
   - Separate ML service
   - Message queue (RabbitMQ/Redis)
   - Async processing (Celery)

## Monitoring & Logging

1. **Audit Logs**
   - All actions tracked
   - IP addresses logged
   - Timestamps recorded

2. **Model Performance**
   - Metrics stored in database
   - Training history tracked
   - Performance trends monitored

3. **Error Handling**
   - Try-except blocks
   - Graceful degradation
   - User-friendly error messages

---

**Document Version:** 1.0
**Last Updated:** 2025-01-15
