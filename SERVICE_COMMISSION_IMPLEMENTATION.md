# Service-Based Commission System Implementation

## Overview

A comprehensive service-based commission system for tracking staff earnings per completed appointment. Supports both simple (Option A) and complex (Option B) commission structures.

## Architecture

### Option A: Simple Commission (Default)
- Uses staff member's `payment_rate` as commission percentage
- Applied automatically when appointment is marked as completed
- No additional configuration needed
- Example: Staff with 10% payment_rate earns 10% commission on each service

### Option B: Complex Commission (Optional)
- Per-service commission rate override via `Service.commission_percentage`
- Allows different commission percentages for different services
- Overrides staff default when set
- Example: Haircut service has 15% commission, Coloring has 20%

## Database Models

### ServiceCommission Model
```python
class ServiceCommission(BaseDocument):
    # References
    staff_id: ObjectId          # Staff member
    appointment_id: ObjectId    # Completed appointment
    service_id: ObjectId        # Service provided
    
    # Commission details
    service_price: Decimal      # Price at time of completion
    commission_percentage: Decimal  # Applied percentage
    commission_amount: Decimal  # Calculated amount
    
    # Status tracking
    status: str                 # "pending" or "paid"
    
    # Timestamps
    earned_date: DateTime       # When commission was earned
    paid_date: DateTime         # When commission was paid (if paid)
```

### Service Model Enhancement
```python
class Service(BaseDocument):
    # ... existing fields ...
    commission_percentage: Decimal  # Optional override (Option B)
```

## API Endpoints

### Calculate Commission
```
POST /api/service-commissions/calculate/{appointment_id}
```
Manually calculate commission for a completed appointment.

### List Staff Commissions
```
GET /api/service-commissions/staff/{staff_id}
Query Parameters:
  - status: "pending" | "paid" (optional)
  - start_date: ISO date string (optional)
  - end_date: ISO date string (optional)
  - page: integer (default: 1)
  - page_size: integer (default: 20, max: 100)
```

### Get Commission Summary
```
GET /api/service-commissions/staff/{staff_id}/summary
Query Parameters:
  - start_date: ISO date string (optional)
  - end_date: ISO date string (optional)

Response:
{
  "summary": {
    "total_earned": 5000,
    "total_pending": 2000,
    "total_paid": 3000,
    "total_services": 50,
    "average_commission": 100
  },
  "breakdown": [
    {
      "service_id": "...",
      "service_name": "Haircut",
      "total_commission": 1500,
      "count": 15
    }
  ]
}
```

### Get Pending Commissions
```
GET /api/service-commissions/staff/{staff_id}/pending
```
Get all pending commissions for a staff member.

### Mark Commission as Paid
```
PATCH /api/service-commissions/{commission_id}/mark-paid
```
Mark a single commission as paid.

### Mark Multiple Commissions as Paid
```
POST /api/service-commissions/staff/{staff_id}/mark-paid-batch
Body: ["commission_id_1", "commission_id_2", ...]
```
Mark multiple commissions as paid in one operation.

## Workflow

### 1. Appointment Completion
When an appointment is marked as completed:
1. Appointment status changes to "completed"
2. ServiceCommissionService automatically calculates commission
3. Commission record created with status "pending"
4. Commission amount = service_price * commission_percentage / 100

### 2. Commission Calculation Logic
```
if service.commission_percentage is set:
    use service.commission_percentage
else:
    use staff.payment_rate

commission_amount = service_price * commission_percentage / 100
```

### 3. Commission Payment
1. Staff/Admin views pending commissions
2. Selects commissions to pay
3. Marks as paid (batch operation supported)
4. Commission status changes to "paid"
5. paid_date is recorded

## Frontend Components

### StaffCommissionDashboard
Main component for viewing and managing commissions.

Features:
- Summary cards (total earned, pending, paid, service count)
- Date range filtering
- Status filtering (pending/paid)
- Service breakdown
- Batch payment operations
- Pagination

