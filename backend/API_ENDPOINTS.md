# API Endpoints Reference

## Authentication Endpoints

### Login
```
POST /api/v1/auth/login
Content-Type: application/json
X-Tenant-ID: {tenant_id}

Request:
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
X-Tenant-ID: {tenant_id}

Response:
{
  "message": "Logged out successfully"
}
```

### Refresh Token
```
POST /api/v1/auth/refresh
Content-Type: application/json

Request:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
X-Tenant-ID: {tenant_id}

Response:
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role_id": "507f1f77bcf86cd799439012",
  "status": "active",
  "mfa_enabled": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Tenant Management Endpoints

### Provision Tenant
```
POST /api/v1/tenants
Content-Type: application/json

Request:
{
  "name": "Salon ABC",
  "email": "owner@salon.com",
  "phone": "+234 123 456 7890",
  "subscription_tier": "starter",
  "region": "us-east-1"
}

Response:
{
  "tenant_id": "507f1f77bcf86cd799439011",
  "admin_user_id": "507f1f77bcf86cd799439012",
  "admin_email": "owner@salon.com",
  "admin_password": "GeneratedPassword123!",
  "api_key": "sk_live_abcdef123456789...",
  "subscription_tier": "starter",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Tenant
```
GET /api/v1/tenants/{tenant_id}
Authorization: Bearer {access_token}

Response:
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Salon ABC",
  "subscription_tier": "starter",
  "status": "active",
  "region": "us-east-1",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Tenant
```
PUT /api/v1/tenants/{tenant_id}
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "subscription_tier": "professional"
}

Response:
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Salon ABC",
  "subscription_tier": "professional",
  "status": "active",
  "region": "us-east-1",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Suspend Tenant
```
POST /api/v1/tenants/{tenant_id}/suspend
Authorization: Bearer {access_token}

Response:
{
  "message": "Tenant suspended successfully"
}
```

### Delete Tenant
```
POST /api/v1/tenants/{tenant_id}/delete
Authorization: Bearer {access_token}

Response:
{
  "message": "Tenant deleted successfully"
}
```

## Health Check

### Health Status
```
GET /health

Response:
{
  "status": "healthy",
  "environment": "development"
}
```

## Root Endpoint

### API Info
```
GET /

Response:
{
  "message": "Salon/Spa/Gym SaaS Platform API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid credentials"
  }
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An internal server error occurred"
  }
}
```

## Authentication Headers

All authenticated endpoints require:
- `Authorization: Bearer {access_token}` - JWT access token
- `X-Tenant-ID: {tenant_id}` - Tenant ID (for multi-tenant endpoints)

## Rate Limiting

- 100 requests/minute per user
- 1000 requests/minute per tenant
- 10,000 requests/minute per API key

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Pagination

List endpoints support pagination:
- `?page=1` - Page number (default: 1)
- `?limit=20` - Items per page (default: 20, max: 100)

Response includes:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering

List endpoints support filtering:
- `?status=active` - Filter by status
- `?created_after=2024-01-01` - Filter by creation date
- `?search=query` - Full-text search

## Sorting

List endpoints support sorting:
- `?sort=created_at` - Sort by field (ascending)
- `?sort=-created_at` - Sort by field (descending)

## API Documentation

- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`
- OpenAPI Schema: `GET /openapi.json`
