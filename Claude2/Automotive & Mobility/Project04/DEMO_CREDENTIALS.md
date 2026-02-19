# 🔐 Demo User Credentials

## Pre-Created User Accounts

After running the dummy data population command, the following demo accounts will be available:

### 1️⃣ Demo User (Standard Account)

```
Username: demo
Email: demo@example.com
Password: demo123
First Name: Demo
Last Name: User
Permissions: Standard User
```

### 2️⃣ Admin User (Administrator Account)

```
Username: admin
Email: admin@example.com
Password: admin123
First Name: Admin
Last Name: User
Permissions: Superuser + Staff (Full Admin Access)
```

### 3️⃣ John Doe (Regular User)

```
Username: john_doe
Email: john@example.com
Password: john123
First Name: John
Last Name: Doe
Permissions: Standard User
```

### 4️⃣ Jane Smith (Regular User)

```
Username: jane_smith
Email: jane@example.com
Password: jane123
First Name: Jane
Last Name: Smith
Permissions: Standard User
```

---

## 🚀 Quick Start with Demo Data

### Step 1: Set Up the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Populate Dummy Data

```bash
# Run the dummy data population command
python manage.py populate_data
```

This command will:
- ✅ Create 4 demo user accounts (listed above)
- ✅ Add 15 major US cities as locations
- ✅ Generate 168 traffic data entries (24 hours × 7 days)
- ✅ Create ~50 routes between locations
- ✅ Add 30 route history entries
- ✅ Generate 30 days of optimization metrics

### Step 3: Start the Server

```bash
python manage.py runserver
```

### Step 4: Log In

Open your browser to:
- **Main App**: http://127.0.0.1:8000/
- **Login Page**: http://127.0.0.1:8000/login/
- **Admin Panel**: http://127.0.0.1:8000/admin/

Use any of the credentials above to log in!

---

## 📊 What's Included in Dummy Data

### Locations (15 Cities)
- New York City
- Los Angeles
- Chicago
- Houston
- Phoenix
- Philadelphia
- San Antonio
- San Diego
- Dallas
- San Jose
- Boston
- Miami
- Seattle
- Denver
- Atlanta

### Traffic Data
- **168 entries** covering:
  - All 24 hours of the day
  - All 7 days of the week
  - Realistic traffic patterns:
    - Rush hours (7-9 AM, 5-7 PM): 1.8-2.5x traffic
    - Daytime (10 AM-4 PM): 1.2-1.5x traffic
    - Night/Low traffic: 0.9-1.2x traffic

### Routes (~50 routes)
- Fastest, Shortest, Scenic, and Eco-friendly options
- Connecting various city pairs
- With realistic distances, times, and costs

### Route History (30 entries)
- Simulated historical route calculations
- Spread across the last 30 days
- Attributed to different users

### Optimization Metrics (30 days)
- Daily statistics for the last month
- Performance tracking data
- Traffic prediction accuracy metrics

---

## 🎯 Testing Different User Types

### As a Regular User (demo, john_doe, jane_smith)
You can:
- ✅ Plan routes
- ✅ View your profile and history
- ✅ Export reports
- ❌ Access admin panel

### As an Admin (admin)
You can:
- ✅ Everything a regular user can do
- ✅ Access Django admin panel at `/admin/`
- ✅ Manage all database records
- ✅ View system-wide analytics
- ✅ Manage users

---

## 🔑 Admin Panel Access

### URL
http://127.0.0.1:8000/admin/

### What You Can Do
1. **Manage Users**: View, edit, create user accounts
2. **View Locations**: See all geographic locations
3. **Analyze Traffic Data**: Review traffic patterns
4. **Inspect Routes**: See all calculated routes
5. **Review History**: Check route calculation history
6. **Monitor Metrics**: View optimization performance

---

## 🧪 Testing Scenarios

### Scenario 1: Route Planning
1. Log in as any user
2. Click on the map to set origin (e.g., New York)
3. Click again to set destination (e.g., Boston)
4. Click "Calculate Routes"
5. View 4 different route options
6. Select and compare routes

### Scenario 2: View Profile & History
1. Log in as `demo` user
2. Click "View Profile" in header
3. See your route history (20 most recent)
4. View total stats: routes, distance, savings

### Scenario 3: Admin Panel
1. Log in as `admin` user
2. Go to http://127.0.0.1:8000/admin/
3. Browse different sections
4. View/add/edit database records

### Scenario 4: Register New User
1. Go to http://127.0.0.1:8000/register/
2. Fill in registration form
3. Automatically logged in after registration
4. Start planning routes immediately

---

## 📝 Creating Additional Test Users

### Option 1: Via Admin Panel
1. Log in as admin
2. Go to Admin Panel → Users
3. Click "Add User"
4. Fill in details and save

### Option 2: Via Command Line
```bash
python manage.py createsuperuser
# Or create regular user via shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('newuser', 'user@example.com', 'password123')
```

### Option 3: Via Registration Page
1. Go to http://127.0.0.1:8000/register/
2. Fill in the form
3. Submit to create account

---

## 🔒 Security Notes

### ⚠️ Important for Production
These credentials are for **DEMO/DEVELOPMENT ONLY**. Before deploying to production:

1. **Change all passwords**
2. **Delete or disable demo accounts**
3. **Set `DEBUG = False`** in settings.py
4. **Update `ALLOWED_HOSTS`** with your domain
5. **Use environment variables** for sensitive data
6. **Enable HTTPS** for secure authentication
7. **Implement rate limiting** for login attempts
8. **Add email verification** for registration

---

## 🛠️ Troubleshooting

### Can't log in?
- Make sure you've run `python manage.py populate_data`
- Check username and password are correct
- Try clearing browser cache and cookies

### Admin panel not accessible?
- Ensure you're using the `admin` user
- Verify the user has `is_superuser=True` and `is_staff=True`

### Data not showing?
- Run migrations: `python manage.py migrate`
- Populate data: `python manage.py populate_data`
- Restart the server

---

## 📚 Related Documentation

- [README.md](README.md) - Full project documentation
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)

---

**✨ Ready to test! Use any demo account and start exploring!**
