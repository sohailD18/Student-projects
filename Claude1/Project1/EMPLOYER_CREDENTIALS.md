# Employer Login Credentials

This document contains the login credentials for all employer accounts.

## Employer Accounts

### 1. InnovateTech
- **Username:** `innovatetech`
- **Password:** `Innovate123`
- **Email:** contact@innovatetech.com
- **Dashboard:** http://127.0.0.1:8000/accounts/employer/

### 2. GrowthHub
- **Username:** `growthhub`
- **Password:** `Growth123`
- **Email:** contact@growthhub.com
- **Dashboard:** http://127.0.0.1:8000/accounts/employer/

### 3. Creative Studio
- **Username:** `creativestudio`
- **Password:** `Creative123`
- **Email:** contact@creativestudio.com
- **Dashboard:** http://127.0.0.1:8000/accounts/employer/

### 4. DataDriven Analytics
- **Username:** `datadriven`
- **Password:** `Data123`
- **Email:** contact@datadriven.com
- **Dashboard:** http://127.0.0.1:8000/accounts/employer/

### 5. TechCorp Inc.
- **Username:** `techcorp`
- **Password:** `TechCorp123`
- **Email:** contact@techcorp.com
- **Dashboard:** http://127.0.0.1:8000/accounts/employer/

---

## How It Works

Each employer account is linked to their respective company. When they log in:

1. They will be redirected to their employer dashboard at `/accounts/employer/`
2. They will see ONLY their own jobs and applications
3. They cannot see jobs or applications from other companies
4. They can:
   - View their posted jobs
   - See applications for their jobs
   - Update application statuses
   - Post new jobs
   - Delete their own jobs

## Security Features

- All employer accounts are protected with `@login_required` decorator
- Only users with `user_type='employer'` can access the employer dashboard
- Each employer sees only their own data (jobs and applications)
- Job seekers cannot access employer dashboard

---

## Test Accounts Reference

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Dashboard:** http://127.0.0.1:8000/admin-panel/
- **Access:** Can see all jobs, applications, and manage all data

### Job Seeker Account
- **Username:** `demo1`
- **Password:** `user1@123`
- **Dashboard:** http://127.0.0.1:8000/ (home page)
- **Access:** Can browse jobs, apply, and save jobs

---

**Note:** If you need to reset any password or create new employer accounts, you can run:
```bash
python manage.py setup_employer_accounts
```
