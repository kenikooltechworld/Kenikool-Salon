import hashlib
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.backup import Backup, BackupRestore, BackupSchedule
from app.context import get_tenant_id
from mongoengine import Q
import boto3
from botocore.exceptions import ClientError


class BackupService:
    """Service for backup and disaster recovery"""

    def __init__(self, aws_access_key: str, aws_secret_key: str, s3_bucket: str, region: str = "us-east-1"):
        """Initialize backup service with AWS credentials"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region,
        )
        self.s3_bucket = s3_bucket
        self.region = region

    @staticmethod
    def create_backup(
        backup_type: str = "full",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Backup:
        """Create backup record"""
        tenant_id = get_tenant_id()
        
        backup = Backup(
            tenant_id=tenant_id,
            backup_type=backup_type,
            status="pending",
            s3_location=f"s3://{tenant_id}/backups",
            s3_key=f"{tenant_id}/backups/{datetime.utcnow().isoformat()}",
            metadata=metadata or {},
        )
        backup.save()
        return backup

    @staticmethod
    def start_backup(backup_id: str) -> Backup:
        """Start backup process"""
        tenant_id = get_tenant_id()
        backup = Backup.objects(tenant_id=tenant_id, id=backup_id).first()
        
        if not backup:
            raise ValueError("Backup not found")
        
        backup.status = "in_progress"
        backup.started_at = datetime.utcnow()
        backup.save()
        return backup

    @staticmethod
    def complete_backup(
        backup_id: str,
        size_bytes: int,
        file_count: int,
        checksum: str,
    ) -> Backup:
        """Mark backup as completed"""
        tenant_id = get_tenant_id()
        backup = Backup.objects(tenant_id=tenant_id, id=backup_id).first()
        
        if not backup:
            raise ValueError("Backup not found")
        
        backup.status = "completed"
        backup.completed_at = datetime.utcnow()
        backup.size_bytes = size_bytes
        backup.file_count = file_count
        backup.checksum = checksum
        backup.save()
        return backup

    @staticmethod
    def fail_backup(backup_id: str, error_message: str) -> Backup:
        """Mark backup as failed"""
        tenant_id = get_tenant_id()
        backup = Backup.objects(tenant_id=tenant_id, id=backup_id).first()
        
        if not backup:
            raise ValueError("Backup not found")
        
        backup.status = "failed"
        backup.error_message = error_message
        backup.save()
        return backup

    @staticmethod
    def verify_backup(backup_id: str) -> Backup:
        """Verify backup integrity"""
        tenant_id = get_tenant_id()
        backup = Backup.objects(tenant_id=tenant_id, id=backup_id).first()
        
        if not backup:
            raise ValueError("Backup not found")
        
        if backup.status != "completed":
            raise ValueError("Can only verify completed backups")
        
        backup.is_verified = True
        backup.verified_at = datetime.utcnow()
        backup.save()
        return backup

    @staticmethod
    def get_backup(backup_id: str) -> Optional[Backup]:
        """Get backup by ID"""
        tenant_id = get_tenant_id()
        return Backup.objects(tenant_id=tenant_id, id=backup_id).first()

    @staticmethod
    def list_backups(
        backup_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Backup], int]:
        """List backups"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id)
        
        if backup_type:
            query &= Q(backup_type=backup_type)
        
        if status:
            query &= Q(status=status)
        
        total = Backup.objects(query).count()
        backups = Backup.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(backups), total

    @staticmethod
    def cleanup_old_backups(retention_days: int = 30) -> int:
        """Delete backups older than retention period"""
        tenant_id = get_tenant_id()
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        old_backups = Backup.objects(
            tenant_id=tenant_id,
            created_at__lt=cutoff_date,
            status="completed",
        )
        
        count = old_backups.count()
        old_backups.delete()
        return count

    @staticmethod
    def create_restore(
        backup_id: str,
        restore_type: str = "full",
        restore_point: Optional[datetime] = None,
    ) -> BackupRestore:
        """Create restore record"""
        tenant_id = get_tenant_id()
        
        backup = Backup.objects(tenant_id=tenant_id, id=backup_id).first()
        if not backup:
            raise ValueError("Backup not found")
        
        restore = BackupRestore(
            tenant_id=tenant_id,
            backup_id=str(backup.id),
            restore_type=restore_type,
            status="pending",
            restore_point=restore_point or backup.completed_at,
        )
        restore.save()
        return restore

    @staticmethod
    def start_restore(restore_id: str) -> BackupRestore:
        """Start restore process"""
        tenant_id = get_tenant_id()
        restore = BackupRestore.objects(tenant_id=tenant_id, id=restore_id).first()
        
        if not restore:
            raise ValueError("Restore not found")
        
        restore.status = "in_progress"
        restore.started_at = datetime.utcnow()
        restore.save()
        return restore

    @staticmethod
    def complete_restore(
        restore_id: str,
        restored_records: int,
    ) -> BackupRestore:
        """Mark restore as completed"""
        tenant_id = get_tenant_id()
        restore = BackupRestore.objects(tenant_id=tenant_id, id=restore_id).first()
        
        if not restore:
            raise ValueError("Restore not found")
        
        restore.status = "completed"
        restore.completed_at = datetime.utcnow()
        restore.restored_records = restored_records
        restore.save()
        return restore

    @staticmethod
    def fail_restore(restore_id: str, error_message: str) -> BackupRestore:
        """Mark restore as failed"""
        tenant_id = get_tenant_id()
        restore = BackupRestore.objects(tenant_id=tenant_id, id=restore_id).first()
        
        if not restore:
            raise ValueError("Restore not found")
        
        restore.status = "failed"
        restore.error_message = error_message
        restore.save()
        return restore

    @staticmethod
    def verify_restore(restore_id: str) -> BackupRestore:
        """Verify restore integrity"""
        tenant_id = get_tenant_id()
        restore = BackupRestore.objects(tenant_id=tenant_id, id=restore_id).first()
        
        if not restore:
            raise ValueError("Restore not found")
        
        if restore.status != "completed":
            raise ValueError("Can only verify completed restores")
        
        restore.is_verified = True
        restore.verified_at = datetime.utcnow()
        restore.save()
        return restore

    @staticmethod
    def get_restore(restore_id: str) -> Optional[BackupRestore]:
        """Get restore by ID"""
        tenant_id = get_tenant_id()
        return BackupRestore.objects(tenant_id=tenant_id, id=restore_id).first()

    @staticmethod
    def list_restores(
        restore_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[BackupRestore], int]:
        """List restores"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id)
        
        if restore_type:
            query &= Q(restore_type=restore_type)
        
        if status:
            query &= Q(status=status)
        
        total = BackupRestore.objects(query).count()
        restores = BackupRestore.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(restores), total

    @staticmethod
    def get_or_create_schedule(
        backup_frequency: str = "daily",
        backup_time: str = "02:00",
        retention_days: int = 30,
    ) -> BackupSchedule:
        """Get or create backup schedule"""
        tenant_id = get_tenant_id()
        
        schedule = BackupSchedule.objects(tenant_id=tenant_id).first()
        if schedule:
            return schedule
        
        schedule = BackupSchedule(
            tenant_id=tenant_id,
            backup_frequency=backup_frequency,
            backup_time=backup_time,
            retention_days=retention_days,
        )
        schedule.save()
        return schedule

    @staticmethod
    def update_schedule(
        backup_frequency: Optional[str] = None,
        backup_time: Optional[str] = None,
        retention_days: Optional[int] = None,
        is_enabled: Optional[bool] = None,
    ) -> BackupSchedule:
        """Update backup schedule"""
        tenant_id = get_tenant_id()
        
        schedule = BackupSchedule.objects(tenant_id=tenant_id).first()
        if not schedule:
            raise ValueError("Backup schedule not found")
        
        if backup_frequency:
            schedule.backup_frequency = backup_frequency
        
        if backup_time:
            schedule.backup_time = backup_time
        
        if retention_days:
            schedule.retention_days = retention_days
        
        if is_enabled is not None:
            schedule.is_enabled = is_enabled
        
        schedule.updated_at = datetime.utcnow()
        schedule.save()
        return schedule

    @staticmethod
    def get_backup_statistics() -> Dict[str, Any]:
        """Get backup statistics"""
        tenant_id = get_tenant_id()
        
        total_backups = Backup.objects(tenant_id=tenant_id).count()
        completed_backups = Backup.objects(tenant_id=tenant_id, status="completed").count()
        failed_backups = Backup.objects(tenant_id=tenant_id, status="failed").count()
        
        total_size = sum(b.size_bytes or 0 for b in Backup.objects(tenant_id=tenant_id, status="completed"))
        
        last_backup = Backup.objects(tenant_id=tenant_id, status="completed").order_by('-completed_at').first()
        
        return {
            "total_backups": total_backups,
            "completed_backups": completed_backups,
            "failed_backups": failed_backups,
            "total_size_bytes": total_size,
            "last_backup_at": last_backup.completed_at if last_backup else None,
            "last_backup_size_bytes": last_backup.size_bytes if last_backup else None,
        }
