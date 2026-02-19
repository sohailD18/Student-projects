# ⚡ Quick Reference Card

## 🚀 Start in 3 Commands

```bash
pip install -r requirements.txt
python manage.py makemigrations && python manage.py migrate
python manage.py populate_data && python manage.py runserver
```

---

## 🔑 Login Credentials

```
┌────────────┬───────────┬──────────┬──────────────┐
│ Username   │ Password  │ Type     │ Access       │
├────────────┼───────────┼──────────┼──────────────┤
│ demo       │ demo123   │ User     │ All features │
│ admin      │ admin123  │ Admin    │ + Admin panel│
│ john_doe   │ john123   │ User     │ All features │
│ jane_smith │ jane123   │ User     │ All features │
└────────────┴───────────┴──────────┴──────────────┘
```

---

## 🌐 URLs

| Page | URL |
|------|-----|
| **Home** | http://127.0.0.1:8000/ |
| **Login** | http://127.0.0.1:8000/login/ |
| **Register** | http://127.0.0.1:8000/register/ |
| **Profile** | http://127.0.0.1:8000/profile/ |
| **Admin** | http://127.0.0.1:8000/admin/ |

---

## 📊 Dummy Data

```
Users:     4 accounts
Locations: 15 cities
Traffic:   168 entries (24h × 7 days)
Routes:    50+ between cities
History:   30 entries
Metrics:   30 days
```

---

## 🎯 How to Use

1. **Open** http://127.0.0.1:8000/
2. **Login** with `demo` / `demo123`
3. **Click map** to set origin (blue)
4. **Click again** for destination (red)
5. **Press** "Calculate Routes"
6. **View** 4 route options
7. **Select** any route to highlight
8. **Export** report as text file

---

## 🛠️ Common Commands

```bash
# Create dummy data
python manage.py populate_data

# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Open admin panel
# Go to http://127.0.0.1:8000/admin/

# Reset database
rm db.sqlite3
python manage.py migrate
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `views.py` | All API endpoints & auth |
| `models.py` | 5 database models |
| `optimization_engine.py` | AI algorithms |
| `populate_data.py` | Dummy data generator |
| `index.html` | Main app |
| `login.html` | Login page |
| `register.html` | Registration page |
| `profile.html` | User profile |

---

## 🎨 Features

✅ Interactive map (Leaflet + OpenStreetMap)
✅ 4 route types (Fastest, Shortest, Scenic, Eco)
✅ AI optimization with traffic simulation
✅ Analytics dashboard (4 charts)
✅ User authentication (Login, Register, Profile)
✅ Export route reports
✅ 15 demo cities
✅ 4 demo accounts
✅ Complete dummy data

---

## 📚 Documentation

- **README.md** - Full documentation
- **QUICK_START.md** - Quick start guide
- **SETUP_GUIDE.md** - Detailed setup
- **DEMO_CREDENTIALS.md** - All accounts
- **FEATURES_SUMMARY.md** - Complete feature list

---

## ⚡ Tech Stack

```
Backend:  Django 4.2 + Python + SQLite
Frontend: HTML5 + CSS3 + Vanilla JavaScript
Maps:     Leaflet.js + OpenStreetMap (FREE!)
Charts:   Chart.js
Auth:     Django Session Authentication
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No such table | `python manage.py migrate` |
| Can't login | Run `python manage.py populate_data` |
| Port 8000 busy | `python manage.py runserver 8001` |
| Static files missing | `python manage.py collectstatic` |
| Routes not calculating | Check browser console |

---

## 🎉 You're Ready!

Visit **http://127.0.0.1:8000/** and login with **demo/demo123**

---

*Built with Django, Python, Leaflet.js, OpenStreetMap & Chart.js*
