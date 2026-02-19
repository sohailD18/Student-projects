# Complete Setup Guide
# AI-Based Demand Forecasting & Inventory Management System

## 🚀 Quick Start (With Authentication & Demo Data)

### Step 1: Navigate to Project
```bash
cd c:\Users\Dell\OneDrive\Desktop\Claude2\E-commerce\Project2
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Admin User (admin/1234)
```bash
python scripts/create_admin.py
```

### Step 5: Create Demo Users
```bash
python scripts/create_demo_users.py
```

### Step 6: Generate Demo Data
```bash
python scripts/generate_dummy_data.py
```

### Step 7: Run Server
```bash
python manage.py runserver
```

### Step 8: Access the Application

**Login Page:** http://127.0.0.1:8000/login/

**Dashboard:** http://127.0.0.1:8000/

**Django Admin:** http://127.0.0.1:8000/admin/

---

## 🔐 User Credentials

### Admin User
- **Username:** `admin`
- **Password:** `1234`
- **Access:** Full system access + Django Admin

### Demo Users
| Username | Password | Role |
|----------|----------|------|
| manager | manager123 | Manager |
| staff1 | staff123 | Staff |
| staff2 | staff123 | Staff |

---

## 📊 Demo Data Generated

### Products (20 items)
**Electronics (5)**
- Wireless Mouse - Stock: 25, Price: $29.99
- USB-C Cable - Stock: 12, Price: $12.99
- Laptop Stand - Stock: 45, Price: $49.99
- Bluetooth Headphones - Stock: 8, Price: $79.99
- Webcam HD - Stock: 150, Price: $59.99

**Clothing (5)**
- Cotton T-Shirt - Stock: 3, Price: $19.99
- Jeans Classic - Stock: 35, Price: $49.99
- Winter Jacket - Stock: 200, Price: $89.99
- Running Shoes - Stock: 22, Price: $79.99
- Socks Pack - Stock: 5, Price: $14.99

**Food & Beverages (5)**
- Organic Coffee - Stock: 120, Price: $15.99
- Green Tea - Stock: 18, Price: $9.99
- Protein Bar - Stock: 65, Price: $24.99
- Almonds Pack - Stock: 9, Price: $12.99
- Olive Oil - Stock: 200, Price: $19.99

**Home & Garden (5)**
- LED Desk Lamp - Stock: 33, Price: $34.99
- Plant Pot Set - Stock: 1, Price: $24.99
- Kitchen Towel Set - Stock: 88, Price: $16.99
- Storage Box - Stock: 44, Price: $19.99
- Wall Clock - Stock: 180, Price: $29.99

### Sales Data
- **Period:** 6 months (180 days)
- **Total Records:** ~3,000+ sales records
- **Features:**
  - Realistic daily sales patterns
  - Weekend spikes
  - Seasonal variations
  - Random fluctuations

---

## 🎯 Features After Login

### Dashboard Features
1. **KPI Cards**
   - Total Products: 20
   - Low Stock Alerts: 5-8 items
   - Total Inventory Value: ~$15,000
   - Average Daily Sales: ~300 units

2. **Interactive Charts**
   - Sales vs Forecast (Line chart)
   - Inventory Status Distribution (Pie chart)
   - Product-specific trend analysis

3. **Inventory Table**
   - Real-time stock levels
   - Predicted demand (30 days)
   - Order quantity suggestions
   - Color-coded status badges

4. **Product Details**
   - Click eye icon (👁️) for details
   - View comprehensive forecast
   - Historical sales charts
   - Trend analysis

---

## 🔧 Authentication System

### User Registration
1. Go to http://127.0.0.1:8000/register/
2. Fill in:
   - First Name
   - Last Name
   - Username
   - Email
   - Password (min 6 characters)
   - Confirm Password
3. Click "Create Account"
4. Login with your credentials

### User Login
1. Go to http://127.0.0.1:8000/login/
2. Enter username and password
3. Click "Login"
4. Redirected to dashboard

### User Profile
- View your profile at: http://127.0.0.1:8000/profile/
- See account information
- View system statistics
- Quick access to dashboard

### Logout
- Click "Logout" in sidebar
- Or use profile page logout button

---

## 📱 API Access (For Developers)

### Authentication Not Required (Current Setup)
API endpoints are accessible without authentication in development mode.

### Key Endpoints
```bash
# All forecasts
curl http://127.0.0.1:8000/api/forecast/all/

# Product forecast
curl http://127.0.0.1:8000/api/forecast/1/

# Trend analysis
curl http://127.0.0.1:8000/api/trend/1/

