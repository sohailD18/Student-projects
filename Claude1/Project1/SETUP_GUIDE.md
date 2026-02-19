# JobPortal - Quick Setup Guide

## Project Status: ✅ COMPLETE & READY TO USE

Your Job Posting & Resume Upload application is now fully built and ready!

---

## 🚀 Quick Start

### 1. Server is Already Running!
The development server is currently running in the background.
- **Application URL:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### 2. Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Demo User Account:**
- Username: `demo_user`
- Password: `demo123`

---

## 📊 What's Included

### ✅ Complete Features

**Job Seekers:**
- Browse jobs with advanced filters
- Search by keyword, location, category
- View detailed job listings
- Apply with resume upload
- Save jobs for later
- Track application status

**Employers:**
- Post new job listings
- Manage posted jobs
- Review applications
- Update application status
- Download resumes
- Add internal notes

**Admin Panel:**
- Full Django admin interface
- Manage categories, jobs, applications
- Advanced filtering and search
- View statistics

---

## 📁 Project Structure

```
jobportal/
├── jobportal/              # Django project settings
├── jobs/                   # Main application
│   ├── models.py          # Database models (Job, JobApplication, SavedJob)
│   ├── views.py           # All view functions
│   ├── forms.py           # Form classes
│   ├── admin.py           # Admin configuration
│   └── urls.py            # App URL routing
├── templates/             # HTML templates (8 pages)
│   ├── base.html         # Base template
│   └── jobs/             # App-specific templates
├── static/               # CSS & JavaScript files
│   ├── css/style.css    # Custom styling
│   └── js/main.js       # JavaScript functionality
├── media/               # Uploaded resumes
├── db.sqlite3          # Database (with sample data!)
└── manage.py          # Django management script
```

---

## 🗄️ Database Models

### 1. JobCategory
- Categories for organizing jobs
- 10 categories pre-loaded

### 2. Job
- Complete job listings
- 6 sample jobs created
- Fields: title, company, location, description, requirements, salary, etc.

### 3. JobApplication
- Applications with resume upload
- Status tracking (Pending → Hired)
- Cover letter and notes

### 4. SavedJob
- Bookmark jobs for later

---

## 🎨 Frontend Features

### Pages Created:
1. **Home Page** - Featured jobs, statistics, search
2. **Job Listing** - Browse and filter all jobs
3. **Job Detail** - Full job info + application form
4. **Post Job** - Create new job listings
5. **My Applications** - Track submitted applications
6. **My Posted Jobs** - Manage your job postings
7. **Saved Jobs** - View bookmarked jobs
8. **Job Applicants** - Review applications (for employers)

### Styling:
- Bootstrap 5.3 for responsive design
- Custom CSS with modern gradients
- Smooth animations and transitions
- Mobile-friendly layout

### JavaScript:
- Dynamic form validation
- AJAX form submissions
- Save/unsave jobs
- Status updates
- File upload handling

---

## 🔧 Available Commands

### Setup & Data:
```bash
# Create job categories
python manage.py setup_categories

# Create sample jobs
python manage.py setup_sample_jobs

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Development:
```bash
# Start server
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

---

## 📝 Sample Data Included

### Job Categories (10):
- Software Development
- Data Science
- Design
- Marketing
- Sales
- Finance
- Human Resources
- Engineering
- Customer Service
- Management

### Sample Jobs (6):
1. Senior Software Engineer - TechCorp Inc.
2. Data Scientist - DataDriven Analytics
3. UI/UX Designer - Creative Studio
4. Marketing Manager - GrowthHub
5. Frontend Developer Intern - StartUp Labs
6. Product Manager - InnovateTech

### Users (2):
1. admin (Admin account)
2. demo_user (Regular user)

---

## 🌐 Access Points

### Main Application:
- **Home:** http://127.0.0.1:8000/
- **Browse Jobs:** http://127.0.0.1:8000/jobs/
- **Post Job:** http://127.0.0.1:8000/jobs/post/
- **My Applications:** http://127.0.0.1:8000/applications/
- **My Jobs:** http://127.0.0.1:8000/my-jobs/
- **Saved Jobs:** http://127.0.0.1:8000/saved-jobs/

### Admin Panel:
- **Admin Login:** http://127.0.0.1:8000/admin/
- **Manage Jobs:** /admin/jobs/job/
- **Manage Applications:** /admin/jobs/jobapplication/
- **Manage Categories:** /admin/jobs/jobcategory/

---

## 🎯 How to Use

### For Job Seekers:
1. Visit homepage
2. Browse or search for jobs
3. Click on a job to view details
4. Login (or register via admin)
5. Apply with resume (PDF/DOC/DOCX, max 5MB)
6. Track status in "My Applications"

### For Employers:
1. Login to your account
2. Click "Post a Job"
3. Fill in job details
4. Submit the job listing
5. View applications in "My Posted Jobs"
6. Review and update status

---

## 🔒 Security Features

- ✅ CSRF protection on all forms
- ✅ File upload validation (type & size)
- ✅ User authentication required
- ✅ Permission checks for actions
- ✅ SQL injection prevention
- ✅ XSS protection

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:
- Django >= 5.2.0
- Pillow >= 10.0.0

---

## 🐛 Troubleshooting

### Server not running?
```bash
python manage.py runserver
```

### Static files not loading?
```bash
python manage.py collectstatic
```

### Database issues?
```bash
python manage.py migrate
```

### Reset everything?
```bash
# Delete database
rm db.sqlite3

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Setup data
python manage.py setup_categories
python manage.py setup_sample_jobs
```

---

## 📱 Screenshots to Try

1. **Home Page:** http://127.0.0.1:8000/
   - View featured jobs
   - See statistics
   - Quick search

2. **Job Listing:** http://127.0.0.1:8000/jobs/
   - Filter by category, type, location
   - Search functionality
   - Pagination

3. **Job Detail:** http://127.0.0.1:8000/jobs/1/
   - Full job description
   - Application form
   - Save job button

4. **Admin Panel:** http://127.0.0.1:8000/admin/
   - Login with admin/admin123
   - Manage all data
   - View statistics

---

## 🎉 Success!

Your JobPortal application is complete and ready to use! The server is running, sample data is loaded, and all features are functional.

**Start exploring now: http://127.0.0.1:8000/**

---

## 📞 Next Steps

1. **Customize the design** - Edit `static/css/style.css`
2. **Add more fields** - Modify `jobs/models.py`
3. **Create custom views** - Add to `jobs/views.py`
4. **Add email notifications** - Setup Django email backend
5. **Deploy** - Use Django deployment guides for production

---

**Enjoy your new JobPortal application! 🚀**
