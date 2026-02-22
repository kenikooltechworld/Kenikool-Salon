# Marketplace Services API Reference

## Overview

The Marketplace Services API provides endpoints for managing third-party marketplace services and integrations. All endpoints require authentication via `get_current_user` dependency.

## Base URL

```
/api/marketplace
```

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Service Browsing Endpoints

### Get Available Services

```
GET /api/marketplace/services
```

**Query Parameters:**

- `category` (optional): Filter by service category
- `search` (optional): Search by service name or description
- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "services": [
    {
      "_id": "service-id",
      "name": "Email Marketing Pro",
      "description": "Advanced email marketing platform",
      "category": "Marketing",
      "rating": 4.8,
      "reviewCount": 245,
      "pricing": {
        "type": "paid",
        "basePrice": 29.99,
        "currency": "USD"
      }
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

### Get Service Details

```
GET /api/marketplace/services/{service_id}
```

**Response:**

```json
{
  "_id": "service-id",
  "name": "Email Marketing Pro",
  "description": "Advanced email marketing platform",
  "category": "Marketing",
  "features": ["Email campaigns", "Automation", "Analytics"],
  "pricing": {...},
  "rating": 4.8,
  "reviewCount": 245,
  "developer": "EmailPro Inc",
  "version": "2.1.0",
  "documentation": "https://docs.emailpro.com",
  "supportUrl": "https://support.emailpro.com",
  "isInstalled": false
}
```

### Get Service Availability

```
GET /api/marketplace/services/{service_id}/availability
```

**Response:**

```json
{
  "serviceId": "service-id",
  "isAvailable": true,
  "regions": ["US", "CA", "UK"],
  "supportedLanguages": ["en", "es", "fr"],
  "requirements": {}
}
```

### Get Service Categories

```
GET /api/marketplace/categories
```

**Response:**

```json
["Marketing", "Communication", "Analytics", "Payments", "Automation"]
```

### Search Services

```
GET /api/marketplace/search
```

**Query Parameters:**

- `q` (required): Search query
- `category` (optional): Filter by category
- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "results": [...],
  "total": 10,
  "skip": 0,
  "limit": 50
}
```

## Service Installation Endpoints

### Install Service

```
POST /api/marketplace/install
```

**Request Body:**

```json
{
  "serviceId": "service-id",
  "configuration": {
    "settings": {},
    "webhookUrl": "https://example.com/webhook",
    "enableNotifications": true,
    "syncFrequency": "daily"
  },
  "billingPlan": "free"
}
```

**Response:**

```json
{
  "id": "installed-service-id",
  "serviceId": "service-id",
  "status": "active",
  "installationDate": "2026-02-10T12:00:00Z"
}
```

### Get Installed Services

```
GET /api/marketplace/installed
```

**Query Parameters:**

- `status` (optional): Filter by status (active, inactive, error)
- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "services": [...],
  "total": 5,
  "skip": 0,
  "limit": 50
}
```

### Get Installed Service

```
GET /api/marketplace/installed/{service_id}
```

**Response:**

```json
{
  "_id": "installed-service-id",
  "tenant_id": "tenant-id",
  "service_id": "service-id",
  "installation_date": "2026-02-10T12:00:00Z",
  "status": "active",
  "configuration": {},
  "billing_status": "active"
}
```

### Uninstall Service

```
POST /api/marketplace/uninstall/{service_id}
```

**Request Body:**

```json
{
  "reason": "No longer needed",
  "keepData": false
}
```

**Response:**

```json
{
  "success": true,
  "message": "Service uninstalled successfully"
}
```

## Service Configuration Endpoints

### Get Service Configuration

```
GET /api/marketplace/services/{service_id}/configuration
```

**Response:**

```json
{
  "serviceId": "service-id",
  "settings": {},
  "webhookUrl": "https://example.com/webhook",
  "enableNotifications": true,
  "syncFrequency": "daily"
}
```

### Update Service Configuration

```
PUT /api/marketplace/services/{service_id}/configuration
```

**Request Body:**

```json
{
  "configuration": {},
  "webhookUrl": "https://example.com/webhook",
  "enableNotifications": true,
  "syncFrequency": "daily"
}
```

**Response:**

```json
{
  "serviceId": "service-id",
  "settings": {},
  "webhookUrl": "https://example.com/webhook",
  "enableNotifications": true,
  "syncFrequency": "daily"
}
```

### Test Service Connection

```
POST /api/marketplace/services/{service_id}/test-connection
```

**Response:**

```json
{
  "success": true,
  "message": "Connection test successful"
}
```

### Sync Service Data

```
POST /api/marketplace/services/{service_id}/sync
```

**Response:**

```json
{
  "success": true,
  "syncedAt": "2026-02-10T12:00:00Z"
}
```

## Service Reviews Endpoints

### Get Service Reviews

```
GET /api/marketplace/services/{service_id}/reviews
```

**Query Parameters:**

- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "reviews": [
    {
      "_id": "review-id",
      "service_id": "service-id",
      "rating": 5,
      "title": "Excellent service",
      "comment": "Great integration",
      "author": "user@example.com",
      "helpful": 10,
      "unhelpful": 1,
      "created_at": "2026-02-10T12:00:00Z"
    }
  ],
  "total": 245,
  "skip": 0,
  "limit": 50
}
```

### Create Service Review

```
POST /api/marketplace/reviews?service_id={service_id}
```

**Request Body:**

```json
{
  "rating": 5,
  "title": "Excellent service",
  "comment": "Great integration"
}
```

**Response:**

```json
{
  "_id": "review-id",
  "service_id": "service-id",
  "rating": 5,
  "title": "Excellent service",
  "comment": "Great integration",
  "author": "user@example.com",
  "helpful": 0,
  "unhelpful": 0,
  "created_at": "2026-02-10T12:00:00Z"
}
```

### Update Service Review

```
PUT /api/marketplace/reviews/{review_id}
```

**Request Body:**

```json
{
  "rating": 4,
  "title": "Good service",
  "comment": "Works well"
}
```

**Response:**

```json
{
  "success": true
}
```

### Delete Service Review

```
DELETE /api/marketplace/reviews/{review_id}
```

**Response:**

```json
{
  "success": true
}
```

### Mark Review as Helpful

```
POST /api/marketplace/reviews/{review_id}/helpful
```

**Response:**

```json
{
  "success": true
}
```

### Mark Review as Unhelpful

```
POST /api/marketplace/reviews/{review_id}/unhelpful
```

**Response:**

```json
{
  "success": true
}
```

## Service Billing Endpoints

### Get Service Billing

```
GET /api/marketplace/services/{service_id}/billing
```

**Response:**

```json
{
  "_id": "billing-id",
  "tenant_id": "tenant-id",
  "service_id": "service-id",
  "amount": 29.99,
  "billing_cycle": "monthly",
  "status": "active",
  "next_billing_date": "2026-03-10T00:00:00Z"
}
```

### Get All Service Billings

```
GET /api/marketplace/billing
```

**Query Parameters:**

- `status` (optional): Filter by status (active, suspended, cancelled)
- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "billings": [...],
  "total": 5,
  "skip": 0,
  "limit": 50
}
```

