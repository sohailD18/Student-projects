# Quick Start Guide - TimeBank

## Fast Setup (5 Minutes)

### 1. Run the Server
```bash
python manage.py runserver
```

### 2. Create Admin Account
Open a new terminal and run:
```bash
python manage.py createsuperuser
```
Follow the prompts to create username, email, and password.

### 3. Access the Application

**Main Site**: http://127.0.0.1:8000/
**Admin Panel**: http://127.0.0.1:8000/admin/

### 4. Register a Test User

1. Click "Sign Up" in the navigation
2. Fill in the registration form
3. Complete your profile with:
   - Skills: "gardening, cooking, cleaning"
   - Availability: "Weekends"
   - Bio: "I love helping my community!"

### 5. Test the Workflow

**As User A (Helper)**:
- Browse Tasks
- Apply for a task
- Wait for assignment

**As User B (Creator)**:
- Post a Task
  - Title: "Need Help with Gardening"
  - Description: "Looking for someone to help with my garden"
  - Required Skills: "gardening"
  - Duration: 2 hours
- Assign helper (manual approval not implemented, first to apply gets it)
- Mark task as complete

**Verify**:
- Credits transferred from creator to helper
- Both users can leave reviews
- Badges awarded for activity

## Common Commands

```bash
# Run server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Reset database (delete everything)
rm db.sqlite3
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell
```

## Default Configuration

- **Database**: SQLite (db.sqlite3)
- **Port**: 8000
- **Debug Mode**: Enabled
- **Static Files**: /static/
- **Media Files**: /media/

## Next Steps

1. **Customize the home page**: Edit `templates/home.html`
2. **Add more badges**: Via admin panel or migrations
3. **Modify skill matching**: Update `tasks/models.py` -> `matches_user_skills()`
4. **Change styling**: Edit `templates/base.html` CSS section
5. **Add email notifications**: Configure Django email backend in settings.py

## Troubleshooting

**Port 8000 already in use?**
```bash
python manage.py runserver 8080
```

**Need to reset everything?**
```bash
rm db.sqlite3
rm -r media/*
python manage.py migrate
```

**Images not showing?**
- Check that media directory exists
- Verify MEDIA_URL in settings.py

## Key Pages to Visit

- [Home](http://127.0.0.1:8000/)
- [Browse Tasks](http://127.0.0.1:8000/tasks/)
- [Leaderboard](http://127.0.0.1:8000/gamification/leaderboard/)
- [Admin Panel](http://127.0.0.1:8000/admin/)
