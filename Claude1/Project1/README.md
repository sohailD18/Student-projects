# JobPortal - Job Posting & Resume Upload Application

A complete full-stack job portal application built with Django (Backend) and HTML/CSS/JavaScript (Frontend) with SQLite database.

## Features

### For Job Seekers:
- Browse and search for jobs by category, type, location, and experience level
- View detailed job descriptions and requirements
- Submit job applications with resume upload
- Save jobs for later viewing
- Track application status
- Download submitted resumes

### For Employers:
- Post new job listings with detailed information
- Manage posted jobs (view, edit, delete)
- Review and manage job applications
- Update application status (Pending, Reviewed, Shortlisted, Interviewed, Offered, Hired, Rejected)
- Add internal notes for applications
- View job statistics (views, applications count)

### Admin Features:
- Full Django Admin interface
- Manage job categories
- Manage all jobs and applications
- Advanced filtering and search
- Date-based hierarchy views

## Tech Stack

**Backend:**
- Django 5.2+
- Python 3.x
- SQLite Database

**Frontend:**
- HTML5
- CSS3
- JavaScript (Vanilla)
- Bootstrap 5.3
- Font Awesome Icons

## Project Structure

```
jobportal/
├── jobportal/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── jobs/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Form classes
│   ├── admin.py           # Admin configuration
│   └── urls.py            # App URLs
├── templates/             # HTML templates
│   ├── base.html
│   └── jobs/
│       ├── home.html
│       ├── job_list.html
│       ├── job_detail.html
│       ├── post_job.html
│       ├── my_applications.html
│       ├── my_posted_jobs.html
│       ├── saved_jobs.html
│       └── job_applicants.html
├── static/                # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── media/                 # Uploaded files (resumes)
├── db.sqlite3            # SQLite database
└── manage.py
```

## Installation

1. **Clone the repository or navigate to the project directory**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run migrations to create the database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create a superuser for admin access:**
```bash
python manage.py createsuperuser
```

5. **Run the development server:**
```bash
python manage.py runserver
```

6. **Access the application:**
- Application: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

## Usage Guide

### Initial Setup

1. **Create Job Categories:**
   - Login to admin panel
   - Navigate to "Job Categories"
   - Add categories (e.g., "Software Development", "Marketing", "Design")

2. **Create Test Users:**
   - Use Django admin to create users
   - Users can login via `/admin/login/`

3. **Post Sample Jobs:**
   - Login as a user
   - Navigate to "Post a Job"
   - Fill in job details and submit

### For Job Seekers

1. Browse jobs on the home page or job listing page
2. Use filters to narrow down search results
3. Click on a job to view details
4. Login to apply for jobs
5. Submit application with resume (PDF/DOC/DOCX, max 5MB)
6. Track applications in "My Applications"

### For Employers

1. Login to your account
2. Click "Post a Job" to create a new listing
3. Fill in job details (title, company, description, requirements, salary, etc.)
4. View applications in "My Posted Jobs"
5. Review applications and update status
6. Download resumes from applicants

## Database Models

### JobCategory
- Categories for organizing jobs
- Fields: name, description, created_at

### Job
- Job listings with comprehensive details
- Fields: title, company, location, category, job_type, experience_level, description, requirements, salary_min, salary_max, is_salary_visible, status, created_by, created_at, updated_at, application_deadline, views_count

### JobApplication
- Applications submitted by job seekers
- Fields: job, applicant_name, email, phone, cover_letter, resume, linkedin_profile, portfolio_url, expected_salary, status, applied_at, updated_at, notes

### SavedJob
- Jobs saved by users for later viewing
- Fields: user, job, created_at

## Features Details

### Job Types
- Full Time
- Part Time
- Contract
- Internship
- Remote

### Experience Levels
- Entry Level
- Mid Level
- Senior Level
- Executive

### Application Status
- Pending
- Reviewed
- Shortlisted
- Interviewed
- Offered
- Rejected
- Hired

### File Upload
- Supported formats: PDF, DOC, DOCX
- Maximum file size: 5MB
- Stored in: media/resumes/YYYY/MM/

## Customization

### Styling
- Edit `static/css/style.css` to customize the appearance
- Uses Bootstrap 5 for responsive design
- Custom CSS variables for easy theming

### Forms
- Modify `jobs/forms.py` to add validation or custom fields
- Form widgets can be customized in the Meta class

### Views
- All views are in `jobs/views.py`
- Add new views and URLs as needed

## Security Considerations

- CSRF protection enabled for all forms
- File upload validation (type and size)
- User authentication required for sensitive operations
- Permission checks for job management
- SQL injection prevention through Django ORM

## Future Enhancements

- User registration system (not using admin login)
- Email notifications for applications
- Advanced search with filters
- Job recommendation system
- Profile building for job seekers
- Company profiles and pages
- Application tracking with email updates
- Chat/messaging between employers and applicants

## Troubleshooting

### Static files not loading:
```bash
python manage.py collectstatic
```

### Media files not uploading:
- Ensure `MEDIA_ROOT` and `MEDIA_URL` are correctly set in `settings.py`
- Check directory permissions

### Database errors:
```bash
python manage.py makemigrations
python manage.py migrate
```

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please create an issue in the repository or contact the development team.

---

**Developed with Django 5.2 and modern web technologies**
