"""Authentication routes with httpOnly cookies and CSRF protection."""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from app.services.auth_service import AuthenticationService
from app.services.rbac_service import RBACService
from app.config import Settings, settings
from app.context import get_tenant_id, set_tenant_id, set_user_id
from app.models.user import User
from app.models.role import Role
from app.models.session import Session
from app.middleware.rate_limit import (
    get_login_attempts,
    increment_login_attempts,
    reset_login_attempts,
    is_account_locked,
    lock_account,
)
from app.middleware.enumeration_prevention import (
    get_generic_error_message,
    constant_time_compare,
    add_timing_delay,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response schema."""

    message: str
    csrf_token: str


class LogoutRequest(BaseModel):
    """Logout request schema."""

    pass


class LogoutResponse(BaseModel):
    """Logout response schema."""

    message: str


class CSRFTokenResponse(BaseModel):
    """CSRF token response schema."""

    csrf_token: str


def get_auth_service() -> AuthenticationService:
    """Get authentication service."""
    return AuthenticationService(settings)


def get_rbac_service() -> RBACService:
    """Get RBAC service."""
    return RBACService()


async def get_current_user_dependency(
    request: Request,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Dependency function to get current user from JWT token in httpOnly cookie.

    Handles token refresh if access_token is expired but refresh_token is valid.
    Returns user data dict with id, email, tenant_id, role_ids, role_names, etc.
    Raises HTTPException if user is not authenticated.
    """
    is_secure = settings.environment != "development"
    
    # Get tokens from cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    # If no access token, try to refresh using refresh token
    if not access_token:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Try to refresh the access token
        try:
            new_access_token = auth_service.refresh_access_token(refresh_token)
            if not new_access_token:
                # Clear all invalid tokens immediately
                response.delete_cookie("refresh_token", path="/", secure=is_secure, httponly=True)
                response.delete_cookie("access_token", path="/", secure=is_secure, httponly=True)
                response.delete_cookie("session_id", path="/", secure=is_secure, httponly=True)
                response.delete_cookie("tenant_id", path="/", secure=is_secure, httponly=True)
                response.delete_cookie("user_id", path="/", secure=is_secure, httponly=True)
                raise HTTPException(status_code=401, detail="Unauthorized")

            # Set new access token in response cookie
            response.set_cookie(
                "access_token",
                new_access_token,
                max_age=auth_service.access_token_expire_minutes * 60,
                httponly=True,
                secure=is_secure,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )
            access_token = new_access_token
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
            # Clear all invalid tokens on refresh failure
            response.delete_cookie("refresh_token", path="/", secure=is_secure, httponly=True)
            response.delete_cookie("access_token", path="/", secure=is_secure, httponly=True)
            response.delete_cookie("session_id", path="/", secure=is_secure, httponly=True)
            response.delete_cookie("tenant_id", path="/", secure=is_secure, httponly=True)
            response.delete_cookie("user_id", path="/", secure=is_secure, httponly=True)
            raise HTTPException(status_code=401, detail="Unauthorized")

    # Verify token and extract claims
    payload = auth_service.verify_token(access_token)
    if not payload:
        # Token is invalid or expired - clear all cookies
        response.delete_cookie("refresh_token", path="/", secure=is_secure, httponly=True)
        response.delete_cookie("access_token", path="/", secure=is_secure, httponly=True)
        response.delete_cookie("session_id", path="/", secure=is_secure, httponly=True)
        response.delete_cookie("tenant_id", path="/", secure=is_secure, httponly=True)
        response.delete_cookie("user_id", path="/", secure=is_secure, httponly=True)
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    if not user_id or not tenant_id:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    # Fetch user from database (only fields we need)
    try:
        user = User.objects(id=user_id, tenant_id=tenant_id).only(
            'email', 'first_name', 'last_name', 'phone', 'role_ids', 
            'status', 'mfa_enabled', 'created_at'
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    # Get role names from role IDs (batch query)
    role_names = []
    if user.role_ids:
        try:
            roles = Role.objects(id__in=user.role_ids, tenant_id=tenant_id).only('name')
            role_names = [role.name for role in roles]
        except Exception as e:
            logger.error(f"Error fetching roles: {e}", exc_info=True)
            # Don't fail if we can't get roles, just return empty list
            role_names = []

    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role_ids": [str(rid) for rid in user.role_ids],
        "role_names": role_names,
        "status": user.status,
        "mfa_enabled": user.mfa_enabled,
        "created_at": user.created_at.isoformat(),
        "tenant_id": str(user.tenant_id),
    }



@router.get("/csrf-token", response_model=CSRFTokenResponse)
async def get_csrf_token(
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    Get CSRF token for login form.
    
    Returns a CSRF token that must be included in login request.
    """
    csrf_token = auth_service.generate_csrf_token()
    return CSRFTokenResponse(csrf_token=csrf_token)


@router.post("/login")
async def login(
    request: Request,
    login_request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    User login endpoint with httpOnly cookies.

    Sets secure httpOnly cookies for authentication including tenant_id.
    Returns JSONResponse with cookies set directly.
    """
    logger.info(f"[LOGIN] Starting login for email: {login_request.email}")
    logger.info(f"[LOGIN] Request details - remember_me: {login_request.remember_me}")
    
    try:
        # Check if account is locked
        if is_account_locked(login_request.email):
            logger.warning(f"Login attempt on locked account: {login_request.email}")
            # Add timing delay to prevent timing attacks
            add_timing_delay()
            raise HTTPException(
                status_code=401,
                detail=get_generic_error_message("login"),
            )

        logger.info(f"[LOGIN] Account not locked, proceeding with authentication")

        # Step 1: Verify email exists (globally unique)
        try:
            user = User.objects(email=login_request.email).first()
            if not user:
                logger.warning(f"[LOGIN] User not found: {login_request.email}")
                # Add timing delay to prevent timing attacks
                add_timing_delay()
                raise HTTPException(
                    status_code=401,
                    detail=get_generic_error_message("login"),
                )
            logger.info(f"[LOGIN] User found: {user.id}")
        except HTTPException:
            # Re-raise HTTPException as-is
            raise
        except Exception as e:
            logger.error(f"[LOGIN] Error looking up user by email: {e}", exc_info=True)
            add_timing_delay()
            raise HTTPException(
                status_code=500,
                detail="Database connection error. Please try again.",
            )

        # Step 2: Get tenant_id from user (email is globally unique, so only one user per email)
        tenant_id = str(user.tenant_id)
        logger.info(f"[LOGIN] Tenant ID: {tenant_id}")
        
        # Step 3: Verify user has a valid tenant_id
        if not tenant_id:
            logger.warning(f"User has no tenant_id: {login_request.email}")
            add_timing_delay()
            raise HTTPException(
                status_code=401,
                detail=get_generic_error_message("login"),
            )

        logger.info(f"[LOGIN] Authenticating user...")

        # Authenticate user
        try:
            user_data = auth_service.authenticate_user(
                login_request.email, login_request.password, tenant_id
            )
            logger.info(f"[LOGIN] Authentication result: {user_data is not None}")
        except Exception as e:
            logger.error(f"[LOGIN] Error during authentication: {e}", exc_info=True)
            add_timing_delay()
            raise HTTPException(
                status_code=500,
                detail="Authentication service error. Please try again.",
            )
        
        if not user_data:
            # Increment failed attempts
            attempts = increment_login_attempts(login_request.email)
            logger.warning(
                f"Login failed for user: {login_request.email} (attempt {attempts})"
            )

            # Lock account after 5 failed attempts
            if attempts >= 5:
                lock_account(login_request.email)
                # Add timing delay to prevent timing attacks
                add_timing_delay()
                raise HTTPException(
                    status_code=401,
                    detail=get_generic_error_message("login"),
                )

            # Add timing delay to prevent timing attacks
            add_timing_delay()
            raise HTTPException(
                status_code=401,
                detail=get_generic_error_message("login"),
            )

        # Reset failed attempts on successful login
        reset_login_attempts(login_request.email)

        # Check if password change is required
        if user_data.get("password_change_required"):
            # Create a limited session for password change only
            # This allows the user to access the change-password-required endpoint
            try:
                # Create a short-lived access token for password change
                access_token = auth_service.create_access_token(
                    user_id=user_data["user_id"],
                    tenant_id=tenant_id,
                    email=user_data["email"],
                    role_ids=user_data["role_ids"],
                    permissions=["change_password"],  # Limited permission
                    expires_delta=timedelta(minutes=15),  # Short expiry
                )

                # Get client IP and user agent
                client_ip = request.client.host if request.client else "unknown"
                user_agent = request.headers.get("user-agent", "unknown")

                # Create temporary session
                session = auth_service.create_session(
                    user_id=user_data["user_id"],
                    tenant_id=tenant_id,
                    token=access_token,
                    refresh_token="",  # No refresh token for limited session
                    ip_address=client_ip,
                    user_agent=user_agent,
                )

                if session:
                    csrf_token = session.csrf_token if hasattr(session, 'csrf_token') else auth_service.generate_csrf_token()
                    
                    # Create response with password change required flag
                    response_data = {
                        "message": "Password change required",
                        "password_change_required": True,
                        "csrf_token": csrf_token,
                    }
                    
                    response = JSONResponse(content=response_data, status_code=403)
                    
                    # Set limited access token cookie
                    is_secure = settings.environment != "development"
                    response.set_cookie(
                        key="access_token",
                        value=access_token,
                        max_age=15 * 60,  # 15 minutes
                        secure=is_secure,
                        httponly=True,
                        samesite="Lax" if not is_secure else "Strict",
                        path="/",
                    )
                    
                    response.set_cookie(
                        key="tenant_id",
                        value=tenant_id,
                        max_age=15 * 60,
                        secure=is_secure,
                        httponly=True,
                        samesite="Lax" if not is_secure else "Strict",
                        path="/",
                    )
                    
                    response.set_cookie(
                        key="user_id",
                        value=str(user_data["user_id"]),
                        max_age=15 * 60,
                        secure=is_secure,
                        httponly=True,
                        samesite="Lax" if not is_secure else "Strict",
                        path="/",
                    )
                    
                    return response
            except Exception as e:
                logger.error(f"Error creating limited session for password change: {e}")
            
            # Fallback to old behavior if session creation fails
            raise HTTPException(
                status_code=403,
                detail="Password change required",
                headers={"X-Password-Change-Required": "true"},
            )

        # Check if MFA is enabled
        if user_data.get("mfa_enabled"):
            # Return temporary token requiring MFA
            raise HTTPException(
                status_code=403,
                detail="MFA required",
                headers={"X-MFA-Required": "true"},
            )

        # Get user permissions
        try:
            permissions = rbac_service.get_user_permissions(
                user_data["user_id"], tenant_id
            )
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            permissions = []

        # Create tokens
        try:
            access_token = auth_service.create_access_token(
                user_id=user_data["user_id"],
                tenant_id=tenant_id,
                email=user_data["email"],
                role_ids=user_data["role_ids"],  # Multiple roles per user
                permissions=permissions,
            )

            refresh_token = auth_service.create_refresh_token(
                user_id=user_data["user_id"],
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(f"Error creating tokens: {e}")
            raise HTTPException(status_code=500, detail="Failed to create authentication tokens")

        # Get client IP and user agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Create session with CSRF token
        session = auth_service.create_session(
            user_id=user_data["user_id"],
            tenant_id=tenant_id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")

        # Get CSRF token from session
        csrf_token = session.csrf_token if hasattr(session, 'csrf_token') else auth_service.generate_csrf_token()
        session_id = str(session.id)

        # Update last login
        try:
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0
            user.save()
        except Exception as e:
            logger.error(f"Error updating user last login: {e}")
            # Don't fail the login if we can't update the user

        logger.info(f"User logged in: {login_request.email}")

        # Create response with JSON body
        response_data = {
            "message": "Logged in successfully",
            "csrf_token": csrf_token,
        }
        
        response = JSONResponse(content=response_data, status_code=200)

        # Set secure httpOnly cookies
        # In development, allow insecure cookies for HTTP localhost
        is_secure = settings.environment != "development"
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=auth_service.access_token_expire_minutes * 60,
            secure=is_secure,  # Only send over HTTPS in production
            httponly=True,  # Not accessible from JavaScript
            samesite="Lax" if not is_secure else "Strict",  # Lax for dev, Strict for prod
            path="/",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=(auth_service.refresh_token_expire_days * 24 * 60 * 60) if not login_request.remember_me else (30 * 24 * 60 * 60),  # 30 days if remember_me
            secure=is_secure,
            httponly=True,
            samesite="Lax" if not is_secure else "Strict",
            path="/",
        )

        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=auth_service.access_token_expire_minutes * 60,
            secure=is_secure,
            httponly=True,
            samesite="Lax" if not is_secure else "Strict",
            path="/",
        )

        # Set tenant_id cookie
        response.set_cookie(
            key="tenant_id",
            value=tenant_id,
            max_age=auth_service.access_token_expire_minutes * 60,
            secure=is_secure,
            httponly=True,
            samesite="Lax" if not is_secure else "Strict",
            path="/",
        )

        # Set user_id cookie
        response.set_cookie(
            key="user_id",
            value=str(user_data["user_id"]),
            max_age=auth_service.access_token_expire_minutes * 60,
            secure=is_secure,
            httponly=True,
            samesite="Lax" if not is_secure else "Strict",
            path="/",
        )

        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"[LOGIN] Unexpected error: {str(e)}", exc_info=True)
        logger.error(f"[LOGIN] Exception type: {type(e).__name__}")
        logger.error(f"[LOGIN] Exception details: {repr(e)}")
        import traceback
        logger.error(f"[LOGIN] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during login",
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    """
    User logout endpoint.

    Invalidates the user's session and clears all authentication cookies.
    """
    # Get session_id and tenant_id from cookies
    session_id = request.cookies.get("session_id")
    tenant_id = request.cookies.get("tenant_id")
    
    # Invalidate session if we have session_id and tenant_id
    if session_id and tenant_id:
        auth_service.invalidate_session(session_id, tenant_id)

    # Clear ALL authentication cookies immediately
    # In development, allow insecure cookies for HTTP localhost
    is_secure = settings.environment != "development"
    
    # Delete all auth-related cookies with proper settings
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
    )
    response.delete_cookie(
        key="session_id",
        path="/",
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
    )
    response.delete_cookie(
        key="tenant_id",
        path="/",
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
    )
    response.delete_cookie(
        key="user_id",
        path="/",
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
    )

    logger.info(f"User logged out from tenant: {tenant_id}")

    return LogoutResponse(message="Logged out successfully")


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthenticationService = Depends(get_auth_service),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    Refresh access token using refresh token from cookie.

    Returns a new access token in httpOnly cookie.
    
    IMPORTANT: Validates refresh token FIRST before checking tenant_id.
    This prevents infinite loops when unauthenticated users make requests.
    """
    # Get refresh token from cookie FIRST
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    # Verify refresh token BEFORE checking tenant_id
    payload = auth_service.verify_token(refresh_token_value)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    tenant_id_from_token = payload.get("tenant_id")

    if not user_id or not tenant_id_from_token:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    # Now check tenant_id cookie (should match token)
    tenant_id = request.cookies.get("tenant_id")
    if not tenant_id:
        # If no tenant_id cookie, use the one from token
        tenant_id = tenant_id_from_token
    elif tenant_id != tenant_id_from_token:
        raise HTTPException(status_code=401, detail="Tenant mismatch")

    # Get user
    user = User.objects(id=user_id, tenant_id=tenant_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Get permissions
    permissions = rbac_service.get_user_permissions(user_id, tenant_id)

    # Create new access token
    access_token = auth_service.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email=user.email,
        role_ids=[str(rid) for rid in user.role_ids],  # Multiple roles per user
        permissions=permissions,
    )

    # Set new access token cookie
    # In development, allow insecure cookies for HTTP localhost
    is_secure = settings.environment != "development"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=auth_service.access_token_expire_minutes * 60,
        secure=is_secure,
        httponly=True,
        samesite="Lax" if not is_secure else "Strict",
        path="/",
    )

    logger.info(f"Token refreshed for user: {user_id}")

    return {
        "message": "Token refreshed successfully",
        "expires_in": auth_service.access_token_expire_minutes * 60,
    }


@router.get("/me")
async def get_current_user(
    current_user: dict = Depends(get_current_user_dependency),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    Get current user information from httpOnly cookie.

    Returns the authenticated user's profile with permissions.
    """
    # Get permissions for the user based on their roles
    user_id = current_user.get("id")
    tenant_id = current_user.get("tenant_id")
    permissions = []
    
    if user_id and tenant_id:
        try:
            permissions = rbac_service.get_user_permissions(user_id, tenant_id)
        except Exception as e:
            logger.error(f"Error fetching permissions: {e}", exc_info=True)
            # Don't fail if we can't get permissions, just return empty list
            permissions = []
    
    # Transform the response to match frontend expectations
    return {
        "user": {
            "id": current_user.get("id"),
            "email": current_user.get("email"),
            "firstName": current_user.get("first_name", ""),
            "lastName": current_user.get("last_name", ""),
            "phone": current_user.get("phone", ""),
            "role": current_user.get("role_names", [""])[0] if current_user.get("role_names") else "",
            "roleNames": current_user.get("role_names", []),
            "tenantId": current_user.get("tenant_id"),
            "avatar": current_user.get("avatar"),
        },
        "permissions": permissions,
    }


@router.post("/delete-account")
async def delete_account(
    current_user: dict = Depends(get_current_user_dependency),
):
    """Delete the current user's account (soft delete with recovery period)."""
    try:
        from app.services.tenant_deletion_service import TenantDeletionService
        from app.models.tenant import Tenant
        
        tenant_id = str(current_user.get("tenant_id"))
        
        # Get tenant info
        tenant = Tenant.objects(id=tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found"
            )
        
        # Soft delete the tenant
        deletion_service = TenantDeletionService(settings)
        result = deletion_service.soft_delete_tenant(tenant_id)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete account"
            )
        
        # TODO: Send recovery email with token
        # For now, just return success
        
        return {
            "success": True,
            "message": "Account deleted successfully",
            "recovery_token": result.get("recovery_token"),
            "grace_period_days": result.get("grace_period_days"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )


class ForcedPasswordChangeRequest(BaseModel):
    """Forced password change request schema."""

    new_password: str


@router.post("/change-password-required")
async def change_password_required(
    request: Request,
    response: Response,
    password_change: ForcedPasswordChangeRequest,
    current_user: dict = Depends(get_current_user_dependency),
    auth_service: AuthenticationService = Depends(get_auth_service),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    Change password when password_change_required flag is set.
    
    This endpoint is used when a user is forced to change their password
    on first login (for Staff, Manager, Customer roles).
    After successful password change, creates a full session for the user.
    """
    try:
        user_id = current_user.get("id")
        tenant_id = current_user.get("tenant_id")
        
        # Get user
        user = User.objects(id=user_id, tenant_id=tenant_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate new password
        if len(password_change.new_password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        # Update password and clear flag
        user.password_hash = auth_service.hash_password(password_change.new_password)
        user.password_change_required = False
        user.save()
        
        logger.info(f"User changed required password: {user.email}")
        
        # Create full session with all permissions
        permissions = rbac_service.get_user_permissions(user_id, tenant_id)
        
        # Create new tokens with full permissions
        access_token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=user.email,
            role_ids=[str(rid) for rid in user.role_ids],
            permissions=permissions,
        )

        refresh_token = auth_service.create_refresh_token(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        # Get client IP and user agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Create full session
        session = auth_service.create_session(
            user_id=user_id,
            tenant_id=tenant_id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        if session:
            csrf_token = session.csrf_token if hasattr(session, 'csrf_token') else auth_service.generate_csrf_token()
            session_id = str(session.id)

            # Create response
            response_data = {
                "success": True,
                "message": "Password changed successfully",
                "csrf_token": csrf_token,
            }
            
            response = JSONResponse(content=response_data, status_code=200)

            # Set full authentication cookies
            is_secure = settings.environment != "development"
            
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=auth_service.access_token_expire_minutes * 60,
                secure=is_secure,
                httponly=True,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=auth_service.refresh_token_expire_days * 24 * 60 * 60,
                secure=is_secure,
                httponly=True,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )

            response.set_cookie(
                key="session_id",
                value=session_id,
                max_age=auth_service.access_token_expire_minutes * 60,
                secure=is_secure,
                httponly=True,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )

            response.set_cookie(
                key="tenant_id",
                value=tenant_id,
                max_age=auth_service.access_token_expire_minutes * 60,
                secure=is_secure,
                httponly=True,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )

            response.set_cookie(
                key="user_id",
                value=str(user_id),
                max_age=auth_service.access_token_expire_minutes * 60,
                secure=is_secure,
                httponly=True,
                samesite="Lax" if not is_secure else "Strict",
                path="/",
            )

            return response
        
        # If session creation fails, return simple success
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to change password"
        )
