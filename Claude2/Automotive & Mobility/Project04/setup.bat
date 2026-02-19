@echo off
REM Intelligent Route Planner - Setup Script for Windows
echo ========================================
echo Intelligent Route Planning System
echo Setup Script
echo ========================================
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Run migrations
echo.
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To create an admin user, run:
echo   python manage.py createsuperuser
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo Then open your browser to:
echo   http://127.0.0.1:8000/
echo.
pause
