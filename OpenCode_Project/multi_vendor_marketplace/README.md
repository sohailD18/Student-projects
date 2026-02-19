# Multi-Vendor Marketplace

A Django-based multi-vendor e-commerce platform where multiple sellers can register, manage their products, process orders, and receive payouts.

## Features

- **Vendor Registration**: Multiple vendors can register and create their stores
- **Product Management**: Vendors can add, edit, and manage their products
- **Order Processing**: Complete order workflow from cart to delivery
- **Commission Tracking**: Admin can track commissions on sales
- **Vendor Dashboard**: Comprehensive dashboard for vendors to monitor their business
- **Payouts**: Automated payout system for vendors
- **Reviews**: Customers can review products and vendors

## Tech Stack

- Django 5.x
- Python 3.8+
- SQLite (default) / PostgreSQL (production)
- Bootstrap 5 for styling

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
multi_vendor_marketplace/
├── manage.py
├── marketplace/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── vendor/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── migrations/
├── templates/
│   ├── base.html
│   └── vendor/
└── static/
    └── marketplace/
```

## Models

### Vendor
- User profile extension for vendors
- Store name, description, logo
- Bank account information for payouts
- Commission rate configuration

### Product
- Product details (name, description, price)
- Inventory management
- Product images
- Category assignment
- Vendor assignment

### Order
- Customer order tracking
- Order status management
- Payment integration

### Commission
- Tracks commission per sale
- Calculates admin revenue
- Payout reference

### Payout
- Vendor payout requests
- Payment status tracking
- Transaction history
