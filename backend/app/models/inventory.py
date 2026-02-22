from mongoengine import StringField, IntField, FloatField, DateTimeField, ObjectIdField, BooleanField
from datetime import datetime
from app.models.base import BaseDocument


class Inventory(BaseDocument):
    """Inventory model for tracking products and supplies"""
    tenant_id = ObjectIdField(required=True)
    name = StringField(required=True, max_length=255)
    sku = StringField(required=True, max_length=100)
    quantity = IntField(required=True, default=0, min_value=0)
    reorder_level = IntField(required=True, default=10, min_value=0)
    unit_cost = FloatField(required=True, default=0.0, min_value=0)
    unit = StringField(required=True, max_length=50, default="unit")  # e.g., "bottle", "box", "piece"
    category = StringField(max_length=100)
    supplier_id = ObjectIdField()
    last_restocked_at = DateTimeField()
    expiry_date = DateTimeField()
    is_active = BooleanField(default=True)
    notes = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'inventory',
        'indexes': [
            ('tenant_id', '_id'),
            ('tenant_id', 'sku'),
            ('tenant_id', 'quantity'),
            ('tenant_id', 'category'),
            ('tenant_id', 'is_active'),
        ]
    }


class InventoryTransaction(BaseDocument):
    """Track all inventory movements"""
    tenant_id = ObjectIdField(required=True)
    inventory_id = ObjectIdField(required=True)
    transaction_type = StringField(required=True, choices=['in', 'out', 'adjustment', 'reconciliation'])
    quantity_change = IntField(required=True)
    reason = StringField(max_length=255)
    reference_id = ObjectIdField()  # e.g., appointment_id, purchase_order_id
    reference_type = StringField(max_length=50)  # e.g., 'appointment', 'purchase_order'
    user_id = ObjectIdField()
    notes = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'inventory_transactions',
        'indexes': [
            ('tenant_id', '_id'),
            ('tenant_id', 'inventory_id'),
            ('tenant_id', 'created_at'),
            ('tenant_id', 'transaction_type'),
        ]
    }


class StockAlert(BaseDocument):
    """Track stock level alerts"""
    tenant_id = ObjectIdField(required=True)
    inventory_id = ObjectIdField(required=True)
    alert_type = StringField(required=True, choices=['low_stock', 'out_of_stock', 'overstock', 'expiry_warning'])
    current_quantity = IntField(required=True)
    threshold = IntField(required=True)
    is_resolved = BooleanField(default=False)
    resolved_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'stock_alerts',
        'indexes': [
            ('tenant_id', '_id'),
            ('tenant_id', 'inventory_id'),
            ('tenant_id', 'alert_type'),
            ('tenant_id', 'is_resolved'),
        ]
    }
