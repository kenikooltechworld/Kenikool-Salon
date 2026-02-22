from mongoengine import StringField, DateTimeField, IntField, BooleanField, DictField
from datetime import datetime
from app.models.base import BaseDocument


class Backup(BaseDocument):
    """Backup record for disaster recovery"""
    tenant_id = StringField(required=True)
    backup_type = StringField(required=True, choices=['full', 'incremental', 'differential'])
    status = StringField(required=True, choices=['pending', 'in_progress', 'completed', 'failed'])
    s3_location = StringField(required=True)
    s3_key = StringField(required=True)
    size_bytes = IntField()
    file_count = IntField()
    checksum = StringField()
    encryption_key_id = StringField()
    started_at = DateTimeField()
    completed_at = DateTimeField()
    error_message = StringField()
    retention_days = IntField(default=30)
    is_verified = BooleanField(default=False)
    verified_at = DateTimeField()
    metadata = DictField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'backups',
        'indexes': [
            ('tenant_id', '-created_at'),
            ('tenant_id', 'status'),
            ('tenant_id', 'backup_type'),
            ('s3_key',),
        ]
    }


class BackupRestore(BaseDocument):
    """Backup restore record"""
    tenant_id = StringField(required=True)
    backup_id = StringField(required=True)
    restore_type = StringField(required=True, choices=['full', 'point_in_time', 'selective'])
    status = StringField(required=True, choices=['pending', 'in_progress', 'completed', 'failed'])
    restore_point = DateTimeField()
    target_database = StringField()
    restored_records = IntField()
    error_message = StringField()
    started_at = DateTimeField()
    completed_at = DateTimeField()
    verified_at = DateTimeField()
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'backup_restores',
        'indexes': [
            ('tenant_id', '-created_at'),
            ('tenant_id', 'status'),
            ('backup_id',),
        ]
    }


class BackupSchedule(BaseDocument):
    """Backup schedule configuration"""
    tenant_id = StringField(required=True, unique=True)
    backup_frequency = StringField(required=True, choices=['daily', 'weekly', 'monthly'])
    backup_time = StringField(required=True)  # HH:MM format
    retention_days = IntField(default=30)
    is_enabled = BooleanField(default=True)
    last_backup_at = DateTimeField()
    next_backup_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'backup_schedules',
        'indexes': [
            ('tenant_id',),
            ('is_enabled',),
        ]
    }
