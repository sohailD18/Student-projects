# AI-Based Financial Transaction Fraud Detection System
# Project Setup Commands

# Step 1: Create Virtual Environment
python -m venv venv

# Step 2: Activate Virtual Environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Step 3: Install Dependencies
pip install -r requirements.txt

# Step 4: Create Django Project
django-admin startproject fraud_detection .

# Step 5: Create Django App
python manage.py startapp transactions

# Step 6: Apply Migrations
python manage.py makemigrations
python manage.py migrate

# Step 7: Create Superuser (optional)
python manage.py createsuperuser

# Step 8: Generate Synthetic Data
python manage.py generate_transactions --count 1000

# Step 9: Train AI Model
python manage.py train_model

# Step 10: Run Development Server
python manage.py runserver

# Access the application at: http://127.0.0.1:8000/
