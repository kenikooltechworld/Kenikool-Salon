@echo off
echo Starting Celery Worker for Salon Management System...
echo.
echo Make sure Redis is running on localhost:6379
echo.

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Starting Celery worker...
echo Press Ctrl+C to stop
echo.

python run_celery.py worker

pause
