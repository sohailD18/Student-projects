# TimeBank - Community Time Exchange Platform

A full-stack web application where users exchange services using time credits instead of money. Built with Django, Bootstrap 5, and SQLite.

## Features

### Core Functionality
- **User Profiles**: Custom profiles with skills, availability, bio, and credit balance tracking
- **Task Management**: Create, browse, apply for, and complete tasks
- **Skill Matching**: System highlights tasks that match your listed skills
- **Credit System**: Time-based currency where 1 hour = 1 credit
- **Reviews & Ratings**: Feedback system with 1-5 star ratings
- **Gamification**: Earn badges for completing tasks, earning hours, and giving reviews
- **Leaderboard**: Top 10 users by credit balance

### User Features
- Sign up with custom profile (skills, availability, bio, profile image)
- Browse and search tasks by skill requirements
- Apply for open tasks matching your skills
- Post tasks and hire helpers with time credits
- Leave and receive reviews after task completion
- Track credit earnings and spending
- Earn badges and climb the leaderboard

## Tech Stack

- **Backend**: Django 5.2.11 (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite (default Django)
- **Styling**: Bootstrap 5 (via CDN)
- **Icons**: FontAwesome 6 (via CDN)

## Project Structure

```
timebank_project/
├── timebank_project/          # Main project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py              # Main URL routing
│   ├── views.py             # Home page view
│   └── admin.py            # Custom admin site
├── users/                   # User authentication & profiles
│   ├── models.py            # Profile model
│   ├── views.py             # Register, login, profile views
│   ├── forms.py             # User & profile forms
│   ├── urls.py              # User routing
│   └── signals.py           # Auto-create profiles
├── tasks/                   # Task management
│   ├── models.py            # Task model
│   ├── views.py             # CRUD & task actions
│   ├── forms.py             # Task forms
│   └── urls.py              # Task routing
├── credits/                 # Credit transactions
│   ├── models.py            # Transaction model
│   ├── views.py             # Wallet view
│   └── urls.py              # Credits routing
├── reviews/                 # Reviews & ratings
│   ├── models.py            # Review model
│   ├── views.py             # Create review view
│   ├── forms.py             # Review forms
│   └── urls.py              # Review routing
├── gamification/            # Badges & leaderboard
│   ├── models.py            # Badge & UserBadge models
│   ├── views.py             # Leaderboard & badges views
│   └── urls.py              # Gamification routing
├── templates/               # HTML templates
│   ├── base.html           # Base template with navbar
│   ├── home.html           # Home page
│   ├── users/              # User templates
│   ├── tasks/              # Task templates
│   ├── credits/            # Credit templates
│   ├── reviews/            # Review templates
│   └── gamification/       # Gamification templates
├── media/                   # User uploads (profile images)
├── static/                  # Static files (CSS, JS)
└── db.sqlite3              # SQLite database
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install django
```

### Step 2: Navigate to Project Directory

```bash
cd timebank_project
```

### Step 3: Run Migrations (Already Applied)

The migrations have already been applied to the database. If you need to reset:

```bash
python manage.py migrate
```

### Step 4: Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 5: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage Guide

### First Time Setup

1. **Create an Admin Account**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Access the Admin Panel**:
   - Go to `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials
   - Manage users, tasks, transactions, and reviews

3. **Register a Regular User**:
   - Visit `http://127.0.0.1:8000/users/register/`
   - Fill in the registration form
   - Your profile will be created automatically

### User Workflow

1. **Complete Your Profile**:
   - Navigate to "My Profile"
   - Add your skills (comma-separated)
   - Set your availability
   - Add a bio and profile image

2. **Browse Tasks**:
   - Go to "Browse Tasks"
   - Filter by skill requirements
   - Green border indicates tasks matching your skills

3. **Apply for Tasks**:
   - Click on a task
   - Click "Apply for Task"
   - Wait for the creator to approve

4. **Post a Task**:
   - Go to "Post Task"
   - Fill in title, description, required skills, and duration
   - Note: You'll pay the estimated credits when task is completed

5. **Complete & Review**:
   - Mark tasks as complete (credits transfer automatically)
   - Leave a review for the other party
   - Earn badges for your activity

### Credit System

- New users start with 0 credits
- Credits are earned by completing tasks
- Credits are spent when your posted tasks are completed
- 1 hour = 1 credit
- View your wallet for transaction history

### Badges

Badges are automatically awarded based on activity:

**Tasks Completed**:
- Helpful Neighbor (5 tasks)
- Community Builder (25 tasks)
- Super Helper (50 tasks)

**Hours Earned**:
- Time Keeper (10 hours)
- Time Lord (50 hours)
- Century Club (100 hours)

**Reviews Given**:
- First Review (1 review)
- Feedback Champion (10 reviews)
- Voice of the Community (50 reviews)

## Key URL Patterns

| Page | URL |
|-------|-----|
| Home | `/` |
| Browse Tasks | `/tasks/` |
| Post Task | `/tasks/create/` |
| My Tasks | `/tasks/my-tasks/` |
| Profile | `/users/profile/` |
| Edit Profile | `/users/profile/edit/` |
| Wallet | `/credits/wallet/` |
| Leaderboard | `/gamification/leaderboard/` |
| Badges | `/gamification/badges/` |
| Login | `/accounts/login/` |
| Register | `/users/register/` |
| Admin | `/admin/` |

## Database Models

### Profile (users)
- `user` (OneToOne to User)
- `skills` (TextField)
- `availability` (CharField)
- `bio` (TextField)
- `profile_image` (ImageField)
- `time_credits_balance` (IntegerField)

### Task (tasks)
- `title` (CharField)
- `description` (TextField)
- `required_skills` (CharField)
- `estimated_duration` (IntegerField)
- `status` (CharField: Open/In Progress/Completed)
- `created_by` (ForeignKey to User)
- `assigned_to` (ForeignKey to User, nullable)
- `created_at`, `updated_at`, `completed_at`

### Transaction (credits)
- `sender` (ForeignKey to User)
- `receiver` (ForeignKey to User)
- `amount` (IntegerField)
- `task` (ForeignKey to Task)
- `timestamp` (DateTimeField)

### Review (reviews)
- `task` (OneToOne to Task)
- `reviewer` (ForeignKey to User)
- `reviewee` (ForeignKey to User)
- `rating` (IntegerField: 1-5)
- `comment` (TextField)
- `created_at` (DateTimeField)

### Badge & UserBadge (gamification)
- `name` (CharField)
- `description` (TextField)
- `badge_type` (CharField)
- `requirement_value` (IntegerField)
- `icon_name` (CharField)

## Customization

### Adding New Badges

1. Access Django Admin
2. Go to "Gamification" -> "Badges"
3. Add a new badge with:
   - Name
   - Description
   - Badge type (tasks_completed, hours_earned, reviews_given)
   - Requirement value
   - Icon name (FontAwesome class)

### Modifying Settings

Edit `timebank_project/settings.py`:
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change to a secure random key
- `ALLOWED_HOSTS`: Add your domain in production
- `DATABASES`: Configure PostgreSQL/MySQL for production

## Development Notes

### Skill Matching Logic
The system matches tasks to users by checking if any required skill (case-insensitive) appears in the user's skills list.

### Credit Validation
Transactions validate that the sender has sufficient credits before completion. The `Transaction.save()` method automatically updates user balances.

### Automatic Profile Creation
Signals automatically create a `Profile` when a new `User` is created. Manual profile creation in views is not necessary.

### Badge Assignment
The `check_and_award_badges()` function is called after:
- Task completion (for both creator and helper)
- Review submission

## Troubleshooting

### Profile Images Not Showing
- Ensure `MEDIA_URL` and `MEDIA_ROOT` are correctly configured in settings.py
- Check that the media directory exists and has proper permissions

### Static Files Not Loading
- Run `python manage.py collectstatic` in production
- Verify `STATIC_URL` and `STATIC_ROOT` settings

### Migrations Not Applying
- Delete `db.sqlite3` and re-run `python manage.py migrate`
- Or use `python manage.py migrate --fake-initial` for existing databases

## License

This project is for educational purposes.

## Credits

Built with Django and Bootstrap 5.
