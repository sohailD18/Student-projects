# AI-Based Financial Transaction Fraud Detection System

A comprehensive fraud detection system built with Django, Scikit-Learn, and Chart.js for real-time financial transaction monitoring and analysis.

## Features

### 8 Core Modules

1. **Transaction Data Ingestion**
   - Django models for storing transaction data
   - Management command to generate synthetic financial data
   - Support for multiple transaction types and locations

2. **Data Preprocessing**
   - StandardScaler for numerical features
   - LabelEncoder for categorical features
   - Temporal feature extraction

3. **AI-Based Fraud Detection Engine**
   - Random Forest classifier (supervised learning)
   - Isolation Forest (unsupervised learning)
   - Real-time fraud prediction
   - Risk scoring (0.0 to 1.0)

4. **Anomaly and Risk Scoring**
   - Automatic fraud prediction on transactions
   - Risk score calculation and storage
   - Fraud reason generation

5. **Fraud Pattern Visualization Dashboard**
   - Transaction trends over time
   - Risk score distribution
   - Fraud by transaction type and category
   - Interactive Chart.js visualizations

6. **Alert and Flagging System**
   - Visual highlighting of high-risk transactions
   - Red/amber backgrounds for flagged transactions
   - Risk level badges

7. **Model Performance Monitoring**
   - Accuracy, Precision, Recall, F1-Score
   - Confusion matrix visualization
   - Training history tracking
   - Detection rate statistics

8. **Fraud Analysis and Reporting**
   - Comprehensive fraud analysis page
   - CSV report download
   - Fraud trends and patterns
   - Risk level distribution

## Tech Stack

- **Backend**: Django 5.0, Python 3.10+
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data/AI**: Pandas, NumPy, Scikit-Learn
- **Visualization**: Chart.js 4.4

## Project Structure

```
Project1/
├── fraud_detection/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── transactions/
│   ├── models.py            # Transaction, ModelMetrics, FraudAlert
│   ├── views.py             # All view functions
│   ├── urls.py              # App URL configuration
│   ├── utils.py             # Data preprocessing utilities
│   ├── ml_engine.py         # AI fraud detection engine
│   ├── admin.py             # Django admin configuration
│   └── management/
│       └── commands/
│           ├── generate_transactions.py  # Generate synthetic data
│           └── train_model.py             # Train AI model
├── templates/
│   ├── base.html            # Base template
│   └── transactions/
│       ├── dashboard.html
│       ├── transaction_list.html
│       ├── transaction_detail.html
│       ├── model_performance.html
│       └── fraud_analysis.html
├── static/
│   └── css/
│       ├── style.css
│       └── chart-custom.css
├── requirements.txt
└── README.md
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Django Project (if starting from scratch)

If you haven't created the project yet:

```bash
django-admin startproject fraud_detection .
python manage.py startapp transactions
```

Then copy all the provided files to the appropriate locations.

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Generate Synthetic Data

```bash
# Generate 1000 transactions with 10% fraud ratio
python manage.py generate_transactions --count 1000 --fraud-ratio 0.1
```

### 6. Train AI Model

```bash
# Train Random Forest model (recommended)
python manage.py train_model --model-type random_forest --save-model

# Or train Isolation Forest
python manage.py train_model --model-type isolation_forest --save-model
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the dashboard.

## Usage Guide

### Dashboard

The main dashboard displays:
- Total transactions and fraud counts
- Fraud rate percentage
- Recent fraud alerts
- High-risk merchants
- Interactive charts

### Transaction List

Browse and filter transactions:
- **Filter by**: All, Fraud Only, Legitimate Only
- **Status**: Flagged, Reviewed
- **Search**: By transaction ID, merchant, or account

High-risk transactions are highlighted with red/amber backgrounds.

### Model Performance

Monitor AI model performance:
- Accuracy, Precision, Recall, F1-Score
- Confusion matrix
- Training history
- Detection statistics

### Fraud Analysis

Comprehensive fraud analysis:
- Total fraud cases and amounts
- Risk level distribution
- Fraud trends over time
- Download CSV reports

## Management Commands

### Generate Transactions

```bash
python manage.py generate_transactions [options]

Options:
  --count INT        Number of transactions to generate (default: 100)
  --fraud-ratio FLOAT  Ratio of fraudulent transactions (default: 0.1)
```

### Train Model

```bash
python manage.py train_model [options]

Options:
  --model-type {isolation_forest,random_forest}  Model type (default: random_forest)
  --save-model                                    Save trained model to disk
  --min-samples INT                              Minimum samples required (default: 100)
```

## API Endpoints

### Dashboard Data
```
GET /api/dashboard-data/
```
Returns JSON data for dashboard charts.

### Predict Transaction
```
POST /api/predict/
Content-Type: application/json

{
  "amount": 1500.00,
  "transaction_type": "purchase",
  "merchant_category": "electronics",
  "country": "US",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Transaction Statistics
```
GET /api/stats/
```

### Recent Activity
```
GET /api/recent-activity/?limit=20
```

## Database Models

### Transaction
- Transaction details (ID, type, amount, location)
- Merchant information
- Account details
- AI detection results (is_fraud, risk_score)
- Timestamps and metadata

### ModelMetrics
- Model performance metrics
- Confusion matrix
- Training parameters
- Timestamps

### FraudAlert
- Alert details and status
- Assigned investigator
- Notes and resolution

### AuditLog
- System actions and events
- Entity tracking
- IP logging

## Customization

### Modify Model Parameters

Edit `ml_engine.py` to adjust model parameters:

```python
default_params = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 2,
    # ... more parameters
}
```

### Add New Features

1. Add fields to `Transaction` model
2. Update `utils.py` preprocessing
3. Retrain the model

### Customize Styling

Edit `static/css/style.css` to modify:
- Color scheme
- Layout
- Components
- Responsive breakpoints

## Troubleshooting

### Model Not Trained Error

If you see "Model not trained" errors:
```bash
python manage.py train_model --save-model
```

### No Data in Dashboard

Generate synthetic data:
```bash
python manage.py generate_transactions --count 1000
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Performance Optimization

- Use database indexes for large datasets
- Implement pagination for transaction lists
- Cache dashboard API responses
- Use Redis for real-time updates (optional)

## Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Use environment variables for sensitive config
- Implement proper authentication (add as needed)
- Enable HTTPS in production

## Future Enhancements

- Real-time WebSocket updates
- User authentication and authorization
- Email alerts for high-risk transactions
- Advanced anomaly detection (Autoencoders)
- Geographic fraud pattern detection
- Behavioral biometrics integration
- API rate limiting
- Multi-language support

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Django documentation: https://docs.djangoproject.com/
3. Review Scikit-Learn documentation: https://scikit-learn.org/

---

**Built with ❤️ using Django and Scikit-Learn**
