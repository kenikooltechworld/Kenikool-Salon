@echo off
echo Starting Salon SaaS Development Environment...
echo.

REM Start Docker infrastructure
echo [1/3] Starting Docker containers (Redis, RabbitMQ, PostgreSQL)...
docker-compose up -d
timeout /t 3 /nobreak

REM Check if Docker started successfully
docker-compose ps | findstr /C:"Up" >nul
if errorlevel 1 (
    echo ERROR: Docker containers failed to start
    pause
    exit /b 1
)

echo [2/3] Starting Backend (FastAPI)...
start cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak

echo [3/3] Starting Frontend (React + Vite)...
start cmd /k "cd salon && npm install && npm run dev"

echo.
echo ============================================
echo Development environment started!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo RabbitMQ: http://localhost:15672 (guest/guest)
echo Redis:    localhost:6379
echo.
echo To stop everything:
echo - Close the terminal windows (Ctrl+C)
echo - Run: docker-compose down
echo ============================================
echo.
pause
