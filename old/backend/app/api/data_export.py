"""
Data Export and Import API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
from bson import ObjectId
import logging
import json
import io
import csv

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["export-import"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("/export/salon-data")
async def export_salon_data(
    format: str = "json",
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Export salon data in specified format"""
    try:
        db = get_db()
        
        # Collect salon data
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        locations = list(db.locations.find({"tenant_id": tenant_id}))
        services = list(db.services.find({"tenant_id": tenant_id}))
        staff = list(db.staff.find({"tenant_id": tenant_id}))
        
        # Convert ObjectIds to strings
        def convert_ids(obj):
            if isinstance(obj, list):
                return [convert_ids(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: str(v) if isinstance(v, ObjectId) else convert_ids(v) 
                        for k, v in obj.items()}
            elif isinstance(obj, ObjectId):
                return str(obj)
            return obj
        
        export_data = {
            "exportDate": datetime.utcnow().isoformat(),
            "tenant": convert_ids(tenant),
            "locations": convert_ids(locations),
            "services": convert_ids(services),
            "staff": convert_ids(staff),
        }
        
        if format == "json":
            content = json.dumps(export_data, indent=2, default=str)
            media_type = "application/json"
            filename = f"salon_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        elif format == "csv":
            # Create CSV with basic salon info
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(["Type", "Name", "Value"])
            
            # Write tenant info
            if tenant:
                writer.writerow(["Tenant", "Name", tenant.get("salon_name", "")])
                writer.writerow(["Tenant", "Created", tenant.get("created_at", "")])
            
            # Write locations
            for location in locations:
                writer.writerow(["Location", location.get("name", ""), 
                               location.get("address", "")])
            
            # Write services
            for service in services:
                writer.writerow(["Service", service.get("name", ""), 
                               service.get("price", "")])
            
            content = output.getvalue()
            media_type = "text/csv"
            filename = f"salon_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        elif format == "excel":
            # For now, return JSON (Excel export would require openpyxl)
            content = json.dumps(export_data, indent=2, default=str)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"salon_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'json', 'csv', or 'excel'"
            )
        
        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting salon data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/import/salon-data", response_model=dict)
async def import_salon_data(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Import salon data from file"""
    try:
        # Read file content
        content = await file.read()
        
        # Parse JSON
        try:
            data = json.loads(content.decode())
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format"
            )
        
        db = get_db()
        
        # Import data (simplified - in production would validate and merge)
        imported_count = 0
        
        # Import locations
        if "locations" in data:
            for location in data["locations"]:
                location["tenant_id"] = tenant_id
                db.locations.insert_one(location)
                imported_count += 1
        
        # Import services
        if "services" in data:
            for service in data["services"]:
                service["tenant_id"] = tenant_id
                db.services.insert_one(service)
                imported_count += 1
        
        # Import staff
        if "staff" in data:
            for staff_member in data["staff"]:
                staff_member["tenant_id"] = tenant_id
                db.staff.insert_one(staff_member)
                imported_count += 1
        
        return {
            "success": True,
            "message": "Data imported successfully",
            "recordsImported": imported_count,
            "importedAt": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing salon data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
