"""
Fraud Detection Service for Gift Cards
Monitors suspicious activity and flags cards for review
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
from app.database import Database

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """Service for detecting and preventing gift card fraud"""
    
    # Fraud detection thresholds
    BALANCE_CHECK_RATE_LIMIT = 10  # Max balance checks per IP per hour
    FAILED_REDEMPTION_LIMIT = 3  # Max failed redemptions before flag
    RAPID_BALANCE_CHECKS = 10  # Rapid checks within 5 minutes
    VELOCITY_LIMIT = 3  # Max redemptions per card per day
    HIGH_VALUE_THRESHOLD = 50000  # High value redemption threshold (₦50,000)
    MULTIPLE_CARDS_THRESHOLD = 3  # Multiple cards from same IP in short time
    
    @staticmethod
    def check_balance_check_rate(
        ip_address: str,
        card_number: str,
        tenant_id: str
    ) -> Dict:
        """
        Check if balance check rate is suspicious
        
        Args:
            ip_address: IP address making the request
            card_number: Gift card number
            tenant_id: Tenant ID
            
        Returns:
            Dict with rate check result
        """
        db = Database.get_db()
        
        # Check balance check attempts in last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        recent_checks = list(db.gift_card_balance_checks.find({
            "ip_address": ip_address,
            "tenant_id": tenant_id,
            "timestamp": {"$gte": one_hour_ago}
        }))
        
        check_count = len(recent_checks)
        
        if check_count >= FraudDetectionService.BALANCE_CHECK_RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for IP {ip_address}: {check_count} checks in 1 hour")
            return {
                "suspicious": True,
                "reason": "rate_limit_exceeded",
                "check_count": check_count,
                "limit": FraudDetectionService.BALANCE_CHECK_RATE_LIMIT,
                "action": "block_ip"
            }
        
        # Check for rapid checks (10+ in 5 minutes)
        five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        rapid_checks = [c for c in recent_checks if c["timestamp"] >= five_min_ago]
        
        if len(rapid_checks) >= FraudDetectionService.RAPID_BALANCE_CHECKS:
            logger.warning(f"Rapid balance checks from IP {ip_address}: {len(rapid_checks)} in 5 minutes")
            return {
                "suspicious": True,
                "reason": "rapid_checks",
                "check_count": len(rapid_checks),
                "action": "block_ip_extended"
            }
        
        return {
            "suspicious": False,
            "check_count": check_count,
            "limit": FraudDetectionService.BALANCE_CHECK_RATE_LIMIT
        }
    
    @staticmethod
    def check_redemption_velocity(
        card_number: str,
        tenant_id: str
    ) -> Dict:
        """
        Check if redemption velocity is suspicious
        
        Args:
            card_number: Gift card number
            tenant_id: Tenant ID
            
        Returns:
            Dict with velocity check result
        """
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({
            "card_number": card_number,
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            return {"suspicious": False, "reason": "card_not_found"}
        
        # Check redemptions in last 24 hours
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_redemptions = [
            t for t in gift_card.get("transactions", [])
            if t.get("type") == "redeem" and t.get("timestamp", datetime.now(timezone.utc)) >= today
        ]
        
        redemption_count = len(today_redemptions)
        
        if redemption_count >= FraudDetectionService.VELOCITY_LIMIT:
            logger.warning(f"High redemption velocity for card {card_number}: {redemption_count} in 24 hours")
            return {
                "suspicious": True,
                "reason": "high_velocity",
                "redemption_count": redemption_count,
                "limit": FraudDetectionService.VELOCITY_LIMIT,
                "action": "flag_card"
            }
        
        return {
            "suspicious": False,
            "redemption_count": redemption_count,
            "limit": FraudDetectionService.VELOCITY_LIMIT
        }
    
    @staticmethod
    def check_unusual_pattern(
        card_number: str,
        amount: float,
        location: Optional[str],
        tenant_id: str
    ) -> Dict:
        """
        Check for unusual redemption patterns
        
        Args:
            card_number: Gift card number
            amount: Redemption amount
            location: Redemption location
            tenant_id: Tenant ID
            
        Returns:
            Dict with pattern check result
        """
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({
            "card_number": card_number,
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            return {"suspicious": False, "reason": "card_not_found"}
        
        # Check for unusually high redemption amount
        card_amount = gift_card.get("amount", 0)
        if amount > card_amount * 0.8:  # More than 80% of card value
            logger.warning(f"Unusual redemption amount for card {card_number}: ₦{amount} (card value: ₦{card_amount})")
            return {
                "suspicious": True,
                "reason": "high_redemption_amount",
                "amount": amount,
                "card_value": card_amount,
                "percentage": (amount / card_amount) * 100,
                "action": "flag_card"
            }
        
        # Check for multiple locations in short time
        recent_transactions = [
            t for t in gift_card.get("transactions", [])
            if t.get("timestamp", datetime.now(timezone.utc)) >= datetime.now(timezone.utc) - timedelta(hours=1)
        ]
        
        locations = set(t.get("location") for t in recent_transactions if t.get("location"))
        
        if len(locations) > 2:
            logger.warning(f"Multiple locations for card {card_number} in 1 hour: {locations}")
            return {
                "suspicious": True,
                "reason": "multiple_locations",
                "locations": list(locations),
                "action": "flag_card"
            }
        
        return {
            "suspicious": False,
            "amount": amount,
            "card_value": card_amount
        }
    
    @staticmethod
    def flag_card(
        card_id: str,
        reason: str,
        severity: str = "medium",
        details: Optional[Dict] = None
    ) -> Dict:
        """
        Flag a card for review
        
        Args:
            card_id: Card ID
            reason: Reason for flagging
            severity: Severity level (low, medium, high)
            details: Additional details
            
        Returns:
            Dict with flag result
        """
        db = Database.get_db()
        
        from bson import ObjectId
        
        # Get card
        gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
        
        if not gift_card:
            return {"success": False, "error": "Card not found"}
        
        # Add flag
        flag_data = {
            "reason": reason,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc),
            "details": details or {}
        }
        
        # Update card
        db.gift_cards.update_one(
            {"_id": ObjectId(card_id)},
            {
                "$push": {"security_flags": flag_data},
                "$inc": {"suspicious_activity_count": 1}
            }
        )
        
        logger.warning(f"Card flagged: {gift_card['card_number']}, reason: {reason}, severity: {severity}")
        
        return {
            "success": True,
            "card_number": gift_card["card_number"],
            "flag_reason": reason,
            "severity": severity
        }
    
    @staticmethod
    def suspend_card(
        card_id: str,
        reason: str,
        suspended_by: Optional[str] = None
    ) -> Dict:
        """
        Temporarily suspend a card
        
        Args:
            card_id: Card ID
            reason: Suspension reason
            suspended_by: User ID who suspended the card
            
        Returns:
            Dict with suspension result
        """
        db = Database.get_db()
        
        from bson import ObjectId
        
        # Get card
        gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
        
        if not gift_card:
            return {"success": False, "error": "Card not found"}
        
        # Suspend card
        db.gift_cards.update_one(
            {"_id": ObjectId(card_id)},
            {
                "$set": {
                    "status": "suspended",
                    "suspended_at": datetime.now(timezone.utc),
                    "suspended_by": suspended_by,
                    "suspension_reason": reason
                },
                "$push": {
                    "audit_log": {
                        "action": "suspended",
                        "user_id": suspended_by,
                        "timestamp": datetime.now(timezone.utc),
                        "details": {"reason": reason}
                    }
                }
            }
        )
        
        logger.warning(f"Card suspended: {gift_card['card_number']}, reason: {reason}")
        
        return {
            "success": True,
            "card_number": gift_card["card_number"],
            "status": "suspended",
            "reason": reason
        }
    
    @staticmethod
    def record_balance_check(
        card_number: str,
        ip_address: str,
        tenant_id: str,
        success: bool = True
    ) -> None:
        """
        Record a balance check attempt
        
        Args:
            card_number: Gift card number
            ip_address: IP address
            tenant_id: Tenant ID
            success: Whether the check was successful
        """
        db = Database.get_db()
        
        check_data = {
            "card_number": card_number,
            "ip_address": ip_address,
            "tenant_id": tenant_id,
            "timestamp": datetime.now(timezone.utc),
            "success": success
        }
        
        db.gift_card_balance_checks.insert_one(check_data)
    
    @staticmethod
    def get_flagged_cards(
        tenant_id: str,
        severity: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all flagged cards for a tenant
        
        Args:
            tenant_id: Tenant ID
            severity: Optional severity filter
            
        Returns:
            List of flagged cards
        """
        db = Database.get_db()
        
        query = {
            "tenant_id": tenant_id,
            "security_flags": {"$exists": True, "$ne": []}
        }
        
        flagged_cards = list(db.gift_cards.find(query).sort("suspicious_activity_count", -1))
        
        # Filter by severity if provided
        if severity:
            flagged_cards = [
                card for card in flagged_cards
                if any(flag.get("severity") == severity for flag in card.get("security_flags", []))
            ]
        
        for card in flagged_cards:
            card["id"] = str(card["_id"])
        
        return flagged_cards
    
    @staticmethod
    def clear_flags(
        card_id: str,
        cleared_by: Optional[str] = None
    ) -> Dict:
        """
        Clear all flags from a card
        
        Args:
            card_id: Card ID
            cleared_by: User ID who cleared the flags
            
        Returns:
            Dict with result
        """
        db = Database.get_db()
        
        from bson import ObjectId
        
        # Get card
        gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id)})
        
        if not gift_card:
            return {"success": False, "error": "Card not found"}
        
        # Clear flags
        db.gift_cards.update_one(
            {"_id": ObjectId(card_id)},
            {
                "$set": {
                    "security_flags": [],
                    "suspicious_activity_count": 0
                },
                "$push": {
                    "audit_log": {
                        "action": "flags_cleared",
                        "user_id": cleared_by,
                        "timestamp": datetime.now(timezone.utc),
                        "details": {}
                    }
                }
            }
        )
        
        logger.info(f"Flags cleared for card: {gift_card['card_number']}")
        
        return {
            "success": True,
            "card_number": gift_card["card_number"],
            "flags_cleared": True
        }
    
    @staticmethod
    async def notify_staff_of_fraud(
        tenant_id: str,
        card_number: str,
        reason: str,
        severity: str,
        details: Dict
    ) -> bool:
        """
        Send email notification to staff about fraudulent activity
        
        Args:
            tenant_id: Tenant ID
            card_number: Gift card number
            reason: Fraud reason
            severity: Severity level
            details: Additional details
            
        Returns:
            True if notification sent successfully
        """
        try:
            from app.services.email_service import EmailService
            from app.database import Database
            
            db = Database.get_db()
            
            # Get tenant/salon info
            tenant = db.tenants.find_one({"_id": tenant_id})
            if not tenant:
                logger.error(f"Tenant not found: {tenant_id}")
                return False
            
            salon_name = tenant.get("name", "Salon")
            
            # Get staff emails (owner and managers)
            staff_emails = []
            
            # Get owner email
            owner = db.users.find_one({"tenant_id": tenant_id, "role": "owner"})
            if owner and owner.get("email"):
                staff_emails.append(owner["email"])
            
            # Get manager emails
            managers = db.users.find({"tenant_id": tenant_id, "role": "manager"})
            for manager in managers:
                if manager.get("email"):
                    staff_emails.append(manager["email"])
            
            if not staff_emails:
                logger.warning(f"No staff emails found for tenant {tenant_id}")
                return False
            
            # Prepare email content
            severity_color = {
                "low": "#fbbf24",
                "medium": "#f97316",
                "high": "#ef4444"
            }.get(severity, "#6b7280")
            
            severity_label = severity.upper()
            
            # Format details for display
            details_html = ""
            for key, value in details.items():
                details_html += f"<tr><td style='padding: 8px; border-bottom: 1px solid #e5e7eb;'><strong>{key.replace('_', ' ').title()}:</strong></td><td style='padding: 8px; border-bottom: 1px solid #e5e7eb;'>{value}</td></tr>"
            
            subject = f"🚨 Fraud Alert: {severity_label} - Gift Card {card_number}"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Fraud Alert</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td align="center" style="padding: 40px 0;">
                            <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="padding: 40px 40px 20px 40px; text-align: center; background-color: {severity_color}; border-radius: 8px 8px 0 0;">
                                        <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">🚨 Fraud Alert</h1>
                                        <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px;">{severity_label} SEVERITY</p>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px;">
                                        <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Suspicious Activity Detected</h2>
                                        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                            Suspicious activity has been detected on a gift card in {salon_name}.
                                        </p>
                                        
                                        <!-- Alert Details -->
                                        <table role="presentation" style="width: 100%; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #e5e7eb; border-radius: 6px;">
                                            <tr style="background-color: #f9fafb;">
                                                <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Card Number</td>
                                                <td style="padding: 12px 16px; color: #4b5563; font-family: monospace;">{card_number}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Reason</td>
                                                <td style="padding: 12px 16px; color: #4b5563;">{reason.replace('_', ' ').title()}</td>
                                            </tr>
                                            <tr style="background-color: #f9fafb;">
                                                <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Severity</td>
                                                <td style="padding: 12px 16px; color: {severity_color}; font-weight: bold;">{severity_label}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Time</td>
                                                <td style="padding: 12px 16px; color: #4b5563;">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Additional Details -->
                                        {f'''
                                        <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 18px;">Additional Details</h3>
                                        <table role="presentation" style="width: 100%; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #e5e7eb; border-radius: 6px;">
                                            {details_html}
                                        </table>
                                        ''' if details_html else ''}
                                        
                                        <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 18px;">Recommended Actions</h3>
                                        <ul style="margin: 0 0 30px 0; padding-left: 20px; color: #4b5563; font-size: 14px; line-height: 1.8;">
                                            <li>Review the card's transaction history</li>
                                            <li>Contact the card holder if possible</li>
                                            <li>Consider temporarily suspending the card</li>
                                            <li>Monitor for additional suspicious activity</li>
                                            <li>Document your investigation findings</li>
                                        </ul>
                                        
                                        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                            Please log in to your dashboard to review this alert and take appropriate action.
                                        </p>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                        <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                            This is an automated fraud detection alert from Kenikool Salon Management
                                        </p>
                                        <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                            © {datetime.now().year} Kenikool Salon Management. All rights reserved.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            # Send email to all staff
            email_service = EmailService()
            success_count = 0
            
            for email in staff_emails:
                try:
                    sent = await email_service.send_email(
                        to=email,
                        subject=subject,
                        html=html
                    )
                    if sent:
                        success_count += 1
                        logger.info(f"Fraud alert sent to {email}")
                except Exception as e:
                    logger.error(f"Failed to send fraud alert to {email}: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending fraud notification: {str(e)}")
            return False
    
    @staticmethod
    def check_failed_redemptions(
        card_number: str,
        tenant_id: str
    ) -> Dict:
        """
        Check for multiple failed redemption attempts
        
        Args:
            card_number: Gift card number
            tenant_id: Tenant ID
            
        Returns:
            Dict with check result
        """
        db = Database.get_db()
        
        # Check failed redemption attempts in last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        failed_attempts = list(db.gift_card_redemption_attempts.find({
            "card_number": card_number,
            "tenant_id": tenant_id,
            "success": False,
            "timestamp": {"$gte": one_hour_ago}
        }))
        
        failed_count = len(failed_attempts)
        
        if failed_count >= FraudDetectionService.FAILED_REDEMPTION_LIMIT:
            logger.warning(f"Multiple failed redemptions for card {card_number}: {failed_count} in 1 hour")
            return {
                "suspicious": True,
                "reason": "multiple_failed_redemptions",
                "failed_count": failed_count,
                "limit": FraudDetectionService.FAILED_REDEMPTION_LIMIT,
                "action": "flag_card"
            }
        
        return {
            "suspicious": False,
            "failed_count": failed_count,
            "limit": FraudDetectionService.FAILED_REDEMPTION_LIMIT
        }
    
    @staticmethod
    def record_redemption_attempt(
        card_number: str,
        tenant_id: str,
        amount: float,
        success: bool,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        error_reason: Optional[str] = None
    ) -> None:
        """
        Record a redemption attempt (success or failure)
        
        Args:
            card_number: Gift card number
            tenant_id: Tenant ID
            amount: Redemption amount
            success: Whether redemption was successful
            ip_address: IP address (optional)
            location: Location (optional)
            error_reason: Error reason if failed (optional)
        """
        db = Database.get_db()
        
        attempt_data = {
            "card_number": card_number,
            "tenant_id": tenant_id,
            "amount": amount,
            "success": success,
            "ip_address": ip_address,
            "location": location,
            "error_reason": error_reason,
            "timestamp": datetime.now(timezone.utc)
        }
        
        db.gift_card_redemption_attempts.insert_one(attempt_data)
    
    @staticmethod
    def check_rapid_succession_redemptions(
        card_number: str,
        tenant_id: str
    ) -> Dict:
        """
        Check for rapid succession redemptions (multiple redemptions in short time)
        
        Args:
            card_number: Gift card number
            tenant_id: Tenant ID
            
        Returns:
            Dict with check result
        """
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({
            "card_number": card_number,
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            return {"suspicious": False, "reason": "card_not_found"}
        
        # Check redemptions in last 10 minutes
        ten_min_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        
        recent_redemptions = [
            t for t in gift_card.get("transactions", [])
            if t.get("type") == "redeem" and t.get("timestamp", datetime.now(timezone.utc)) >= ten_min_ago
        ]
        
        if len(recent_redemptions) >= 2:
            logger.warning(f"Rapid succession redemptions for card {card_number}: {len(recent_redemptions)} in 10 minutes")
            return {
                "suspicious": True,
                "reason": "rapid_succession_redemptions",
                "redemption_count": len(recent_redemptions),
                "action": "flag_card"
            }
        
        return {
            "suspicious": False,
            "redemption_count": len(recent_redemptions)
        }
    
    @staticmethod
    def check_multiple_cards_same_ip(
        ip_address: str,
        tenant_id: str
    ) -> Dict:
        """
        Check for multiple different cards being used from same IP
        
        Args:
            ip_address: IP address
            tenant_id: Tenant ID
            
        Returns:
            Dict with check result
        """
        db = Database.get_db()
        
        # Check balance checks from this IP in last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        recent_checks = list(db.gift_card_balance_checks.find({
            "ip_address": ip_address,
            "tenant_id": tenant_id,
            "timestamp": {"$gte": one_hour_ago}
        }))
        
        # Count unique cards
        unique_cards = set(check["card_number"] for check in recent_checks)
        
        if len(unique_cards) >= FraudDetectionService.MULTIPLE_CARDS_THRESHOLD:
            logger.warning(f"Multiple cards from same IP {ip_address}: {len(unique_cards)} cards in 1 hour")
            return {
                "suspicious": True,
                "reason": "multiple_cards_same_ip",
                "card_count": len(unique_cards),
                "threshold": FraudDetectionService.MULTIPLE_CARDS_THRESHOLD,
                "action": "block_ip"
            }
        
        return {
            "suspicious": False,
            "card_count": len(unique_cards),
            "threshold": FraudDetectionService.MULTIPLE_CARDS_THRESHOLD
        }
