# Kenikool Salon Management SaaS - Backend

Python FastAPI backend with GraphQL API for multi-tenant salon management platform.

## ✅ Current Status

**Backend is running successfully with GraphQL!**

- ✅ FastAPI server running on `http://localhost:8000`
- ✅ Root endpoint working: `GET /` → Returns API info
- ✅ Health check endpoint working: `GET /health` → Returns status
- ✅ GraphQL endpoint: `http://localhost:8000/graphql` with GraphiQL interface
- ✅ Authentication system implemented (JWT + bcrypt)
- ✅ User registration and login mutations working
- ✅ All authentication tests passing (7/7)
- ✅ Auto-reload enabled for development
- ⚠️ MongoDB connection optional (runs in limited mode without database)
- 📝 See MONGODB_SETUP.md for database setup instructions

**Test the API:**

```bash
# REST endpoints
curl http://localhost:8000/
# Response: {"message":"Kenikool Salon Management SaaS API","version":"v1","environment":"development"}

curl http://localhost:8000/health
# Response: {"status":"healthy","database":"disconnected"}

# GraphQL endpoint (open in browser)
http://localhost:8000/graphql
```

**Test GraphQL Mutations:**

Open http://localhost:8000/graphql in your browser and try:

```graphql
# Register a new salon
mutation {
  register(
    input: {
      salonName: "My Salon"
      ownerName: "John Doe"
      email: "john@example.com"
      phone: "+2348012345678"
      password: "password123"
    }
  ) {
    accessToken
    user {
      id
      email
      fullName
      role
    }
  }
}

# Login
mutation {
  login(input: { email: "john@example.com", password: "password123" }) {
    accessToken
    user {
      id
      email
      fullName
    }
  }
}
```

## Tech Stack

- **Framework**: FastAPI (async Python web framework)
- **API**: GraphQL with Strawberry
- **Database**: MongoDB with Motor (async driver)
- **Task Queue**: Celery + Redis
- **Authentication**: JWT with bcrypt
- **Testing**: pytest + Hypothesis (property-based testing)

## Prerequisites

- Python 3.10 or higher
- MongoDB (local or MongoDB Atlas)
- Redis (for Celery task queue)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
```

### 4. Run MongoDB (if local)

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

### 5. Run Redis (if local)

```bash
# Using Docker
docker run -d -p 6379:6379 --name redis redis:latest

# Or install Redis locally
```

## Running the Application

### Development Server

```bash
# Run with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql (coming soon)
- **API Docs**: http://localhost:8000/docs

### Run Celery Worker (for background tasks)

```bash
# Run worker only
python run_celery.py worker

# Run beat scheduler only (for periodic tasks)
python run_celery.py beat

# Run both worker and beat (development only)
python run_celery.py both
```

**Celery Tasks:**

- **24-hour reminders**: Runs daily at 9 AM
- **2-hour reminders**: Runs every 30 minutes
- **Waitlist notifications**: Runs every 15 minutes
- **Booking confirmations**: Triggered immediately on booking creation

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic models
│   ├── graphql/             # GraphQL schema & resolvers
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   ├── middleware/          # Custom middleware
│   └── celery_app.py        # Celery configuration
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Property-Based Tests

```bash
pytest tests/property/ -v
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## GraphQL

GraphQL endpoint will be available at `/graphql` with:

- Queries for data fetching
- Mutations for data modification
- Subscriptions for real-time updates

## Development

### Code Formatting

```bash
black app/
```

### Linting

```bash
flake8 app/
```

### Type Checking

```bash
mypy app/
```

## Deployment

### Free Tier Options

1. **Railway**: Deploy with one click
2. **Render**: Free tier with auto-deploy from Git
3. **Fly.io**: Free tier with global deployment

### Environment Variables

Ensure all required environment variables are set in production:

- Database credentials
- API keys (Cloudinary, Twilio, Paystack, Flutterwave)
- JWT secrets
- CORS origins

## License

Proprietary - Kenikool Tech World
