"""Routes for backup management."""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from bson import ObjectId
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.models.backup import Backup, BackupRestore, BackupSchedule

logger = logging.getLogger(__name__)


def get_tenant_id_from_context() -> ObjectId:
    return get_tenant_id()


router = APIRouter(prefix="/backups", tags=["backups"])


def _doc_to_dict(doc) -> dict:
    return {
        "id": str(doc.id),
        "backup_type": doc.backup_type,
        "status": doc.status,
        "s3_location": doc.s3_location,
        "s3_key": doc.s3_key,
        "size_bytes": doc.size_bytes,
        "file_count": doc.file_count,
        "checksum": doc.checksum,
        "encryption_key_id": doc.encryption_key_id,
        "started_at": doc.started_at.isoformat() if doc.started_at else None,
        "completed_at": doc.completed_at.isoformat() if doc.completed_at else None,
        "error_message": doc.error_message,
        "retention_days": doc.retention_days,
        "is_verified": doc.is_verified,
        "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
        "metadata": doc.metadata,
        "created_at": doc.created_at.isoformat(),
    }


@router.get("", response_model=dict)
@tenant_isolated
async def get_backups(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Get all backups for the tenant."""
    try:
        items = Backup.objects(tenant_id=tenant_id).order_by("-created_at").skip(skip).limit(limit)
        total = Backup.objects(tenant_id=tenant_id).count()
        return {"backups": [_doc_to_dict(b) for b in items], "total": total}
    except Exception as e:
        logger.error(f"Failed to get backups: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get backups")


@router.get("/statistics", response_model=dict)
@tenant_isolated
async def get_backup_statistics(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get backup statistics for the tenant."""
    try:
        all_backups = Backup.objects(tenant_id=tenant_id)
        total = all_backups.count()
        completed = all_backups.filter(status="completed").count()
        failed = all_backups.filter(status="failed").count()
        total_size = sum(b.size_bytes for b in all_backups if b.size_bytes) or 0
        last = all_backups.order_by("-created_at").first()
        last_backup_at = last.created_at.isoformat() if last else None
        last_backup_size = last.size_bytes if last and last.size_bytes else 0
        return {
            "total_backups": total,
            "completed_backups": completed,
            "failed_backups": failed,
            "total_size_bytes": total_size,
            "last_backup_at": last_backup_at,
            "last_backup_size_bytes": last_backup_size,
        }
    except Exception as e:
        logger.error(f"Failed to get backup statistics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get backup statistics")


@router.get("/schedule", response_model=dict)
@tenant_isolated
async def get_backup_schedule(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get the backup schedule for the tenant."""
    try:
        schedule = BackupSchedule.objects(tenant_id=tenant_id).first()
        if not schedule:
            return {
                "id": str(tenant_id),
                "backup_frequency": "daily",
                "backup_time": "00:00",
                "retention_days": 30,
                "is_enabled": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        return {
            "id": str(schedule.id),
            "backup_frequency": schedule.backup_frequency,
            "backup_time": schedule.backup_time,
            "retention_days": schedule.retention_days,
            "is_enabled": schedule.is_enabled,
            "last_backup_at": schedule.last_backup_at.isoformat() if schedule.last_backup_at else None,
            "next_backup_at": schedule.next_backup_at.isoformat() if schedule.next_backup_at else None,
            "created_at": schedule.created_at.isoformat(),
            "updated_at": schedule.updated_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get backup schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get backup schedule")


@router.post("", response_model=dict)
@tenant_isolated
async def create_backup(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    backup_type: str = Body("full", embed=True),
):
    """Create a new backup."""
    try:
        from app.services.tenant_service import TenantService
        tenant = TenantService.get_tenant(tenant_id)
        s3_key = f"backups/{tenant_id}/{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{backup_type}.bak"
        backup = Backup(
            tenant_id=tenant_id,
            backup_type=backup_type,
            status="in_progress",
            s3_location="",
            s3_key=s3_key,
            retention_days=30,
        )
        backup.save()
        return _doc_to_dict(backup)
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create backup")


@router.post("/{backup_id}/verify", response_model=dict)
@tenant_isolated
async def verify_backup(
    backup_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Verify a backup."""
    try:
        backup = Backup.objects(id=ObjectId(backup_id), tenant_id=tenant_id).first()
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        backup.is_verified = True
        backup.verified_at = datetime.utcnow()
        backup.save()
        return _doc_to_dict(backup)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify backup: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to verify backup")


@router.post("/{backup_id}/restore", response_model=dict)
@tenant_isolated
async def create_restore(
    backup_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    restore_type: str = Body("full", embed=True),
    restore_point: Optional[str] = Body(None, embed=True),
):
    """Create a restore operation."""
    try:
        from bson.errors import InvalidId
        try:
            bkp = Backup.objects(id=ObjectId(backup_id), tenant_id=tenant_id).first()
        except InvalidId:
            bkp = None
        if not bkp:
            raise HTTPException(status_code=404, detail="Backup not found")
        restore = BackupRestore(
            tenant_id=tenant_id,
            backup_id=ObjectId(backup_id),
            restore_type=restore_type,
            status="pending",
            target_database="",
        )
        import datetime as dt
        if restore_point:
            try:
                restore.restore_point = dt.datetime.fromisoformat(restore_point)
            except Exception:
                pass
        restore.save()
        return {
            "id": str(restore.id),
            "backup_id": str(restore.backup_id),
            "status": restore.status,
            "created_at": restore.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create restore: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create restore")


@router.get("/restores", response_model=dict)
@tenant_isolated
async def get_restores(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Get restore history."""
    try:
        items = BackupRestore.objects(tenant_id=tenant_id).order_by("-created_at").skip(skip).limit(limit)
        total = BackupRestore.objects(tenant_id=tenant_id).count()
        result = []
        for r in items:
            result.append({
                "id": str(r.id),
                "backup_id": str(r.backup_id),
                "status": r.status,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat(),
            })
        return {"restores": result, "total": total}
    except Exception as e:
        logger.error(f"Failed to get restores: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get restores")


@router.post("/restores/{restore_id}/verify", response_model=dict)
@tenant_isolated
async def verify_restore(
    restore_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Verify a restore operation."""
    try:
        restore = BackupRestore.objects(id=ObjectId(restore_id), tenant_id=tenant_id).first()
        if not restore:
            raise HTTPException(status_code=404, detail="Restore not found")
        restore.is_verified = True
        restore.verified_at = datetime.utcnow()
        restore.save()
        return {"id": str(restore.id), "is_verified": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify restore: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to verify restore")


@router.put("/schedule", response_model=dict)
@tenant_isolated
async def update_backup_schedule(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    backup_frequency: str = Body(...),
    backup_time: str = Body(...),
    retention_days: int = Body(30),
    is_enabled: bool = Body(True),
):
    """Update backup schedule."""
    try:
        schedule, _ = BackupSchedule.objects.get_or_create(
            tenant_id=tenant_id,
            defaults={
                "backup_frequency": backup_frequency,
                "backup_time": backup_time,
                "retention_days": retention_days,
                "is_enabled": is_enabled,
            },
        )
        schedule.backup_frequency = backup_frequency
        schedule.backup_time = backup_time
        schedule.retention_days = retention_days
        schedule.is_enabled = is_enabled
        schedule.updated_at = datetime.utcnow()
        schedule.save()
        return {
            "id": str(schedule.id),
            "backup_frequency": schedule.backup_frequency,
            "backup_time": schedule.backup_time,
            "retention_days": schedule.retention_days,
            "is_enabled": schedule.is_enabled,
            "updated_at": schedule.updated_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to update backup schedule: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to update backup schedule")


@router.get("/{backup_id}/download")
@tenant_isolated
async def download_backup(
    backup_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Download a backup."""
    try:
        backup = Backup.objects(id=ObjectId(backup_id), tenant_id=tenant_id).first()
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        return {"s3_key": backup.s3_key, "s3_location": backup.s3_location, "filename": backup.s3_key.split("/")[-1]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get download info")
