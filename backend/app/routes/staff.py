"""Staff management routes."""

import logging
from typing import Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from bson import ObjectId
from app.models.staff import Staff
from app.models.user import User
from app.models.appointment import Appointment
from app.models.shift import Shift
from app.models.time_off_request import TimeOffRequest
from app.models.staff_commission import StaffCommission
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.schemas.staff import StaffCreate, StaffUpdate, StaffResponse, StaffListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/staff", tags=["staff"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def staff_to_response(staff: Staff, user: User = None) -> dict:
    """Convert Staff model to response."""
    if user is None:
        user = User.objects(id=staff.user_id, tenant_id=staff.tenant_id).first()
    
    role_ids = []
    try:
        if user and hasattr(user, "role_ids"):
            role_ids = [str(rid) for rid in (user.role_ids or [])]
    except Exception:
        pass
    
    return {
        "id": str(staff.id),
        "user_id": str(staff.user_id),
        "firstName": user.first_name if user else "",
        "lastName": user.last_name if user else "",
        "email": user.email if user else "",
        "phone": user.phone if user else "",
        "role_ids": role_ids,
        "service_ids": [str(sid) for sid in getattr(staff, "service_ids", [])],
        "specialties": staff.specialties,
        "certifications": staff.certifications,
        "certification_files": staff.certification_files,
        "payment_type": staff.payment_type,
        "payment_rate": float(staff.payment_rate),
        "hire_date": staff.hire_date.isoformat() if staff.hire_date else None,
        "bio": staff.bio,
        "profile_image_url": staff.profile_image_url,
        "status": staff.status,
        "createdAt": staff.created_at.isoformat() if staff.created_at else None,
        "updatedAt": staff.updated_at.isoformat() if staff.updated_at else None,
    }


def _sync_service_staff_ids(tenant_id: ObjectId, service_ids: list, staff_id: ObjectId):
    """
    Keep `service.staff_ids` in sync with `staff.service_ids`.
    
    For each service in service_ids, ensure staff_id is present on the Service.staff_ids list.
    For each service previously assigned to this staff but no longer in service_ids, remove it.
    """
    from app.models.service import Service
    from mongoengine import Q

    new_set = {ObjectId(sid) if isinstance(sid, str) else sid for sid in (service_ids or [])}

    if new_set:
        for sid in new_set:
            try:
                svc = Service.objects(tenant_id=tenant_id, pk=sid).first()
                if not svc:
                    continue
                existing = {ObjectId(x) for x in (svc.staff_ids or [])}
                if staff_id not in existing:
                    existing.add(staff_id)
                    svc.staff_ids = list(existing)
                    svc.save()
            except Exception:
                pass

    old_services = Service.objects(tenant_id=tenant_id, staff_ids=staff_id)
    for svc in old_services:
        if svc.id not in new_set:
            cleaned = [x for x in (svc.staff_ids or []) if x != staff_id]
            svc.staff_ids = cleaned
            svc.save()


