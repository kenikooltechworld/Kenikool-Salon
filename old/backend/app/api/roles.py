"""
Roles and Permissions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/roles", tags=["roles"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def list_roles(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all roles for tenant"""
    try:
        db = get_db()
        roles = list(
            db.roles.find({"tenant_id": tenant_id})
        )
        
        # Convert ObjectIds to strings
        for role in roles:
            if "_id" in role:
                role["_id"] = str(role["_id"])
        
        return {
            "roles": roles,
            "total": len(roles)
        }
    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{role_id}", response_model=dict)
async def get_role(
    role_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get single role"""
    try:
        db = get_db()
        role = db.roles.find_one({
            "_id": ObjectId(role_id),
            "tenant_id": tenant_id
        })
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        role["_id"] = str(role["_id"])
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create new role"""
    try:
        db = get_db()
        
        role_doc = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "description": data.get("description", ""),
            "permissions": data.get("permissions", []),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        
        result = db.roles.insert_one(role_doc)
        role_doc["_id"] = str(result.inserted_id)
        
        return role_doc
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=dict)
async def update_role(
    role_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update role"""
    try:
        db = get_db()
        
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        if "name" in data:
            update_data["name"] = data["name"]
        if "description" in data:
            update_data["description"] = data["description"]
        if "permissions" in data:
            update_data["permissions"] = data["permissions"]
        
        result = db.roles.update_one(
            {
                "_id": ObjectId(role_id),
                "tenant_id": tenant_id
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        role = db.roles.find_one({
            "_id": ObjectId(role_id)
        })
        role["_id"] = str(role["_id"])
        
        return role
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete role"""
    try:
        db = get_db()
        
        result = db.roles.delete_one({
            "_id": ObjectId(role_id),
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return {"message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
