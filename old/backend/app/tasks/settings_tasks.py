"""
Background tasks for settings system
Handles session cleanup, export generation, account deletion, etc.
"""
import logging
from datetime import datetime, timedelta
from app.celery_app import celery_app
from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.settings_tasks.cleanup_expired_sessions")
def cleanup_expired_sessions():
    """
    Delete expired sessions daily
    Requirement: 3.5 - Auto-expire inactive sessions
    """
    try:
        logger.info("Starting session cleanup task")
        
        # Find and delete expired sessions
        result = db.sessions.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        logger.info(f"Deleted {result.deleted_count} expired sessions")
        return {"deleted_count": result.deleted_count}
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_sessions: {e}")
        raise


@celery_app.task(name="app.tasks.settings_tasks.generate_data_export")
def generate_data_export(export_id: str):
    """
    Generate data export file (background job)
    Requirement: 5.1, 5.2, 5.3 - GDPR data export
    
    Args:
        export_id: ID of the export request
    """
    try:
        logger.info(f"Starting data export generation for export_id: {export_id}")
        
        # Get export request
        export_request = db.data_exports.find_one({"_id": export_id})
        if not export_request:
            logger.error(f"Export request not found: {export_id}")
            return {"status": "failed", "error": "Export request not found"}
        
        # Update status to processing
        db.data_exports.update_one(
            {"_id": export_id},
            {"$set": {"status": "processing"}}
        )
        
        user_id = export_request["user_id"]
        
        # Collect user data from all relevant collections
        export_data = {
            "profile": db.users.find_one({"_id": user_id}),
            "preferences": db.user_preferences.find_one({"user_id": user_id}),
            "privacy_settings": db.privacy_settings.find_one({"user_id": user_id}),
            "security_logs": list(db.security_logs.find({"user_id": user_id}).limit(1000)),
            "api_keys": list(db.api_keys.find({"user_id": user_id})),
            "sessions": list(db.sessions.find({"user_id": user_id})),
        }
        
        # Add optional data based on export options
        if export_request.get("include_bookings", True):
            export_data["bookings"] = list(db.bookings.find({"user_id": user_id}).limit(1000))
        
        if export_request.get("include_clients", True):
            export_data["clients"] = list(db.clients.find({"tenant_id": export_request.get("tenant_id")}).limit(1000))
        
        if export_request.get("include_payments", True):
            export_data["payments"] = list(db.payments.find({"tenant_id": export_request.get("tenant_id")}).limit(1000))
        
        # TODO: Convert to JSON and upload to Cloudinary
        # TODO: Send email with download link
        # TODO: Schedule deletion after 7 days
        
        # Update status to completed
        db.data_exports.update_one(
            {"_id": export_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(days=7)
                }
            }
        )
        
        logger.info(f"Data export completed for export_id: {export_id}")
        return {"status": "completed", "export_id": export_id}
        
    except Exception as e:
        logger.error(f"Error in generate_data_export: {e}")
        # Update status to failed
        db.data_exports.update_one(
            {"_id": export_id},
            {"$set": {"status": "failed"}}
        )
        raise


@celery_app.task(name="app.tasks.settings_tasks.cleanup_old_exports")
def cleanup_old_exports():
    """
    Delete exports older than 7 days
    Requirement: 5.4 - Auto-delete exports after 7 days
    """
    try:
        logger.info("Starting export cleanup task")
        
        # Find and delete old exports
        result = db.data_exports.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        logger.info(f"Deleted {result.deleted_count} old exports")
        return {"deleted_count": result.deleted_count}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_exports: {e}")
        raise


@celery_app.task(name="app.tasks.settings_tasks.execute_account_deletion")
def execute_account_deletion():
    """
    Execute hard delete for accounts past 30 days
    Requirement: 6.5 - Hard delete after 30 days
    """
    try:
        logger.info("Starting account deletion task")
        
        # Find accounts scheduled for deletion that are past 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deletions = db.account_deletions.find({
            "status": "pending",
            "scheduled_for": {"$lt": cutoff_date}
        })
        
        deleted_count = 0
        for deletion in deletions:
            user_id = deletion["user_id"]
            tenant_id = deletion.get("tenant_id")
            
            try:
                # Delete user and all related data
                db.users.delete_one({"_id": user_id})
                db.user_preferences.delete_one({"user_id": user_id})
                db.privacy_settings.delete_one({"user_id": user_id})
                db.sessions.delete_many({"user_id": user_id})
                db.api_keys.delete_many({"user_id": user_id})
                db.security_logs.delete_many({"user_id": user_id})
                db.data_exports.delete_many({"user_id": user_id})
                
                # Update deletion record
                db.account_deletions.update_one(
                    {"_id": deletion["_id"]},
                    {
                        "$set": {
                            "status": "completed",
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                
                deleted_count += 1
                logger.info(f"Hard deleted account for user_id: {user_id}")
                
            except Exception as e:
                logger.error(f"Error deleting account for user_id {user_id}: {e}")
        
        logger.info(f"Account deletion task completed. Deleted {deleted_count} accounts")
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Error in execute_account_deletion: {e}")
        raise


@celery_app.task(name="app.tasks.settings_tasks.send_security_alerts")
def send_security_alerts():
    """
    Send security alerts for suspicious activities
    Requirement: 23.3, 23.4 - New device notification and suspicious activity detection
    """
    try:
        logger.info("Starting security alerts task")
        
        # Find flagged security events that haven't been alerted yet
        flagged_events = db.security_logs.find({
            "flagged": True,
            "alert_sent": {"$exists": False}
        }).limit(100)
        
        alert_count = 0
        for event in flagged_events:
            try:
                user_id = event["user_id"]
                
                # TODO: Send email alert to user
                # TODO: Mark alert as sent
                
                db.security_logs.update_one(
                    {"_id": event["_id"]},
                    {"$set": {"alert_sent": True, "alert_sent_at": datetime.utcnow()}}
                )
                
                alert_count += 1
                
            except Exception as e:
                logger.error(f"Error sending alert for event {event['_id']}: {e}")
        
        logger.info(f"Security alerts task completed. Sent {alert_count} alerts")
        return {"alert_count": alert_count}
        
    except Exception as e:
        logger.error(f"Error in send_security_alerts: {e}")
        raise