@router.get("/user/{user_id}", response_model=dict)
@tenant_isolated
async def get_staff_by_user_id(
    user_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get staff profile by user ID."""
    try:
        staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff profile not found for this user")
        
        user = User.objects(id=ObjectId(user_id), tenant_id=tenant_id).first()
        return staff_to_response(staff, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get staff by user ID: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get staff profile")


@router.put("/user/{user_id}", response_model=dict)
@tenant_isolated
async def update_staff_by_user_id(
    user_id: str,
    staff_data: StaffUpdate,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Update staff profile by user ID."""
    try:
        staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff profile not found for this user")

        if staff_data.service_ids is not None:
            staff.service_ids = [ObjectId(sid) if isinstance(sid, str) else sid for sid in staff_data.service_ids]
        if staff_data.specialties is not None:
            staff.specialties = staff_data.specialties
        if staff_data.certifications is not None:
            staff.certifications = staff_data.certifications
        if staff_data.certification_files is not None:
            staff.certification_files = staff_data.certification_files
        if staff_data.payment_type is not None:
            staff.payment_type = staff_data.payment_type
        if staff_data.payment_rate is not None:
            staff.payment_rate = staff_data.payment_rate
        if staff_data.hire_date is not None:
            staff.hire_date = staff_data.hire_date
        if staff_data.bio is not None:
            staff.bio = staff_data.bio
        if staff_data.profile_image_url is not None:
            staff.profile_image_url = staff_data.profile_image_url
        if staff_data.status is not None:
            staff.status = staff_data.status
        
        if staff_data.role_ids is not None:
            user = User.objects(id=ObjectId(user_id), tenant_id=tenant_id).first()
            if user:
                user.role_ids = [ObjectId(rid) if isinstance(rid, str) else rid for rid in staff_data.role_ids]
                user.save()

        staff.save()
        logger.info(f"Updated staff profile by user ID: {user_id}")
        _sync_service_staff_ids(tenant_id, staff_data.service_ids, staff.id)

        user = User.objects(id=staff.user_id).first()
        return staff_to_response(staff, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update staff by user ID: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to update staff profile")


@router.get("", response_model=dict)
@tenant_isolated
async def list_staff(
    status: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List staff members for the tenant.

    Returns a paginated list of staff members with optional filtering by status and specialty.
    By default, excludes terminated staff from active pickers.
    """
    try:
        # Query staff members - exclude terminated by default for active pickers
        query = Staff.objects(tenant_id=tenant_id, status__ne="terminated")

        # Apply additional filters
        if status:
            query = query(status=status)
        
        if specialty:
            query = query(specialties=specialty)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        staff_members = query.skip(skip).limit(page_size).order_by("-created_at")

        # Get user details for each staff member
        user_ids = [staff.user_id for staff in staff_members]
        users = User.objects(id__in=user_ids).only(
            "id", "first_name", "last_name", "email", "phone", "role_ids"
        )
        user_map = {user.id: user for user in users}

        staff_list = []
        for staff in staff_members:
            user = user_map.get(staff.user_id)
            staff_list.append(staff_to_response(staff, user))

        return {
            "staff": staff_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Failed to list staff: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list staff")


@router.get("/{staff_id}", response_model=dict)
@tenant_isolated
async def get_staff(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific staff member.

    Returns the staff member details for the given staff ID.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        user = User.objects(id=staff.user_id).first()
        return staff_to_response(staff, user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to get staff: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get staff")



@router.post("", response_model=dict)
@tenant_isolated
async def create_staff(
    staff_data: StaffCreate,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new staff member.

    Creates a new staff profile with the provided details.
    If user_id is provided, uses existing user. Otherwise creates a new user.
    """
    try:
        data_dump = staff_data.model_dump()
        logger.info(f"=== BACKEND RECEIVED DATA ===")
        logger.info(f"Full data: {data_dump}")
        logger.info(f"Specialties: {data_dump.get('specialties')} (type: {type(data_dump.get('specialties'))}, len: {len(data_dump.get('specialties', []))})")
        logger.info(f"Certifications: {data_dump.get('certifications')} (type: {type(data_dump.get('certifications'))}, len: {len(data_dump.get('certifications', []))})")
        logger.info(f"Certification Files: {data_dump.get('certification_files')} (type: {type(data_dump.get('certification_files'))}, len: {len(data_dump.get('certification_files', []))})")
        
        user_id = staff_data.user_id
        user = None
        temp_password = None
        
        # If user_id is provided and not None/empty, validate it exists
        if user_id and user_id.strip():
            try:
                user = User.objects(id=ObjectId(user_id), tenant_id=tenant_id).first()
                if not user:
                    logger.error(f"User not found for user_id: {user_id}")
                    raise HTTPException(status_code=400, detail="User not found")
            except Exception as e:
                logger.error(f"Invalid user_id format: {user_id}, error: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid user_id format")
        else:
            # Create a new user if user_id is not provided
            logger.info(f"Creating new user for staff: {staff_data.email}")
            # Generate a temporary password (should be changed by user)
            import secrets
            from app.services.auth_service import AuthenticationService
            from app.config import settings
            
            temp_password = secrets.token_urlsafe(12)
            
            try:
                # Check if user with this email already exists
                existing_user = User.objects(email=staff_data.email, tenant_id=tenant_id).first()
                if existing_user:
                    logger.error(f"User with email {staff_data.email} already exists")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"A user with email '{staff_data.email}' already exists in your salon. Please use a different email address."
                    )
                
                user = User(
                    tenant_id=tenant_id,
                    email=staff_data.email,
                    first_name=staff_data.firstName,
                    last_name=staff_data.lastName,
                    phone=staff_data.phone,
                    status="active"
                )
                
                # Hash password using AuthenticationService
                auth_service = AuthenticationService(settings)
                user.password_hash = auth_service.hash_password(temp_password)
                
                # Force password change on first login
                user.password_change_required = True
                
                # Assign staff role if provided
                if staff_data.role_ids:
                    user.role_ids = [ObjectId(rid) if isinstance(rid, str) else rid for rid in staff_data.role_ids]
                
                user.save()
                user_id = str(user.id)
                logger.info(f"Created new user for staff: {user_id}")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to create user: {str(e)}", exc_info=True)
                # Check if it's a duplicate key error
                error_str = str(e)
                if "E11000" in error_str or "duplicate key" in error_str:
                    # Extract email from error if possible
                    email = staff_data.email
                    raise HTTPException(
                        status_code=400, 
                        detail=f"A user with email '{email}' already exists in your salon. Please use a different email address."
                    )
                raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")

        # Check if staff profile already exists for this user
        existing_staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if existing_staff:
            logger.error(f"Staff profile already exists for user: {user_id}")
            raise HTTPException(status_code=400, detail="Staff profile already exists for this user")

        # Create new staff profile
        try:
            new_staff = Staff(
                tenant_id=tenant_id,
                user_id=ObjectId(user_id),
                service_ids=[ObjectId(sid) if isinstance(sid, str) else sid for sid in (staff_data.service_ids or [])],
                specialties=staff_data.specialties,
                certifications=staff_data.certifications,
                certification_files=staff_data.certification_files,
                payment_type=staff_data.payment_type,
                payment_rate=staff_data.payment_rate,
                hire_date=staff_data.hire_date,
                bio=staff_data.bio,
                profile_image_url=staff_data.profile_image_url,
                status=staff_data.status,
            )
            
            new_staff.save()
            logger.info(f"Created staff profile for user: {user_id}")
            _sync_service_staff_ids(tenant_id, staff_data.service_ids, new_staff.id)
        except Exception as e:
            logger.error(f"Failed to create staff profile: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Failed to create staff profile: {str(e)}")
        
        # Send email with temporary password if new user was created
        if temp_password:
            try:
                from app.tasks import send_email
                from app.models.tenant import Tenant
                from app.models.role import Role
                
                logger.info(f"[StaffEmail] Preparing welcome email for new staff user={user_id} email={staff_data.email}")
                
                # Fetch tenant name and logo for email branding
                tenant = Tenant.objects(id=tenant_id).first()
                salon_name = tenant.name if tenant else "your salon"
                salon_logo_url = tenant.logo_url if tenant and tenant.logo_url else None
                salon_subdomain = tenant.subdomain if tenant else None
                
                # Get role names
                role_names = []
                if user.role_ids:
                    roles = Role.objects(id__in=user.role_ids).only('name')
                    role_names = [role.name for role in roles]
                
                # Build tenant-specific login URL
                if salon_subdomain:
                    # Use subdomain-based URL
                    login_url = f"https://{salon_subdomain}.{settings.platform_domain}/login"
                else:
                    # Fallback to frontend URL
                    login_url = f"{settings.frontend_url}/login"
                
                logger.info(f"[StaffEmail] Sending welcome email to={staff_data.email} salon={salon_name} roles={role_names}")
                
                result = send_email(
                    to=staff_data.email,
                    subject=f"Welcome to {salon_name} - Staff Account Created",
                    template="staff_welcome",
                    context={
                        "first_name": staff_data.firstName,
                        "last_name": staff_data.lastName,
                        "email": staff_data.email,
                        "temp_password": temp_password,
                        "salon_name": salon_name,
                        "salon_logo_url": salon_logo_url,
                        "roles": role_names,
                        "login_url": login_url,
                    }
                )
                
                logger.info(f"[StaffEmail] Sent welcome email to staff={staff_data.email} result={result}")
            except Exception as e:
                logger.error(f"[StaffEmail] Failed to send welcome email to staff={staff_data.email} error={str(e)}", exc_info=True)
                raise
        
        # Initialize staff settings for the new staff member
        try:
            from app.models.staff_settings import StaffSettings
            
            staff_settings = StaffSettings(
                tenant_id=tenant_id,
                user_id=ObjectId(user_id),
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone or "",
                email_bookings=True,
                email_reminders=True,
                email_messages=True,
                sms_bookings=False,
                sms_reminders=False,
                push_bookings=True,
                push_reminders=True,
            )
            staff_settings.save()
            logger.info(f"Created staff settings for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to create staff settings: {str(e)}")
            # Don't fail the request if settings creation fails
        
        # Auto-create default availability from tenant business hours
        try:
            from app.models.availability import Availability
            from app.models.tenant import Tenant
            from app.services.tenant_settings_service import TenantSettingsService
            
            tenant_settings = TenantSettingsService.get_settings(str(tenant_id))
            business_hours = tenant_settings.get("business_hours") if tenant_settings else None
            
            if not business_hours:
                business_hours = {
                    "monday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "tuesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "wednesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "thursday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "friday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "saturday": {"open_time": "10:00", "close_time": "16:00", "is_closed": False},
                    "sunday": {"open_time": "00:00", "close_time": "00:00", "is_closed": True},
                }
            
            day_map = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6,
            }
            
            created_availability = []
            for day_name, hours in business_hours.items():
                if hours.get("is_closed"):
                    continue
                
                day_of_week = day_map.get(day_name)
                if day_of_week is None:
                    continue
                
                open_time = hours["open_time"]
                close_time = hours["close_time"]
                
                if len(open_time) == 5:
                    open_time = f"{open_time}:00"
                if len(close_time) == 5:
                    close_time = f"{close_time}:00"
                
                availability = Availability(
                    tenant_id=tenant_id,
                    staff_id=new_staff.id,
                    day_of_week=day_of_week,
                    start_time=open_time,
                    end_time=close_time,
                    is_recurring=True,
                    effective_from=date.today(),
                    effective_to=None,
                    breaks=[],
                    slot_interval_minutes=30,
                    buffer_time_minutes=15,
                    concurrent_bookings_allowed=1,
                    is_active=True,
                    notes=f"Default availability from business hours ({day_name})",
                )
                availability.save()
                created_availability.append(f"{day_name}:{open_time}-{close_time}")
            
            logger.info(f"[StaffCreate] Created {len(created_availability)} default availability records for staff {new_staff.id}: {created_availability}")
        except Exception as e:
            logger.error(f"Failed to create default availability for staff {new_staff.id}: {str(e)}", exc_info=True)
        
        return staff_to_response(new_staff, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create staff: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to create staff: {str(e)}")


@router.put("/{staff_id}", response_model=dict)
@tenant_isolated
async def update_staff(
    staff_id: str,
    staff_data: StaffUpdate,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update a staff member.

    Updates the staff profile details for the given staff ID.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")

        # Update fields
        if staff_data.service_ids is not None:
            staff.service_ids = [ObjectId(sid) if isinstance(sid, str) else sid for sid in staff_data.service_ids]
        if staff_data.specialties is not None:
            staff.specialties = staff_data.specialties
        if staff_data.certifications is not None:
            staff.certifications = staff_data.certifications
        if staff_data.certification_files is not None:
            staff.certification_files = staff_data.certification_files
        if staff_data.payment_type is not None:
            staff.payment_type = staff_data.payment_type
        if staff_data.payment_rate is not None:
            staff.payment_rate = staff_data.payment_rate
        if staff_data.hire_date is not None:
            staff.hire_date = staff_data.hire_date
        if staff_data.bio is not None:
            staff.bio = staff_data.bio
        if staff_data.profile_image_url is not None:
            staff.profile_image_url = staff_data.profile_image_url
        if staff_data.status is not None:
            staff.status = staff_data.status
        
        # Update role_ids on the associated user account
        if staff_data.role_ids is not None:
            user = User.objects(id=staff.user_id, tenant_id=tenant_id).first()
            if user:
                user.role_ids = [ObjectId(rid) if isinstance(rid, str) else rid for rid in staff_data.role_ids]
                user.save()

        staff.save()
        logger.info(f"Updated staff profile: {staff.id}")
        _sync_service_staff_ids(tenant_id, staff_data.service_ids, staff.id)

        user = User.objects(id=staff.user_id).first()
        return staff_to_response(staff, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update staff: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update staff")


@router.delete("/{staff_id}", response_model=dict)
@tenant_isolated
async def delete_staff(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Soft delete a staff member by marking as terminated.
    
    This preserves historical appointment data while preventing
    the staff member from being assigned to new bookings.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")

        staff.status = "terminated"
        staff.save()
        logger.info(f"Staff soft deleted (terminated): {staff_id}")
        
        return {"message": "Staff member terminated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete staff: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to delete staff")


@router.post("/{staff_id}/certificates", response_model=dict)
@tenant_isolated
async def upload_staff_certificate(
    staff_id: str,
    request: dict,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Upload a certificate file for a staff member.

    Accepts base64 encoded file data and stores the URL in certification_files.
    """
    try:
        from app.services.media_service import upload_media, MediaUploadError
        
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        # Extract base64 data from request
        base64_data = request.get("base64_data")
        if not base64_data:
            raise HTTPException(status_code=400, detail="base64_data is required")
        
        # Upload to Cloudinary
        try:
            url = upload_media(
                base64_data=base64_data,
                media_type="document",
                folder="staff-certificates",
            )
        except MediaUploadError as e:
            logger.error(f"Certificate upload failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Add URL to certification_files if not already present
        if url not in staff.certification_files:
            staff.certification_files.append(url)
            staff.save()
            logger.info(f"Added certificate for staff {staff_id}: {url}")
        
        return {
            "message": "Certificate uploaded successfully",
            "url": url,
            "certification_files": staff.certification_files,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload certificate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to upload certificate")


@router.delete("/{staff_id}/certificates/{file_url}", response_model=dict)
@tenant_isolated
async def delete_staff_certificate(
    staff_id: str,
    file_url: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Delete a certificate file for a staff member.

    Removes the certificate URL from the staff member's certification_files list.
    """
    try:
        from urllib.parse import unquote
        
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        # URL decode the file_url parameter
        decoded_url = unquote(file_url)
        
        # Remove URL from certification_files
        if decoded_url in staff.certification_files:
            staff.certification_files.remove(decoded_url)
            staff.save()
            logger.info(f"Removed certificate for staff {staff_id}: {decoded_url}")
        
        return {
            "message": "Certificate deleted successfully",
            "certification_files": staff.certification_files,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete certificate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to delete certificate")


@router.get("/{staff_id}/payment-structure", response_model=dict)
@tenant_isolated
async def get_staff_payment_structure(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get staff payment structure information."""
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        user = User.objects(id=staff.user_id, tenant_id=tenant_id).first()
        
        return {
            "payment_type": staff.payment_type,
            "payment_rate": float(staff.payment_rate),
            "staff_name": f"{user.first_name if user else ''} {user.last_name if user else ''}".strip(),
            "hire_date": staff.hire_date.isoformat() if staff.hire_date else None,
            "status": staff.status,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment structure: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get payment structure")


@router.get("/user/{user_id}/payment-structure", response_model=dict)
@tenant_isolated
async def get_staff_payment_structure_by_user(
    user_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get staff payment structure by user ID."""
    try:
        staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff profile not found for this user")
        
        user = User.objects(id=ObjectId(user_id), tenant_id=tenant_id).first()
        
        return {
            "payment_type": staff.payment_type,
            "payment_rate": float(staff.payment_rate),
            "staff_name": f"{user.first_name if user else ''} {user.last_name if user else ''}".strip(),
            "hire_date": staff.hire_date.isoformat() if staff.hire_date else None,
            "status": staff.status,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment structure: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get payment structure")


@router.get("/{staff_id}/metrics", response_model=dict)
@tenant_isolated
async def get_staff_metrics(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get dashboard metrics for a staff member.

    Returns today's appointments, upcoming shifts, pending time off, and earnings summary.
    Validates that the staff member belongs to the tenant.
    """
    try:
        # Verify staff member exists and belongs to tenant
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get today's appointments
        today_appointments = Appointment.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_time__gte=today_start,
            start_time__lt=today_end,
            status__in=["scheduled", "confirmed", "in_progress", "completed"],
        ).count()
        
        # Get upcoming shifts
        upcoming_shifts = Shift.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_time__gte=now,
            status__in=["scheduled", "in_progress"],
        ).count()
        
        # Get pending time off requests
        pending_time_off = TimeOffRequest.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status="pending",
        ).count()
        
        # Get earnings summary
        commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        )
        
        total_earnings = sum(
            (c.commission_amount for c in commissions),
            0
        )
        
        # Calculate this month and this week earnings
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        this_month_earnings = sum(
            (c.commission_amount for c in commissions if c.created_at >= month_start),
            0
        )
        
        this_week_earnings = sum(
            (c.commission_amount for c in commissions if c.created_at >= week_start),
            0
        )
        
        return {
            "todayAppointments": today_appointments,
            "upcomingShifts": upcoming_shifts,
            "pendingTimeOff": pending_time_off,
            "earningsSummary": {
                "total": float(total_earnings),
                "thisMonth": float(this_month_earnings),
                "thisWeek": float(this_week_earnings),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get staff metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get staff metrics")


@router.get("/{staff_id}/activity-feed", response_model=dict)
@tenant_isolated
async def get_staff_activity_feed(
    staff_id: str,
    limit: int = Query(10, ge=1, le=50),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get recent activity feed for a staff member.

    Returns the last N events (appointments, shifts, time off, earnings, reviews).
    Validates that the staff member belongs to the tenant.
    """
    try:
        # Verify staff member exists and belongs to tenant
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        events = []
        
        # Get recent appointments
        recent_appointments = Appointment.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        ).order_by("-updated_at").limit(limit)
        
        for appt in recent_appointments:
            customer = appt.customer_id
            customer_name = "Unknown Customer"
            if customer:
                from app.models.customer import Customer
                cust = Customer.objects(id=customer).first()
                if cust:
                    customer_name = f"{cust.first_name} {cust.last_name}".strip()
            
            events.append({
                "id": str(appt.id),
                "type": "appointment",
                "title": f"Appointment with {customer_name}",
                "description": f"Status: {appt.status}",
                "timestamp": appt.updated_at.isoformat(),
                "metadata": {
                    "appointmentId": str(appt.id),
                    "status": appt.status,
                },
            })
        
        # Get recent shifts
        recent_shifts = Shift.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        ).order_by("-updated_at").limit(limit)
        
        for shift in recent_shifts:
            events.append({
                "id": str(shift.id),
                "type": "shift",
                "title": f"Shift on {shift.start_time.strftime('%b %d')}",
                "description": f"Status: {shift.status}",
                "timestamp": shift.updated_at.isoformat(),
                "metadata": {
                    "shiftId": str(shift.id),
                    "status": shift.status,
                },
            })
        
        # Get recent time off requests
        recent_time_off = TimeOffRequest.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        ).order_by("-updated_at").limit(limit)
        
        for time_off in recent_time_off:
            events.append({
                "id": str(time_off.id),
                "type": "timeoff",
                "title": f"Time Off Request",
                "description": f"Status: {time_off.status}",
                "timestamp": time_off.updated_at.isoformat(),
                "metadata": {
                    "timeOffId": str(time_off.id),
                    "status": time_off.status,
                },
            })
        
        # Get recent commissions
        recent_commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        ).order_by("-created_at").limit(limit)
        
        for commission in recent_commissions:
            events.append({
                "id": str(commission.id),
                "type": "earnings",
                "title": f"Commission Earned",
                "description": f"Amount: ₦{float(commission.commission_amount):.2f}",
                "timestamp": commission.created_at.isoformat(),
                "metadata": {
                    "commissionId": str(commission.id),
                    "amount": float(commission.commission_amount),
                },
            })
        
        # Sort by timestamp descending and limit to requested count
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        events = events[:limit]
        
        return {
            "events": events,
            "total": len(events),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get activity feed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get activity feed")


@router.get("/{staff_id}/performance-metrics", response_model=dict)
@tenant_isolated
async def get_staff_performance_metrics(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get performance metrics for a staff member.

    Returns ratings, appointment stats, and customer satisfaction derived from appointment history.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")

        completed_appointments = Appointment.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status="completed",
        )
        total_completed = completed_appointments.count()

        reviews = AppointmentHistory.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            rating__gt=0,
        )

        total_reviews = reviews.count()
        avg_rating = reviews.average("rating") if total_reviews > 0 else (float(staff.rating) if staff.rating else 0.0)

        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for r in reviews:
            star = max(1, min(5, r.rating))
            rating_distribution[str(star)] += 1

        total_earnings = sum(c.commission_amount for c in StaffCommission.objects(tenant_id=tenant_id, staff_id=ObjectId(staff_id)))

        recent_reviews = []
        for r in reviews.order_by("-appointment_date").limit(10):
            recent_reviews.append({
                "id": str(r.id),
                "customerId": str(r.customer_id),
                "customerName": "",
                "appointmentId": str(r.appointment_id),
                "serviceName": "",
                "rating": r.rating,
                "feedback": r.feedback or "",
                "appointmentDate": r.appointment_date.isoformat(),
                "createdAt": r.created_at.isoformat(),
            })

        return {
            "averageRating": round(avg_rating, 1),
            "totalReviews": total_reviews,
            "appointmentsCompleted": total_completed,
            "customerSatisfaction": min(100, int((avg_rating / 5) * 100)),
            "totalEarnings": round(float(total_earnings), 2),
            "ratingDistribution": rating_distribution,
            "recentReviews": recent_reviews,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get performance metrics")


@router.get("/{staff_id}/reviews", response_model=dict)
@tenant_isolated
async def get_staff_reviews(
    staff_id: str,
    limit: int = Query(25, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get customer reviews for a staff member.

    Returns recent reviews sorted by appointment date descending.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")

        reviews = AppointmentHistory.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            rating__gt=0,
        ).order_by("-appointment_date").limit(limit)

        result = []
        for r in reviews:
            result.append({
                "id": str(r.id),
                "customerId": str(r.customer_id),
                "customerName": "",
                "appointmentId": str(r.appointment_id),
                "serviceName": "",
                "rating": r.rating,
                "feedback": r.feedback or "",
                "appointmentDate": r.appointment_date.isoformat(),
                "createdAt": r.created_at.isoformat(),
            })

        return {"reviews": result, "total": reviews.count()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reviews: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get reviews")


