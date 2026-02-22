"""
Duplicate Detection API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.middleware.tenant_isolation import get_current_tenant_id
from app.schemas.client import ClientSchema

router = APIRouter()


@router.get("/api/clients/duplicates")
async def get_duplicates(
    tenant_id: str = Depends(get_current_tenant_id),
    min_similarity: float = Query(0.85, ge=0.0, le=1.0)
) -> Dict:
    """
    Get potential duplicate client pairs.
    
    Args:
        tenant_id: Current tenant ID
        min_similarity: Minimum similarity threshold (0.0-1.0)
    
    Returns:
        List of potential duplicate pairs with similarity scores
    """
    try:
        duplicates = DuplicateDetectionService.find_duplicates(
            tenant_id=tenant_id,
            min_similarity=min_similarity
        )
        return {
            "status": "success",
            "count": len(duplicates),
            "duplicates": duplicates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/clients/merge")
async def merge_clients(
    tenant_id: str = Depends(get_current_tenant_id),
    primary_id: str = None,
    secondary_id: str = None,
    field_preferences: Optional[Dict] = None
) -> Dict:
    """
    Merge two client records.
    
    Args:
        tenant_id: Current tenant ID
        primary_id: ID of primary client (will be kept)
        secondary_id: ID of secondary client (will be merged into primary)
        field_preferences: Dict of field preferences for merge
    
    Returns:
        Merge result with undo window information
    """
    if not primary_id or not secondary_id:
        raise HTTPException(status_code=400, detail="primary_id and secondary_id required")
    
    try:
        result = DuplicateDetectionService.merge_clients(
            tenant_id=tenant_id,
            primary_id=primary_id,
            secondary_id=secondary_id,
            field_preferences=field_preferences
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/clients/{client_id}/undo-merge")
async def undo_merge(
    client_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Undo a merge operation within the 24-hour window.
    
    Args:
        client_id: ID of the merged client
        tenant_id: Current tenant ID
    
    Returns:
        Undo result
    """
    try:
        result = DuplicateDetectionService.undo_merge(
            tenant_id=tenant_id,
            primary_id=client_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
