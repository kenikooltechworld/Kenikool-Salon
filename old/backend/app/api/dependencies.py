"""
FastAPI dependencies for authentication and request info
Requirements: 3.1, 3.5, 4.5, 4.6
"""
from fastapi import Depends, HTTPException, status, Header, Request
from typing import Dict, Optional
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)


async def get_current_user(request: Request) -> Dict:
    """
    Get current authenticated user from cookies
    
    Requirements: 3.1, 3.5
    
    CRITICAL: This function MUST validate the user is authenticated.
    In a SaaS platform, every request MUST have a valid authenticated user
    with a real tenant_id. No random IDs or defaults allowed.
    
    Returns:
        Dict with user_id, tenant_id, session_id, and other user info
        
    Raises:
        HTTPException: If user is not authenticated
    """
    try:
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            logger.error("❌ SECURITY: No access_token cookie - user not authenticated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please log in."
            )
        
        # Decode JWT token to extract user info
        try:
            from app.utils.security import decode_access_token
            
            # Decode the JWT token
            payload = decode_access_token(access_token)
            
            # CRITICAL: Validate required fields exist in JWT
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            
            if not user_id:
                logger.error("❌ SECURITY: JWT missing 'sub' (user_id)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user_id"
                )
            
            if not tenant_id:
                logger.error("❌ SECURITY: JWT missing 'tenant_id'")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing tenant_id"
                )
            
            # Extract user info from JWT payload
            user_info = {
                "id": user_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "session_id": payload.get("session_id", ""),
                "email": payload.get("email", ""),
                "role": payload.get("role", "user")
            }
            
            logger.info(f"✅ User authenticated from cookie: {user_info['email']} (tenant: {tenant_id})")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ SECURITY: JWT decode failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SECURITY: Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user_via_api_key(
    x_api_key: Optional[str] = Header(None)
) -> Dict:
    """
    Get current user from API key authentication
    
    Requirements: 4.5, 4.6
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        Dict with user_id, tenant_id, and other user info
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    try:
        from app.services.api_key_service import api_key_service
        
        # Validate API key (Requirement 4.5, 4.6)
        user_info = await api_key_service.validate_api_key(x_api_key)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )


async def get_request_info() -> Dict:
    """
    Get request metadata (IP, device, browser, etc.)
    
    Returns:
        Dict with request metadata
    """
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # This is a placeholder - in actual implementation, extract from request context
    return {
        "ip_address": "0.0.0.0",
        "device": "Unknown",
        "browser": "Unknown",
        "user_agent": "Unknown",
        "location": "Unknown"
    }


def get_request_info_from_request(request: "StarletteRequest") -> Dict:
    """
    Extract request info from FastAPI request object
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict with request metadata
    """
    import re
    from user_agents import parse
    
    # Get IP address
    ip_address = request.client.host if request.client else "unknown"
    
    # Get user agent
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Parse user agent
    try:
        ua = parse(user_agent)
        device = f"{ua.browser.family} on {ua.os.family}"
        browser = f"{ua.browser.family} {ua.browser.version_string}"
    except:
        device = "Unknown"
        browser = "Unknown"
    
    # Get location from IP (simplified - in production use GeoIP service)
    location = "Unknown"
    
    return {
        "ip_address": ip_address,
        "device": device,
        "browser": browser,
        "user_agent": user_agent,
        "location": location
    }


async def get_tenant_id(current_user: Dict = Depends(get_current_user)) -> str:
    """
    Get tenant ID from the authenticated user (from cookies)
    
    CRITICAL: In a SaaS platform, every request MUST be tied to an authenticated user.
    The tenant_id comes from the user's JWT token in cookies, not from random generation.
    
    Returns:
        str: Tenant ID from authenticated user
        
    Raises:
        HTTPException: If tenant_id not found in authenticated user
    """
    try:
        # Get tenant_id from authenticated user (already validated by get_current_user)
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            logger.error("❌ SECURITY: Authenticated user has no tenant_id!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        logger.info(f"✅ Tenant ID from authenticated user (cookie): {tenant_id}")
        return tenant_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SECURITY: Failed to get tenant_id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to determine tenant"
        )


async def require_owner_or_admin(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Require user to be owner or admin
    
    Args:
        current_user: Current user from authentication
        
    Returns:
        Dict: Current user if authorized
        
    Raises:
        HTTPException: If user is not owner or admin
    """
    role = current_user.get("role", "").lower()
    if role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can perform this action"
        )
    return current_user


async def get_current_user_and_tenant(request: Request) -> tuple[Dict, str]:
    """
    Get current user and tenant ID in one call to avoid dependency issues
    
    Returns:
        tuple: (user_dict, tenant_id)
    """
    try:
        # Get current user first
        current_user = await get_current_user(request)
        
        # Get tenant_id from authenticated user
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            logger.error("❌ SECURITY: Authenticated user has no tenant_id!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        return current_user, tenant_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SECURITY: Failed to get user and tenant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_tenant_id(request: Request) -> str:
    """
    Get tenant ID from the authenticated user (from cookies)
    
    Returns:
        str: Tenant ID
    """
    current_user = await get_current_user(request)
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        logger.error("❌ SECURITY: Authenticated user has no tenant_id!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no tenant association"
        )
    
    return tenant_id


def get_database():
    """
    Get database instance
    
    Returns:
        Database instance
    """
    from app.database import Database
    return Database.get_db()


def get_db():
    """
    Alias for get_database for consistency
    
    Returns:
        Database instance
    """
    return get_database()


def require_roles(allowed_roles: list):
    """
    Create a dependency that requires user to have one of the allowed roles
    
    Args:
        allowed_roles: List of allowed roles
        
    Returns:
        Dependency function
    """
    async def check_role(current_user: Dict = Depends(get_current_user)) -> Dict:
        """
        Check if user has one of the allowed roles
        
        Args:
            current_user: Current user from authentication
            
        Returns:
            Dict: Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_role = current_user.get("role", "").lower()
        if user_role not in [role.lower() for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return check_role
