"""Customer Authentication Routes"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from bson import ObjectId
from app.schemas.customer_auth import (
    CustomerRegister,
    CustomerToken,
    CustomerProfile,
    CustomerProfileUpdate
)
from app.services.customer_auth_service import CustomerAuthService
from app.middleware.tenant_context import get_tenant_id
from app.middleware.customer_auth import get_current_customer
from app.models.customer import Customer
from app.models.tenant import Tenant

router = APIRouter(prefix="/public/customer-auth", tags=["Customer Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_customer(
    request: Request,
    customer_data: CustomerRegister
):
    """Register a new customer account"""
    tenant_id = get_tenant_id(request)
    
    try:
        customer = CustomerAuthService.register_customer(
            tenant_id=tenant_id,
            email=customer_data.email,
            phone=customer_data.phone,
            password=customer_data.password,
            first_name=customer_data.first_name,
            last_name=customer_data.last_name
        )
        
        # Send verification email
        CustomerAuthService.send_verification_email(customer)
        
        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "customer_id": str(customer.id)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=CustomerToken)
async def login_customer(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Customer login"""
    tenant_id = get_tenant_id(request)
    
    customer = CustomerAuthService.authenticate_customer(
        tenant_id=tenant_id,
        email=form_data.username,
        password=form_data.password
    )
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = CustomerAuthService.create_access_token(customer)
    
    return CustomerToken(
        access_token=token,
        token_type="bearer",
        customer_id=str(customer.id),
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name
    )


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    """Verify customer email"""
    success = CustomerAuthService.verify_email_token(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.get("/me", response_model=CustomerProfile)
async def get_current_customer_profile(
    current_customer: Customer = Depends(get_current_customer)
):
    """Get current customer profile"""
    return CustomerProfile(
        id=str(current_customer.id),
        email=current_customer.email,
        first_name=current_customer.first_name,
        last_name=current_customer.last_name,
        phone=current_customer.phone,
        address=current_customer.address,
        date_of_birth=str(current_customer.date_of_birth) if current_customer.date_of_birth else None,
        email_verified=current_customer.email_verified,
        phone_verified=current_customer.phone_verified,
        communication_preference=current_customer.communication_preference,
        notification_preferences=current_customer.notification_preferences,
        outstanding_balance=float(current_customer.outstanding_balance),
        created_at=current_customer.created_at
    )


@router.put("/me", response_model=CustomerProfile)
async def update_customer_profile(
    profile_data: CustomerProfileUpdate,
    current_customer: Customer = Depends(get_current_customer)
):
    """Update customer profile"""
    update_data = profile_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if hasattr(current_customer, key):
            setattr(current_customer, key, value)
    
    current_customer.updated_at = datetime.utcnow()
    current_customer.save()
    
    return CustomerProfile(
        id=str(current_customer.id),
        email=current_customer.email,
        first_name=current_customer.first_name,
        last_name=current_customer.last_name,
        phone=current_customer.phone,
        address=current_customer.address,
        date_of_birth=str(current_customer.date_of_birth) if current_customer.date_of_birth else None,
        email_verified=current_customer.email_verified,
        phone_verified=current_customer.phone_verified,
        communication_preference=current_customer.communication_preference,
        notification_preferences=current_customer.notification_preferences,
        outstanding_balance=float(current_customer.outstanding_balance),
        created_at=current_customer.created_at
    )


@router.post("/setup-password")
async def setup_customer_password(
    request: Request,
    data: dict = Body(...)
):
    """
    Set up password for customer created by owner.
    
    This endpoint allows customers who were created by business owners
    to set up their password and access the customer portal.
    """
    tenant_id = get_tenant_id(request)
    
    token = data.get("token")
    password = data.get("password")
    
    if not token or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and password are required"
        )
    
    # Find customer with this token
    customer = Customer.objects(
        tenant_id=tenant_id,
        password_reset_token=token
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired setup token"
        )
    
    # Check if token is expired
    if customer.password_reset_expires and customer.password_reset_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup token has expired. Please contact the business to resend the invitation."
        )
    
    # Set password
    customer.password_hash = CustomerAuthService.hash_password(password)
    customer.password_reset_token = None
    customer.password_reset_expires = None
    customer.email_verified = True  # Auto-verify since they came from owner invitation
    customer.updated_at = datetime.utcnow()
    customer.save()
    
    # Create access token
    access_token = CustomerAuthService.create_access_token(customer)
    
    return {
        "message": "Password set up successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "customer_id": str(customer.id),
        "email": customer.email,
        "first_name": customer.first_name,
        "last_name": customer.last_name
    }


@router.post("/resend-setup-invitation/{customer_id}")
async def resend_setup_invitation(
    request: Request,
    customer_id: str
):
    """
    Resend password setup invitation to customer.
    
    This endpoint allows business owners to resend the setup invitation
    if the customer didn't receive it or the token expired.
    """
    tenant_id = get_tenant_id(request)
    
    try:
        customer = Customer.objects(id=ObjectId(customer_id), tenant_id=tenant_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check if customer already has a password
        if customer.password_hash:
            raise HTTPException(
                status_code=400,
                detail="Customer already has portal access"
            )
        
        # Generate new setup token
        import secrets
        setup_token = secrets.token_urlsafe(32)
        customer.password_reset_token = setup_token
        customer.password_reset_expires = datetime.utcnow() + timedelta(days=7)
        customer.save()
        
        # Send setup email
        from app.tasks import send_email
        from app.config import settings
        from app.services.email_template_service import EmailTemplateService
        
        tenant = Tenant.objects(id=tenant_id).first()
        if tenant:
            platform_domain = settings.platform_domain
            setup_url = f"https://{tenant.subdomain}.{platform_domain}/customer/setup-password?token={setup_token}"
            booking_url = f"https://{tenant.subdomain}.{platform_domain}/book"
            
            tenant_settings = tenant.settings or {}
            
            email_context = {
                "customer_name": f"{customer.first_name} {customer.last_name}",
                "customer_email": customer.email,
                "customer_phone": customer.phone,
                "business_name": tenant.name,
                "business_address": tenant.address,
                "business_phone": tenant_settings.get("phone"),
                "business_email": tenant_settings.get("email"),
                "logo_url": tenant.logo_url,
                "primary_color": tenant.primary_color or "#6366f1",
                "secondary_color": tenant.secondary_color or "#8b5cf6",
                "booking_url": booking_url,
                "setup_url": setup_url,
            }
            
            rendered_html = EmailTemplateService.render_customer_welcome_email(
                str(tenant_id),
                email_context
            )
            
            if rendered_html:
                send_email.delay(
                    to=customer.email,
                    subject=f"Set up your {tenant.name} customer portal access",
                    template="custom",
                    context={"html_content": rendered_html},
                )
        
        return {"message": "Setup invitation sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resend setup invitation: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to resend setup invitation")
