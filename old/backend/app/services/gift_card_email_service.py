"""
Gift Card Email Service
Handles all email communications for gift cards with HTML templates and delivery tracking
"""

from datetime import datetime, timezone
from typing import Dict, Optional
import logging
from app.database import Database
from app.services.email_service import email_service
from app.services.qr_service import QRCodeService
from bson import ObjectId

logger = logging.getLogger(__name__)


class GiftCardEmailService:
    """Service for sending gift card emails with templates"""
    
    @staticmethod
    async def send_gift_card_delivery_email(
        card_id: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        message: Optional[str] = None,
        salon_name: str = "Kenikool Salon"
    ) -> Dict:
        """
        Send gift card delivery email with QR code
        
        Args:
            card_id: Gift card ID
            recipient_email: Recipient email address
            recipient_name: Recipient name
            message: Personal message from sender
            salon_name: Salon name for branding
            
        Returns:
            Dict with delivery status
        """
        try:
            db = Database.get_db()
            
            # Get gift card
            gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
            
            if not gift_card:
                logger.error(f"Gift card not found: {card_id}")
                return {"success": False, "error": "Card not found"}
            
            # Generate QR code
            qr_code_data = QRCodeService.generate_qr_code_base64(gift_card["card_number"])
            
            # Format expiration date
            expires_at = gift_card.get("expires_at", datetime.now(timezone.utc))
            expiration_date = expires_at.strftime("%B %d, %Y")
            
            # Build email HTML
            email_html = GiftCardEmailService._build_delivery_email(
                card_number=gift_card["card_number"],
                amount=gift_card.get("amount", 0),
                recipient_name=recipient_name or gift_card.get("recipient_name", "Valued Customer"),
                message=message or gift_card.get("message"),
                expiration_date=expiration_date,
                qr_code_data=qr_code_data,
                salon_name=salon_name,
                design_theme=gift_card.get("design_theme", "default")
            )
            
            # Send email
            success = await email_service.send_email(
                to=recipient_email,
                subject=f"Your {salon_name} Gift Card - ₦{gift_card.get('amount', 0):,.0f}",
                html=email_html
            )
            
            if success:
                # Update delivery status
                db.gift_cards.update_one(
                    {"_id": ObjectId(card_id)},
                    {
                        "$set": {
                            "delivery_status": "delivered",
                            "last_delivery_attempt": datetime.now(timezone.utc)
                        },
                        "$inc": {"delivery_attempts": 1},
                        "$push": {
                            "audit_log": {
                                "action": "email_delivered",
                                "timestamp": datetime.now(timezone.utc),
                                "details": {"recipient_email": recipient_email}
                            }
                        }
                    }
                )
                
                logger.info(f"Gift card email sent: {gift_card['card_number']} to {recipient_email}")
                return {
                    "success": True,
                    "card_number": gift_card["card_number"],
                    "recipient_email": recipient_email
                }
            else:
                # Update failed delivery attempt
                db.gift_cards.update_one(
                    {"_id": ObjectId(card_id)},
                    {
                        "$set": {"last_delivery_attempt": datetime.now(timezone.utc)},
                        "$inc": {"delivery_attempts": 1}
                    }
                )
                
                logger.error(f"Failed to send gift card email: {gift_card['card_number']}")
                return {"success": False, "error": "Email delivery failed"}
                
        except Exception as e:
            logger.error(f"Error sending gift card email: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def send_expiration_reminder(
        card_id: str,
        days_until_expiration: int,
        salon_name: str = "Kenikool Salon"
    ) -> Dict:
        """
        Send expiration reminder email
        
        Args:
            card_id: Gift card ID
            days_until_expiration: Days until card expires
            salon_name: Salon name for branding
            
        Returns:
            Dict with delivery status
        """
        try:
            db = Database.get_db()
            
            # Get gift card
            gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
            
            if not gift_card:
                logger.error(f"Gift card not found: {card_id}")
                return {"success": False, "error": "Card not found"}
            
            recipient_email = gift_card.get("recipient_email")
            if not recipient_email:
                logger.warning(f"No recipient email for card: {card_id}")
                return {"success": False, "error": "No recipient email"}
            
            # Build email HTML
            email_html = GiftCardEmailService._build_expiration_reminder_email(
                card_number=gift_card["card_number"],
                balance=gift_card.get("balance", 0),
                days_until_expiration=days_until_expiration,
                expiration_date=gift_card.get("expires_at", datetime.now(timezone.utc)).strftime("%B %d, %Y"),
                salon_name=salon_name
            )
            
            # Send email
            success = await email_service.send_email(
                to=recipient_email,
                subject=f"Your {salon_name} Gift Card Expires in {days_until_expiration} Day{'s' if days_until_expiration > 1 else ''}!",
                html=email_html
            )
            
            if success:
                # Mark reminder as sent
                reminder_key = f"reminder_{days_until_expiration}d"
                db.gift_cards.update_one(
                    {"_id": ObjectId(card_id)},
                    {
                        "$set": {reminder_key: True},
                        "$push": {
                            "audit_log": {
                                "action": f"reminder_sent_{days_until_expiration}d",
                                "timestamp": datetime.now(timezone.utc),
                                "details": {}
                            }
                        }
                    }
                )
                
                logger.info(f"Expiration reminder sent for card {gift_card['card_number']}")
                return {"success": True, "card_number": gift_card["card_number"]}
            else:
                logger.error(f"Failed to send expiration reminder: {gift_card['card_number']}")
                return {"success": False, "error": "Email delivery failed"}
                
        except Exception as e:
            logger.error(f"Error sending expiration reminder: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_redemption_confirmation(
        card_id: str,
        amount_redeemed: float,
        remaining_balance: float,
        transaction_id: str,
        salon_name: str = "Kenikool Salon"
    ) -> Dict:
        """
        Send redemption confirmation email
        
        Args:
            card_id: Gift card ID
            amount_redeemed: Amount redeemed
            remaining_balance: Remaining balance
            transaction_id: Transaction ID
            salon_name: Salon name for branding
            
        Returns:
            Dict with delivery status
        """
        try:
            db = Database.get_db()
            
            # Get gift card
            gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
            
            if not gift_card:
                logger.error(f"Gift card not found: {card_id}")
                return {"success": False, "error": "Card not found"}
            
            recipient_email = gift_card.get("recipient_email")
            if not recipient_email:
                logger.warning(f"No recipient email for card: {card_id}")
                return {"success": False, "error": "No recipient email"}
            
            # Build email HTML
            email_html = GiftCardEmailService._build_redemption_confirmation_email(
                card_number=gift_card["card_number"],
                amount_redeemed=amount_redeemed,
                remaining_balance=remaining_balance,
                transaction_id=transaction_id,
                salon_name=salon_name
            )
            
            # Send email
            success = await email_service.send_email(
                to=recipient_email,
                subject=f"Redemption Confirmation - {salon_name}",
                html=email_html
            )
            
            if success:
                logger.info(f"Redemption confirmation sent for card {gift_card['card_number']}")
                return {"success": True, "card_number": gift_card["card_number"]}
            else:
                logger.error(f"Failed to send redemption confirmation: {gift_card['card_number']}")
                return {"success": False, "error": "Email delivery failed"}
                
        except Exception as e:
            logger.error(f"Error sending redemption confirmation: {str(e)}")
            return {"success": False, "error": str(e)}

    # HTML Template Builders
    
    @staticmethod
    def _build_delivery_email(
        card_number: str,
        amount: float,
        recipient_name: str,
        message: Optional[str],
        expiration_date: str,
        qr_code_data: str,
        salon_name: str,
        design_theme: str
    ) -> str:
        """Build gift card delivery email HTML"""
        theme_colors = {
            "default": {"primary": "#667eea", "secondary": "#764ba2"},
            "christmas": {"primary": "#c41e3a", "secondary": "#165b33"},
            "birthday": {"primary": "#ff69b4", "secondary": "#ff1493"},
            "valentine": {"primary": "#ff1493", "secondary": "#ff69b4"},
            "elegant": {"primary": "#1a1a1a", "secondary": "#d4af37"},
        }
        
        colors = theme_colors.get(design_theme, theme_colors["default"])
        
        message_section = ""
        if message:
            message_section = f"""
            <div class="message-box">
                <p><strong>Message from sender:</strong></p>
                <p>{message}</p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; }}
                .logo {{ font-size: 24px; font-weight: bold; color: {colors['primary']}; }}
                .card-container {{
                    background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 30px 0;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .card-title {{ font-size: 28px; font-weight: bold; margin-bottom: 20px; }}
                .card-amount {{ font-size: 48px; font-weight: bold; margin: 20px 0; }}
                .card-number {{ font-family: 'Courier New', monospace; font-size: 14px; letter-spacing: 2px; margin: 20px 0; }}
                .expiration {{ font-size: 14px; margin-top: 15px; opacity: 0.9; }}
                .qr-code {{ margin: 30px 0; text-align: center; }}
                .qr-code img {{ max-width: 200px; border: 3px solid white; border-radius: 10px; }}
                .message-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid {colors['primary']};
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .message-box p {{ color: #333; line-height: 1.6; }}
                .instructions {{
                    background-color: #f0f0f0;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .instructions h3 {{ color: {colors['primary']}; margin-bottom: 15px; }}
                .instructions ol {{ margin-left: 20px; }}
                .instructions li {{ margin: 10px 0; color: #333; }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
                .button {{
                    display: inline-block;
                    background-color: {colors['primary']};
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{salon_name}</div>
                    <p style="color: #666; margin-top: 10px;">Gift Card</p>
                </div>
                
                <h2 style="text-align: center; color: #333; margin: 20px 0;">Hello {recipient_name}!</h2>
                <p style="text-align: center; color: #666; margin-bottom: 20px;">You've received a gift card! 🎉</p>
                
                <div class="card-container">
                    <div class="card-title">Gift Card</div>
                    <div class="card-amount">₦{amount:,.0f}</div>
                    <div class="card-number">Card #: {card_number}</div>
                    <div class="expiration">Valid until {expiration_date}</div>
                    
                    <div class="qr-code">
                        <p style="margin-bottom: 10px; font-size: 12px;">Scan to redeem</p>
                        <img src="{qr_code_data}" alt="QR Code">
                    </div>
                </div>
                
                {message_section}
                
                <div class="instructions">
                    <h3>How to use your gift card:</h3>
                    <ol>
                        <li>Visit {salon_name} in person or online</li>
                        <li>Tell us you'd like to use your gift card</li>
                        <li>Provide your card number: <strong>{card_number}</strong></li>
                        <li>Or simply scan the QR code above</li>
                        <li>Enjoy your services!</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="https://kenikool.com/gift-cards/{card_number}" class="button">View Your Gift Card</a>
                </div>
                
                <div class="footer">
                    <p>This gift card is valid until {expiration_date}</p>
                    <p>For questions or support, contact us at support@kenikool.com or call +234 (0) 123 456 7890</p>
                    <p style="margin-top: 10px; color: #999;">© {datetime.now(timezone.utc).year} {salon_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _build_expiration_reminder_email(
        card_number: str,
        balance: float,
        days_until_expiration: int,
        expiration_date: str,
        salon_name: str
    ) -> str:
        """Build expiration reminder email HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .alert {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .alert h2 {{ color: #856404; margin-bottom: 10px; }}
                .alert p {{ color: #856404; }}
                .card-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ font-weight: bold; color: #333; }}
                .info-value {{ color: #666; }}
                .balance {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; padding: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="text-align: center; color: #333; margin: 20px 0;">{salon_name}</h1>
                
                <div class="alert">
                    <h2>⚠️ Your Gift Card is Expiring Soon!</h2>
                    <p>Your gift card will expire in <strong>{days_until_expiration} day{'s' if days_until_expiration > 1 else ''}</strong>.</p>
                </div>
                
                <div class="card-info">
                    <div class="info-row">
                        <span class="info-label">Card Number:</span>
                        <span class="info-value">{card_number}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Remaining Balance:</span>
                        <span class="balance">₦{balance:,.0f}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Expires:</span>
                        <span class="info-value">{expiration_date}</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <p style="color: #333; margin-bottom: 15px;">Don't let your balance go to waste!</p>
                    <a href="https://kenikool.com/gift-cards/{card_number}" class="button">Use Your Gift Card Now</a>
                </div>
                
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 10px;">Quick Tips:</h3>
                    <ul style="margin-left: 20px; color: #666;">
                        <li>Visit us in person to redeem your balance</li>
                        <li>Call us to book an appointment</li>
                        <li>Share your gift card with a friend</li>
                        <li>Transfer your balance to another card</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>For questions or support, contact us at support@kenikool.com</p>
                    <p style="margin-top: 10px; color: #999;">© {datetime.now(timezone.utc).year} {salon_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_redemption_confirmation_email(
        card_number: str,
        amount_redeemed: float,
        remaining_balance: float,
        transaction_id: str,
        salon_name: str
    ) -> str:
        """Build redemption confirmation email HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .success {{ background-color: #d4edda; border: 2px solid #28a745; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .success h2 {{ color: #155724; margin-bottom: 10px; }}
                .success p {{ color: #155724; }}
                .receipt {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #dee2e6; }}
                .receipt-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #dee2e6; }}
                .receipt-row:last-child {{ border-bottom: none; }}
                .receipt-label {{ font-weight: bold; color: #333; }}
                .receipt-value {{ color: #666; }}
                .footer {{ text-align: center; padding: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="text-align: center; color: #333; margin: 20px 0;">{salon_name}</h1>
                
                <div class="success">
                    <h2>✓ Redemption Successful!</h2>
                    <p>Your gift card has been successfully redeemed.</p>
                </div>
                
                <div class="receipt">
                    <div class="receipt-row">
                        <span class="receipt-label">Transaction ID:</span>
                        <span class="receipt-value">{transaction_id}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Card Number:</span>
                        <span class="receipt-value">{card_number}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Amount Redeemed:</span>
                        <span class="receipt-value">₦{amount_redeemed:,.0f}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Remaining Balance:</span>
                        <span class="receipt-value">₦{remaining_balance:,.0f}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Date & Time:</span>
                        <span class="receipt-value">{datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                </div>
                
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 10px;">What's Next?</h3>
                    <p style="color: #666; margin-bottom: 10px;">You have ₦{remaining_balance:,.0f} remaining on your gift card.</p>
                    <p style="color: #666;">You can use your remaining balance on your next visit or transfer it to another card.</p>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing {salon_name}!</p>
                    <p style="margin-top: 10px; color: #999;">© {datetime.now(timezone.utc).year} {salon_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """


    @staticmethod
    async def send_transfer_confirmation_email(
        card_id: str,
        card_number: str,
        recipient_email: str,
        recipient_name: Optional[str],
        transfer_type: str,  # "sent" or "received"
        amount: float,
        new_balance: float,
        other_card_number: str,
        salon_name: str = "Kenikool Salon"
    ) -> Dict:
        """
        Send transfer confirmation email
        
        Args:
            card_id: Gift card ID
            card_number: Gift card number
            recipient_email: Recipient email address
            recipient_name: Recipient name
            transfer_type: "sent" or "received"
            amount: Amount transferred
            new_balance: New balance after transfer
            other_card_number: The other card involved in transfer
            salon_name: Salon name for branding
            
        Returns:
            Dict with delivery status
        """
        try:
            # Build email HTML
            email_html = GiftCardEmailService._build_transfer_confirmation_email(
                card_number=card_number,
                recipient_name=recipient_name or "Valued Customer",
                transfer_type=transfer_type,
                amount=amount,
                new_balance=new_balance,
                other_card_number=other_card_number,
                salon_name=salon_name
            )
            
            # Determine subject based on transfer type
            if transfer_type == "sent":
                subject = f"Transfer Confirmation - ₦{amount:,.0f} Sent from Your Gift Card"
            else:
                subject = f"Transfer Confirmation - ₦{amount:,.0f} Received on Your Gift Card"
            
            # Send email
            success = await email_service.send_email(
                to=recipient_email,
                subject=subject,
                html=email_html
            )
            
            if success:
                logger.info(f"Transfer confirmation sent for card {card_number}")
                return {"success": True, "card_number": card_number}
            else:
                logger.error(f"Failed to send transfer confirmation: {card_number}")
                return {"success": False, "error": "Email delivery failed"}
                
        except Exception as e:
            logger.error(f"Error sending transfer confirmation: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def _build_transfer_confirmation_email(
        card_number: str,
        recipient_name: str,
        transfer_type: str,
        amount: float,
        new_balance: float,
        other_card_number: str,
        salon_name: str
    ) -> str:
        """Build transfer confirmation email HTML"""
        
        if transfer_type == "sent":
            title = "Transfer Sent Successfully"
            icon = "📤"
            message = f"You have successfully transferred ₦{amount:,.0f} from your gift card to card {other_card_number}."
            action_label = "Transferred to"
        else:
            title = "Transfer Received"
            icon = "📥"
            message = f"You have received ₦{amount:,.0f} on your gift card from card {other_card_number}."
            action_label = "Received from"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .success {{ background-color: #d4edda; border: 2px solid #28a745; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
                .success h2 {{ color: #155724; margin-bottom: 10px; font-size: 24px; }}
                .success .icon {{ font-size: 48px; margin-bottom: 10px; }}
                .success p {{ color: #155724; line-height: 1.6; }}
                .transfer-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #dee2e6; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #dee2e6; }}
                .detail-row:last-child {{ border-bottom: none; }}
                .detail-label {{ font-weight: bold; color: #333; }}
                .detail-value {{ color: #666; }}
                .amount {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .balance {{ font-size: 20px; font-weight: bold; color: #007bff; }}
                .info-box {{ background-color: #e7f3ff; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .info-box p {{ color: #004085; line-height: 1.6; }}
                .button {{ display: inline-block; background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; padding: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{salon_name}</div>
                    <p style="color: #666; margin-top: 10px;">Gift Card Transfer Confirmation</p>
                </div>
                
                <h2 style="text-align: center; color: #333; margin: 20px 0;">Hello {recipient_name}!</h2>
                
                <div class="success">
                    <div class="icon">{icon}</div>
                    <h2>{title}</h2>
                    <p style="margin-top: 10px;">{message}</p>
                </div>
                
                <div class="transfer-details">
                    <div class="detail-row">
                        <span class="detail-label">Your Card Number:</span>
                        <span class="detail-value">{card_number}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">{action_label}:</span>
                        <span class="detail-value">{other_card_number}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Amount Transferred:</span>
                        <span class="amount">₦{amount:,.0f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">New Balance:</span>
                        <span class="balance">₦{new_balance:,.0f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date & Time:</span>
                        <span class="detail-value">{datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}</span>
                    </div>
                </div>
                
                <div class="info-box">
                    <p><strong>What's Next?</strong></p>
                    <p style="margin-top: 10px;">Your gift card balance has been updated. You can use your remaining balance at {salon_name} anytime.</p>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="https://kenikool.com/gift-cards/{card_number}" class="button">View Your Gift Card</a>
                </div>
                
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 10px;">Important Information:</h3>
                    <ul style="margin-left: 20px; color: #666;">
                        <li>Transfers are limited to 1 per card per day</li>
                        <li>This transaction has been recorded in your gift card audit log</li>
                        <li>If you did not authorize this transfer, please contact us immediately</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>For questions or support, contact us at support@kenikool.com or call +234 (0) 123 456 7890</p>
                    <p style="margin-top: 10px; color: #999;">© {datetime.now(timezone.utc).year} {salon_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
