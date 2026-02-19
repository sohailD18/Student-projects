# Authentication System - User Guide

## ✅ Authentication Fixed!

The JobPortal now has a **complete custom authentication system** with proper Login and Register pages. No more redirects to Django admin!

---

## 🔐 New Authentication Features

### 1. **Custom Login Page**
- URL: `http://127.0.0.1:8000/accounts/login/`
- Beautiful, user-friendly interface
- Username/password authentication
- Auto-redirect after login
- Demo credentials displayed on page

### 2. **Custom Registration Page**
- URL: `http://127.0.0.1:8000/accounts/register/`
- Full registration form with validation
- Fields: Username, Email, First Name, Last Name, Password
- Password strength validation
- Email verification ready
- Auto-login after registration

### 3. **User Profile Page**
- URL: `http://127.0.0.1:8000/accounts/profile/`
- View and edit profile information
- Account statistics
- Member since date
- Account type indicator

### 4. **Custom Logout**
- URL: `http://127.0.0.1:8000/accounts/logout/`
- One-click logout
- Success message
- Auto-redirect to home

---

## 🎯 How It Works

### Login Flow:
1. User clicks **"Login / Register"** in navigation
2. Redirected to custom login page
3. Enters username and password
4. On success: Redirected to home with welcome message
5. On failure: Error message displayed

### Registration Flow:
1. User clicks **"Register here"** on login page
2. Fills in registration form
3. Password must be 8+ characters
4. On success: Account created + Auto-login + Redirect to home
5. On error: Validation errors shown

### Navigation Menu:
**Not Logged In:**
- Shows "Login / Register" button
- Redirects to custom login page

**Logged In:**
- Shows username with dropdown
- Options:
  - **My Profile** - View/edit profile
  - **Admin Panel** (if staff) - Django admin
  - **Logout** - Sign out

---

## 🔑 Test Accounts

### Admin Account:
- **Username:** admin
- **Password:** admin123
- **Access:** All features + Admin Panel

### Demo User Account:
- **Username:** demo_user
- **Password:** demo123
- **Access:** Regular user features

---

## 📝 Form Fields

### Registration Form:
1. **First Name** (Optional)
2. **Last Name** (Optional)
3. **Username** (Required, unique)
4. **Email** (Required, unique)
5. **Password** (Required, min 8 chars)
6. **Confirm Password** (Required, must match)

### Password Requirements:
- Minimum 8 characters
- Can't be too similar to personal info
- Can't be a common password
- Can't be entirely numeric

---

## 🎨 Page Features

### Login Page:
- Clean, centered design
- Input icons for better UX
- Demo accounts displayed
- Link to registration page
- Error message display

### Registration Page:
- Two-column layout for names
- Real-time password matching validation
- Password requirements listed
- Terms checkbox
- Link to login page

### Profile Page:
- User avatar icon
- Account information display
- Quick statistics (applications, jobs, saved)
- Edit profile form
- Account type badge

---

## 🔗 URL Structure

```
/accounts/login/          → Custom login page
/accounts/register/       → Custom registration page
/accounts/logout/         → Custom logout
/accounts/profile/        → User profile page
```

---

## 🛠️ Technical Details

### Files Created:
1. **accounts/views.py** - Authentication views
2. **accounts/forms.py** - Custom registration form
3. **accounts/urls.py** - URL configuration
4. **templates/accounts/login.html** - Login page
5. **templates/accounts/register.html** - Registration page
6. **templates/accounts/profile.html** - Profile page

### Settings Updated:
```python
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'jobs:home'
LOGOUT_REDIRECT_URL = 'jobs:home'
```

### Navigation Updated:
- Changed from `/admin/login/` to `{% url 'accounts:login' %}`
- Added profile link in dropdown
- Changed logout to custom URL
- Only show admin link for staff users

---

## ✨ Features Added

### Security:
- ✅ CSRF protection on all forms
- ✅ Password validation
- ✅ Session management
- ✅ Required authentication for protected views

### User Experience:
- ✅ Beautiful, responsive design
- ✅ Real-time form validation
- ✅ Success/error messages
- ✅ Auto-redirect after actions
- ✅ Remember login state

### Functionality:
- ✅ User registration
- ✅ User login/logout
- ✅ Profile management
- ✅ Application tracking
- ✅ Job posting (for authenticated users)

---

## 📱 How to Use

### To Login:
1. Go to http://127.0.0.1:8000/
2. Click **"Login / Register"** in top right
3. Enter username and password
4. Click **"Sign In"**

### To Register:
1. Go to http://127.0.0.1:8000/
2. Click **"Login / Register"** in top right
3. Click **"Register here"** link
4. Fill in the form
5. Click **"Create Account"**
6. You'll be automatically logged in!

### To View Profile:
1. Login to your account
2. Click your username in top right
3. Select **"My Profile"**

### To Logout:
1. Click your username in top right
2. Click **"Logout"**

---

## 🎯 What's Fixed

### Before:
- ❌ Login button redirected to `/admin/login/`
- ❌ No custom registration page
- ❌ No user profile page
- ❌ Admin-style login interface

### After:
- ✅ Beautiful custom login page
- ✅ Full registration system
- ✅ User profile management
- ✅ Modern, user-friendly interface
- ✅ Proper logout functionality
- ✅ Demo accounts shown on login page

---

## 🚀 Ready to Use!

The authentication system is now complete and working. Users can:
- Register new accounts
- Login with credentials
- Manage their profiles
- Access all job portal features

**Server is running at:** http://127.0.0.1:8000/

**Try it now:**
1. Visit http://127.0.0.1:8000/accounts/login/
2. Use **admin / admin123** or **demo_user / demo123**
3. Or register a new account!

---

**All authentication features are fully functional! 🎉**
