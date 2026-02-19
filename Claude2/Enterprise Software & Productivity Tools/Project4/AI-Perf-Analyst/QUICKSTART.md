# Quick Start Guide - AI Performance Analyst

## 🚀 Get Running in 5 Minutes

### Option 1: Using Setup Script (Recommended)

1. **Double-click `setup.bat`**
   - This will create a virtual environment
   - Install all dependencies
   - Set up the database
   - Optionally create an admin user

2. **Activate the virtual environment**
   ```bash
   venv\Scripts\activate
   ```

3. **Start the server**
   ```bash
   python manage.py runserver
   ```

4. **Open your browser**
   Go to: `http://127.0.0.1:8000/`

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database
python manage.py makemigrations
python manage.py migrate

# 5. Run server
python manage.py runserver
```

## 📚 Basic Usage

### 1. Add Your First Employee
1. Click **"Add Employee"** in the navigation
2. Enter:
   - Name: John Doe
   - Department: Engineering
   - Role: Software Engineer
   - Join Date: (today's date)
3. Click **"Save Employee"**

### 2. Log Performance Data
1. Click **"Add Record"**
2. Select the employee
3. Enter metrics:
   - Date: today
   - Hours Worked: 8
   - Tasks Completed: 10
   - Efficiency: 7.5
   - Quality: 8.0
4. Click **"Save Record"**

### 3. View Analysis
1. Go to **"Employees"**
2. Click on any employee name
3. See:
   - Performance charts
   - AI predictions
   - Recommendations
   - Strengths & weaknesses

### 4. Add More Data
To see meaningful predictions, add multiple records:
- Add records for different dates
- Vary the scores to see trends
- Add 5-10 records for best results

## 🎯 Test with Sample Data

### Sample Employee 1: High Performer
- Name: Alice Johnson
- Add 6 records with increasing scores (6 → 9)
- Result: "Promotion Candidate"

### Sample Employee 2: Needs Improvement
- Name: Bob Smith
- Add 6 records with declining scores (7 → 4)
- Result: "Needs Training"

### Sample Employee 3: Stable Performer
- Name: Carol Davis
- Add 6 records with consistent scores (around 6-7)
- Result: "Stable"

## 📊 Understanding the Dashboard

### Statistics Cards
- **Total Employees**: Number of employees in system
- **Average Efficiency**: Mean efficiency score (1-10)
- **Average Quality**: Mean quality rating (1-10)
- **Total Records**: Total performance entries

### Top Performers
Shows top 5 employees by overall score with ranks (🥇🥈🥉)

### Department Statistics
Breakdown of metrics by department

### Category Distribution
Visual breakdown of performance categories

## 🤖 Understanding AI Predictions

### Confidence Level
- **High (80-100%)**: Lots of data, consistent patterns
- **Medium (50-79%)**: Some data, moderate consistency
- **Low (<50%)**: Not enough data yet

### Prediction Metrics
- **Efficiency**: Expected task completion rate
- **Quality**: Expected work quality
- **Overall Score**: Combined performance metric
- **Productivity**: Expected tasks per hour

### Performance Categories
- **Promotion Candidate**: Excellence in all areas (8.5+)
- **High Potential**: Strong performance with positive trends
- **Stable**: Meeting expectations consistently
- **Needs Training**: Areas requiring improvement

## 🎨 Customization Tips

### Change Colors
Edit `performance/static/performance/css/styles.css`:
```css
:root {
    --primary-color: #2563eb;  /* Main blue */
    --success-color: #10b981;  /* Green */
    --danger-color: #ef4444;   /* Red */
}
```

### Modify Prediction Algorithm
Edit `performance/analysis.py`:
```python
def predict_next_month_performance(df):
    # Adjust weights for different prediction styles
    weights = [1, 2, 3]  # Current: recent data weighted more
    # Try: [1, 1, 1] for equal weighting
```

### Add New Metrics
1. Add field to `models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Update forms and templates

## 🔧 Common Commands

```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Reset database
del db.sqlite3
python manage.py migrate

# Access admin panel
# URL: http://127.0.0.1:8000/admin/

# Run on different port
python manage.py runserver 8080
```

## 💡 Tips for Best Results

1. **Add Regular Data**: Log performance weekly or monthly
2. **Be Consistent**: Use the same scoring criteria
3. **Add Context**: Use manager notes for important events
4. **Review Trends**: Check dashboard regularly
5. **Export Reports**: Use print reports for performance reviews

## 🐛 Having Issues?

### Server Won't Start
- Check if port 8000 is in use
- Try: `python manage.py runserver 8080`

### Database Errors
- Delete `db.sqlite3` and run migrations again
- See README.md for details

### Import Errors
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

## 📞 Need Help?

- Check the full [README.md](README.md)
- Review Django documentation: https://docs.djangoproject.com/
- Open an issue on the project repository

---

**Enjoy using AI Performance Analyst! 🚀**
