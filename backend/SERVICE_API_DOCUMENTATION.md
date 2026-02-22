# Service Management API Documentation

## Overview

The Service Management API provides endpoints for creating, reading, updating, and deleting services offered by a salon, spa, or gym. Services are tenant-isolated, meaning each tenant can only access their own services.

## Data Model

### Service

A service represents a specific treatment or activity offered by a business.

**Fields:**
- `id` (ObjectId): Unique identifier
- `tenant_id` (ObjectId): Tenant that owns this service
- `name` (string): Service name (required, max 255 chars)
- `description` (string): Service description (optional, max 1000 chars)
- `duration_minutes` (integer): Service duration in minutes (required, > 0)
- `price` (decimal): Service price (required, >= 0)
- `category` (string): Service category (required, max 100 chars)
- `is_active` (boolean): Whether service is active (default: true)
- `is_published` (boolean): Whether service is published to public booking (default: false)
- `public_description` (string): Description for public booking interface (optional, max 1000 chars)
- `public_image_url` (string): Image URL for public booking (optional, max 500 chars)
- `allow_public_booking` (boolean): Whether customers can book this service publicly (default: false)
- `tags` (array): Service tags for categorization (default: [])
- `created_at` (timestamp): Creation timestamp
- `updated_at` (timestamp): Last update timestamp

## API Endpoints

### Create Service

**Endpoint:** `POST /v1/services`

**Description:** Create a new service for the tenant.

**Request Body:**
```json
{
  "name": "Haircut",
  "description": "Professional haircut service",
  "duration_minutes": 30,
  "price": "25.00",
  "category": "Hair",
  "is_active": true,
  "is_published": true,
  "public_description": "Get a professional haircut from our experienced stylists",
  "public_image_url": "https://example.com/haircut.jpg",
  "allow_public_booking": true,
  "tags": ["haircut", "styling", "men"]
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Haircut",
  "description": "Professional haircut service",
  "duration_minutes": 30,
  "price": "25.00",
  "category": "Hair",
  "is_active": true,
  "is_published": true,
  "public_description": "Get a professional haircut from our experienced stylists",
  "public_image_url": "https://example.com/haircut.jpg",
  "allow_public_booking": true,
  "tags": ["haircut", "styling", "men"],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Get Service

**Endpoint:** `GET /v1/services/{service_id}`

**Description:** Get a specific service by ID.

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Haircut",
  "description": "Professional haircut service",
  "duration_minutes": 30,
  "price": "25.00",
  "category": "Hair",
  "is_active": true,
  "is_published": true,
  "public_description": "Get a professional haircut from our experienced stylists",
  "public_image_url": "https://example.com/haircut.jpg",
  "allow_public_booking": true,
  "tags": ["haircut", "styling", "men"],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### List Services

**Endpoint:** `GET /v1/services`

**Description:** List all services for the tenant with optional filtering.

**Query Parameters:**
- `category` (string, optional): Filter by category
- `is_active` (boolean, optional): Filter by active status
- `page` (integer, default: 1): Page number for pagination
- `page_size` (integer, default: 10, max: 100): Number of items per page

**Example:** `GET /v1/services?category=Hair&is_active=true&page=1&page_size=10`

**Response (200 OK):**
```json
{
  "services": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Haircut",
      "description": "Professional haircut service",
      "duration_minutes": 30,
      "price": "25.00",
      "category": "Hair",
      "is_active": true,
      "is_published": true,
      "public_description": "Get a professional haircut from our experienced stylists",
      "public_image_url": "https://example.com/haircut.jpg",
      "allow_public_booking": true,
      "tags": ["haircut", "styling", "men"],
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

### Update Service

**Endpoint:** `PUT /v1/services/{service_id}`

**Description:** Update a service. Only provided fields are updated.

**Request Body (all fields optional):**
```json
{
  "name": "Premium Haircut",
  "price": "35.00",
  "duration_minutes": 45,
  "is_active": true,
  "is_published": true
}
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Premium Haircut",
  "description": "Professional haircut service",
  "duration_minutes": 45,
  "price": "35.00",
  "category": "Hair",
  "is_active": true,
  "is_published": true,
  "public_description": "Get a professional haircut from our experienced stylists",
  "public_image_url": "https://example.com/haircut.jpg",
  "allow_public_booking": true,
  "tags": ["haircut", "styling", "men"],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

### Delete Service

**Endpoint:** `DELETE /v1/services/{service_id}`

**Description:** Delete a service.

**Response (200 OK):**
```json
{
  "message": "Service deleted successfully"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Failed to create service"
}
```

### 401 Unauthorized
```json
{
  "detail": "Tenant context required"
}
```

### 404 Not Found
```json
{
  "detail": "Service not found"
}
```

## Filtering Examples

### Filter by Category
```
GET /v1/services?category=Hair
```

### Filter by Active Status
```
GET /v1/services?is_active=true
```

### Filter by Multiple Criteria
```
GET /v1/services?category=Hair&is_active=true&page=1&page_size=20
```

## Pagination

Services are returned in paginated format. Use `page` and `page_size` parameters to control pagination.

**Example:**
```
GET /v1/services?page=2&page_size=20
```

Returns services 21-40 (assuming 20 items per page).

## Tenant Isolation

All service endpoints are tenant-isolated. The tenant context is automatically extracted from the request and used to filter services. Services from other tenants are never returned, and cross-tenant access is prevented at the database level.

## Authentication

All service endpoints require authentication. The tenant context is extracted from the JWT token in the Authorization header.

**Example:**
```
Authorization: Bearer <jwt_token>
```

## Usage Examples

### Create a Service
```bash
curl -X POST http://localhost:8000/v1/services \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Haircut",
    "duration_minutes": 30,
    "price": "25.00",
    "category": "Hair"
  }'
```

### List Services
```bash
curl -X GET http://localhost:8000/v1/services \
  -H "Authorization: Bearer <token>"
```

### List Services by Category
```bash
curl -X GET "http://localhost:8000/v1/services?category=Hair" \
  -H "Authorization: Bearer <token>"
```

### Get a Specific Service
```bash
curl -X GET http://localhost:8000/v1/services/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer <token>"
```

### Update a Service
```bash
curl -X PUT http://localhost:8000/v1/services/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "30.00",
    "duration_minutes": 45
  }'
```

### Delete a Service
```bash
curl -X DELETE http://localhost:8000/v1/services/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer <token>"
```

## Implementation Notes

- All services are automatically filtered by tenant_id
- Service names must be unique within a tenant (enforced at application level)
- Prices are stored as Decimal for accuracy
- Services can be marked as inactive without deleting them
- Public booking fields allow services to be published to the public booking interface
- Tags can be used for additional categorization and filtering
