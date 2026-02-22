"""
Privacy & GDPR Compliance API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Optional
from app.services.privacy_gdpr_service import PrivacyGDPRService
from app.middleware.tenant_isolation import get_current_tenant_id

router = APIRouter()


@router.post("/api/clients/{client_id}/consent")
async def record_consent(
    client_id: str,
    consent_type: str,
    request: Request,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Record client consent for GDPR compliance.
    
    Args:
        client_id: Client ID
        consent_type: Type of consent (e.g., 'marketing', 'data_processing')
        request: HTTP request (for IP and user agent)
        tenant_id: Current tenant ID
    
    Returns:
        Consent record confirmation
    """
    try:
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        result = PrivacyGDPRService.record_consent(
            tenant_id=tenant_id,
            client_id=client_id,
            consent_type=consent_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/clients/{client_id}/export-data")
async def export_client_data(
    client_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Export all client data in machine-readable format (GDPR right to data portability).
    
    Args:
        client_id: Client ID
        tenant_id: Current tenant ID
    
    Returns:
        Complete client data export
    """
    try:
        export_data = PrivacyGDPRService.export_client_data(
            tenant_id=tenant_id,
            client_id=client_id
        )
        return {
            "status": "success",
            "data": export_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/clients/{client_id}/anonymize")
async def anonymize_client(
    client_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Anonymize client PII while preserving analytics data.
    
    Args:
        client_id: Client ID
        tenant_id: Current tenant ID
    
    Returns:
        Anonymization confirmation
    """
    try:
        result = PrivacyGDPRService.anonymize_client(
            tenant_id=tenant_id,
            client_id=client_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tenants/{tenant_id}/retention-policy")
async def set_retention_policy(
    tenant_id: str,
    policy: Dict,
    current_tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Set data retention policy for tenant.
    
    Args:
        tenant_id: Tenant ID
        policy: Retention policy configuration
        current_tenant_id: Current tenant ID (for authorization)
    
    Returns:
        Policy confirmation
    """
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        result = PrivacyGDPRService.set_retention_policy(
            tenant_id=tenant_id,
            policy=policy
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/tenants/{tenant_id}/retention-cleanup")
async def process_retention_cleanup(
    tenant_id: str,
    current_tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Process automatic data retention cleanup.
    
    Args:
        tenant_id: Tenant ID
        current_tenant_id: Current tenant ID (for authorization)
    
    Returns:
        Cleanup results
    """
    if tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        result = PrivacyGDPRService.process_retention_cleanup(
            tenant_id=tenant_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
