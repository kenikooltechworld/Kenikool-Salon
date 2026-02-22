"""
Celery tasks for automated marketing campaigns
"""
from celery import shared_task
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.services.campaign_automation_service import CampaignAutomationService
from app.services.automation_service import AutomationService
from app.services.channel_service import ChannelService
from bson import ObjectId

logger = logging.getLogger(__name__)


@shared_task(
    name="check_birthday_campaigns",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # Retry after 5 minutes
)
def check_birthday_campaigns_task(self):
    """
    Daily task to check for birthdays and send campaigns
    
    This task:
    - Checks for clients with birthdays today
    - Retrieves automation settings for each tenant
    - Sends birthday campaigns via configured channels
    - Records execution in automation history
    - Implements retry logic for failed sends
    
    This task should be scheduled to run daily (e.g., at 9 AM)
    
    Requirements: 3.2, 3.3
    """
    logger.info("Starting birthday campaigns check...")
    
    try:
        db = Database.get_db()
        automation_service = AutomationService(db)
        
        # Get all active tenants
        tenants = list(db.tenants.find({"status": "active"}))
        
        total_sent = 0
        total_failed = 0
        total_recipients = 0
        
        for tenant in tenants:
            try:
                tenant_id = str(tenant["_id"])
                
                # Get automation settings for this tenant
                settings = automation_service.get_settings(tenant_id)
                if not settings or not settings.get("enabled"):
                    logger.debug(f"Automation disabled for tenant: {tenant_id}")
                    continue
                
                birthday_config = settings.get("birthday_campaigns", {})
                if not birthday_config.get("enabled"):
                    logger.debug(f"Birthday campaigns disabled for tenant: {tenant_id}")
                    continue
                
                # Send birthday campaigns for this tenant
                sent_count, failed_count, recipient_count = send_birthday_campaigns_for_tenant(
                    db=db,
                    tenant_id=tenant_id,
                    birthday_config=birthday_config,
                    automation_service=automation_service
                )
                
                total_sent += sent_count
                total_failed += failed_count
                total_recipients += recipient_count
                
                if sent_count > 0 or failed_count > 0:
                    logger.info(
                        f"Birthday campaigns for tenant {tenant_id}: "
                        f"sent={sent_count}, failed={failed_count}, recipients={recipient_count}"
                    )
                    
                    # Record execution in automation history
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="birthday",
                        campaign_id="auto_birthday",
                        recipients_count=recipient_count,
                        sent_count=sent_count,
                        failed_count=failed_count,
                        status="success" if failed_count == 0 else "partial"
                    )
            
            except Exception as e:
                logger.error(f"Error processing birthday campaigns for tenant {tenant.get('_id')}: {e}", exc_info=True)
                
                # Record failed execution
                try:
                    tenant_id = str(tenant["_id"])
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="birthday",
                        campaign_id="auto_birthday",
                        recipients_count=0,
                        sent_count=0,
                        failed_count=0,
                        status="failed",
                        error_message=str(e)
                    )
                except Exception as record_error:
                    logger.error(f"Failed to record execution error: {record_error}")
        
        logger.info(
            f"Birthday campaigns check completed. "
            f"Total sent: {total_sent}, failed: {total_failed}, recipients: {total_recipients}"
        )
        
        return {
            "status": "completed",
            "total_sent": total_sent,
            "total_failed": total_failed,
            "total_recipients": total_recipients,
            "tenants_processed": len(tenants)
        }
    
    except Exception as e:
        logger.error(f"Fatal error in birthday campaigns task: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


def send_birthday_campaigns_for_tenant(
    db,
    tenant_id: str,
    birthday_config: Dict,
    automation_service: AutomationService
) -> tuple:
    """
    Send birthday campaigns to clients with birthdays today
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        birthday_config: Birthday automation configuration
        automation_service: AutomationService instance
    
    Returns:
        Tuple of (sent_count, failed_count, recipient_count)
    """
    today = datetime.utcnow()
    sent_count = 0
    failed_count = 0
    
    # Get clients with birthdays today
    clients = list(db.clients.find({
        "tenant_id": tenant_id,
        "$expr": {
            "$and": [
                {"$eq": [{"$dayOfMonth": "$birthday"}, today.day]},
                {"$eq": [{"$month": "$birthday"}, today.month]}
            ]
        }
    }))
    
    recipient_count = len(clients)
    
    if recipient_count == 0:
        logger.debug(f"No birthday clients found for tenant {tenant_id}")
        return 0, 0, 0
    
    # Get tenant info for personalization
    tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
    tenant_name = tenant.get("salon_name", "our salon") if tenant else "our salon"
    
    # Get channels and message template
    channels = birthday_config.get("channels", ["sms"])
    message_template = birthday_config.get("message_template", 
        "Happy Birthday {{client_name}}! 🎉 Celebrate with us! Get {{discount_percentage}}% off your next visit at {{salon_name}}. Book now!")
    discount_percentage = birthday_config.get("discount_percentage", 10)
    send_time = birthday_config.get("send_time", "09:00")
    
    # Check if we should send now based on configured send time
    hour, minute = map(int, send_time.split(":"))
    now = datetime.utcnow()
    
    # Allow 1-hour window for sending
    if not (hour <= now.hour < hour + 1):
        logger.debug(f"Not in send window for tenant {tenant_id}. Configured: {send_time}, Current: {now.hour}:{now.minute}")
        return 0, 0, recipient_count
    
    # Process each client
    for client in clients:
        try:
            client_id = str(client["_id"])
            client_name = client.get("name", "Valued Client")
            
            # Check if birthday campaign already sent today
            existing_send = db.campaign_sends.find_one({
                "tenant_id": tenant_id,
                "client_id": client_id,
                "campaign_type": "birthday",
                "sent_at": {
                    "$gte": datetime(today.year, today.month, today.day),
                    "$lte": datetime(today.year, today.month, today.day, 23, 59, 59)
                }
            })
            
            if existing_send:
                logger.debug(f"Birthday campaign already sent to client {client_id} today")
                continue
            
            # Render message template with client data
            message_content = message_template.replace("{{client_name}}", client_name)
            message_content = message_content.replace("{{discount_percentage}}", str(discount_percentage))
            message_content = message_content.replace("{{salon_name}}", tenant_name)
            
            # Send via each configured channel
            for channel in channels:
                try:
                    send_birthday_message(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client=client,
                        channel=channel,
                        message_content=message_content,
                        discount_percentage=discount_percentage
                    )
                    sent_count += 1
                    logger.info(f"Birthday campaign sent to {client_name} via {channel}")
                
                except Exception as channel_error:
                    failed_count += 1
                    logger.error(
                        f"Failed to send birthday campaign to {client_name} via {channel}: {channel_error}",
                        exc_info=True
                    )
                    
                    # Record failed send
                    record_failed_send(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        channel=channel,
                        message_content=message_content,
                        error_message=str(channel_error)
                    )
        
        except Exception as e:
            failed_count += 1
            logger.error(f"Error processing birthday campaign for client {client.get('_id')}: {e}", exc_info=True)
    
    return sent_count, failed_count, recipient_count


def send_birthday_message(
    db,
    tenant_id: str,
    client_id: str,
    client: Dict,
    channel: str,
    message_content: str,
    discount_percentage: int
) -> None:
    """
    Send birthday message to a client via specified channel
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        client_id: Client ID
        client: Client document
        channel: Channel (sms, whatsapp, email)
        message_content: Message content
        discount_percentage: Discount percentage for tracking
    
    Raises:
        Exception: If message sending fails
    """
    # Validate message for channel
    validation = ChannelService.validate_message(channel, message_content)
    if not validation.get("valid"):
        raise ValueError(f"Message validation failed: {validation.get('error')}")
    
    # Get contact info based on channel
    if channel == "sms":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "whatsapp":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "email":
        contact = client.get("email")
        if not contact:
            raise ValueError("Client has no email address")
        if not ChannelService.validate_email(contact):
            raise ValueError(f"Invalid email address: {contact}")
    
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # TODO: Integrate with actual messaging providers (Termii, WhatsApp API, SendGrid)
    # For now, we'll record the send in the database
    
    # Calculate cost
    cost = ChannelService.calculate_cost(channel, 1)
    
    # Record campaign send
    campaign_send = {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "campaign_id": "auto_birthday",
        "campaign_type": "birthday",
        "channel": channel,
        "message_content": message_content,
        "contact": contact,
        "status": "sent",
        "sent_at": datetime.utcnow(),
        "delivered_at": None,
        "error_code": None,
        "error_message": None,
        "retry_count": 0,
        "cost": cost,
        "discount_percentage": discount_percentage
    }
    
    result = db.campaign_sends.insert_one(campaign_send)
    campaign_send["_id"] = str(result.inserted_id)
    
    logger.debug(f"Birthday campaign send recorded: {campaign_send['_id']}")


def record_failed_send(
    db,
    tenant_id: str,
    client_id: str,
    channel: str,
    message_content: str,
    error_message: str,
    campaign_type: str = "birthday"
) -> None:
    """
    Record a failed campaign send
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        client_id: Client ID
        channel: Channel
        message_content: Message content
        error_message: Error message
        campaign_type: Campaign type (birthday, winback, etc.)
    """
    campaign_id = f"auto_{campaign_type}"
    
    campaign_send = {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "campaign_id": campaign_id,
        "campaign_type": campaign_type,
        "channel": channel,
        "message_content": message_content,
        "status": "failed",
        "sent_at": datetime.utcnow(),
        "error_message": error_message,
        "retry_count": 0,
        "cost": 0.0
    }
    
    result = db.campaign_sends.insert_one(campaign_send)
    logger.debug(f"Failed {campaign_type} campaign send recorded: {result.inserted_id}")


@shared_task(
    name="check_winback_campaigns",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # Retry after 5 minutes
)
def check_winback_campaigns_task(self):
    """
    Daily task to check for inactive clients and send win-back campaigns
    
    This task:
    - Checks for clients inactive for configured period
    - Retrieves automation settings for each tenant
    - Respects frequency limits to avoid sending too often
    - Sends win-back campaigns via configured channels
    - Records execution in automation history
    - Implements retry logic for failed sends
    
    This task should be scheduled to run daily (e.g., at 10 AM)
    
    Requirements: 3.4, 3.5
    """
    logger.info("Starting win-back campaigns check...")
    
    try:
        db = Database.get_db()
        automation_service = AutomationService(db)
        
        # Get all active tenants
        tenants = list(db.tenants.find({"status": "active"}))
        
        total_sent = 0
        total_failed = 0
        total_recipients = 0
        
        for tenant in tenants:
            try:
                tenant_id = str(tenant["_id"])
                
                # Get automation settings for this tenant
                settings = automation_service.get_settings(tenant_id)
                if not settings or not settings.get("enabled"):
                    logger.debug(f"Automation disabled for tenant: {tenant_id}")
                    continue
                
                winback_config = settings.get("winback_campaigns", {})
                if not winback_config.get("enabled"):
                    logger.debug(f"Win-back campaigns disabled for tenant: {tenant_id}")
                    continue
                
                # Send win-back campaigns for this tenant
                sent_count, failed_count, recipient_count = send_winback_campaigns_for_tenant(
                    db=db,
                    tenant_id=tenant_id,
                    winback_config=winback_config,
                    automation_service=automation_service
                )
                
                total_sent += sent_count
                total_failed += failed_count
                total_recipients += recipient_count
                
                if sent_count > 0 or failed_count > 0:
                    logger.info(
                        f"Win-back campaigns for tenant {tenant_id}: "
                        f"sent={sent_count}, failed={failed_count}, recipients={recipient_count}"
                    )
                    
                    # Record execution in automation history
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="winback",
                        campaign_id="auto_winback",
                        recipients_count=recipient_count,
                        sent_count=sent_count,
                        failed_count=failed_count,
                        status="success" if failed_count == 0 else "partial"
                    )
            
            except Exception as e:
                logger.error(f"Error processing win-back campaigns for tenant {tenant.get('_id')}: {e}", exc_info=True)
                
                # Record failed execution
                try:
                    tenant_id = str(tenant["_id"])
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="winback",
                        campaign_id="auto_winback",
                        recipients_count=0,
                        sent_count=0,
                        failed_count=0,
                        status="failed",
                        error_message=str(e)
                    )
                except Exception as record_error:
                    logger.error(f"Failed to record execution error: {record_error}")
        
        logger.info(
            f"Win-back campaigns check completed. "
            f"Total sent: {total_sent}, failed: {total_failed}, recipients: {total_recipients}"
        )
        
        return {
            "status": "completed",
            "total_sent": total_sent,
            "total_failed": total_failed,
            "total_recipients": total_recipients,
            "tenants_processed": len(tenants)
        }
    
    except Exception as e:
        logger.error(f"Fatal error in win-back campaigns task: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


def send_winback_campaigns_for_tenant(
    db,
    tenant_id: str,
    winback_config: Dict,
    automation_service: AutomationService
) -> tuple:
    """
    Send win-back campaigns to inactive clients
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        winback_config: Win-back automation configuration
        automation_service: AutomationService instance
    
    Returns:
        Tuple of (sent_count, failed_count, recipient_count)
    """
    sent_count = 0
    failed_count = 0
    
    # Get configuration
    inactive_days = winback_config.get("inactive_days", 90)
    frequency_limit_days = winback_config.get("frequency_limit_days", 30)
    channels = winback_config.get("channels", ["sms"])
    message_template = winback_config.get("message_template",
        "We miss you {{client_name}}! 💇 It's been a while since your last visit. Come back and enjoy {{discount_percentage}}% off at {{salon_name}}!")
    discount_percentage = winback_config.get("discount_percentage", 15)
    send_time = winback_config.get("send_time", "10:00")
    
    # Calculate cutoff date for inactive clients
    cutoff_date = datetime.utcnow() - timedelta(days=inactive_days)
    
    # Get clients who haven't visited in X days
    clients = list(db.clients.find({
        "tenant_id": tenant_id,
        "last_visit_date": {"$lt": cutoff_date}
    }))
    
    recipient_count = len(clients)
    
    if recipient_count == 0:
        logger.debug(f"No inactive clients found for tenant {tenant_id} (inactive for {inactive_days} days)")
        return 0, 0, 0
    
    # Get tenant info for personalization
    tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
    tenant_name = tenant.get("salon_name", "our salon") if tenant else "our salon"
    
    # Check if we should send now based on configured send time
    hour, minute = map(int, send_time.split(":"))
    now = datetime.utcnow()
    
    # Allow 1-hour window for sending
    if not (hour <= now.hour < hour + 1):
        logger.debug(f"Not in send window for tenant {tenant_id}. Configured: {send_time}, Current: {now.hour}:{now.minute}")
        return 0, 0, recipient_count
    
    # Process each client
    for client in clients:
        try:
            client_id = str(client["_id"])
            client_name = client.get("name", "Valued Client")
            
            # Check frequency limit - don't send if already sent within frequency_limit_days
            recent_send = db.campaign_sends.find_one({
                "tenant_id": tenant_id,
                "client_id": client_id,
                "campaign_type": "winback",
                "sent_at": {
                    "$gte": datetime.utcnow() - timedelta(days=frequency_limit_days)
                }
            })
            
            if recent_send:
                logger.debug(
                    f"Win-back campaign frequency limit reached for client {client_id}. "
                    f"Last sent: {recent_send.get('sent_at')}"
                )
                continue
            
            # Render message template with client data
            message_content = message_template.replace("{{client_name}}", client_name)
            message_content = message_content.replace("{{discount_percentage}}", str(discount_percentage))
            message_content = message_content.replace("{{salon_name}}", tenant_name)
            
            # Send via each configured channel
            for channel in channels:
                try:
                    send_winback_message(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client=client,
                        channel=channel,
                        message_content=message_content,
                        discount_percentage=discount_percentage,
                        inactive_days=inactive_days
                    )
                    sent_count += 1
                    logger.info(f"Win-back campaign sent to {client_name} via {channel}")
                
                except Exception as channel_error:
                    failed_count += 1
                    logger.error(
                        f"Failed to send win-back campaign to {client_name} via {channel}: {channel_error}",
                        exc_info=True
                    )
                    
                    # Record failed send
                    record_failed_send(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        channel=channel,
                        message_content=message_content,
                        error_message=str(channel_error),
                        campaign_type="winback"
                    )
        
        except Exception as e:
            failed_count += 1
            logger.error(f"Error processing win-back campaign for client {client.get('_id')}: {e}", exc_info=True)
    
    return sent_count, failed_count, recipient_count


def send_winback_message(
    db,
    tenant_id: str,
    client_id: str,
    client: Dict,
    channel: str,
    message_content: str,
    discount_percentage: int,
    inactive_days: int
) -> None:
    """
    Send win-back message to a client via specified channel
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        client_id: Client ID
        client: Client document
        channel: Channel (sms, whatsapp, email)
        message_content: Message content
        discount_percentage: Discount percentage for tracking
        inactive_days: Number of days inactive
    
    Raises:
        Exception: If message sending fails
    """
    # Validate message for channel
    validation = ChannelService.validate_message(channel, message_content)
    if not validation.get("valid"):
        raise ValueError(f"Message validation failed: {validation.get('error')}")
    
    # Get contact info based on channel
    if channel == "sms":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "whatsapp":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "email":
        contact = client.get("email")
        if not contact:
            raise ValueError("Client has no email address")
        if not ChannelService.validate_email(contact):
            raise ValueError(f"Invalid email address: {contact}")
    
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # TODO: Integrate with actual messaging providers (Termii, WhatsApp API, SendGrid)
    # For now, we'll record the send in the database
    
    # Calculate cost
    cost = ChannelService.calculate_cost(channel, 1)
    
    # Record campaign send
    campaign_send = {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "campaign_id": "auto_winback",
        "campaign_type": "winback",
        "channel": channel,
        "message_content": message_content,
        "contact": contact,
        "status": "sent",
        "sent_at": datetime.utcnow(),
        "delivered_at": None,
        "error_code": None,
        "error_message": None,
        "retry_count": 0,
        "cost": cost,
        "discount_percentage": discount_percentage,
        "inactive_days": inactive_days
    }
    
    result = db.campaign_sends.insert_one(campaign_send)
    campaign_send["_id"] = str(result.inserted_id)
    
    logger.debug(f"Win-back campaign send recorded: {campaign_send['_id']}")


@shared_task(
    name="check_post_visit_campaigns",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # Retry after 5 minutes
)
def check_post_visit_campaigns_task(self):
    """
    Periodic task to check for completed visits and send post-visit campaigns
    
    This task:
    - Checks for visits completed within the configured delay window
    - Retrieves automation settings for each tenant
    - Sends post-visit campaigns via configured channels
    - Records execution in automation history
    - Implements retry logic for failed sends
    
    This task should be scheduled to run periodically (e.g., every hour)
    
    Requirements: 6.2
    """
    logger.info("Starting post-visit campaigns check...")
    
    try:
        db = Database.get_db()
        automation_service = AutomationService(db)
        
        # Get all active tenants
        tenants = list(db.tenants.find({"status": "active"}))
        
        total_sent = 0
        total_failed = 0
        total_recipients = 0
        
        for tenant in tenants:
            try:
                tenant_id = str(tenant["_id"])
                
                # Get automation settings for this tenant
                settings = automation_service.get_settings(tenant_id)
                if not settings or not settings.get("enabled"):
                    logger.debug(f"Automation disabled for tenant: {tenant_id}")
                    continue
                
                post_visit_config = settings.get("post_visit_campaigns", {})
                if not post_visit_config.get("enabled"):
                    logger.debug(f"Post-visit campaigns disabled for tenant: {tenant_id}")
                    continue
                
                # Send post-visit campaigns for this tenant
                sent_count, failed_count, recipient_count = send_post_visit_campaigns_for_tenant(
                    db=db,
                    tenant_id=tenant_id,
                    post_visit_config=post_visit_config,
                    automation_service=automation_service
                )
                
                total_sent += sent_count
                total_failed += failed_count
                total_recipients += recipient_count
                
                if sent_count > 0 or failed_count > 0:
                    logger.info(
                        f"Post-visit campaigns for tenant {tenant_id}: "
                        f"sent={sent_count}, failed={failed_count}, recipients={recipient_count}"
                    )
                    
                    # Record execution in automation history
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="post_visit",
                        campaign_id="auto_post_visit",
                        recipients_count=recipient_count,
                        sent_count=sent_count,
                        failed_count=failed_count,
                        status="success" if failed_count == 0 else "partial"
                    )
            
            except Exception as e:
                logger.error(f"Error processing post-visit campaigns for tenant {tenant.get('_id')}: {e}", exc_info=True)
                
                # Record failed execution
                try:
                    tenant_id = str(tenant["_id"])
                    automation_service.record_execution(
                        tenant_id=tenant_id,
                        automation_type="post_visit",
                        campaign_id="auto_post_visit",
                        recipients_count=0,
                        sent_count=0,
                        failed_count=0,
                        status="failed",
                        error_message=str(e)
                    )
                except Exception as record_error:
                    logger.error(f"Failed to record execution error: {record_error}")
        
        logger.info(
            f"Post-visit campaigns check completed. "
            f"Total sent: {total_sent}, failed: {total_failed}, recipients: {total_recipients}"
        )
        
        return {
            "status": "completed",
            "total_sent": total_sent,
            "total_failed": total_failed,
            "total_recipients": total_recipients,
            "tenants_processed": len(tenants)
        }
    
    except Exception as e:
        logger.error(f"Fatal error in post-visit campaigns task: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


def send_post_visit_campaigns_for_tenant(
    db,
    tenant_id: str,
    post_visit_config: Dict,
    automation_service: AutomationService
) -> tuple:
    """
    Send post-visit campaigns to clients who completed visits
    
    This function:
    - Finds visits completed within the delay window
    - Checks if post-visit campaign already sent for each visit
    - Sends campaign via configured channels
    - Records sends in database
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        post_visit_config: Post-visit automation configuration
        automation_service: AutomationService instance
    
    Returns:
        Tuple of (sent_count, failed_count, recipient_count)
    
    Requirements: 6.2
    """
    sent_count = 0
    failed_count = 0
    
    # Get configuration
    delay_days = post_visit_config.get("delay_days", 1)
    channels = post_visit_config.get("channels", ["sms"])
    message_template = post_visit_config.get("message_template",
        "Thank you for visiting {{salon_name}}, {{client_name}}! We hope you enjoyed your experience. Share your feedback or book your next appointment!")
    
    # Calculate the time window for visits to trigger
    # We want visits that completed delay_days ago (allowing 1-hour window for processing)
    now = datetime.utcnow()
    window_start = now - timedelta(days=delay_days, hours=1)
    window_end = now - timedelta(days=delay_days)
    
    # Find bookings/visits completed in the window
    # Assuming bookings collection has completed_at or end_time field
    completed_bookings = list(db.bookings.find({
        "tenant_id": tenant_id,
        "status": "completed",
        "completed_at": {
            "$gte": window_start,
            "$lte": window_end
        }
    }))
    
    recipient_count = len(completed_bookings)
    
    if recipient_count == 0:
        logger.debug(
            f"No completed visits found for tenant {tenant_id} "
            f"in window {window_start} to {window_end}"
        )
        return 0, 0, 0
    
    # Get tenant info for personalization
    tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
    tenant_name = tenant.get("salon_name", "our salon") if tenant else "our salon"
    
    # Process each booking/visit
    for booking in completed_bookings:
        try:
            booking_id = str(booking["_id"])
            client_id_raw = booking.get("client_id")
            
            # Convert client_id to ObjectId if it's not already
            if isinstance(client_id_raw, ObjectId):
                client_id_obj = client_id_raw
                client_id = str(client_id_raw)
            else:
                client_id = str(client_id_raw)
                try:
                    client_id_obj = ObjectId(client_id)
                except Exception:
                    logger.warning(f"Invalid client_id format for booking {booking_id}: {client_id}")
                    failed_count += 1
                    continue
            
            # Check if post-visit campaign already sent for this booking
            existing_send = db.campaign_sends.find_one({
                "tenant_id": tenant_id,
                "booking_id": booking_id,
                "campaign_type": "post_visit"
            })
            
            if existing_send:
                logger.debug(f"Post-visit campaign already sent for booking {booking_id}")
                continue
            
            # Get client details
            client = db.clients.find_one({"_id": client_id_obj})
            if not client:
                logger.warning(f"Client not found for booking {booking_id}")
                failed_count += 1
                continue
            
            client_name = client.get("name", "Valued Client")
            
            # Render message template with client data
            message_content = message_template.replace("{{client_name}}", client_name)
            message_content = message_content.replace("{{salon_name}}", tenant_name)
            
            # Send via each configured channel
            for channel in channels:
                try:
                    send_post_visit_message(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        booking_id=booking_id,
                        client=client,
                        channel=channel,
                        message_content=message_content,
                        delay_days=delay_days
                    )
                    sent_count += 1
                    logger.info(f"Post-visit campaign sent to {client_name} via {channel} for booking {booking_id}")
                
                except Exception as channel_error:
                    failed_count += 1
                    logger.error(
                        f"Failed to send post-visit campaign to {client_name} via {channel}: {channel_error}",
                        exc_info=True
                    )
                    
                    # Record failed send
                    record_failed_send(
                        db=db,
                        tenant_id=tenant_id,
                        client_id=client_id,
                        channel=channel,
                        message_content=message_content,
                        error_message=str(channel_error),
                        campaign_type="post_visit"
                    )
        
        except Exception as e:
            failed_count += 1
            logger.error(f"Error processing post-visit campaign for booking {booking.get('_id')}: {e}", exc_info=True)
    
    return sent_count, failed_count, recipient_count


def send_post_visit_message(
    db,
    tenant_id: str,
    client_id: str,
    booking_id: str,
    client: Dict,
    channel: str,
    message_content: str,
    delay_days: int
) -> None:
    """
    Send post-visit message to a client via specified channel
    
    Args:
        db: Database connection
        tenant_id: Tenant ID
        client_id: Client ID
        booking_id: Booking ID that triggered the campaign
        client: Client document
        channel: Channel (sms, whatsapp, email)
        message_content: Message content
        delay_days: Number of days after visit when message was sent
    
    Raises:
        Exception: If message sending fails
    
    Requirements: 6.2
    """
    # Validate message for channel
    validation = ChannelService.validate_message(channel, message_content)
    if not validation.get("valid"):
        raise ValueError(f"Message validation failed: {validation.get('error')}")
    
    # Get contact info based on channel
    if channel == "sms":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "whatsapp":
        contact = client.get("phone")
        if not contact:
            raise ValueError("Client has no phone number")
        if not ChannelService.validate_phone(contact):
            raise ValueError(f"Invalid phone number: {contact}")
    
    elif channel == "email":
        contact = client.get("email")
        if not contact:
            raise ValueError("Client has no email address")
        if not ChannelService.validate_email(contact):
            raise ValueError(f"Invalid email address: {contact}")
    
    else:
        raise ValueError(f"Unsupported channel: {channel}")
    
    # TODO: Integrate with actual messaging providers (Termii, WhatsApp API, SendGrid)
    # For now, we'll record the send in the database
    
    # Calculate cost
    cost = ChannelService.calculate_cost(channel, 1)
    
    # Record campaign send
    campaign_send = {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "booking_id": booking_id,
        "campaign_id": "auto_post_visit",
        "campaign_type": "post_visit",
        "channel": channel,
        "message_content": message_content,
        "contact": contact,
        "status": "sent",
        "sent_at": datetime.utcnow(),
        "delivered_at": None,
        "error_code": None,
        "error_message": None,
        "retry_count": 0,
        "cost": cost,
        "delay_days": delay_days
    }
    
    result = db.campaign_sends.insert_one(campaign_send)
    campaign_send["_id"] = str(result.inserted_id)
    
    logger.debug(f"Post-visit campaign send recorded: {campaign_send['_id']}")


@shared_task(name="send_custom_campaign")
def send_custom_campaign_task(tenant_id: str, campaign_id: str):
    """
    Send a custom campaign to targeted clients
    
    Args:
        tenant_id: Tenant ID
        campaign_id: Campaign ID
    """
    logger.info(f"Starting custom campaign send: {campaign_id}")
    
    db = Database.get_db()
    
    # Get campaign details
    campaign = db.campaigns.find_one({"_id": campaign_id, "tenant_id": tenant_id})
    
    if not campaign:
        logger.error(f"Campaign not found: {campaign_id}")
        return {"status": "error", "message": "Campaign not found"}
    
    # TODO: Implement custom campaign sending logic based on campaign configuration
    # This would include:
    # - Getting target audience based on campaign filters
    # - Sending messages via configured channels (SMS, Email, WhatsApp)
    # - Recording campaign sends
    # - Tracking campaign performance
    
    logger.info(f"Custom campaign send completed: {campaign_id}")
    
    return {
        "status": "completed",
        "campaign_id": campaign_id
    }
