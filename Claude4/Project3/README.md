# AI-Enabled Worker Safety and Hazard Detection System

**A complete full-stack project for BCA Final Year**

This system uses computer vision and AI to detect safety violations in real-time, including missing PPE (helmets, safety vests) and unauthorized access to restricted zones.

## 📋 Project Overview

The AI-Enabled Worker Safety System provides:

- **Real-time video monitoring** with AI-powered object detection
- **Safety violation detection** (no helmet, no vest, restricted zone intrusion)
- **Live dashboard** with statistics and alerts
- **Incident logging** with snapshots and confidence scores
- **Reports and analytics** for safety compliance tracking

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Django 5.0 |
| **Database** | SQLite (default) |
| **Computer Vision** | OpenCV with DNN module |
| **AI Model** | MobileNet SSD / COCO dataset |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Video Streaming** | MJPEG streaming |

## 📁 Project Structure

```
safety_system/                # Root Django project directory
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── safety_system/            # Project configuration
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
│
├── monitoring/               # Main application
│   ├── __init__.py
│   ├── apps.py               # App configuration
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Admin interface
│   └── detection.py          # AI detection module
│
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   └── monitoring/
│       ├── dashboard.html    # Main dashboard
│       ├── reports.html      # Reports page
│       └── settings.html     # Settings page
│
├── static/                   # Static files
│   └── monitoring/
│       ├── css/
│       │   └── dashboard.css # Dashboard styles
│       └── js/
│           └── dashboard.js  # Dashboard scripts
│
├── media/                    # Uploaded files (snapshots)
│   └── snapshots/            # Violation snapshots
│
└── models/                   # AI model files (optional)
    └── MobileNetSSD_*.caffemodel
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Webcam or video file for testing
- Virtual environment (recommended)

### Step 1: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
cd safety_system
pip install -r requirements.txt
```

### Step 3: Run Database Migrations

```bash
python manage.py makemigrations monitoring
python manage.py migrate
```

### Step 4: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 5: Run the Development Server

```bash
python manage.py runserver
```

The server will start at: **http://127.0.0.1:8000**

### Step 6: Access the Application

- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Reports:** http://127.0.0.1:8000/reports/
- **Settings:** http://127.0.0.1:8000/settings/

## 📸 Using AI Detection Models

### Option 1: Using Haar Cascade (Default - Built-in)

The system includes a fallback detection using OpenCV's Haar Cascade, which works without additional model files.

### Option 2: Using MobileNet SSD (Recommended)

For better accuracy, download the MobileNet SSD model:

1. Download model files:
   - [MobileNetSSD_deploy.prototxt](https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.prototxt)
   - [MobileNetSSD_deploy.caffemodel](https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel)

2. Place them in the `models/` directory:

```bash
mkdir models
# Download and copy model files to models/ directory
```

3. The system will automatically load the models if found.

### Option 3: Custom Training for PPE Detection

