@echo off
REM FinRisk AI - Quick Start Script
REM This script will set up and run the FinRisk AI application

echo ========================================
echo FinRisk AI - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 2: Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)
echo Database setup complete!
echo.

echo Step 3: Starting development server...
echo.
echo ========================================
echo FinRisk AI is now running!
echo Open your browser to: http://127.0.0.1:8000/
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause
