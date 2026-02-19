# AI-Based Intelligent Examination Performance Analysis System

## BCA Final Year Project

An intelligent examination system that goes beyond simple marksheets to provide students and teachers with deep insights into strengths, weaknesses, and topic-wise performance using AI-powered data analysis.

## Tech Stack

- **Backend:** Django 4.2+ (Python)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (No React/Vue)
- **Database:** SQLite (default Django DB)
- **Data Visualization:** Chart.js
- **AI/Logic:** Python (Custom logic for analysis)

## Features

### For Students
- Register and take exams
- Real-time exam interface with timer
- Auto-graded results with detailed answer review
- **AI-Powered Performance Analysis:**
  - Topic-wise accuracy breakdown
  - Weak and strong topic identification
  - Personalized improvement suggestions
  - Performance trends over time
  - Interactive charts and visualizations

### For Teachers
- Create and manage subjects and topics
- Design exams with multiple-choice questions
- Link questions to specific topics for better analysis
- Publish exams to students
- View student results and performance statistics

## Project Structure

```
examination_system/
├── manage.py
├── examination_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── examination_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       ├── base.html
│       ├── examination_app/
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── student_dashboard.html
│       │   ├── teacher_dashboard.html
│       │   ├── take_exam.html
│       │   ├── exam_result.html
│       │   ├── performance_report.html
│       │   ├── create_exam.html
│       │   ├── manage_exam.html
│       │   ├── manage_subjects.html
│       │   └── profile.html
│       └── ...
└── static/
    └── examination_app/
        ├── css/
        │   └── style.css
        └── js/
            └── main.js
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Navigate to Project Directory

```bash
cd examination_system
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

### Step 7: Access Application

Open your browser and navigate to:
- **Application:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

## Database Models

### Core Models
1. **User** (Custom User Model)
   - Extends Django's AbstractUser
   - Roles: Student, Teacher
   - Additional fields: phone_number, date_of_birth

2. **Subject**
   - Academic subjects (Math, Science, etc.)
   - Fields: name, code, description

3. **Topic**
   - Linked to Subject (e.g., Algebra under Math)
   - Crucial for topic-wise analysis
   - Fields: subject, name, chapter_number

4. **Exam**
   - Created by teachers
   - Fields: title, subject, total_marks, duration, status

5. **Question**
   - Linked to Exam and Topic
   - Supports MCQ and True/False
   - Fields: text, options A-D, correct_answer, marks

6. **StudentAnswer**
   - Stores student's answers
   - Auto-graded on save
   - Fields: student, question, selected_answer, is_correct

7. **ExamResult**
   - Overall exam results
   - Fields: score, percentage, time_taken, status

8. **PerformanceAnalysis**
   - AI-generated insights
   - Fields: weak_topics, strong_topics, suggestions, detailed_insights

## AI Performance Analysis Algorithm

The `analyze_performance()` function in `views.py` implements the core AI logic:

1. **Data Collection:** Fetches all student answers for a subject
2. **Topic-wise Calculation:** Computes accuracy per topic
3. **Classification:**
   - Weak topics: Accuracy < 50%
   - Strong topics: Accuracy ≥ 70%
4. **Trend Analysis:** Compares recent vs older performance
5. **Suggestion Generation:** Creates personalized feedback
6. **Storage:** Saves insights to PerformanceAnalysis model

## Key Features Implementation

### Auto-Grading
When a student submits an exam:
1. Answers are saved to `StudentAnswer` model
2. Model's `save()` method auto-calculates `is_correct` and `marks_obtained`
3. Overall result is computed and stored in `ExamResult`
4. `analyze_performance()` is triggered automatically

### Chart.js Integration
- **Radar/Polar Charts:** Topic-wise performance visualization
- **Bar Charts:** Accuracy comparison across topics
- **Line Charts:** Performance trends over time
- **Doughnut Charts:** Strong topics breakdown

### Exam Interface Features
- Countdown timer
- Question navigator
- Progress tracking
- Auto-save to `ExamProgress` model
- Warning before submission

## Usage Instructions

### For Teachers
1. Register as a Teacher
2. Create Subjects and Topics
3. Create Exams and add Questions
   - Link questions to Topics for better analysis
4. Publish Exams when ready
5. View student results

### For Students
1. Register as a Student
2. Browse available exams
3. Take exams with timer
4. View detailed results
5. Check AI-powered performance reports
6. Follow suggestions for improvement

## Screenshots Reference

### Dashboards
- **Teacher Dashboard:** Overview of created exams and student results
- **Student Dashboard:** Available exams, completed exams, performance insights

### Analysis Report
- **Radar Charts:** Subject-wise performance
- **Bar Charts:** Topic-wise accuracy
- **Weak/Strong Topics:** Visual identification
- **AI Suggestions:** Personalized recommendations
- **Trends:** Improvement over time

## Future Enhancements

- [ ] Add question bank import/export
- [ ] Support for descriptive questions
- [ ] Email notifications
- [ ] PDF report generation
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native/Flutter)

## Author

BCA Final Year Project
AI-Based Intelligent Examination Performance Analysis System

## License

This project is created for educational purposes.

---

**Note:** This is a BCA final year project demonstrating the integration of Django, data analysis, and AI concepts for educational assessment.
