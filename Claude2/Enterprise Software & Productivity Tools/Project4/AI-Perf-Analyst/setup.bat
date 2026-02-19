@echo off
REM AI Performance Analyst - Setup Script
REM This script helps you set up and run the project

echo ========================================
echo AI Performance Analyst Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://python.org
    pause
    exit /b 1
)

echo Python detected successfully
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Run migrations
echo Creating database...
python manage.py makemigrations
python manage.py migrate
echo.

REM Ask if user wants to create superuser
echo.
echo Do you want to create an admin user? (Y/N)
set /p create_superuser=

if /i "%create_superuser%"=="Y" (
    python manage.py createsuperuser
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Then open: http://127.0.0.1:8000/
echo.
pause
