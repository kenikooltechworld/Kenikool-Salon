"""
Celery tasks for retention campaigns
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from app.services.retention_service import get_at_risk_clients
from app.services.retention_campaign_service import generate_retention_message, select_template_for_risk_level
from app.services.termii_service import send_whatsapp
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    """Base task class that handles async functions"""
    
    def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(*args, **kwargs))
    
    async def run(self, *args, **kwargs):
        raise NotImplementedError()


@celery_app.task(base=AsyncTask, bind=True)
async def run_retention_campaign(self, tenant_id: str, min_risk_level: str = "medium"):
    """
    Run automated retention campaign for at-risk clients
    Scheduled to run daily
    """
    try:
        db = Database.get_db()
        
        # Get tenant
        from bson import ObjectId
        tenant = await db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if not tenant:
            logger.error(f"Tenant {tenant_id} not found")
            return {"success": False, "error": "Tenant not found"}
        
        # Get at-risk clients
        at_risk_clients = await get_at_risk_clients(tenant_id, db, min_risk_level)
        
        if not at_risk_clients:
            logger.info(f"No at-risk clients found for tenant {tenant_id}")
            return {"success": True, "sent": 0}
        
        # Create campaign record
        campaign_data = {
            "tenant_id": tenant_id,
            "campaign_type": "retention",
            "min_risk_level": min_risk_level,
            "target_count": len(at_risk_clients),
            "sent_count": 0,
            "status": "running",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "messages": []
        }
        
        campaign_result = await db.campaigns.insert_one(campaign_data)
        campaign_id = str(campaign_result.inserted_id)
        
        sent_count = 0
        failed_count = 0
        
        # Send messages to at-risk clients
        for client in at_risk_clients[:50]:  # Limit to 50 per run
            try:
                # Select template
                template_type = select_template_for_risk_level(
                    client["risk_level"],
                    client["days_since_last_visit"]
                )
                
                # Get client's favorite stylist (most recent booking)
                recent_booking = await db.bookings.find_one({
                    "client_id": client["client_id"],
                    "tenant_id": tenant_id,
                    "status": "completed"
                }, sort=[("booking_date", -1)])
                
                stylist_name = recent_booking.get("stylist_name", "your stylist") if recent_booking else "your stylist"
                
                # Generate message
                message = generate_retention_message(
                    template_type,
                    {
                        "name": client["client_name"],
                        "days_since_last_visit": client["days_since_last_visit"]
                    },
                    {
                        "salon_name": tenant["salon_name"],
                        "phone": tenant["phone"]
                    },
                    stylist_name=stylist_name,
                    discount=10 if client["risk_level"] == "high" else 5
                )
                
                # Send message
                success = await send_whatsapp(client["client_phone"], message)
                
                # Record message
                message_record = {
                    "client_id": client["client_id"],
                    "client_name": client["client_name"],
                    "client_phone": client["client_phone"],
                    "risk_level": client["risk_level"],
                    "template_type": template_type,
                    "sent": success,
                    "sent_at": datetime.utcnow() if success else None
                }
                
                await db.campaigns.update_one(
                    {"_id": ObjectId(campaign_id)},
                    {"$push": {"messages": message_record}}
                )
                
                if success:
                    sent_count += 1
                    logger.info(f"Retention message sent to {client['client_name']}")
                else:
                    failed_count += 1
            
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending retention message to {client.get('client_name')}: {e}")
        
        # Update campaign status
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "sent_count": sent_count,
                    "failed_count": failed_count,
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Retention campaign completed for tenant {tenant_id}: {sent_count} sent, {failed_count} failed")
        return {
            "success": True,
            "campaign_id": campaign_id,
            "sent": sent_count,
            "failed": failed_count
        }
    
    except Exception as e:
        logger.error(f"Error in run_retention_campaign task: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(base=AsyncTask, bind=True)
async def send_birthday_campaigns(self):
    """
    Send birthday messages to clients
    Runs daily
    """
    try:
        db = Database.get_db()
        
        # Get all tenants
        tenants = await db.tenants.find({"is_active": True}).to_list(length=None)
        
        total_sent = 0
        
        for tenant in tenants:
            tenant_id = str(tenant["_id"])
            
            # Get clients with birthdays today
            # Note: This requires birthday field in client model
            today = datetime.utcnow()
            
            clients = await db.clients.find({
                "tenant_id": tenant_id,
                "birthday_month": today.month,
                "birthday_day": today.day
            }).to_list(length=None)
            
            for client in clients:
                try:
                    # Generate birthday message
                    message = generate_retention_message(
                        "birthday",
                        {"name": client["name"]},
                        {
                            "salon_name": tenant["salon_name"],
                            "phone": tenant["phone"]
                        },
                        free_service="hair treatment"
                    )
                    
                    # Send message
                    success = await send_whatsapp(client["phone"], message)
                    
                    if success:
                        total_sent += 1
                        logger.info(f"Birthday message sent to {client['name']}")
                
                except Exception as e:
                    logger.error(f"Error sending birthday message: {e}")
        
        logger.info(f"Birthday campaigns completed: {total_sent} messages sent")
        return {"success": True, "sent": total_sent}
    
    except Exception as e:
        logger.error(f"Error in send_birthday_campaigns task: {e}")
        return {"success": False, "error": str(e)}
