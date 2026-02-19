# OptiFlow - AI-Based Business Process Optimizer

A comprehensive Django-based application for analyzing and optimizing business processes using AI-powered bottleneck detection and statistical analysis.

## Features

- **Workflow Modeling**: Define business processes with multiple steps
- **Data Collection**: Log operational data with execution times and status tracking
- **AI Engine**: Statistical analysis using standard deviation, moving averages, and outlier detection
- **Recommendation System**: AI-generated optimization suggestions with impact scores
- **Interactive Dashboard**: Real-time metrics and KPI visualization
- **Data Visualization**: Chart.js integration for cycle times, efficiency metrics, and throughput
- **Reporting**: Detailed optimization impact reports

## Tech Stack

- **Backend**: Python 3.x / Django 4.2+
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **UI Framework**: Bootstrap 5 (via CDN)
- **Charts**: Chart.js (via CDN)
- **AI/Statistics**: Python standard library (statistics module)

## Project Structure

```
optiflow/
├── manage.py                 # Django management script
├── optiflow/
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── core/
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL configuration
│   ├── admin.py             # Admin configuration
│   ├── ai_engine.py         # AI analysis engine
│   ├── templates/core/      # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── analytics.html
│   │   ├── process_list.html
│   │   ├── process_form.html
│   │   ├── log_entry.html
│   │   ├── log_list.html
│   │   └── process_analysis.html
│   └── management/commands/
│       └── seed_db.py       # Database seeding command
└── db.sqlite3               # SQLite database (created after migrations)
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Navigate to Project Directory

```bash
cd "c:\Users\Dell\OneDrive\Desktop\Claude2\Enterprise Software & Productivity Tools\Project2"
```

### Step 2: Install Django

```bash
pip install django
```

### Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Seed Database with Dummy Data

```bash
python manage.py seed_db
```

This will create:
- 5 business processes
- 31 process steps
- 1000 operational logs
- 5 AI-generated recommendations

### Step 5: Create Superuser (Optional - for Admin Access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

### Step 7: Access the Application

Open your browser and navigate to:
- **Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Database Models

### BusinessProcess
- Complete workflow definition
- Target cycle time tracking
- Status management (active/inactive/archived)

### ProcessStep
- Individual workflow steps
- Step types: manual, automated, approval, notification, integration
- Estimated duration tracking

### OperationalData
- Execution logs with timing metrics
- Status tracking (pending/in_progress/completed/failed/skipped)
- Priority levels
- JSON metadata support

### Recommendation
- AI-generated optimization suggestions
- Priority levels (low/medium/high/critical)
- Impact scoring
- Potential savings calculation

### ProcessMetric
- Aggregated metrics storage
- Time-series data points

## AI Engine Features

The `ai_engine.py` module provides:

### Statistical Analysis
- **Mean, Median, Standard Deviation**: Core statistical calculations
- **Moving Averages**: Trend detection over time windows
- **Percentile Calculations**: P50, P95, etc.
- **IQR Method**: Outlier detection using Interquartile Range

### Bottleneck Detection
- Identifies steps exceeding normal execution times
- Uses configurable confidence threshold (default: 1.5 std deviations)
- Calculates severity scores based on deviation and frequency
- Generates detailed bottleneck reports

### Recommendation Generation
- Automatic categorization (bottleneck/automation/resource/process/performance)
- Priority assignment based on impact analysis
- Potential savings calculation
- Actionable improvement suggestions

### Efficiency Metrics
- Efficiency score calculation
- Consistency scoring (coefficient of variation)
- Trend analysis (improving/stable/degrading)
- Health assessment scoring

## URLs and Views

| URL Pattern | View Function | Description |
|-------------|--------------|-------------|
| `/` | `dashboard` | Main dashboard with metrics |
| `/processes/` | `process_list` | List all processes |
| `/process/create/` | `process_create` | Create new process |
| `/process/<id>/` | `process_detail` | Process details |
| `/process/<id>/dashboard/` | `process_dashboard` | Process-specific dashboard |
| `/process/<id>/analyze/` | `process_analysis` | AI analysis of process |
| `/log/entry/` | `log_entry` | Log operational data |
| `/log/list/` | `log_list` | List all logs |
| `/analytics/` | `analytics_dashboard` | Analytics dashboard |
| `/recommendations/` | `recommendation_list` | View all recommendations |
| `/reports/optimization/` | `optimization_report` | Impact report |

## Usage Guide

### 1. Create a Business Process

1. Navigate to **Processes** → **Create Process**
2. Fill in process details (name, description, target cycle time)
3. Submit the form

### 2. Add Process Steps

1. Go to the process detail page
2. Click **Add Step**
3. Define step name, order, type, and estimated duration

### 3. Log Operational Data

1. Navigate to **Data Logs** → **New Log Entry**
2. Select process and step
3. Enter execution details (start/end time, status, notes)
4. Submit the log

### 4. Run AI Analysis

1. Go to **Analytics** → Select a process
2. Click **Analyze**
3. View bottlenecks, efficiency metrics, and recommendations

### 5. Review Recommendations

1. Navigate to **Recommendations**
2. Filter by status or priority
3. View details and take action (approve/implement/reject)

## Customization

### Adjust AI Sensitivity

Edit `core/ai_engine.py`:

```python
# In ProcessAnalyzer.__init__
# Lower value = more sensitive (detects more bottlenecks)
# Higher value = less sensitive (detects only severe bottlenecks)
confidence_threshold = 1.5  # Default: 1.5, range: 1.0-3.0
```

### Modify Database

Edit `optiflow/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # or mysql
        'NAME': 'optiflow_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Endpoints

### Get Process Metrics
```
GET /api/process/<id>/metrics/
```
Returns JSON with process metrics and step performance data.

### Trigger Process Analysis
```
GET /api/process/<id>/analyze/
```
Runs AI analysis and returns results as JSON.

## Troubleshooting

### Migration Errors
```bash
# Delete database and re-migrate
del db.sqlite3
python manage.py migrate
python manage.py seed_db
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8080
```

### Template Not Found
Ensure `core/templates/core/` directory exists and contains all HTML files.

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions, please refer to the Django documentation:
- https://docs.djangoproject.com/
- https://docs.djangoproject.com/en/4.2/topics/db/models/
- https://docs.djangoproject.com/en/4.2/topics/http/views/

---

**Built with Django, Bootstrap 5, and Chart.js**
