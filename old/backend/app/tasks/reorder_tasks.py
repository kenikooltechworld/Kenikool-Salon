from celery import shared_task
from datetime import datetime
from app.database import Database
from app.services.auto_reorder_service import AutoReorderService
from app.services.alert_service import AlertService


@shared_task
def auto_create_purchase_orders():
    """Auto-create purchase orders daily at 10 AM"""
    db = get_db()
    reorder_service = AutoReorderService(db)
    alert_service = AlertService(db)

    candidates = reorder_service.get_reorder_candidates()
    created_pos = []
    failed_products = []

    for product in candidates:
        try:
            po = reorder_service.create_auto_reorder_po(
                str(product["_id"]),
                created_by="system_auto_reorder",
            )
            if po:
                created_pos.append(po)
        except Exception as e:
            failed_products.append(
                {
                    "product_id": str(product["_id"]),
                    "error": str(e),
                }
            )

    # Send notification to owner for approval
    if created_pos:
        alert_service.create_alert(
            alert_type="forecast_alert",
            product_id="",
            title=f"Auto-Reorder: {len(created_pos)} POs Created",
            message=f"{len(created_pos)} purchase orders have been auto-generated and are ready for review",
            severity="medium",
            metadata={
                "po_count": len(created_pos),
                "failed_count": len(failed_products),
            },
        )

    return {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "created_pos": len(created_pos),
        "failed_products": len(failed_products),
    }