# Model accuracy
curl http://127.0.0.1:8000/api/accuracy/1/

# Comprehensive report
curl http://127.0.0.1:8000/api/report/1/comprehensive/

# Replenishment report
curl http://127.0.0.1:8000/api/reports/replenishment/
```

---

## 🎨 UI Features

### Sidebar Navigation
- **Dashboard** - Main forecasting dashboard
- **My Profile** - User profile page
- **Admin Panel** - Django Admin (opens in new tab)
- **Logout** - Logout and return to login page

### User Info Display
- Current user's name
- Role (Administrator/Staff Member)
- Avatar icon

### Dashboard Features
- Real-time KPI cards
- Interactive charts with Chart.js
- Search and filter inventory table
- Pagination for large datasets
- Product detail modals
- One-click refresh

---

## 🔒 Security Features

### Password Requirements
- Minimum 6 characters
- Password confirmation during registration

### Session Management
- Login required for dashboard access
- Automatic redirect to login if not authenticated
- Session-based authentication

### User Roles
- **Superuser:** Full access + Django Admin
- **Staff:** Dashboard access only

---

## 📈 Demo Scenarios

### Scenario 1: View Low Stock Items
1. Login with any user
2. On dashboard, look for red status badges
3. Filter by "Low Stock" or "Critical"
4. See suggested order quantities

### Scenario 2: Check Product Forecast
1. Use dropdown in "Sales vs Forecast" chart
2. Select any product (e.g., "Wireless Mouse")
3. View historical sales (blue line)
4. View AI forecast (green dashed line)
5. See 30-day prediction

### Scenario 3: View Product Details
1. In inventory table, click eye icon (👁️)
2. View comprehensive product report
3. See detailed metrics
4. View extended forecast chart

### Scenario 4: Check Trend Analysis
```bash
# Use API to get trend analysis
curl http://127.0.0.1:8000/api/trend/1/

# Response includes:
# - Growth rate percentage
# - Trend direction
# - Volatility
# - Peak sales day
```

---

## 🛠️ Troubleshooting

### Issue: Can't login
**Solution:**
1. Verify credentials from list above
2. Create admin again: `python scripts/create_admin.py`
3. Clear browser cache

### Issue: Dashboard redirects to login
**Solution:** This is expected behavior. You must login first.

### Issue: No data showing
**Solution:**
1. Run dummy data script: `python scripts/generate_dummy_data.py`
2. Refresh browser

### Issue: Admin user doesn't work
**Solution:**
1. Recreate admin: `python scripts/create_admin.py`
2. Verify username is "admin" and password is "1234"

---

## 📝 Script Overview

### create_admin.py
- Creates superuser with credentials: admin/1234
- Resets password if user already exists
- Email: admin@inventory.com

### create_demo_users.py
- Creates 3 demo users (manager, staff1, staff2)
- All passwords: staff123 or manager123
- Useful for testing authentication

### generate_dummy_data.py
- Creates 20 products across 4 categories
- Generates 180 days of sales data
- Creates ~3,000+ sales records
- Realistic sales patterns with trends

---

## 🎓 Learning Path

### 1. First Time Setup
Run all scripts in order:
```bash
python manage.py makemigrations
python manage.py migrate
python scripts/create_admin.py
python scripts/create_demo_users.py
python scripts/generate_dummy_data.py
python manage.py runserver
```

### 2. Explore the Dashboard
- Login with admin/1234
- View KPI cards
- Explore charts
- Check inventory table

### 3. Test Authentication
- Logout
- Login with different users
- Register a new user
- View profile page

### 4. Try API Endpoints
- Use browser or curl
- Access various endpoints
- View JSON responses

---

## 📚 Additional Resources

- **[README.md](README.md)** - Complete project overview
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[SETUP.md](SETUP.md)** - Detailed installation guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference

---

## ✅ Setup Checklist

- [ ] Install dependencies
- [ ] Run migrations
- [ ] Create admin user (admin/1234)
- [ ] Create demo users
- [ ] Generate dummy data
- [ ] Start server
- [ ] Login to dashboard
- [ ] Explore features
- [ ] Test API endpoints
- [ ] Try different user accounts

---

**System Ready!** 🎉

You now have a fully functional AI-powered inventory management system with:
- ✅ User authentication
- ✅ 20 demo products
- ✅ 6 months of sales data
- ✅ AI demand forecasting
- ✅ Trend analysis
- ✅ Model accuracy metrics
- ✅ Comprehensive reports

**Login:** http://127.0.0.1:8000/login/
**Dashboard:** http://127.0.0.1:8000/
**Admin Panel:** http://127.0.0.1:8000/admin/
