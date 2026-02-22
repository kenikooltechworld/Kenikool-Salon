from celery import shared_task
from datetime import datetime, timedelta
from app.database import Database
from app.services.alert_service import AlertService
from app.services.forecasting_service import ForecastingService
from bson import ObjectId


@shared_task
def send_low_stock_alerts():
    """Send low stock alerts daily at 9 AM"""
    db = get_db()
    alert_service = AlertService(db)
    products = db.inventory.find({"quantity": {"$gt": 0}})

    for product in products:
        prefs = alert_service.get_alert_preferences(str(product["_id"]))

        if not prefs.get("email_notifications"):
            continue

        threshold = prefs.get("low_stock_threshold", product.get("reorder_point", 10))

        if product["quantity"] < threshold:
            alert_service.send_low_stock_alert(
                str(product["_id"]),
                product["quantity"],
                threshold,
            )

    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}


@shared_task
def send_expiration_warnings():
    """Send expiration warnings daily at 8 AM"""
    db = get_db()
    alert_service = AlertService(db)
    thirty_days_from_now = datetime.utcnow() + timedelta(days=30)

    products = db.inventory.find({"batch_tracking_enabled": True})

    for product in products:
        batches = product.get("batches", [])

        for batch in batches:
            expiration_date = batch.get("expiration_date")
            if expiration_date and expiration_date <= thirty_days_from_now:
                alert_service.send_expiration_warning(
                    str(product["_id"]),
                    batch.get("batch_id"),
                    expiration_date,
                )

    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}


@shared_task
def refresh_inventory_forecasts():
    """Refresh inventory forecasts daily at 2 AM"""
    db = get_db()
    forecasting_service = ForecastingService(db)
    products = db.inventory.find({})

    count = 0
    for product in products:
        try:
            forecasting_service.calculate_forecast(str(product["_id"]))
            count += 1
        except Exception as e:
            print(f"Error calculating forecast for product {product['_id']}: {e}")

    return {"status": "completed", "products_updated": count, "timestamp": datetime.utcnow().isoformat()}


@shared_task
def send_overdue_po_reminders():
    """Send overdue PO reminders daily at 10 AM"""
    db = get_db()
    alert_service = AlertService(db)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    purchase_orders = db.purchase_orders.find(
        {
            "status": {"$in": ["sent", "pending"]},
            "expected_delivery_date": {"$lt": datetime.utcnow()},
        }
    )

    for po in purchase_orders:
        days_overdue = (datetime.utcnow() - po.get("expected_delivery_date", datetime.utcnow())).days

        supplier = db.suppliers.find_one({"_id": ObjectId(po.get("supplier_id"))})
        supplier_name = supplier.get("name", "Unknown") if supplier else "Unknown"

        alert_service.send_overdue_po_reminder(
            str(po["_id"]),
            supplier_name,
            days_overdue,
        )

    return {"status": "completed", "timestamp": datetime.utcnow().isoformat()}
