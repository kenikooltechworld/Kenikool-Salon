"""Registration routes for salon owner registration."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.registration_service import RegistrationService
from app.services.auth_service import AuthenticationService
from app.services.rbac_service import RBACService
from app.config import settings
from app.schemas.registration import (
    RegisterRequest,
    RegisterResponse,
    VerifyCodeRequest,
    VerifyCodeResponse,
    ResendCodeRequest,
    ResendCodeResponse,
)
from app.tasks import send_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["registration"])


def get_registration_service() -> RegistrationService:
    """Get registration service."""
    return RegistrationService(settings)


def get_auth_service() -> AuthenticationService:
    """Get authentication service."""
    return AuthenticationService(settings)


def get_rbac_service() -> RBACService:
    """Get RBAC service."""
    return RBACService()


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: Request,
    register_request: RegisterRequest,
    registration_service: RegistrationService = Depends(get_registration_service),
):
    """
    Register a new salon owner (Phase 1: Validation).
    
    Validates registration data and sends verification code via email.
    Rate limited to 5 requests per minute per IP.
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Validate registration data
    is_valid, error_message = registration_service.validate_registration_data(
        register_request.dict()
    )
    if not is_valid:
        logger.warning(f"Registration validation failed for {register_request.email}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Check uniqueness
    is_unique, error_message = registration_service.check_uniqueness(
        register_request.email,
        register_request.phone,
        register_request.salon_name,
    )
    if not is_unique:
        logger.warning(f"Registration uniqueness check failed for {register_request.email}: {error_message}")
        raise HTTPException(status_code=409, detail=error_message)

    # Create temporary registration
    try:
        temp_reg_data = registration_service.create_temp_registration(
            register_request.dict()
        )
        
        # Send verification email asynchronously
        send_email.delay(
            to=register_request.email,
            subject="Verify Your Salon Registration",
            template="registration_verification",
            context={
                "salon_name": register_request.salon_name,
                "verification_code": temp_reg_data["verification_code"],
                "expires_in_minutes": 15,
            },
        )

        # Only save temp_reg after email is sent successfully
        temp_reg_object = temp_reg_data["temp_reg_object"]
        temp_reg_object.save()

        logger.info(f"Registration created for {register_request.email}")

        return RegisterResponse(
            success=True,
            message="Verification code sent to your email",
            data={
                "temp_registration_id": str(temp_reg_object.id),
                "email": temp_reg_data["email"],
                "expires_at": temp_reg_data["verification_code_expires"],
            },
        )

    except Exception as e:
        logger.error(f"Error creating registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create registration")


@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(
    verify_request: VerifyCodeRequest,
    registration_service: RegistrationService = Depends(get_registration_service),
    auth_service: AuthenticationService = Depends(get_auth_service),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    Verify registration code and create accounts (Phase 3: Verification).
    
    Creates tenant, user, and subscription if code is valid.
    Rate limited to 10 requests per minute per email.
    """
    # Verify code and create accounts
    success, error_message, account_data = registration_service.verify_code(
        verify_request.email,
        verify_request.code,
    )

    if not success:
        logger.warning(f"Code verification failed for {verify_request.email}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Create JWT tokens for new user
    try:
        permissions = rbac_service.get_user_permissions(
            account_data["user_id"],
            account_data["tenant_id"],
        )

        access_token = auth_service.create_access_token(
            user_id=account_data["user_id"],
            tenant_id=account_data["tenant_id"],
            email=account_data["email"],
            role_ids=account_data["role_ids"],  # Multiple roles
            permissions=permissions,
        )

        refresh_token = auth_service.create_refresh_token(
            user_id=account_data["user_id"],
            tenant_id=account_data["tenant_id"],
        )

        # Send welcome email asynchronously
        try:
            send_email.delay(
                to=account_data["email"],
                subject="Welcome to Kenikool!",
                template="welcome",
                context={
                    "owner_name": account_data.get("owner_name", ""),
                    "salon_name": account_data.get("salon_name", ""),
                    "email": account_data["email"],
                    "full_url": account_data["full_url"],
                    "subscription_tier": "Trial (30 days)",
                },
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {account_data['email']}: {str(e)}")
            # Don't fail the registration if email fails, just log it

        logger.info(f"Registration verified for {verify_request.email}")

        return VerifyCodeResponse(
            success=True,
            message="Registration verified successfully",
            data={
                "tenant_id": account_data["tenant_id"],
                "subdomain": account_data["subdomain"],
                "full_url": account_data["full_url"],
                "user_id": account_data["user_id"],
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        )

    except Exception as e:
        logger.error(f"Error verifying code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify code")


@router.post("/resend-code", response_model=ResendCodeResponse)
async def resend_code(
    resend_request: ResendCodeRequest,
    registration_service: RegistrationService = Depends(get_registration_service),
):
    """
    Resend verification code to email.
    
    Rate limited to 3 requests per minute per email.
    """
    # Resend verification code
    success, error_message, verification_code = registration_service.resend_verification_code(
        resend_request.email
    )

    if not success:
        logger.warning(f"Resend code failed for {resend_request.email}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Send verification email asynchronously
    try:
        send_email.delay(
            to=resend_request.email,
            subject="Your New Verification Code",
            template="registration_verification",
            context={
                "verification_code": verification_code,
                "expires_in_minutes": 15,
            },
        )

        logger.info(f"Verification code resent for {resend_request.email}")

        # Get the updated temp registration to return the new expiration time
        from app.models.temp_registration import TempRegistration
        temp_reg = TempRegistration.objects(email=resend_request.email).first()
        
        return ResendCodeResponse(
            success=True,
            message="New verification code sent to your email",
            data={
                "expires_at": temp_reg.verification_code_expires.isoformat() + "Z" if temp_reg else None,
            } if temp_reg else None,
        )

    except Exception as e:
        logger.error(f"Error resending code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resend code")
