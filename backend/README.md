# Salon/Spa/Gym SaaS Platform - Backend

A comprehensive multi-tenant SaaS platform backend for managing salons, spas, and gyms built with FastAPI, MongoDB, Redis, and Celery.

## Features

- **Multi-Tenant Architecture**: Complete data isolation between tenants
- **User Authentication**: JWT-based authentication with OAuth 2.0 support
- **Role-Based Access Control**: Granular permission management
- **Multi-Factor Authentication**: TOTP and SMS-based MFA
- **Appointment Booking**: Real-time availability and booking system
- **Staff Management**: Scheduling and shift management
- **Async Task Processing**: Celery with RabbitMQ for background jobs
- **Caching**: Redis for sessions and caching
- **Comprehensive Testing**: Unit tests and property-based tests

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB Atlas with Mongoengine ODM
- **Cache**: Redis 7+
- **Message Queue**: RabbitMQ with Celery
- **Testing**: pytest with Hypothesis for property-based tests

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration management
│   ├── middleware.py        # CORS, logging, error handling
│   ├── models/              # Mongoengine models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # Utility functions
│   └── tasks/               # Celery tasks
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── migrations/              # Database migrations
├── docker/
│   └── Dockerfile           # Python application
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .dockerignore            # Docker ignore file
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- MongoDB Atlas account
- Redis (via Docker)
- RabbitMQ (via Docker)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run FastAPI server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   Swagger documentation: `http://localhost:8000/docs`

### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - FastAPI backend on port 8000
   - React frontend on port 3000
   - Redis on port 6379
   - RabbitMQ on port 5672 (AMQP) and 15672 (Management UI)
   - Celery worker for async tasks

2. **View logs**
   ```bash
   docker-compose logs -f api
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

## API Documentation

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Authentication

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

## Testing

### Run all tests

```bash
pytest
```

### Run specific test file

```bash
pytest tests/unit/test_config.py -v
```

### Run with coverage

```bash
pytest --cov=app tests/
```

### Run property-based tests

```bash
pytest tests/unit/test_config.py -v --hypothesis-seed=0
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `ENVIRONMENT`: development, staging, or production
- `DATABASE_URL`: MongoDB Atlas connection string
- `REDIS_URL`: Redis connection URL
- `RABBITMQ_URL`: RabbitMQ connection URL
- `JWT_SECRET_KEY`: Secret key for JWT signing

## Database

### MongoDB Atlas Setup

1. Create MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Create a database user
4. Get connection string (mongodb+srv://...)
5. Add connection string to `.env` as `DATABASE_URL`

### Database Migrations

Migrations are managed through Mongoengine models. To create indexes:

```bash
python -c "from app.models import *; from mongoengine import connect; connect('salon_db'); print('Indexes created')"
```

## Celery Tasks

### Start Celery worker

```bash
celery -A app.tasks worker --loglevel=info
```

### Monitor tasks

```bash
celery -A app.tasks events
```

## Logging

Logs are configured in `app/config.py`. Set `LOG_LEVEL` environment variable to control verbosity:
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

## Security

- All passwords are hashed with bcrypt (salt rounds ≥12)
- JWT tokens are signed with RS256 algorithm
- All API endpoints require authentication
- CORS is configured for frontend communication
- Rate limiting is enforced on all endpoints

## Performance

- Redis caching for frequently accessed data
- MongoDB indexes for fast queries
- Connection pooling for database and Redis
- Async task processing with Celery
- Request ID tracking for debugging

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests for new functionality
4. Run tests and ensure they pass
5. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
