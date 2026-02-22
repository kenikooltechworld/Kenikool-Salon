"""Customer preference management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from bson import ObjectId
from app.models.customer import Customer
from app.models.customer_preference import CustomerPreference
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.schemas.customer_preference import (
    CustomerPreferenceCreate,
    CustomerPreferenceUpdate,
    CustomerPreferenceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customer_preferences"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def preference_to_response(preference: CustomerPreference) -> dict:
    """Convert CustomerPreference model to response."""
    return {
        "id": str(preference.id),
        "customer_id": str(preference.customer_id),
        "preferred_staff_ids": [str(staff_id) for staff_id in preference.preferred_staff_ids],
        "preferred_service_ids": [str(service_id) for service_id in preference.preferred_service_ids],
        "communication_methods": preference.communication_methods,
        "preferred_time_slots": preference.preferred_time_slots,
        "language": preference.language,
        "notes": preference.notes,
        "created_at": preference.created_at.isoformat(),
        "updated_at": preference.updated_at.isoformat(),
    }


@router.get("/{customer_id}/preferences", response_model=dict)
@tenant_isolated
async def get_customer_preferences(
    customer_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get customer preferences.

    Returns the preferences for the given customer ID.
    """
    try:
        # Verify customer exists and belongs to tenant
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Get or create preferences
        preference = CustomerPreference.objects(
            customer_id=ObjectId(customer_id),
            tenant_id=tenant_id
        ).first()

        if not preference:
            # Create default preferences if they don't exist
            preference = CustomerPreference(
                customer_id=ObjectId(customer_id),
                tenant_id=tenant_id,
            )
            preference.save()

        return preference_to_response(preference)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer preferences: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get customer preferences")


@router.put("/{customer_id}/preferences", response_model=dict)
@tenant_isolated
async def update_customer_preferences(
    customer_id: str,
    preference_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update customer preferences.

    Updates the preferences for the given customer ID.
    """
    try:
        # Verify customer exists and belongs to tenant
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Get or create preferences
        preference = CustomerPreference.objects(
            customer_id=ObjectId(customer_id),
            tenant_id=tenant_id
        ).first()

        if not preference:
            preference = CustomerPreference(
                customer_id=ObjectId(customer_id),
                tenant_id=tenant_id,
            )

        # Update fields
        if "preferred_staff_ids" in preference_data:
            preference.preferred_staff_ids = [
                ObjectId(staff_id) for staff_id in preference_data["preferred_staff_ids"]
            ]
        if "preferred_service_ids" in preference_data:
            preference.preferred_service_ids = [
                ObjectId(service_id) for service_id in preference_data["preferred_service_ids"]
            ]
        if "communication_methods" in preference_data:
            preference.communication_methods = preference_data["communication_methods"]
        if "preferred_time_slots" in preference_data:
            preference.preferred_time_slots = preference_data["preferred_time_slots"]
        if "language" in preference_data:
            preference.language = preference_data["language"]
        if "notes" in preference_data:
            preference.notes = preference_data["notes"]

        preference.save()
        logger.info(f"Updated preferences for customer: {customer_id}")

        return preference_to_response(preference)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update customer preferences: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update customer preferences")