### Update Billing Plan

```
PUT /api/marketplace/services/{service_id}/billing-plan
```

**Request Body:**

```json
{
  "billingPlan": "paid"
}
```

**Response:**

```json
{
  "success": true
}
```

### Get Billing History

```
GET /api/marketplace/services/{service_id}/billing-history
```

**Query Parameters:**

- `skip` (optional, default: 0): Number of results to skip
- `limit` (optional, default: 50, max: 100): Number of results to return

**Response:**

```json
{
  "history": [...],
  "total": 12,
  "skip": 0,
  "limit": 50
}
```

### Get Total Spending

```
GET /api/marketplace/spending
```

**Response:**

```json
{
  "totalMonthly": 149.97,
  "totalAnnual": 1799.64,
  "currency": "USD"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Database Setup

Before using the API, seed the marketplace services:

```bash
python backend/seed_marketplace_services.py
```

This will populate the `marketplace_services` collection with 6 sample services.

## Collections

The API uses the following MongoDB collections:

- `marketplace_services` - Available services catalog
- `installed_services` - User-installed services
- `service_reviews` - Customer reviews
- `service_billing` - Billing information
- `service_billing_history` - Billing history records

## Rate Limiting

No rate limiting is currently implemented. Consider adding rate limiting for production deployments.

## Pagination

All list endpoints support pagination using `skip` and `limit` parameters:

- `skip`: Number of results to skip (default: 0)
- `limit`: Number of results to return (default: 50, max: 100)

## Sorting

Sorting is not currently implemented. Consider adding sorting support for production deployments.

## Filtering

List endpoints support filtering using query parameters:

- `category`: Filter by service category
- `status`: Filter by status
- `search`: Search by name or description

## Caching

The frontend uses React Query for caching. Cache invalidation occurs on mutations.

## WebSocket Support

WebSocket support is not currently implemented. Consider adding real-time updates for production deployments.

---

**Last Updated**: February 10, 2026
**API Version**: 1.0.0
