# Staff Service Assignment Feature - Design

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Dashboard                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Staff Management                                    │  │
│  │  ├─ Create Staff Form (with Services)               │  │
│  │  ├─ Edit Staff Form (with Services)                 │  │
│  │  └─ Staff List                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Staff Routes                                        │  │
│  │  ├─ POST /api/v1/staff (create with services)       │  │
│  │  ├─ PUT /api/v1/staff/{id} (update services)        │  │
│  │  ├─ GET /api/v1/staff (list with filtering)         │  │
│  │  └─ GET /api/v1/public/staff (public booking)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Staff Collection                                    │  │
│  │  ├─ id: ObjectId                                     │  │
│  │  ├─ service_ids: [ObjectId]  ◄── NEW FIELD         │  │
│  │  ├─ specialties: [String]                            │  │
│  │  ├─ status: String                                   │  │
│  │  └─ is_available_for_public_booking: Boolean         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Design

### Staff Form Component

**Location**: `salon/src/components/staff/StaffForm.tsx`

**Services Section**:
- Displays after Roles section
- Shows all available services as checkboxes
- Multiple selection allowed
- Loads services from `/api/v1/services` endpoint
- Displays "No services available" message if empty
- Pre-populates with existing service_ids when editing

**Form State**:
```typescript
{
  service_ids: string[]  // Array of selected service IDs
}
```

**Handlers**:
- `handleServiceToggle(serviceId: string)` - Add/remove service from selection
- Services fetched on component mount via `useEffect`

### User Experience Flow

**Create Staff**:
1. Admin opens Create Staff form
2. Fills basic information (name, email, phone)
3. Selects roles
4. **NEW**: Selects services from checkboxes
5. Fills payment info, bio, specialties, certifications
6. Submits form
7. Services are saved with staff record

**Edit Staff**:
1. Admin opens Edit Staff form
2. Form pre-populates with existing data
3. **NEW**: Service checkboxes show current selections
4. Admin can add/remove services
5. Submits form
6. Services are updated

## Backend Design

### Staff Model Update

**File**: `backend/app/models/staff.py`

**New Field**:
```python
service_ids: List[ObjectId] = Field(default_factory=list)
```

**Constraints**:
- Optional field (defaults to empty list)
- Stores ObjectId references to Service documents
- No validation on service existence (handled at API level)

### API Endpoints

#### GET /api/v1/staff
**Query Parameters**:
- `service_id` (optional): Filter staff by service
- `status` (optional): Filter by status
- `is_available_for_public_booking` (optional): Filter by public booking availability

**Filtering Logic**:
```python
query = {
    "tenant_id": tenant_id_obj,
}

if service_id:
    query["service_ids"] = ObjectId(service_id)

if status:
    query["status"] = status

if is_available_for_public_booking is not None:
    query["is_available_for_public_booking"] = is_available_for_public_booking

staff = Staff.objects(**query)
```

#### POST /api/v1/staff
**Request Body**:
```json
{
  "user_id": "ObjectId",
  "service_ids": ["ObjectId"],
  "specialties": ["String"],
  "certifications": ["String"],
  "bio": "String",
  "profile_image_url": "String",
  "payment_type": "String",
  "payment_rate": 0,
  "hire_date": "Date",
  "status": "String",
  "is_available_for_public_booking": false
}
```

**Validation**:
- Verify all service_ids exist and belong to tenant
- Verify user_id exists
- Verify tenant_id from context

#### PUT /api/v1/staff/{id}
**Request Body**: Same as POST

**Validation**:
- Verify staff exists
- Verify all service_ids exist and belong to tenant
- Verify tenant_id from context

#### GET /api/v1/public/staff
**Query Parameters**:
- `service_id` (required): Filter by service

**Response**: Array of PublicStaffResponse (public fields only)

**Filtering**:
```python
query = {
    "tenant_id": tenant_id_obj,
    "service_ids": ObjectId(service_id),
    "is_available_for_public_booking": True,
    "status": "active",
}

staff = Staff.objects(**query)
```

### Public Booking Integration

**File**: `backend/app/routes/public_booking.py`

**Staff Filtering**:
- When customer selects a service in public booking wizard
- Call `GET /api/v1/public/staff?service_id={service_id}`
- Backend filters staff by:
  1. Service ID in service_ids array
  2. is_available_for_public_booking = True
  3. status = "active"
  4. tenant_id matches

**Empty State Handling**:
- If no staff returned, frontend displays empty state
- Shows helpful message with action buttons
- Toast notification appears

## Data Migration

### Migration Script

**File**: `backend/migrations/populate_staff_services.py`

**Purpose**: Populate existing staff records with services

**Logic**:
1. Get all published services with allow_public_booking = True
2. For each staff member with is_available_for_public_booking = True:
   - Add all published service IDs to service_ids array
3. Only migrate active staff members
4. Log migration results

**Idempotency**:
- Check if service_ids already populated
- Skip if already migrated
- Safe to run multiple times

**Execution Methods**:
- Docker: `docker-compose exec backend python -m backend.migrations.populate_staff_services`
- Direct: `python backend/migrations/populate_staff_services.py`
- MongoDB: Direct query update

## Database Schema

### Staff Collection Index

**New Index**:
```python
# For efficient filtering by service
db.staff.create_index([("tenant_id", 1), ("service_ids", 1)])
```

### Query Performance

**Optimized Queries**:
- `Staff.objects(tenant_id=X, service_ids=Y)` - Uses compound index
- `Staff.objects(tenant_id=X, status="active")` - Uses existing index
- `Staff.objects(tenant_id=X, is_available_for_public_booking=True)` - Uses existing index

## Error Handling

### Frontend Errors

**Service Loading Failure**:
- Display "No services available" message
- Allow form submission without services
- Show error toast

**Form Submission Failure**:
- Display error message in form
- Show error toast
- Preserve form data

### Backend Errors

**Invalid Service ID**:
- Return 400 Bad Request
- Message: "Invalid service ID format"

**Service Not Found**:
- Return 404 Not Found
- Message: "Service not found"

**Unauthorized Access**:
- Return 403 Forbidden
- Message: "Tenant not found"

## Testing Strategy

### Unit Tests

**Frontend**:
- Service toggle handler
- Service list rendering
- Empty state display
- Form submission with services

**Backend**:
- Staff creation with services
- Staff update with services
- Staff filtering by service
- Public staff filtering

### Integration Tests

**End-to-End**:
- Create staff with services
- Edit staff services
- Public booking staff filtering
- Empty state in public booking

### Property-Based Tests

**Correctness Properties**:
1. Service assignment persists correctly
2. Public booking only shows assigned staff
3. Service filtering returns correct results
4. Migration doesn't lose data

## Deployment Checklist

- [ ] Update Staff model with service_ids field
- [ ] Update Staff schema with service_ids
- [ ] Update StaffForm component with services section
- [ ] Update Staff type definition with service_ids
- [ ] Create database index for service_ids
- [ ] Run migration script
- [ ] Test staff creation with services
- [ ] Test staff editing with services
- [ ] Test public booking staff filtering
- [ ] Test empty state display
- [ ] Verify backward compatibility
- [ ] Deploy to production

## Rollback Plan

**If Issues Occur**:
1. Revert StaffForm component changes
2. Revert Staff model changes
3. Remove database index
4. Restore staff records from backup
5. Notify users of temporary unavailability

**Data Safety**:
- Backup staff collection before migration
- Migration is idempotent (safe to retry)
- No data loss if rolled back
