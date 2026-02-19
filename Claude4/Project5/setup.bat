@echo off
echo ==========================================
echo AI Trip Planner - Quick Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and add it to your PATH
    pause
    exit /b 1
)

echo [1/7] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/7] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/7] Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed
    pause
    exit /b 1
)

echo [5/7] Seeding sample locations...
python manage.py seed_locations
if errorlevel 1 (
    echo WARNING: Location seeding failed (optional)
)

echo [6/7] Training AI model...
python manage.py train_model
if errorlevel 1 (
    echo ERROR: Model training failed
    pause
    exit /b 1
)

echo [7/7] Creating superuser (optional)...
echo.
echo You can create a superuser later by running: python manage.py createsuperuser
echo.

echo ==========================================
echo Setup Completed Successfully!
echo ==========================================
echo.
echo To start the server:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run server: python manage.py runserver
echo   3. Open browser: http://127.0.0.1:8000/
echo.

pause
