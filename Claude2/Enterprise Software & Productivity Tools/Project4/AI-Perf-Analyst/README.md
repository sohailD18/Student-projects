# AI Performance Analyst 🤖📊

**Employee Performance Analysis and Decision Support System**

A comprehensive web application for tracking, analyzing, and predicting employee performance using AI-powered insights. Built with Django, this system provides managers with actionable data-driven recommendations to optimize workforce productivity.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **📊 Performance Dashboard** - Real-time overview of all employee metrics
- **👥 Employee Management** - Add, view, and manage employee profiles
- **📝 Performance Logging** - Record daily/weekly performance metrics
- **🤖 AI Prediction Engine** - Predict next month's performance using weighted averages and trend analysis
- **💡 Smart Recommendations** - Get actionable insights for employee development
- **📈 Visual Analytics** - Interactive charts powered by Chart.js
- **📄 Printable Reports** - Generate comprehensive performance summaries

### AI/Analysis Capabilities
- **Performance Prediction** - Forecast future performance based on historical data
- **Trend Analysis** - Identify improving, stable, or declining performance patterns
- **Strength/Weakness Detection** - Automatically tag employees as:
  - High Potential
  - Promotion Candidate
  - Needs Training
  - Stable Performer
- **Productivity Metrics** - Track tasks completed per hour
- **Quality Assessment** - Monitor work quality over time

### Key Metrics Tracked
- Tasks Completed
- Efficiency Score (1-10)
- Quality Rating (1-10)
- Hours Worked
- Productivity Rate (tasks/hour)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation Steps

1. **Navigate to the project directory**
   ```bash
   cd AI-Perf-Analyst
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv

   # macOS/Linux
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional - for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```
AI-Perf-Analyst/
│
├── AI_Perf_Analyst/          # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI configuration
│
├── performance/               # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── urls.py                # App URL routing
│   ├── admin.py               # Admin configuration
│   ├── analysis.py            # AI/Analysis engine
│   ├── templates/performance/ # HTML templates
│   └── static/performance/    # CSS & JS files
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Usage Guide

### 1. Add Employees
1. Click "Add Employee" in the navigation
2. Fill in employee details (name, department, role, join date)
3. Save to create the employee profile

### 2. Log Performance Records
1. Click "Add Record" in the navigation
2. Select an employee from the dropdown
3. Enter performance metrics:
   - Date of the record
   - Hours worked
   - Tasks completed
   - Efficiency score (1-10)
   - Quality rating (1-10)
   - Manager notes (optional)
4. Save the record

### 3. View Employee Analysis
1. Go to "Employees" and click on any employee
2. View:
   - Performance trend charts
   - AI predictions for next month
   - Strengths and weaknesses
   - Actionable recommendations
   - Recent performance records

### 4. Generate Reports
1. On any employee detail page, click "Print Report"
2. A printable report opens in a new tab
3. Use your browser's print function (Ctrl+P / Cmd+P) to save as PDF

## 🤖 AI Analysis Engine

The system uses several AI techniques:

### Prediction Algorithm
- **Weighted Moving Average**: Recent data gets higher weight
- **Trend Analysis**: Linear regression to identify performance trajectories
- **Confidence Scoring**: Calculates prediction reliability based on data consistency

### Performance Categorization
Employees are automatically categorized based on:
- Average efficiency scores
- Quality ratings
- Overall performance trends
- Prediction confidence levels

### Recommendation Logic
The system generates recommendations considering:
- Current performance levels
- Historical trends
- Strengths and weaknesses
- Predicted future performance

## 📊 Sample Data

To test the system with sample data:

1. Create a few employees in different departments
2. Add performance records spanning 3-6 months
3. Vary the scores to see different trends:
   - Improving performance (increase scores over time)
   - Declining performance (decrease scores over time)
   - Stable performance (consistent scores)

## 🔧 Configuration

### Database
- Default: SQLite (included)
- To switch to PostgreSQL/MySQL, modify `DATABASES` in `settings.py`

### Static Files
- CSS location: `performance/static/performance/css/styles.css`
- For production, configure `STATIC_ROOT` in `settings.py`

### Debug Mode
- Set `DEBUG = False` in `settings.py` for production
- Update `ALLOWED_HOSTS` with your domain

## 🎨 Customization

### Colors and Styling
Edit `performance/static/performance/css/styles.css` to customize:
- Color scheme (CSS variables at the top)
- Layout and spacing
- Responsive breakpoints
- Print styles

### AI Algorithms
Modify `performance/analysis.py` to customize:
- Prediction algorithms
- Categorization logic
- Recommendation rules
- Trend calculation methods

## 📈 Dashboard Metrics

The dashboard displays:
- **Total Employees**: Active employees in the system
- **Average Efficiency**: Mean efficiency across all records
- **Average Quality**: Mean quality rating across all records
- **Total Records**: Number of performance entries
- **Top Performers**: Top 5 employees by overall score
- **Department Statistics**: Breakdown by department
- **Category Distribution**: Performance category counts

## 🔒 Security Considerations

**For Development:**
- Uses Django's built-in security features
- DEBUG mode enabled
- No authentication required (prototype)

**For Production:**
- Set `DEBUG = False`
- Implement user authentication
- Set up HTTPS
- Configure `ALLOWED_HOSTS`
- Change `SECRET_KEY`
- Use environment variables for sensitive data

## 🐛 Troubleshooting

### Common Issues

**Migration Errors**
```bash
# Delete existing database and migrations
rm db.sqlite3
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

**Port Already in Use**
```bash
# Use a different port
python manage.py runserver 8080
```

**Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Enhanced AI prediction models
- Additional visualization types
- Export to Excel/CSV
- Email notifications
- Mobile app version
- Advanced filtering and search

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

Built with ❤️ using Django and AI/ML techniques

## 🙏 Acknowledgments

- Django Framework
- Chart.js for visualizations
- Pandas for data analysis
- Modern CSS design principles

---

**Note**: This is a demonstration project. For production use, implement proper authentication, security measures, and data validation.

For questions or issues, please open an issue on the project repository.
