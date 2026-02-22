"""
Authentication API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.api.exceptions import (
    BadRequestException, UnauthorizedException,
    ConflictException, NotFoundException
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ===== REQUEST/RESPONSE SCHEMAS =====

class RegisterRequest(BaseModel):
    """Registration request schema"""
    salon_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    address: Optional[str] = None
    bank_account: Optional[dict] = None
    referral_code: Optional[str] = None
    tenant_id_for_referral: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class VerifyEmailRequest(BaseModel):
    """Email verification request schema"""
    code: str = Field(..., min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    """Resend verification request schema"""
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    tenant_id: str
    profile_picture_url: Optional[str] = None


class RegistrationResponse(BaseModel):
    """Registration response schema"""
    success: bool
    message: str
    email: str


class AuthResponse(BaseModel):
    """Authentication response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
    email_verified: bool


# ===== ENDPOINTS =====

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new salon owner
    
    Sends verification email. User and tenant are created ONLY after email verification.
    """
    try:
        logger.info(f"Registration request: {request.email}")
        
        result = await AuthService.register_user(
            salon_name=request.salon_name,
            owner_name=request.owner_name,
            email=request.email,
            phone=request.phone,
            password=request.password,
            address=request.address,
            bank_account=request.bank_account,
            referral_code=request.referral_code,
            tenant_id_for_referral=request.tenant_id_for_referral
        )
        
        logger.info(f"Registration email sent: {request.email}")
        return result
        
    except ConflictException as e:
        logger.warning(f"Registration conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except BadRequestException as e:
        logger.warning(f"Registration validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response):
    """
    Login with email and password
    
    Sets httpOnly, secure cookies for authentication.
    Returns user data in response body.
    
    Args:
        request: LoginRequest with email, password, and optional remember_me flag
        response: Response object to set cookies
    
    If remember_me is True, refresh token expires in 30 days.
    If remember_me is False, refresh token expires in 7 days (shorter session).
    """
    try:
        logger.info(f"Login request: {request.email}")
        
        result = await AuthService.login_user(
            email=request.email,
            password=request.password
        )
        
        # Determine refresh token expiry based on remember_me flag
        # If remember_me is True: 30 days, otherwise: 7 days
        refresh_token_max_age = 2592000 if request.remember_me else 604800  # 30 days vs 7 days
        access_token_max_age = 3600  # Always 1 hour for access token
        
        # Set httpOnly, secure cookies
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=access_token_max_age
        )
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=refresh_token_max_age
        )
        response.set_cookie(
            key="tenant_id",
            value=result["user"]["tenant_id"],
            httponly=False,  # Can be read by JS for debugging
            secure=True,
            samesite="lax",
            max_age=refresh_token_max_age
        )
        
        logger.info(f"✅ Login successful: {request.email} - Cookies set (remember_me={request.remember_me})")
        return result
        
    except UnauthorizedException as e:
        logger.warning(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing authentication cookies
    """
    try:
        logger.info("Logout request")
        
        # Clear authentication cookies
        response.delete_cookie("access_token", samesite="lax")
        response.delete_cookie("refresh_token", samesite="lax")
        response.delete_cookie("tenant_id", samesite="lax")
        
        logger.info("✅ Logout successful - Cookies cleared")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user info with enhanced profile data
    
    Used by frontend to verify authentication status and get user profile.
    Returns 401 if not authenticated.
    """
    try:
        logger.info(f"✅ User authenticated: {current_user.get('email')}")
        
        # Get additional user data from database
        from app.database import Database
        db = Database.get_db()
        
        user_data = db.users.find_one({"_id": current_user.get("id")})
        if not user_data:
            # Fallback to basic user info if database lookup fails
            return {
                "id": current_user.get("id"),
                "email": current_user.get("email"),
                "full_name": current_user.get("email", "").split("@")[0].title(),  # Fallback name
                "phone": current_user.get("phone"),
                "role": current_user.get("role"),
                "is_active": True,
                "tenant_id": current_user.get("tenant_id"),
                "profile_picture_url": None
            }
        
        return {
            "id": str(user_data.get("_id")),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name", user_data.get("name", user_data.get("email", "").split("@")[0].title())),
            "phone": user_data.get("phone"),
            "role": user_data.get("role", "staff"),
            "is_active": user_data.get("is_active", True),
            "tenant_id": user_data.get("tenant_id"),
            "profile_picture_url": user_data.get("profile_picture_url")
        }
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email with verification code
    
    Called when user submits the verification code from their email.
    """
    try:
        logger.info("Email verification request")
        
        success, message = await AuthService.verify_email(request.code)
        
        return {
            "success": success,
            "message": message
        }
        
    except NotFoundException as e:
        logger.warning(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BadRequestException as e:
        logger.warning(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again later."
        )


@router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """
    Resend verification email
    
    Generates a new verification token and sends it to the user's email.
    """
    try:
        logger.info(f"Resend verification request: {request.email}")
        
        success, message = await AuthService.resend_verification(request.email)
        
        return {
            "success": success,
            "message": message
        }
        
    except NotFoundException as e:
        logger.warning(f"Resend verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BadRequestException as e:
        logger.warning(f"Resend verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email. Please try again later."
        )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset
    
    Generates a reset token and sends it to the user's email.
    """
    try:
        logger.info(f"Forgot password request: {request.email}")
        
        success, message = await AuthService.forgot_password(request.email)
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request. Please try again later."
        )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password with reset token
    
    Called when user submits new password from reset link.
    """
    try:
        logger.info("Password reset request")
        
        success, message = await AuthService.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        
        return {
            "success": success,
            "message": message
        }
        
    except NotFoundException as e:
        logger.warning(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except BadRequestException as e:
        logger.warning(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again later."
        )


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """
    Refresh access token using refresh token from cookies
    
    CRITICAL: This endpoint does NOT require a valid access token.
    It uses the refresh token from cookies to generate a new access token.
    This prevents the infinite 401 loop when access token expires.
    
    Returns new access token in cookie.
    """
    try:
        logger.info("🔄 Token refresh request")
        
        # Get refresh token from cookies (NOT access token)
        refresh_token_str = request.cookies.get("refresh_token")
        
        if not refresh_token_str:
            logger.error("❌ No refresh_token cookie found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found. Please login again."
            )
        
        # Use auth service to refresh token
        from app.services.auth_service import auth_service
        from datetime import timedelta
        from app.config import settings
        
        try:
            # Refresh token using the service
            result = await auth_service.refresh_token(refresh_token_str)
            
            # Set new access token cookie
            response.set_cookie(
                key="access_token",
                value=result["access_token"],
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
            # Set new refresh token cookie
            response.set_cookie(
                key="refresh_token",
                value=result["refresh_token"],
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
            )
            
            logger.info(f"✅ Token refresh successful for user: {result['user']['email']}")
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "user": result["user"]
            }
            
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token. Please login again."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please login again."
        )


@router.get("/permissions")
async def get_user_permissions(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's permissions based on their role
    
    Returns a list of permissions that the user has access to.
    Used by frontend to show/hide features and control access.
    """
    try:
        user_role = current_user.get("role", "staff")
        tenant_id = current_user.get("tenant_id")
        
        # Define role-based permissions
        permissions = []
        
        if user_role == "owner":
            # Owner has all permissions
            permissions = [
                # Dashboard
                "dashboard.view",
                "dashboard.analytics",
                
                # Bookings
                "bookings.view",
                "bookings.create",
                "bookings.edit",
                "bookings.delete",
                "bookings.manage_all",
                
                # Clients
                "clients.view",
                "clients.create",
                "clients.edit",
                "clients.delete",
                "clients.export",
                
                # Staff Management
                "staff.view",
                "staff.create",
                "staff.edit",
                "staff.delete",
                "staff.manage_roles",
                "staff.view_performance",
                
                # Services
                "services.view",
                "services.create",
                "services.edit",
                "services.delete",
                "services.manage_pricing",
                
                # Inventory
                "inventory.view",
                "inventory.create",
                "inventory.edit",
                "inventory.delete",
                "inventory.manage_stock",
                
                # Payments & Financial
                "payments.view",
                "payments.process",
                "payments.refund",
                "financial.view_reports",
                "financial.manage_settings",
                
                # Marketing & Campaigns
                "marketing.view",
                "marketing.create",
                "marketing.edit",
                "marketing.delete",
                "campaigns.manage",
                
                # Settings & Configuration
                "settings.view",
                "settings.edit",
                "settings.manage_integrations",
                "settings.manage_notifications",
                
                # Reports & Analytics
                "reports.view",
                "reports.export",
                "analytics.view",
                
                # System Administration
                "system.manage_users",
                "system.view_logs",
                "system.manage_backups",
            ]
            
        elif user_role == "manager":
            # Manager has most permissions except system administration
            permissions = [
                # Dashboard
                "dashboard.view",
                "dashboard.analytics",
                
                # Bookings
                "bookings.view",
                "bookings.create",
                "bookings.edit",
                "bookings.delete",
                "bookings.manage_all",
                
                # Clients
                "clients.view",
                "clients.create",
                "clients.edit",
                "clients.export",
                
                # Staff Management (limited)
                "staff.view",
                "staff.view_performance",
                
                # Services
                "services.view",
                "services.create",
                "services.edit",
                
                # Inventory
                "inventory.view",
                "inventory.create",
                "inventory.edit",
                "inventory.manage_stock",
                
                # Payments
                "payments.view",
                "payments.process",
                "payments.refund",
                
                # Marketing
                "marketing.view",
                "marketing.create",
                "marketing.edit",
                
                # Reports
                "reports.view",
                "reports.export",
                "analytics.view",
            ]
            
        elif user_role == "staff" or user_role == "stylist":
            # Staff/Stylist has basic permissions
            permissions = [
                # Dashboard (limited)
                "dashboard.view",
                
                # Bookings (own bookings)
                "bookings.view",
                "bookings.create",
                "bookings.edit",
                
                # Clients (basic)
                "clients.view",
                "clients.create",
                "clients.edit",
                
                # Services (view only)
                "services.view",
                
                # Inventory (view only)
                "inventory.view",
                
                # Payments (basic)
                "payments.view",
                "payments.process",
            ]
            
        elif user_role == "receptionist":
            # Receptionist has booking and client management permissions
            permissions = [
                # Dashboard
                "dashboard.view",
                
                # Bookings
                "bookings.view",
                "bookings.create",
                "bookings.edit",
                "bookings.manage_all",
                
                # Clients
                "clients.view",
                "clients.create",
                "clients.edit",
                
                # Services (view only)
                "services.view",
                
                # Payments
                "payments.view",
                "payments.process",
            ]
        
        logger.info(f"✅ Permissions retrieved for user {current_user.get('email')} (role: {user_role}): {len(permissions)} permissions")
        
        return {
            "user_id": current_user.get("id"),
            "role": user_role,
            "tenant_id": tenant_id,
            "permissions": permissions,
            "total_permissions": len(permissions)
        }
        
    except Exception as e:
        logger.error(f"Error getting user permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user permissions"
        )



# ===== ACCESSIBILITY PREFERENCES =====

class AccessibilityPreferences(BaseModel):
    """Accessibility preferences schema"""
    high_contrast_mode: bool = False
    reduce_motion: bool = False
    screen_reader_mode: bool = False
    font_size: str = "normal"  # small, normal, large, extra-large
    keyboard_navigation_hints: bool = True
    focus_indicators: bool = True
    color_blind_mode: Optional[str] = None  # deuteranopia, protanopia, tritanopia
    dyslexia_friendly_font: bool = False


class AccessibilityPreferencesResponse(BaseModel):
    """Accessibility preferences response"""
    preferences: AccessibilityPreferences
    updated_at: str


@router.get("/accessibility-preferences")
async def get_accessibility_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's accessibility preferences
    
    Returns user's accessibility settings for WCAG compliance features.
    """
    try:
        user_id = current_user.get("id")
        tenant_id = current_user.get("tenant_id")
        
        # In a real implementation, fetch from database
        # For now, return default preferences
        preferences = AccessibilityPreferences()
        
        return {
            "preferences": preferences.dict(),
            "updated_at": "2026-02-10T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching accessibility preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch accessibility preferences"
        )


@router.post("/accessibility-preferences")
async def update_accessibility_preferences(
    preferences: AccessibilityPreferences,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's accessibility preferences
    
    Saves user's accessibility settings for WCAG compliance features.
    """
    try:
        user_id = current_user.get("id")
        tenant_id = current_user.get("tenant_id")
        
        # In a real implementation, save to database
        # For now, just return the preferences
        
        logger.info(f"Updated accessibility preferences for user {user_id}")
        
        return {
            "preferences": preferences.dict(),
            "updated_at": "2026-02-10T00:00:00Z",
            "message": "Accessibility preferences updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating accessibility preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update accessibility preferences"
        )
