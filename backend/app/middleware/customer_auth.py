"""Customer Authentication Middleware"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.customer_auth_service import CustomerAuthService
from app.middleware.tenant_context import get_tenant_id
from app.models.customer import Customer

security = HTTPBearer()


async def get_current_customer(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Customer:
    """Get current authenticated customer from JWT token"""
    token = credentials.credentials
    tenant_id = get_tenant_id(request)
    
    customer = CustomerAuthService.get_customer_from_token(token, tenant_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return customer


async def get_current_customer_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> Customer | None:
    """Get current authenticated customer from JWT token (optional)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    tenant_id = get_tenant_id(request)
    
    return CustomerAuthService.get_customer_from_token(token, tenant_id)
