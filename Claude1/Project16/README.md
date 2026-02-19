# EduProctor - Online Examination Monitoring & Integrity System

A comprehensive AI-powered online exam proctoring platform built with Django that ensures examination integrity through real-time monitoring, behavior analysis, and violation detection.

![EduProctor](https://img.shields.io/badge/version-2.0-blue) ![Django](https://img.shields.io/badge/Django-6.0.1-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue)

## 🎯 Features

### Core Modules

| Module | Status | Description |
|--------|--------|-------------|
| **Candidate Identity Verification** | ✅ Complete | Student authentication with ID validation |
| **Live Exam Session Monitoring** | ✅ Enhanced | Camera access + periodic frame capture (30s) |
| **Behavior Pattern Analysis** | ✅ Active | Tab switch, copy/paste, idle detection |
| **Tab & Screen Activity Detection** | ✅ Complete | Visibility change, fullscreen monitoring |
| **Violation Flagging System** | ✅ Complete | Real-time API logging with weighted severity |
| **Exam Session Recording** | ✅ Complete | Session metadata with IP/browser tracking |
| **Violation Scoring Engine** | ✅ Enhanced | Weighted severity (5-30 points per violation) |
| **Integrity Report Generator** | ✅ Complete | Detailed reports with session timeline |

### Violation Severity Levels

```
Tab Switch:          5 points   (Low)
Copy/Paste:          10 points  (Medium)
No Movement:         5 points   (Low)
No Face:             15 points  (High)
Multiple Faces:      25 points  (Very High)
Phone Detected:      30 points  (Critical)
Suspicious Object:   20 points  (High)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (included with Python)

### Installation

1. **Clone or download the project**

2. **Navigate to project directory**
   ```bash
   cd Project16
   ```

3. **Install dependencies** (if needed)
   ```bash
   pip install django
   ```

4. **Load demo data**
   ```bash
   python manage.py load_demo_data
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Student Login: http://localhost:8000/login/
   - Admin Dashboard: http://localhost:8000/admin/
   - Django Admin: http://localhost:8000/admin/monitoring/

### Demo Credentials

| Student ID | Name |
|------------|------|
| STU001 | John Smith |
| STU002 | Emily Johnson |
| STU003 | Michael Brown |
| STU004 | Sarah Davis |
| STU005 | David Wilson |
| STU006 | Jessica Martinez |
| STU007 | Chris Taylor |
| STU008 | Amanda Anderson |

**Note:** Click on any student ID badge on the login page to auto-fill credentials.

## 📁 Project Structure

```
Project16/
├── eduproctor/              # Django project settings
│   ├── settings.py          # Main configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI application
├── monitoring/              # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Admin interface
│   ├── templates/           # HTML templates
│   │   └── monitoring/
│   │       ├── base.html          # Base template
│   │       ├── login.html         # Student login
│   │       ├── dashboard.html     # Student dashboard
│   │       ├── exam.html          # Exam interface
│   │       ├── results.html       # Results page
│   │       ├── integrity_report.html  # Detailed report
│   │       ├── admin_dashboard.html    # Admin panel
│   │       └── create_exam.html       # Exam creation
│   └── management/          # Management commands
│       └── commands/
│           └── load_demo_data.py   # Demo data loader
├── manage.py                # Django management script
└── db.sqlite3               # SQLite database
```

## 🎨 UI/UX Features

### Design Enhancements

- **Modern gradient design** with purple theme
- **Responsive layout** for mobile and desktop
- **Animated elements** (confetti, hover effects)
- **Real-time status indicators** (camera, focus, violations)
- **Color-coded severity levels** for quick assessment
- **Interactive exam cards** with detailed metadata
- **Smooth page transitions** and micro-interactions

### User Interface Components

1. **Login Page**: Split-screen design with feature highlights
2. **Dashboard**: Quick stats, exam cards, recent activity
3. **Exam Interface**: Timer, questions, camera preview, violation alerts
4. **Results Page**: Score summary, violation breakdown, confetti animation
5. **Integrity Report**: Session timeline, severity breakdown, recommendations
6. **Admin Panel**: Session monitoring, statistics, quick actions

## 🔧 Configuration

### Exam Settings

Each exam can be configured with:
- Subject/title
- Duration (minutes)
- Passing score percentage
- Instructions
- Multiple choice questions

### Monitoring Settings

Adjust in [exam.html](monitoring/templates/monitoring/exam.html):
- Frame capture interval (default: 30 seconds)
- Idle detection timeout (default: 30 seconds)
- Timer warning thresholds (default: 5 min, 1 min)

## 📊 Database Models

### Core Models

| Model | Purpose |
|-------|---------|
| `Student` | Student information |
| `Exam` | Exam configuration |
| `Question` | Individual questions |
| `Choice` | Multiple choice options |
| `ExamSession` | Session tracking |
| `ExamResult` | Results & scoring |
| `ProctorLog` | Violation records |

## 🔒 Security Features

1. **CSRF Protection** on all forms
2. **Session Management** for authentication
3. **Keyboard Shortcut Blocking** during exams
4. **Tab Switch Detection** with immediate logging
5. **Copy/Paste Prevention** with violation tracking
6. **Fullscreen Requirement** for monitoring
7. **IP Address Logging** for session audit

## 🐛 Troubleshooting

### Common Issues

**Issue**: Camera not accessing
- **Solution**: Ensure browser permissions allow camera access

**Issue**: Migrations error
- **Solution**: Run `python manage.py migrate`

**Issue**: Demo data not loading
- **Solution**: Run `python manage.py load_demo_data` again

**Issue**: Port 8000 already in use
- **Solution**: Run `python manage.py runserver 8001`

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG = False` in [settings.py](eduproctor/settings.py)
2. Configure `ALLOWED_HOSTS`
3. Set up production database (PostgreSQL recommended)
4. Configure static files serving
5. Set up HTTPS
6. Configure media file storage for screenshots
7. Set up proper logging
8. Configure email for notifications

### Environment Variables

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/db
```

## 📈 Future Enhancements

Features marked as "planned" in the code require additional libraries:

1. **Face Detection**: `opencv-python`, `face_recognition`
2. **Phone Detection**: YOLO, SSD object detection models
3. **Behavior Pattern Analysis (ML)**: TensorFlow/PyTorch
4. **Video Recording Storage**: Media file storage configuration
5. **Real-time Proctor Dashboard**: WebSocket implementation

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Built with ❤️ using Django and Bootstrap

---

**Version**: 2.0
**Last Updated**: 2025-01-29
**Django Version**: 6.0.1
