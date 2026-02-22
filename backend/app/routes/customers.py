"""Customer management routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from bson import ObjectId
from app.models.customer import Customer
from app.services.appointment_history_service import AppointmentHistoryService
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def customer_to_response(customer: Customer) -> dict:
    """Convert Customer model to response."""
    return {
        "id": str(customer.id),
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "date_of_birth": customer.date_of_birth.isoformat() if customer.date_of_birth else None,
        "preferred_staff_id": str(customer.preferred_staff_id) if customer.preferred_staff_id else None,
        "preferred_services": [str(service_id) for service_id in customer.preferred_services],
        "communication_preference": customer.communication_preference,
        "status": customer.status,
        "created_at": customer.created_at.isoformat(),
        "updated_at": customer.updated_at.isoformat(),
    }


@router.get("", response_model=dict)
@tenant_isolated
async def list_customers(
    search: Optional[str] = Query(None, description="Search by name or phone"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List customers for the tenant.

    Returns a paginated list of customers with optional filtering by status and search by name/phone.
    """
    try:
        # Query customers
        query = Customer.objects(tenant_id=tenant_id)

        # Apply search filter
        if search:
            # Search by first name, last name, or phone
            query = query(
                __raw__={
                    "$or": [
                        {"first_name": {"$regex": search, "$options": "i"}},
                        {"last_name": {"$regex": search, "$options": "i"}},
                        {"phone": {"$regex": search, "$options": "i"}},
                    ]
                }
            )

        # Apply status filter
        if status:
            query = query(status=status)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        customers = query.skip(skip).limit(page_size).order_by("-created_at")

        # Convert to response format
        customer_list = [customer_to_response(customer) for customer in customers]

        return {
            "customers": customer_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Failed to list customers: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list customers")


@router.get("/{customer_id}/history", response_model=dict)
@tenant_isolated
async def get_customer_history(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get customer appointment history.

    Returns paginated appointment history for the given customer ID.
    """
    try:
        from app.models.service import Service
        from app.models.staff import Staff
        
        customer_id_obj = ObjectId(customer_id)
        
        # Verify customer exists
        customer = Customer.objects(id=customer_id_obj, tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get history entries
        history_entries, total = AppointmentHistoryService.get_customer_history(
            tenant_id=tenant_id,
            customer_id=customer_id_obj,
            page=page,
            page_size=page_size,
        )
        
        # Batch fetch all related data to avoid N+1 queries
        from app.models.user import User
        
        service_ids = [entry.service_id for entry in history_entries]
        staff_ids = [entry.staff_id for entry in history_entries]
        
        # Fetch all services at once
        services = {s.id: s for s in Service.objects(tenant_id=tenant_id, id__in=service_ids)}
        
        # Fetch all staff at once
        staff_list = Staff.objects(tenant_id=tenant_id, id__in=staff_ids)
        user_ids = [s.user_id for s in staff_list if s.user_id]
        
        # Fetch all users at once
        users = {u.id: u for u in User.objects(id__in=user_ids)}
        
        # Create staff lookup
        staff_lookup = {s.id: s for s in staff_list}
        
        # Convert to response format
        history_list = []
        for entry in history_entries:
            service = services.get(entry.service_id)
            staff = staff_lookup.get(entry.staff_id)
            
            service_name = service.name if service else "Unknown Service"
            
            # Get staff name from User model via staff.user_id
            staff_name = "Unknown Staff"
            if staff and staff.user_id:
                user = users.get(staff.user_id)
                if user:
                    staff_name = f"{user.first_name} {user.last_name}"
            
            history_item = {
                "id": str(entry.id),
                "appointment_id": str(entry.appointment_id),
                "service_id": str(entry.service_id),
                "staff_id": str(entry.staff_id),
                "service_name": service_name,
                "staff_name": staff_name,
                "appointment_date": entry.appointment_date.isoformat(),
                "appointment_time": entry.appointment_date.strftime("%H:%M"),
                "notes": entry.notes or "",
                "rating": 0,
                "feedback": "",
            }
            history_list.append(history_item)
        
        return {
            "history": history_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer history: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get customer history")


@router.get("/{customer_id}", response_model=dict)
@tenant_isolated
async def get_customer(
    customer_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific customer.

    Returns the customer details for the given customer ID.
    """
    try:
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return customer_to_response(customer)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to get customer: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get customer")


@router.post("", response_model=dict)
@tenant_isolated
async def create_customer(
    customer_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new customer.

    Creates a new customer profile with the provided details.
    """
    try:
        logger.info(f"Creating customer with data: {customer_data}")
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "phone"]
        for field in required_fields:
            if field not in customer_data or not customer_data[field]:
                raise HTTPException(status_code=400, detail=f"{field} is required")

        # Check if customer with same email already exists
        existing_customer = Customer.objects(email=customer_data["email"], tenant_id=tenant_id).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this email already exists")

        # Convert preferred_services to ObjectIds
        preferred_services = []
        if customer_data.get("preferred_services"):
            preferred_services = [ObjectId(service_id) for service_id in customer_data["preferred_services"]]

        # Convert preferred_staff_id to ObjectId if provided
        preferred_staff_id = None
        if customer_data.get("preferred_staff_id"):
            preferred_staff_id = ObjectId(customer_data["preferred_staff_id"])

        # Create new customer
        new_customer = Customer(
            tenant_id=tenant_id,
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            email=customer_data["email"],
            phone=customer_data["phone"],
            address=customer_data.get("address"),
            date_of_birth=customer_data.get("date_of_birth"),
            preferred_staff_id=preferred_staff_id,
            preferred_services=preferred_services,
            communication_preference=customer_data.get("communication_preference", "email"),
            status=customer_data.get("status", "active"),
        )
        
        new_customer.save()
        logger.info(f"Created customer: {new_customer.id}")
        return customer_to_response(new_customer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create customer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create customer")


@router.put("/{customer_id}", response_model=dict)
@tenant_isolated
async def update_customer(
    customer_id: str,
    customer_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update a customer.

    Updates the customer profile details for the given customer ID.
    """
    try:
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Check if email is being changed and if it already exists
        if "email" in customer_data and customer_data["email"] != customer.email:
            existing_customer = Customer.objects(email=customer_data["email"], tenant_id=tenant_id).first()
            if existing_customer:
                raise HTTPException(status_code=400, detail="Customer with this email already exists")

        # Update fields
        if "first_name" in customer_data:
            customer.first_name = customer_data["first_name"]
        if "last_name" in customer_data:
            customer.last_name = customer_data["last_name"]
        if "email" in customer_data:
            customer.email = customer_data["email"]
        if "phone" in customer_data:
            customer.phone = customer_data["phone"]
        if "address" in customer_data:
            customer.address = customer_data["address"]
        if "date_of_birth" in customer_data:
            customer.date_of_birth = customer_data["date_of_birth"]
        if "preferred_staff_id" in customer_data:
            customer.preferred_staff_id = ObjectId(customer_data["preferred_staff_id"]) if customer_data["preferred_staff_id"] else None
        if "preferred_services" in customer_data:
            customer.preferred_services = [ObjectId(service_id) for service_id in customer_data["preferred_services"]]
        if "communication_preference" in customer_data:
            customer.communication_preference = customer_data["communication_preference"]
        if "status" in customer_data:
            customer.status = customer_data["status"]

        customer.save()
        logger.info(f"Updated customer: {customer.id}")
        
        return customer_to_response(customer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update customer: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update customer")


@router.delete("/{customer_id}", response_model=dict)
@tenant_isolated
async def delete_customer(
    customer_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Delete a customer.

    Deletes the customer profile for the given customer ID.
    """
    try:
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer_id_str = str(customer.id)
        customer.delete()
        logger.info(f"Deleted customer: {customer_id_str}")
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete customer: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to delete customer")
