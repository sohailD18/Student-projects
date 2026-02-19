# GovExamPortal - Government Examination Information and Aspirant Support System

A Django-powered web application for government job aspirants that provides comprehensive exam information and AI-powered personalized recommendations.

## Features

- **Exam Database**: Comprehensive information on UPSC, SSC, Banking, Railways, State PSC, and Defence examinations
- **Smart Recommendations**: AI-powered exam suggestions based on your profile (age, qualification, preferences)
- **Advanced Search**: Filter exams by type, qualification, age limit, and keywords
- **User Profiles**: Create and manage your aspirant profile for personalized experience
- **Exam Details**: View complete syllabus, eligibility criteria, important dates, and official links
- **Mobile Responsive**: Fully responsive design using Bootstrap 5
- **Admin Panel**: Easy-to-use Django admin for managing exams and user profiles

## Tech Stack

- **Backend**: Django 4.2+ (Python)
- **Database**: SQLite (default, easily upgradable to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5 (CDN)
- **AI/Logic**: Python-based recommendation engine (rule-based)

## Project Structure

```
GovExamPortal/
├── GovExamPortal/          # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py
├── core/                   # Core app (home, about, search)
│   ├── views.py
│   ├── urls.py
│   └── templates/core/
├── exams/                  # Exams app
│   ├── models.py           # Exam model
│   ├── views.py            # Exam list, detail views
│   ├── urls.py
│   └── templates/exams/
├── users/                  # Users app
│   ├── models.py           # UserProfile model
│   ├── views.py            # Dashboard, profile, recommendations
│   ├── signals.py          # Auto-create UserProfile
│   ├── urls.py
│   └── templates/users/
├── templates/              # Base templates
│   ├── base.html
│   └── registration/
├── static/                 # Static files (optional)
├── media/                  # User uploaded files (optional)
├── manage.py
├── requirements.txt
└── seed_data.py           # Sample data script
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project** to your local machine:
   ```bash
   cd Project8
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations** to create the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser** for admin access:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create username and password.

5. **Seed sample exam data** (optional but recommended):
   ```bash
   python manage.py shell < seed_data.py
   ```

   Or manually from Python shell:
   ```bash
   python manage.py shell
   >>> exec(open('seed_data.py').read())
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Website: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage Guide

### For Aspirants

1. **Register**: Create an account at `/users/register/`
2. **Complete Profile**: Fill in your age, qualification, category, and preferences
3. **View Dashboard**: See personalized exam recommendations based on your profile
4. **Browse Exams**: Explore all available exams with filters
5. **View Details**: Check eligibility, syllabus, dates for each exam

### For Administrators

1. **Access Admin**: Login at `/admin/`
2. **Manage Exams**: Add, edit, delete exam information
3. **View Users**: See registered users and their profiles
4. **Track Progress**: Monitor user registrations and profile completions

## URL Structure

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/about/` | About page |
| `/search/` | Search exams |
| `/exams/` | Browse all exams |
| `/exams/<id>/` | Exam detail page |
| `/users/register/` | User registration |
| `/users/profile/` | Profile management |
| `/users/dashboard/` | User dashboard |
| `/users/my-exams/` | Personalized recommendations |
| `/admin/` | Django admin panel |

## Smart Recommendation Algorithm

The AI recommendation engine considers:

1. **Age Matching**: Compares user's age with exam age limits
2. **Qualification Matching**: Verifies educational qualification requirements
3. **Preference Scoring**: Boosts scores for preferred exam types
4. **Urgency Bonus**: Prioritizes exams with approaching deadlines
5. **Proximity Bonus**: Scores based on how close user's age is to exam limits

### Example Logic

```python
# User Profile
Age: 25 years
Qualification: Graduate
Preferences: UPSC, SSC

# Recommended Exams:
1. Civil Services (UPSC) - Age: 21-32, Grad ✓, Preference ✓
2. SSC CGL - Age: 18-30, Grad ✓, Preference ✓
3. IBPS PO - Age: 20-30, Grad ✓, Preference ✗ (lower score)
```

## Models

### Exam Model

- `title`: Exam name
- `exam_type`: UPSC, SSC, Banking, Railways, State PSC, Defence
- `age_limit_min` & `age_limit_max`: Age range
- `educational_qualification`: Required qualification
- `application_start_date`, `application_end_date`, `exam_date`: Important dates
- `syllabus_text`: Detailed syllabus
- Methods: `is_upcoming()`, `is_application_open()`, `days_until_exam()`

### UserProfile Model

- `user`: OneToOne link to Django User
- `date_of_birth`: For age calculation
- `category`: General/OBC/SC/ST/EWS/PWD
- `highest_qualification`: 10th, 12th, Diploma, Graduate, etc.
- `preferred_exam_types`: Comma-separated preferences
- Methods: `age`, `get_preferred_exam_types_list()`, `is_eligible_for_exam()`

## Frontend Technologies

- **Bootstrap 5**: Responsive UI framework
- **Bootstrap Icons**: Icon library
- **Custom CSS**: Additional styling for cards, badges, hover effects

## Development Notes

### Extending the Project

1. **Add Email Notifications**: Configure Django email settings for deadline alerts
2. **Enhanced AI**: Integrate scikit-learn for ML-based recommendations
3. **Study Materials**: Add file upload for PDF notes
4. **Discussion Forum**: Add comments/discussion feature for each exam
5. **Exam Results**: Track and display examination results
6. **Mock Tests**: Add online quiz functionality
7. **Mobile App**: Convert to Django REST Framework for mobile API

### Database Migration

To switch to PostgreSQL or MySQL:

1. Install the database driver (`psycopg2` or `mysqlclient`)
2. Update `DATABASES` in `GovExamPortal/settings.py`
3. Run `python manage.py migrate` on the new database

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   python manage.py runserver 8080
   ```

2. **Migration errors**:
   ```bash
   python manage.py makemigrations core exams users
   python manage.py migrate
   ```

3. **Static files not loading**:
   ```bash
   python manage.py collectstatic
   ```

4. **Signals not working**: Ensure `users.apps.UsersConfig` properly loads signals

## Contributing

This is an educational project. Feel free to:
- Add new features
- Improve the recommendation algorithm
- Enhance UI/UX
- Add more exam categories
- Create unit tests

## License

This project is open for educational purposes. Feel free to use, modify, and distribute.

## Support

For questions or issues:
- Check Django documentation: https://docs.djangoproject.com/
- Bootstrap docs: https://getbootstrap.com/docs/5.3/

## Future Enhancements

- [ ] Email notifications for exam deadlines
- [ ] Calendar integration (Google/Outlook)
- [ ] Study planner and scheduler
- [ ] Community forum and discussion boards
- [ ] Mock test series with performance analytics
- [ ] Video tutorials and guidance section
- [ ] Success stories and interview tips
- [ ] Mobile application (React Native/Flutter)
- [ ] Regional language support (Hindi, Tamil, etc.)
- [ ] SMS alerts for important notifications

---

**Built with Django 4.2, Bootstrap 5, and Python 3.8+**

**Version**: 1.0.0
**Last Updated**: February 2025