### CommissionDisplay
Component for showing commission info during appointment completion.

Shows:
- Service price
- Commission percentage
- Commission amount
- Staff member name

## Service Methods

### ServiceCommissionService

```python
# Calculate commission for completed appointment
calculate_commission_for_appointment(tenant_id, appointment_id) -> ServiceCommission

# Get single commission
get_service_commission(tenant_id, commission_id) -> ServiceCommission

# List commissions with filtering
list_staff_commissions(
    tenant_id, staff_id,
    status=None,
    start_date=None,
    end_date=None,
    page=1,
    page_size=20
) -> (List[ServiceCommission], int)

# Get commission summary
get_commission_summary(tenant_id, staff_id, start_date=None, end_date=None) -> dict

# Get breakdown by service
get_commission_by_service(tenant_id, staff_id, start_date=None, end_date=None) -> List[dict]

# Mark commission as paid
mark_commission_as_paid(tenant_id, commission_id) -> ServiceCommission

# Mark multiple as paid
mark_commissions_as_paid(tenant_id, staff_id, commission_ids) -> int

# Get pending commissions
get_pending_commissions(tenant_id, staff_id) -> (List[ServiceCommission], Decimal)
```

## Implementation Details

### Auto-Calculation on Appointment Completion
The commission is automatically calculated when an appointment is marked as completed in the appointment routes:

```python
# In complete_appointment endpoint
appointment.status = "completed"
appointment.save()

# Auto-calculate commission
ServiceCommissionService.calculate_commission_for_appointment(tenant_id, appointment_id)
```

### Idempotency
Commission calculation is idempotent - calling it multiple times for the same appointment returns the same commission record.

### Audit Trail
All commission records include:
- earned_date: When commission was earned
- paid_date: When commission was paid
- created_at/updated_at: Record timestamps

### Accuracy
- Uses Decimal type for all monetary calculations
- Prevents floating-point precision errors
- Supports up to 2 decimal places

## Configuration

### Option A Setup (Default)
1. Set staff member's `payment_rate` field
2. Appointments automatically calculate commission using this rate
3. No additional configuration needed

### Option B Setup (Optional)
1. Set `commission_percentage` on Service model
2. This overrides staff's payment_rate for that service
3. Can be set per-service for fine-grained control

## Testing

Comprehensive property-based tests in `test_service_commission_properties.py`:

- Commission calculation accuracy
- Filtering and pagination
- Status transitions
- Batch operations
- Edge cases (zero rates, date ranges)

Run tests:
```bash
pytest backend/tests/unit/test_service_commission_properties.py -v
```

## Edge Cases Handled

1. **Non-completed appointments**: Commission not calculated
2. **Missing staff/service**: Returns None gracefully
3. **Duplicate calculations**: Idempotent - returns existing record
4. **Zero commission rate**: Creates record with 0 amount
5. **Date filtering**: Inclusive range filtering
6. **Batch operations**: Atomic updates

## Future Enhancements

1. **Tiered commissions**: Different rates based on volume
2. **Commission caps**: Maximum commission per period
3. **Bonus structures**: Performance-based bonuses
4. **Payout scheduling**: Automatic payout on schedule
5. **Commission disputes**: Dispute resolution workflow
6. **Reporting**: Advanced commission analytics

## Security Considerations

1. **Tenant isolation**: All queries filtered by tenant_id
2. **Authorization**: Endpoints require authentication
3. **Audit logging**: All commission changes logged
4. **Data validation**: Decimal precision validated
5. **Idempotency**: Prevents duplicate charges

## Performance

- Indexed queries on: tenant_id, staff_id, status, earned_date
- Compound indexes for common filter combinations
- Pagination support for large datasets
- Efficient aggregation for summaries

## Integration Points

1. **Appointment completion**: Auto-triggers commission calculation
2. **Staff management**: Uses staff.payment_rate
3. **Service management**: Uses service.commission_percentage
4. **Reporting**: Commission data available for reports
5. **Payroll**: Commission records feed into payroll system
