"""Staff management routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from bson import ObjectId
from app.models.staff import Staff
from app.models.user import User
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
        user = User.objects(id=staff.user_id).first()
    
    return {
        "id": str(staff.id),
        "user_id": str(staff.user_id),
        "firstName": user.first_name if user else "",
        "lastName": user.last_name if user else "",
        "email": user.email if user else "",
        "phone": user.phone if user else "",
        "specialties": staff.specialties,
        "certifications": staff.certifications,
        "certification_files": staff.certification_files,
        "payment_type": staff.payment_type,
        "payment_rate": float(staff.payment_rate),
        "hire_date": staff.hire_date.isoformat() if staff.hire_date else None,
        "bio": staff.bio,
        "profile_image_url": staff.profile_image_url,
        "status": staff.status,
        "createdAt": staff.created_at.isoformat(),
        "updatedAt": staff.updated_at.isoformat(),
    }


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
    """
    try:
        # Query staff members
        query = Staff.objects(tenant_id=tenant_id)

        # Apply filters
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
        staff_list = []
        for staff in staff_members:
            user = User.objects(id=staff.user_id).first()
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
        logger.info(f"Creating staff with data: {staff_data}")
        
        user_id = staff_data.user_id
        user = None
        temp_password = None
        
        # If user_id is provided and not None/empty, validate it exists
        if user_id and user_id.strip():
            try:
                user = User.objects(id=ObjectId(user_id), tenant_id=tenant_id).first()
                if not user:
                    raise HTTPException(status_code=400, detail="User not found")
            except Exception as e:
                logger.error(f"Invalid user_id format: {user_id}")
                raise HTTPException(status_code=400, detail="Invalid user_id format")
        else:
            # Create a new user if user_id is not provided
            # Generate a temporary password (should be changed by user)
            import secrets
            from app.services.auth_service import AuthenticationService
            from app.config import settings
            
            temp_password = secrets.token_urlsafe(12)
            
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
            
            # Assign staff role if provided
            if staff_data.role_ids:
                user.role_ids = [ObjectId(rid) if isinstance(rid, str) else rid for rid in staff_data.role_ids]
            
            user.save()
            user_id = str(user.id)
            logger.info(f"Created new user for staff: {user_id}")

        # Check if staff profile already exists for this user
        existing_staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if existing_staff:
            raise HTTPException(status_code=400, detail="Staff profile already exists for this user")

        # Create new staff profile
        new_staff = Staff(
            tenant_id=tenant_id,
            user_id=ObjectId(user_id),
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
        
        # Send email with temporary password if new user was created
        if temp_password:
            try:
                from app.tasks import send_email
                from app.models.tenant import Tenant
                from app.models.role import Role
                
                # Fetch tenant name for email branding
                tenant = Tenant.objects(id=tenant_id).first()
                salon_name = tenant.name if tenant else "your salon"
                
                # Get role names
                role_names = []
                if user.role_ids:
                    roles = Role.objects(id__in=user.role_ids).only('name')
                    role_names = [role.name for role in roles]
                
                # Build login URL (adjust based on your frontend URL)
                login_url = f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else "https://your-salon.com/login"
                
                send_email.delay(
                    to=staff_data.email,
                    subject=f"Welcome to {salon_name} - Staff Account Created",
                    template="staff_welcome",
                    context={
                        "first_name": staff_data.firstName,
                        "last_name": staff_data.lastName,
                        "email": staff_data.email,
                        "temp_password": temp_password,
                        "salon_name": salon_name,
                        "roles": role_names,
                        "login_url": login_url,
                    }
                )
                logger.info(f"Sent welcome email to staff: {staff_data.email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")
                # Don't fail the request if email fails
        
        return staff_to_response(new_staff, user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create staff: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create staff")


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
        if staff_data.specialties is not None:
            staff.specialties = staff_data.specialties
        if staff_data.certifications is not None:
            staff.certifications = staff_data.certifications
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

        staff.save()
        logger.info(f"Updated staff profile: {staff.id}")
        
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
    Delete a staff member.

    Deletes the staff profile for the given staff ID.
    """
    try:
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff member not found")

        staff_id_str = str(staff.id)
        staff.delete()
        logger.info(f"Deleted staff profile: {staff_id_str}")
        return {"message": "Staff member deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete staff: {str(e)}")
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
