"""
Celery tasks for inventory management
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from app.services.termii_service import send_whatsapp
from bson import ObjectId
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


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def deduct_inventory_for_service(self, booking_id: str):
    """
    Automatically deduct inventory when a service is completed
    """
    try:
        db = Database.get_db()
        
        # Get booking
        booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
        if booking is None:
            logger.error(f"Booking {booking_id} not found")
            return {"success": False, "error": "Booking not found"}
        
        # Get service
        service = await db.services.find_one({"_id": ObjectId(booking["service_id"])})
        if service is None:
            logger.error(f"Service {booking['service_id']} not found")
            return {"success": False, "error": "Service not found"}
        
        # Check if service has product mappings
        product_mappings = service.get("product_mappings", [])
        if not product_mappings:
            logger.info(f"No product mappings for service {booking['service_id']}")
            return {"success": True, "deducted": 0}
        
        deducted_count = 0
        low_stock_products = []
        
        # Deduct inventory for each product
        for mapping in product_mappings:
            product_id = mapping["product_id"]
            quantity_to_deduct = mapping["quantity_per_service"]
            
            # Get product
            product = await db.inventory.find_one({"_id": ObjectId(product_id)})
            if product is None:
                logger.warning(f"Product {product_id} not found")
                continue
            
            # Check if sufficient quantity
            if product["quantity"] < quantity_to_deduct:
                logger.warning(f"Insufficient inventory for product {product_id}")
                continue
            
            # Calculate new quantity
            new_quantity = product["quantity"] - quantity_to_deduct
            
            # Create transaction
            transaction = {
                "transaction_type": "usage",
                "quantity": -quantity_to_deduct,
                "booking_id": booking_id,
                "service_id": booking["service_id"],
                "notes": f"Auto-deducted for service: {service['name']}",
                "created_by": "system",
                "created_at": datetime.utcnow()
            }
            
            # Update product
            await db.inventory.update_one(
                {"_id": ObjectId(product_id)},
                {
                    "$set": {
                        "quantity": new_quantity,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {"transactions": transaction}
                }
            )
            
            deducted_count += 1
            logger.info(f"Inventory deducted: {product_id}, quantity: {quantity_to_deduct}")
            
            # Check for low stock
            if new_quantity <= product["low_stock_threshold"]:
                low_stock_products.append(product_id)
        
        # Send low stock alerts
        for product_id in low_stock_products:
            try:
                send_low_stock_alert.delay(product_id)
            except Exception as e:
                logger.warning(f"Failed to queue low stock alert: {e}")
        
        logger.info(f"Inventory deduction complete for booking {booking_id}: {deducted_count} products")
        return {"success": True, "deducted": deducted_count}
    
    except Exception as e:
        logger.error(f"Error in deduct_inventory_for_service task: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_low_stock_alert(self, product_id: str):
    """
    Send low stock alert to salon owner
    """
    try:
        db = Database.get_db()
        
        # Get product
        product = await db.inventory.find_one({"_id": ObjectId(product_id)})
        if product is None:
            logger.error(f"Product {product_id} not found")
            return {"success": False, "error": "Product not found"}
        
        # Get tenant
        tenant = await db.tenants.find_one({"_id": ObjectId(product["tenant_id"])})
        if tenant is None:
            logger.error(f"Tenant {product['tenant_id']} not found")
            return {"success": False, "error": "Tenant not found"}
        
        # Get owner
        owner = await db.users.find_one({
            "tenant_id": product["tenant_id"],
            "role": "owner"
        })
        
        if owner is None:
            logger.error(f"Owner not found for tenant {product['tenant_id']}")
            return {"success": False, "error": "Owner not found"}
        
        # Build alert message
        shortage = product["low_stock_threshold"] - product["quantity"]
        message = f"""
LOW STOCK ALERT - {tenant['salon_name']}

Product: {product['name']}
Current Stock: {product['quantity']} {product['unit']}
Threshold: {product['low_stock_threshold']} {product['unit']}
Shortage: {shortage} {product['unit']}

Please reorder soon to avoid stockouts.
"""
        
        # Send alert
        success = await send_whatsapp(owner["phone"], message.strip())
        
        if success:
            logger.info(f"Low stock alert sent for product {product_id}")
            return {"success": True}
        else:
            logger.warning(f"Failed to send low stock alert for product {product_id}")
            return {"success": False, "error": "Failed to send message"}
    
    except Exception as e:
        logger.error(f"Error in send_low_stock_alert task: {e}")
        raise self.retry(exc=e, countdown=60)
