@echo off
echo Starting Email Marketing Platform...
echo.
echo Access the application at: http://127.0.0.1:8000/
echo Login with: admin / admin123
echo.
echo Press Ctrl+C to stop the server
echo.
venv\Scripts\python.exe manage.py runserver
pause