For production use, consider training a custom model on datasets like:
- [Safety Helmet Detection Dataset](https://www.kaggle.com/datasets)
- [Safety Vest Dataset](https://www.roboflow.com/)

## 🎯 Features & Usage

### 1. Live Monitoring Dashboard

- Real-time video feed from webcam/video file
- Bounding boxes around detected persons
- Restricted zone overlays
- Live statistics (workers detected, violations)
- Real-time alerts panel

### 2. Safety Incident Logging

The system automatically logs:
- **Timestamp** of detection
- **Camera ID** that detected the incident
- **Hazard Type** (No Helmet, No Vest, etc.)
- **Confidence Score** (0-100%)
- **Snapshot Image** of the violation
- **Resolution Status** (resolved/pending)

### 3. Reports Page

- View all incidents with filtering
- Filter by date range and hazard type
- Export reports to CSV
- Mark incidents as resolved
- View violation snapshots

### 4. Settings Configuration

- **Camera Configuration:** Add multiple cameras (webcam, IP camera, video file)
- **Restricted Zones:** Define monitored restricted areas
- **Detection Settings:** Adjust confidence threshold and snapshot interval

## 🎨 Customization

### Change Camera Source

Edit `safety_system/settings.py`:

```python
DETECTION_CONFIG = {
    'camera_source': 0,  # 0 for webcam, or 'path/to/video.mp4'
}
```

### Adjust Detection Confidence

In `monitoring/detection.py`, modify:

```python
def __init__(self, confidence_threshold=0.5):  # Change 0.5 to desired value
```

### Add Custom Hazard Types

Edit `monitoring/models.py`:

```python
HAZARD_TYPES = [
    ('NO_HELMET', 'No Helmet'),
    ('NO_VEST', 'No Safety Vest'),
    # Add your custom types here
]
```

## 📊 Database Models

### SafetyIncident
- Stores each detected safety violation
- Includes snapshot image, confidence score, timestamp
- Tracks resolution status

### SystemMetrics
- Daily statistics (workers detected, violations, safety score)
- Aggregated metrics for reporting

### RestrictedZone
- Defined restricted areas (coordinates)
- Used for intrusion detection

### CameraConfig
- Multiple camera configuration
- Supports webcam, IP camera, RTSP streams

## 🔧 Troubleshooting

### Camera Not Working

**Problem:** "Camera Offline" error

**Solutions:**
1. Check if webcam is connected
2. Try changing `camera_source` in settings
3. Test with a video file instead of webcam
4. Ensure OpenCV is installed correctly: `pip install opencv-python`

### Import Errors

**Problem:** "No module named 'cv2'"

**Solution:**
```bash
pip install opencv-python
```

### Database Errors

**Problem:** "no such table: monitoring_safetyincident"

**Solution:**
```bash
python manage.py migrate
```

### Port Already in Use

**Problem:** "Error: That port is already in use"

**Solution:**
```bash
python manage.py runserver 8001
```

## 🚀 Deployment

For production deployment:

### 1. Update Settings

```python
# safety_system/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
STATIC_ROOT = '/var/www/static/'
MEDIA_ROOT = '/var/www/media/'
```

### 2. Collect Static Files

```bash
python manage.py collectstatic
```

### 3. Use Production Server

```bash
pip install gunicorn
gunicorn safety_system.wsgi:application
```

### 4. Set Up Database (Optional)

For production, consider PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'safety_system',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/monitoring/api/incidents/` | GET | Get recent incidents and stats |
| `/monitoring/api/statistics/` | GET | Get weekly statistics |
| `/monitoring/api/status/` | GET | Get system status |
| `/monitoring/api/resolve/<id>/` | POST | Mark incident as resolved |
| `/monitoring/api/zone/add/` | POST | Add restricted zone |
| `/monitoring/video-feed/` | GET | Live video stream |

## 🎓 Academic Project Guidelines

### Project Report Sections

1. **Introduction** - Overview of workplace safety and AI
2. **Literature Review** - Object detection techniques, OpenCV, YOLO
3. **System Design** - Architecture, database schema, UI design
4. **Implementation** - Code explanation, algorithms used
5. **Testing** - Test cases, screenshots, results
6. **Conclusion** - Findings, limitations, future scope

### Key Topics to Cover

- **Computer Vision**: How OpenCV processes video frames
- **Object Detection**: MobileNet SSD / YOLO algorithms
- **Django Framework**: MTV architecture, ORM, views
- **Real-time Processing**: Frame-by-frame analysis
- **Database Design**: Relational model for incidents

## 📝 Future Enhancements

- [ ] Custom YOLO model for helmet and vest detection
- [ ] Face recognition for worker identification
- [ ] Email/SMS alerts on violations
- [ ] Mobile app for remote monitoring
- [ ] Integration with IoT sensors
- [ ] Multi-camera simultaneous monitoring
- [ ] Historical trend analysis
- [ ] PDF report generation

## 📄 License

This project is created for educational purposes. Feel free to use and modify as needed.

## 👥 Contributors

Created for BCA Final Year Project.

## 📞 Support

For issues or questions:
- Check the Troubleshooting section above
- Review Django and OpenCV documentation
- Check error logs in `logs/safety_system.log`

---

**Good luck with your project! 🎓**
