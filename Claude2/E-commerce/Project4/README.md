# E-Commerce Customer Sentiment Analysis

A full-stack web application for analyzing customer sentiment on product reviews using Django, TextBlob, and Chart.js with **User Authentication**.

## Features

1. **User Authentication**
   - User registration with validation
   - Secure login/logout
   - Demo credentials for quick testing
   - Protected routes (login required)

2. **Review Submission Form**
   - Product category selection
   - Review text input with character counter
   - Interactive star rating system
   - Automatic sentiment analysis on submission

3. **Sentiment Analysis**
   - Powered by TextBlob NLP library
   - Classifies reviews as Positive, Neutral, or Negative
   - Calculates sentiment polarity scores

4. **Seller Dashboard**
   - Welcome banner with user name
   - Total reviews count
   - Average rating display
   - Sentiment distribution (Positive/Neutral/Negative counts)
   - Interactive Pie Chart for sentiment distribution
   - Bar Chart for ratings frequency
   - Recent reviews list with color-coded sentiment badges
   - Real-time data refresh
   - User menu with logout functionality

5. **Enhanced Design**
   - Modern gradient backgrounds
   - Smooth animations and transitions
   - Responsive mobile-friendly layout
   - User dropdown menus
   - Field icons for better UX
   - Loading states and spinners
   - Password strength indicators
   - Copy-to-clipboard demo credentials

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite
- **NLP/AI**: TextBlob
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Visualization**: Chart.js
- **Authentication**: Django's built-in auth system
- **API**: RESTful API with JSON responses

## Project Structure

```
Project4/
├── config/                 # Django project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── sentiment_analysis/     # Django app
│   ├── __init__.py
│   ├── models.py          # Review model with auto-sentiment analysis
│   ├── views.py           # Form handling, auth & API endpoints
│   ├── urls.py            # App URL routing
│   ├── admin.py           # Admin configuration
│   ├── apps.py
│   ├── management/        # Management commands
│   │   └── commands/
│   │       └── create_demo_user.py
│   ├── templates/
│   │   ├── login.html     # Login page with demo credentials
│   │   ├── register.html  # Registration page
│   │   ├── index.html     # Review submission form
│   │   └── dashboard.html # Analytics dashboard
│   └── static/
│       ├── css/
│       │   └── style.css  # Modern responsive styling
│       └── js/
│           ├── script.js  # Form submission logic
│           └── dashboard.js # Dashboard charts
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download TextBlob Corpus

```bash
python -m textblob.download_corpora
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Demo User (Recommended)

```bash
python manage.py create_demo_user
```

This creates a demo user with:
- **Username**: `demo`
- **Password**: `demo123`

Or manually create a superuser:

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

- **Login Page**: http://127.0.0.1:8000/login/
- **Dashboard**: http://127.0.0.1:8000/ (redirects to login if not authenticated)
- **Submit Review**: http://127.0.0.1:8000/submit/
- **Register**: http://127.0.0.1:8000/register/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Demo Credentials

Use these credentials to quickly test the application:

```
Username: demo
Password: demo123
```

These are also displayed on the login page with copy-to-clipboard buttons.

## API Endpoints

### Authentication Routes
- `GET /login/` - Login page
- `POST /login/` - Login form submission
- `GET /register/` - Registration page
- `POST /register/` - Registration form submission
- `GET /logout/` - Logout user

### Page Routes (Authentication Required)
- `GET /` - Analytics dashboard page
- `GET /submit/` - Review submission form page

### API Routes
- `POST /api/submit-review/` - Submit a new review (JSON, requires auth)
- `GET /api/dashboard-data/` - Get dashboard statistics (JSON, requires auth)
- `GET /api/recent-reviews/` - Get recent reviews (JSON, requires auth)

## Usage

### 1. Login or Register

**Option A: Use Demo Credentials**
1. Go to http://127.0.0.1:8000/login/
2. Click the copy buttons next to demo credentials
3. Paste and login

**Option B: Create New Account**
1. Go to http://127.0.0.1:8000/register/
2. Fill in username, email, and password
3. Submit the form
4. Login with your new credentials

### 2. Submit a Review

1. Click "New Review" or go to `/submit/`
2. Select a product category
3. Write your review
4. Select a star rating (1-5)
5. Click "Submit Review"
6. View the sentiment analysis result instantly
7. Navigate to dashboard to see updated statistics

### 3. View Analytics Dashboard

1. Access dashboard at `/` or click "Dashboard"
2. View real-time statistics:
   - Welcome banner with your name
   - Total reviews, average rating
   - Sentiment breakdown (Positive/Neutral/Negative)
   - Visual charts (pie chart for sentiment, bar chart for ratings)
   - Recent reviews list with color-coded badges
3. Click "Refresh" to update data
4. Use user menu (top right) to logout

## Authentication Features

- **Password Security**: Passwords are hashed using Django's built-in password hashing
- **Session Management**: Secure session-based authentication
- **Protected Routes**: All main pages require login
- **User-Specific Reviews**: Each review is associated with the logged-in user
- **Logout**: Secure logout with session cleanup

## Design Enhancements

- **Gradient Backgrounds**: Beautiful purple gradient theme
- **User Menu**: Dropdown menu with user info and logout
- **Welcome Banner**: Personalized greeting on dashboard
- **Icons Throughout**: SVG icons for better visual hierarchy
- **Loading States**: Animated spinners for better UX
- **Password Strength**: Real-time password strength indicator
- **Copy Buttons**: One-click copy for demo credentials
- **Smooth Transitions**: All interactions have smooth animations
- **Responsive Design**: Works on desktop, tablet, and mobile

## Security Notes

- The app uses Django's built-in authentication system
- Passwords are never stored in plain text
- CSRF protection is enabled
- All API endpoints require authentication
- In production, change `SECRET_KEY` and set `DEBUG = False`

## License

MIT License
