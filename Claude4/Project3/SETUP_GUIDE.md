# Quick Setup Guide

## Fast Setup (5 Minutes)

### 1. Install Python Dependencies

```bash
pip install django opencv-python numpy pillow
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Admin User

```bash
python manage.py createsuperuser
```

### 4. Start Server

```bash
python manage.py runserver
```

### 5. Open Browser

Navigate to: http://127.0.0.1:8000/

---

## Common Issues & Solutions

### Issue: Camera not working

**Solution:** If you don't have a webcam, edit `monitoring/detection.py` and change:

```python
# For webcam (default)
self.cap = cv2.VideoCapture(0)

# For video file (replace with your video path)
self.cap = cv2.VideoCapture('path/to/video.mp4')
```

### Issue: Port 8000 already in use

**Solution:** Use a different port:

```bash
python manage.py runserver 8001
```

### Issue: No module named 'cv2'

**Solution:** Install OpenCV:

```bash
pip install opencv-python
```

---

## Testing Without Webcam

1. Download any sample video file (mp4 format)
2. Place it in the project root
3. Edit `monitoring/detection.py` line ~136:

```python
global_stream = VideoStream(source='your_video.mp4')
```

---

## Admin Access

- **URL:** http://127.0.0.1:8000/admin/
- **Login:** Use the superuser credentials created in step 3
- **Features:** View incidents, manage zones, configure cameras

---

## Project Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/dashboard/` | Live monitoring feed |
| Reports | `/reports/` | Incident history |
| Settings | `/settings/` | Configuration |
| Admin | `/admin/` | Django admin panel |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `safety_system/settings.py` | Main configuration |
| `monitoring/detection.py` | AI detection logic |
| `monitoring/models.py` | Database models |
| `templates/monitoring/dashboard.html` | Main dashboard |

---

## Uninstall / Clean Up

```bash
# Remove database
rm db.sqlite3

# Remove migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Remove virtual environment
deactivate
rm -rf venv
```

---

## Need Help?

Check the main [README.md](README.md) for detailed documentation.
