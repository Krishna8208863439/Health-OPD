@echo off
title HealthCare Plus - Local Server
echo.
echo ========================================
echo   HealthCare Plus - Starting Server
echo ========================================
echo.

cd /d "%~dp0Smart_Healthcare_System (2)\Smart_Healthcare_System\Enhanced_Healthcare_System"

if not exist app.py (
    echo ERROR: app.py not found. Check project folder structure.
    pause
    exit /b 1
)

echo Installing dependencies (if needed)...
pip install -q flask flask-login werkzeug reportlab 2>nul

echo.
echo Starting app on http://localhost:5001
echo Press Ctrl+C to stop.
echo.

python app.py
pause
