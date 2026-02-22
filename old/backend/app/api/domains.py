"""
API endpoints for custom domain management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.services.domain_service import DomainService
from app.api.exceptions import NotFoundException, BadRequestException
from app.middleware.domain_routing import get_tenant_id_from_request
from starlette.requests import Request

router = APIRouter(prefix="/api/domains", tags=["domains"])


@router.post("")
async def create_domain(
    request: Request,
    domain: str
):
    """Create a new custom domain request"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        result = await DomainService.create_domain_request(tenant_id, domain)
        return result
    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{domain}/verify")
async def verify_domain(
    request: Request,
    domain: str
):
    """Verify domain DNS configuration and provision SSL"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        result = await DomainService.verify_domain(tenant_id, domain)
        return result
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("")
async def list_domains(request: Request):
    """Get all domains for tenant"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        domains = await DomainService.get_domains(tenant_id)
        return {"domains": domains}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{domain_id}")
async def get_domain(
    request: Request,
    domain_id: str
):
    """Get single domain details"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        domain = await DomainService.get_domain(domain_id, tenant_id)
        return domain
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{domain_id}")
async def delete_domain(
    request: Request,
    domain_id: str
):
    """Delete custom domain"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        await DomainService.delete_domain(domain_id, tenant_id)
        return {"status": "deleted"}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{domain_id}/dns-records")
async def get_dns_instructions(
    request: Request,
    domain_id: str
):
    """Get DNS configuration instructions for domain"""
    try:
        tenant_id = get_tenant_id_from_request(request)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found"
            )

        records = await DomainService.get_dns_instructions(domain_id, tenant_id)
        return {"dns_records": records}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
