from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertType(str, Enum):
    LOW_STOCK = "low_stock"
    URGENT_STOCK = "urgent_stock"
    EXPIRATION_WARNING = "expiration_warning"
    FORECAST_ALERT = "forecast_alert"
    OVERDUE_PO = "overdue_po"


class AlertStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DISMISSED = "dismissed"


class AlertService:
    def __init__(self, db, email_config: Optional[Dict] = None):
        self.db = db
        self.alerts_collection: Collection = db.inventory_alerts
        self.products_collection: Collection = db.inventory
        self.alert_prefs_collection: Collection = db.alert_preferences
        self.email_config = email_config or {}

    def create_alert(
        self,
        alert_type: AlertType,
        product_id: str,
        title: str,
        message: str,
        severity: str = "medium",
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Create a new alert"""
        alert = {
            "type": alert_type.value,
            "product_id": product_id,
            "title": title,
            "message": message,
            "severity": severity,
            "status": AlertStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "sent_at": None,
            "dismissed_at": None,
            "dismissed_reason": None,
            "metadata": metadata or {},
        }

        result = self.alerts_collection.insert_one(alert)
        return {"id": str(result.inserted_id), **alert}

    def send_low_stock_alert(self, product_id: str, current_stock: float, threshold: float) -> Dict:
        """Send low stock alert"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        prefs = self.alert_prefs_collection.find_one({"product_id": product_id}) or {}

        alert = self.create_alert(
            alert_type=AlertType.LOW_STOCK,
            product_id=product_id,
            title=f"Low Stock Alert: {product['name']}",
            message=f"Stock level ({current_stock}) is below threshold ({threshold})",
            severity="medium",
            metadata={
                "current_stock": current_stock,
                "threshold": threshold,
                "product_name": product["name"],
            },
        )

        if prefs.get("email_notifications"):
            self._send_email_alert(alert, prefs.get("email"))

        return alert

    def send_urgent_stock_alert(self, product_id: str, current_stock: float, critical_level: float) -> Dict:
        """Send urgent stock alert (SMS/WhatsApp)"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        prefs = self.alert_prefs_collection.find_one({"product_id": product_id}) or {}

        alert = self.create_alert(
            alert_type=AlertType.URGENT_STOCK,
            product_id=product_id,
            title=f"URGENT: Critical Stock Level - {product['name']}",
            message=f"Stock level ({current_stock}) is critically low (critical: {critical_level})",
            severity="critical",
            metadata={
                "current_stock": current_stock,
                "critical_level": critical_level,
                "product_name": product["name"],
            },
        )

        if prefs.get("sms_notifications"):
            self._send_sms_alert(alert, prefs.get("phone"))

        return alert

    def send_expiration_warning(self, product_id: str, batch_id: str, expiration_date: datetime) -> Dict:
        """Send expiration warning for batches"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        days_until_expiry = (expiration_date - datetime.utcnow()).days

        alert = self.create_alert(
            alert_type=AlertType.EXPIRATION_WARNING,
            product_id=product_id,
            title=f"Expiration Warning: {product['name']}",
            message=f"Batch {batch_id} expires in {days_until_expiry} days",
            severity="high" if days_until_expiry <= 7 else "medium",
            metadata={
                "batch_id": batch_id,
                "expiration_date": expiration_date.isoformat(),
                "days_until_expiry": days_until_expiry,
                "product_name": product["name"],
            },
        )

        prefs = self.alert_prefs_collection.find_one({"product_id": product_id}) or {}
        if prefs.get("email_notifications"):
            self._send_email_alert(alert, prefs.get("email"))

        return alert

    def send_forecast_alert(self, product_id: str, predicted_stockout_date: datetime, confidence: float) -> Dict:
        """Send forecast alert for predicted stockouts"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        days_until_stockout = (predicted_stockout_date - datetime.utcnow()).days

        alert = self.create_alert(
            alert_type=AlertType.FORECAST_ALERT,
            product_id=product_id,
            title=f"Forecast Alert: {product['name']}",
            message=f"Predicted stockout in {days_until_stockout} days (confidence: {confidence:.0%})",
            severity="high" if days_until_stockout <= 7 else "medium",
            metadata={
                "predicted_stockout_date": predicted_stockout_date.isoformat(),
                "days_until_stockout": days_until_stockout,
                "confidence": confidence,
                "product_name": product["name"],
            },
        )

        prefs = self.alert_prefs_collection.find_one({"product_id": product_id}) or {}
        if prefs.get("email_notifications"):
            self._send_email_alert(alert, prefs.get("email"))

        return alert

    def send_overdue_po_reminder(self, po_id: str, supplier_name: str, days_overdue: int) -> Dict:
        """Send reminder for overdue purchase orders"""
        alert = self.create_alert(
            alert_type=AlertType.OVERDUE_PO,
            product_id="",
            title=f"Overdue PO Reminder: {supplier_name}",
            message=f"Purchase order is {days_overdue} days overdue",
            severity="high",
            metadata={
                "po_id": po_id,
                "supplier_name": supplier_name,
                "days_overdue": days_overdue,
            },
        )

        return alert

    def dismiss_alert(self, alert_id: str, reason: Optional[str] = None) -> Dict:
        """Dismiss an alert"""
        result = self.alerts_collection.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "status": AlertStatus.DISMISSED.value,
                    "dismissed_at": datetime.utcnow(),
                    "dismissed_reason": reason,
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError(f"Alert {alert_id} not found")

        return {"success": True, "message": "Alert dismissed"}

    def get_alerts(
        self,
        product_id: Optional[str] = None,
        alert_type: Optional[AlertType] = None,
        status: Optional[AlertStatus] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """Get alerts with optional filters"""
        query = {}

        if product_id:
            query["product_id"] = product_id
        if alert_type:
            query["type"] = alert_type.value
        if status:
            query["status"] = status.value

        alerts = list(
            self.alerts_collection.find(query)
            .sort("created_at", -1)
            .limit(limit)
        )

        return [
            {**alert, "_id": str(alert["_id"]), "id": str(alert["_id"])}
            for alert in alerts
        ]

    def set_alert_preferences(
        self,
        product_id: str,
        email_notifications: bool = True,
        sms_notifications: bool = False,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        low_stock_threshold: Optional[float] = None,
        critical_stock_level: Optional[float] = None,
    ) -> Dict:
        """Set alert preferences for a product"""
        prefs = {
            "product_id": product_id,
            "email_notifications": email_notifications,
            "sms_notifications": sms_notifications,
            "email": email,
            "phone": phone,
            "low_stock_threshold": low_stock_threshold,
            "critical_stock_level": critical_stock_level,
            "updated_at": datetime.utcnow(),
        }

        result = self.alert_prefs_collection.update_one(
            {"product_id": product_id},
            {"$set": prefs},
            upsert=True,
        )

        return {"success": True, "data": prefs}

    def get_alert_preferences(self, product_id: str) -> Dict:
        """Get alert preferences for a product"""
        prefs = self.alert_prefs_collection.find_one({"product_id": product_id})
        if not prefs:
            return {}
        return {**prefs, "_id": str(prefs["_id"])}

    def _send_email_alert(self, alert: Dict, recipient_email: Optional[str]) -> bool:
        """Send email alert"""
        if not recipient_email or not self.email_config.get("smtp_server"):
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_config.get("from_email")
            msg["To"] = recipient_email
            msg["Subject"] = alert["title"]

            body = f"""
            {alert['message']}
            
            Alert Type: {alert['type']}
            Severity: {alert['severity']}
            Time: {alert['created_at']}
            """

            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.email_config.get("smtp_server"), self.email_config.get("smtp_port", 587)) as server:
                server.starttls()
                server.login(self.email_config.get("smtp_user"), self.email_config.get("smtp_password"))
                server.send_message(msg)

            self.alerts_collection.update_one(
                {"_id": ObjectId(alert["id"])},
                {"$set": {"status": AlertStatus.SENT.value, "sent_at": datetime.utcnow()}},
            )

            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def _send_sms_alert(self, alert: Dict, phone_number: Optional[str]) -> bool:
        """Send SMS alert (placeholder for SMS service integration)"""
        if not phone_number:
            return False

        try:
            # Placeholder for SMS service integration (Twilio, etc.)
            message = f"{alert['title']}: {alert['message']}"

            self.alerts_collection.update_one(
                {"_id": ObjectId(alert["id"])},
                {"$set": {"status": AlertStatus.SENT.value, "sent_at": datetime.utcnow()}},
            )

            return True
        except Exception as e:
            print(f"Failed to send SMS alert: {e}")
            return False
