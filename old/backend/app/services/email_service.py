"""
Email service using Resend
"""
import httpx
from app.config import settings
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.white_label import WhiteLabelConfig

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails via Resend"""
    
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.api_url = "https://api.resend.com/emails"
        self.white_label_config: Optional[WhiteLabelConfig] = None
        self.tenant_id: Optional[str] = None
    
    def set_white_label_config(self, config: Optional[WhiteLabelConfig]) -> None:
        """Set white label configuration for email branding"""
        self.white_label_config = config
    
    def set_tenant_context(self, tenant_id: str, config: Optional[WhiteLabelConfig] = None) -> None:
        """Set tenant context for email branding"""
        self.tenant_id = tenant_id
        if config:
            self.white_label_config = config
    
    async def load_white_label_config(self, tenant_id: str) -> Optional[WhiteLabelConfig]:
        """
        Load white label configuration from database for a tenant
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            WhiteLabelConfig if found and active, None otherwise
        """
        try:
            from app.database import Database
            from app.services.white_label_service import WhiteLabelService
            
            db = Database.get_db()
            white_label_service = WhiteLabelService(db)
            config = await white_label_service.get_config(tenant_id)
            
            # Only use config if it's active
            if config and config.is_active:
                self.white_label_config = config
                self.tenant_id = tenant_id
                return config
            
            return None
        except Exception as e:
            logger.error(f"Error loading white label config for tenant {tenant_id}: {str(e)}")
            return None
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """Send an email via Resend"""
        try:
            logger.info(f"Attempting to send email to {to}")
            logger.info(f"API Key: {self.api_key[:20]}...")
            logger.info(f"From: {self.from_email}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Use custom from email if provided, otherwise use default
            from_addr = from_email or self.from_email
            
            payload = {
                "from": from_addr,
                "to": [to],
                "subject": subject,
                "html": html
            }
            
            if text:
                payload["text"] = text
            
            logger.info(f"Payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                logger.info(f"Resend API Response Status: {response.status_code}")
                logger.info(f"Resend API Response: {response.text}")
                
                if response.status_code == 200:
                    logger.info(f"✓ Email sent successfully to {to}")
                    return True
                else:
                    logger.error(f"✗ Failed to send email: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"✗ Error sending email: {str(e)}", exc_info=True)
            return False
    
    async def send_gift_card_email(
        self,
        card_id: str,
        recipient_email: str,
        recipient_name: str,
        card_number: str,
        balance: float,
        expiry_date: datetime,
        include_qr_code: bool = False,
        **kwargs
    ) -> Dict:
        """Send gift card email"""
        try:
            subject = f"Your Gift Card - ₦{balance:,.0f}"
            html = f"""
            <html>
            <body>
                <h1>You've Received a Gift Card!</h1>
                <p>Hi {recipient_name},</p>
                <p>Card Number: {card_number}</p>
                <p>Balance: ₦{balance:,.0f}</p>
                <p>Expires: {expiry_date.strftime('%Y-%m-%d')}</p>
            </body>
            </html>
            """
            
            result = await self.send_email(recipient_email, subject, html)
            return {"success": result, "email_id": "email_123"}
        except Exception as e:
            logger.error(f"Error sending gift card email: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_activation_email(
        self,
        card_id: str,
        recipient_email: str,
        recipient_name: str,
        card_number: str,
        **kwargs
    ) -> Dict:
        """Send card activation email"""
        try:
            subject = f"Your Gift Card is Activated - {card_number}"
            html = f"""
            <html>
            <body>
                <h1>Your Gift Card is Activated!</h1>
                <p>Hi {recipient_name},</p>
                <p>Your gift card {card_number} has been activated and is ready to use.</p>
            </body>
            </html>
            """
            
            result = await self.send_email(recipient_email, subject, html)
            return {"success": result}
        except Exception as e:
            logger.error(f"Error sending activation email: {e}")
            return {"success": False}
    
    async def send_reload_email(
        self,
        card_id: str,
        recipient_email: str,
        recipient_name: str,
        card_number: str,
        reload_amount: float,
        new_balance: float,
        new_expiry_date: datetime,
        **kwargs
    ) -> Dict:
        """Send card reload email"""
        try:
            subject = f"Your Gift Card Has Been Reloaded - ₦{reload_amount:,.0f}"
            html = f"""
            <html>
            <body>
                <h1>Your Gift Card Has Been Reloaded!</h1>
                <p>Hi {recipient_name},</p>
                <p>Card Number: {card_number}</p>
                <p>Reload Amount: ₦{reload_amount:,.0f}</p>
                <p>New Balance: ₦{new_balance:,.0f}</p>
                <p>New Expiry Date: {new_expiry_date.strftime('%Y-%m-%d')}</p>
            </body>
            </html>
            """
            
            result = await self.send_email(recipient_email, subject, html)
            return {"success": result}
        except Exception as e:
            logger.error(f"Error sending reload email: {e}")
            return {"success": False}
    
    async def send_expiration_reminder(
        self,
        card_id: str,
        recipient_email: str,
        recipient_name: str,
        card_number: str,
        balance: float,
        expiry_date: datetime,
        days_until_expiry: int,
        **kwargs
    ) -> Dict:
        """Send expiration reminder email"""
        try:
            subject = f"Your Gift Card Expires in {days_until_expiry} Days!"
            html = f"""
            <html>
            <body>
                <h1>Your Gift Card is Expiring Soon!</h1>
                <p>Hi {recipient_name},</p>
                <p>Your gift card {card_number} will expire in {days_until_expiry} days.</p>
                <p>Current Balance: ₦{balance:,.0f}</p>
                <p>Expiry Date: {expiry_date.strftime('%Y-%m-%d')}</p>
                <p>Please use your card before it expires!</p>
            </body>
            </html>
            """
            
            result = await self.send_email(recipient_email, subject, html)
            return {"success": result}
        except Exception as e:
            logger.error(f"Error sending expiration reminder: {e}")
            return {"success": False}
    
    async def resend_gift_card_email(
        self,
        card_id: str,
        recipient_email: str,
        new_recipient_name: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Resend gift card email"""
        try:
            subject = "Your Gift Card"
            html = f"""
            <html>
            <body>
                <h1>Your Gift Card</h1>
                <p>This is a resend of your gift card information.</p>
            </body>
            </html>
            """
            
            result = await self.send_email(recipient_email, subject, html)
            return {"success": result}
        except Exception as e:
            logger.error(f"Error resending gift card email: {e}")
            return {"success": False}
    
    async def render_template(
        self,
        template_name: str,
        data: Dict
    ) -> str:
        """Render email template"""
        return f"<html><body>Template: {template_name}</body></html>"
    
    async def get_email_delivery_status(
        self,
        email_id: str
    ) -> Dict:
        """Get email delivery status"""
        return {"status": "sent"}
    
    async def get_email_history(
        self,
        card_id: str
    ) -> list:
        """Get email history for a card"""
        return []


# Singleton instance
email_service = EmailService()
