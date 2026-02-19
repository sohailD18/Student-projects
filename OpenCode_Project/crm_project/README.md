# Customer Relationship Management (CRM) System

A Django-based CRM system for managing customer relationships, tracking deals, logging activities, and managing tasks.

## Features

- **Contact Management**: Store and manage contact information for customers and prospects
- **Company Management**: Organize contacts by company with company details
- **Deal Tracking**: Track sales opportunities through the pipeline
- **Activity Logging**: Log calls, emails, meetings, and notes
- **Task Management**: Create and track tasks with due dates
- **Pipeline Visualization**: Visual pipeline with drag-and-drop functionality
- **Reporting**: Sales reports and analytics dashboard
- **Lead Management**: Track and convert leads

## Tech Stack

- Django 5.x
- Python 3.8+
- SQLite (default) / PostgreSQL (production)
- Bootstrap 5 for styling
- Chart.js for analytics

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install django pillow django-crispy-forms crispy-bootstrap5
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run server:
```bash
python manage.py runserver
```

## Project Structure

```
crm_project/
├── manage.py
├── crm/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── contacts/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
├── deals/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
├── activities/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
├── templates/
│   ├── base.html
│   └── ...
└── static/
    └── crm/
```

## Models

### Contact
- Name, email, phone, address
- Company association
- Job title and department
- Status (Lead, Customer, etc.)
- Tags and notes

### Company
- Company name and logo
- Industry and company size
- Contact information
- Website and social links
- Related contacts

### Deal
- Deal name and value
- Pipeline stage
- Expected close date
- Associated contact/company
- Deal owner

### Pipeline
- Pipeline stages
- Stage order and color
- Win probability

### Activity
- Activity type (Call, Email, Meeting, Note)
- Related contact/company/deal
- Activity date and duration
- Description

### Task
- Task title and description
- Due date and priority
- Related contact/company/deal
- Task status
