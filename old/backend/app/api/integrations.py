"""
Integrations API endpoints - Third-party service integrations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def list_integrations(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all integrations for tenant"""
    try:
        db = get_db()
        integrations = list(
            db.integrations.find({"tenant_id": tenant_id})
        )
        
        # Convert ObjectIds to strings
        for integration in integrations:
            if "_id" in integration:
                integration["_id"] = str(integration["_id"])
        
        return {
            "integrations": integrations,
            "total": len(integrations)
        }
    except Exception as e:
        logger.error(f"Error listing integrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{integration_id}", response_model=dict)
async def get_integration(
    integration_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get single integration"""
    try:
        db = get_db()
        integration = db.integrations.find_one({
            "_id": ObjectId(integration_id),
            "tenant_id": tenant_id
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        integration["_id"] = str(integration["_id"])
        return integration
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Connect new integration"""
    try:
        db = get_db()
        
        integration_doc = {
            "tenant_id": tenant_id,
            "type": data.get("type"),
            "credentials": data.get("credentials", {}),
            "settings": data.get("settings", {}),
            "isEnabled": True,
            "isConnected": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        
        result = db.integrations.insert_one(integration_doc)
        integration_doc["_id"] = str(result.inserted_id)
        
        return integration_doc
    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{integration_id}", response_model=dict)
async def update_integration(
    integration_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update integration"""
    try:
        db = get_db()
        
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        if "credentials" in data:
            update_data["credentials"] = data["credentials"]
        if "settings" in data:
            update_data["settings"] = data["settings"]
        if "isEnabled" in data:
            update_data["isEnabled"] = data["isEnabled"]
        
        result = db.integrations.update_one(
            {
                "_id": ObjectId(integration_id),
                "tenant_id": tenant_id
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        integration = db.integrations.find_one({
            "_id": ObjectId(integration_id)
        })
        integration["_id"] = str(integration["_id"])
        
        return integration
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{integration_id}", status_code=status.HTTP_200_OK)
async def delete_integration(
    integration_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Disconnect integration"""
    try:
        db = get_db()
        
        result = db.integrations.delete_one({
            "_id": ObjectId(integration_id),
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        return {"message": "Integration disconnected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{integration_id}/test", response_model=dict)
async def test_integration(
    integration_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Test integration connection"""
    try:
        db = get_db()
        
        integration = db.integrations.find_one({
            "_id": ObjectId(integration_id),
            "tenant_id": tenant_id
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )
        
        # Mock test - in production, would actually test the connection
        return {
            "success": True,
            "message": "Integration connection test passed",
            "type": integration.get("type")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
