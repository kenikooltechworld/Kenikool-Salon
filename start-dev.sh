#!/bin/bash

echo "Starting Salon SaaS Development Environment..."
echo ""

# Start Docker infrastructure
echo "[1/3] Starting Docker containers (Redis, RabbitMQ, PostgreSQL)..."
docker-compose up -d
sleep 3

# Check if Docker started successfully
if ! docker-compose ps | grep -q "Up"; then
    echo "ERROR: Docker containers failed to start"
    exit 1
fi

# Start Backend
echo "[2/3] Starting Backend (FastAPI)..."
(
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

sleep 5

# Start Frontend
echo "[3/3] Starting Frontend (React + Vite)..."
(
    cd salon
    npm install
    npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "Development environment started!"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "RabbitMQ: http://localhost:15672 (guest/guest)"
echo "Redis:    localhost:6379"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop everything:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  docker-compose down"
echo "============================================"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
