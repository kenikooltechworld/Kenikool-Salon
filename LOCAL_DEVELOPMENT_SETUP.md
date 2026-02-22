# Local Development Setup

Only Docker infrastructure (Redis, RabbitMQ). Frontend and Backend run locally with hot reload.

## Quick Start

### 1. Start Docker Infrastructure
```bash
docker-compose up -d
```

Starts: Redis, RabbitMQ

### 2. Start Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: http://localhost:8000

### 3. Start Frontend (Terminal 2)
```bash
cd salon
npm install
npm run dev
```

Frontend: http://localhost:3000

## Stop Everything

```bash
# Terminal 1 & 2: Ctrl+C
# Docker:
docker-compose down
```
