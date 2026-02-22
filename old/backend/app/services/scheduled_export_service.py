"""
Scheduled export service for automated analytics data exports
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ScheduledExportService:
    """Service for managing scheduled analytics exports"""

    def __init__(self):
        """Initialize scheduled export service"""
        self.exports = {}
        self.schedules = {}

    async def create_scheduled_export(
        self,
        tenant_id: str,
        name: str,
        format: str,
        schedule: str,
        recipients: List[str],
        filters: List[Dict[str, Any]] = None,
        date_range: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a scheduled export"""
        try:
            export_id = f"scheduled_export_{datetime.utcnow().timestamp()}"
            
            export_config = {
                "export_id": export_id,
                "tenant_id": tenant_id,
                "name": name,
                "format": format,
                "schedule": schedule,
                "recipients": recipients,
                "filters": filters or [],
                "date_range": date_range or {
                    "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "next_run": self._calculate_next_run(schedule),
                "last_run": None,
                "run_count": 0
            }
            
            self.schedules[export_id] = export_config
            logger.info(f"Scheduled export created: {export_id}")
            return export_config
        except Exception as e:
            logger.error(f"Error creating scheduled export: {e}")
            raise

    async def get_scheduled_export(self, export_id: str) -> Optional[Dict[str, Any]]:
        """Get scheduled export details"""
        try:
            return self.schedules.get(export_id)
        except Exception as e:
            logger.error(f"Error getting scheduled export: {e}")
            raise

    async def list_scheduled_exports(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List all scheduled exports for a tenant"""
        try:
            return [
                export for export in self.schedules.values()
                if export["tenant_id"] == tenant_id
            ]
        except Exception as e:
            logger.error(f"Error listing scheduled exports: {e}")
            raise

    async def update_scheduled_export(
        self,
        export_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update a scheduled export"""
        try:
            if export_id not in self.schedules:
                raise ValueError(f"Export {export_id} not found")
            
            export = self.schedules[export_id]
            
            # Update allowed fields
            allowed_fields = ["name", "format", "schedule", "recipients", "filters", "status"]
            for field, value in kwargs.items():
                if field in allowed_fields:
                    export[field] = value
            
            export["updated_at"] = datetime.utcnow().isoformat()
            
            # Recalculate next run if schedule changed
            if "schedule" in kwargs:
                export["next_run"] = self._calculate_next_run(kwargs["schedule"])
            
            logger.info(f"Scheduled export updated: {export_id}")
            return export
        except Exception as e:
            logger.error(f"Error updating scheduled export: {e}")
            raise

    async def delete_scheduled_export(self, export_id: str) -> Dict[str, Any]:
        """Delete a scheduled export"""
        try:
            if export_id not in self.schedules:
                raise ValueError(f"Export {export_id} not found")
            
            export = self.schedules.pop(export_id)
            logger.info(f"Scheduled export deleted: {export_id}")
            return {"status": "deleted", "export_id": export_id}
        except Exception as e:
            logger.error(f"Error deleting scheduled export: {e}")
            raise

    async def pause_scheduled_export(self, export_id: str) -> Dict[str, Any]:
        """Pause a scheduled export"""
        try:
            return await self.update_scheduled_export(export_id, status="paused")
        except Exception as e:
            logger.error(f"Error pausing scheduled export: {e}")
            raise

    async def resume_scheduled_export(self, export_id: str) -> Dict[str, Any]:
        """Resume a paused scheduled export"""
        try:
            export = await self.update_scheduled_export(export_id, status="active")
            export["next_run"] = self._calculate_next_run(export["schedule"])
            return export
        except Exception as e:
            logger.error(f"Error resuming scheduled export: {e}")
            raise

    async def get_export_history(self, export_id: str) -> List[Dict[str, Any]]:
        """Get execution history for a scheduled export"""
        try:
            if export_id not in self.exports:
                return []
            
            return self.exports[export_id]
        except Exception as e:
            logger.error(f"Error getting export history: {e}")
            raise

    async def record_export_execution(
        self,
        export_id: str,
        status: str,
        file_size: int = 0,
        error_message: str = None
    ) -> Dict[str, Any]:
        """Record an export execution"""
        try:
            execution = {
                "execution_id": f"exec_{datetime.utcnow().timestamp()}",
                "export_id": export_id,
                "status": status,
                "executed_at": datetime.utcnow().isoformat(),
                "file_size": file_size,
                "error_message": error_message
            }
            
            if export_id not in self.exports:
                self.exports[export_id] = []
            
            self.exports[export_id].append(execution)
            
            # Update schedule with execution info
            if export_id in self.schedules:
                schedule = self.schedules[export_id]
                schedule["last_run"] = datetime.utcnow().isoformat()
                schedule["run_count"] = schedule.get("run_count", 0) + 1
                schedule["next_run"] = self._calculate_next_run(schedule["schedule"])
            
            logger.info(f"Export execution recorded: {execution['execution_id']}")
            return execution
        except Exception as e:
            logger.error(f"Error recording export execution: {e}")
            raise

    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time based on schedule"""
        now = datetime.utcnow()
        if schedule == "daily":
            next_run = now + timedelta(days=1)
        elif schedule == "weekly":
            next_run = now + timedelta(weeks=1)
        elif schedule == "monthly":
            next_run = now + timedelta(days=30)
        elif schedule == "hourly":
            next_run = now + timedelta(hours=1)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.isoformat()

    async def get_pending_exports(self) -> List[Dict[str, Any]]:
        """Get all exports that are due to run"""
        try:
            now = datetime.utcnow()
            pending = []
            
            for export_id, export in self.schedules.items():
                if export["status"] != "active":
                    continue
                
                next_run = datetime.fromisoformat(export["next_run"])
                if next_run <= now:
                    pending.append(export)
            
            return pending
        except Exception as e:
            logger.error(f"Error getting pending exports: {e}")
            raise
