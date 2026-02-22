from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.inventory import Inventory, InventoryTransaction, StockAlert
from app.models.appointment import Appointment
from app.context import get_tenant_id
from mongoengine import Q


class InventoryService:
    """Service for inventory management"""

    @staticmethod
    def create_inventory(
        name: str,
        sku: str,
        quantity: int,
        reorder_level: int,
        unit_cost: float,
        unit: str = "unit",
        category: Optional[str] = None,
        supplier_id: Optional[str] = None,
        expiry_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Inventory:
        """Create new inventory item"""
        tenant_id = get_tenant_id()
        
        # Check for duplicate SKU
        existing = Inventory.objects(tenant_id=tenant_id, sku=sku).first()
        if existing:
            raise ValueError(f"SKU {sku} already exists")
        
        inventory = Inventory(
            tenant_id=tenant_id,
            name=name,
            sku=sku,
            quantity=quantity,
            reorder_level=reorder_level,
            unit_cost=unit_cost,
            unit=unit,
            category=category,
            supplier_id=supplier_id,
            expiry_date=expiry_date,
            notes=notes,
        )
        inventory.save()
        return inventory

    @staticmethod
    def get_inventory(inventory_id: str) -> Optional[Inventory]:
        """Get inventory by ID"""
        tenant_id = get_tenant_id()
        return Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()

    @staticmethod
    def list_inventory(
        category: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Inventory], int]:
        """List inventory items"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, is_active=is_active)
        
        if category:
            query &= Q(category=category)
        
        total = Inventory.objects(query).count()
        items = Inventory.objects(query).skip(skip).limit(limit)
        
        return list(items), total

    @staticmethod
    def update_inventory(
        inventory_id: str,
        **kwargs
    ) -> Inventory:
        """Update inventory item"""
        tenant_id = get_tenant_id()
        inventory = Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()
        
        if not inventory:
            raise ValueError("Inventory not found")
        
        # Don't allow direct quantity updates (use transactions instead)
        if 'quantity' in kwargs:
            del kwargs['quantity']
        
        kwargs['updated_at'] = datetime.utcnow()
        inventory.update(**kwargs)
        return inventory.reload()

    @staticmethod
    def deduct_inventory(
        inventory_id: str,
        quantity: int,
        reason: str = "service_completion",
        reference_id: Optional[str] = None,
        reference_type: str = "appointment",
    ) -> InventoryTransaction:
        """Deduct inventory (e.g., when service is completed)"""
        tenant_id = get_tenant_id()
        inventory = Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()
        
        if not inventory:
            raise ValueError("Inventory not found")
        
        if inventory.quantity < quantity:
            raise ValueError(f"Insufficient inventory. Available: {inventory.quantity}, Requested: {quantity}")
        
        # Create transaction
        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            inventory_id=inventory.id,
            transaction_type='out',
            quantity_change=-quantity,
            reason=reason,
            reference_id=reference_id,
            reference_type=reference_type,
        )
        transaction.save()
        
        # Update inventory
        inventory.quantity -= quantity
        inventory.updated_at = datetime.utcnow()
        inventory.save()
        
        # Check for low stock alert
        if inventory.quantity <= inventory.reorder_level:
            InventoryService._create_stock_alert(
                inventory_id=inventory.id,
                alert_type='low_stock' if inventory.quantity > 0 else 'out_of_stock',
                current_quantity=inventory.quantity,
                threshold=inventory.reorder_level,
            )
        
        return transaction

    @staticmethod
    def restock_inventory(
        inventory_id: str,
        quantity: int,
        supplier_id: Optional[str] = None,
    ) -> InventoryTransaction:
        """Restock inventory"""
        tenant_id = get_tenant_id()
        inventory = Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()
        
        if not inventory:
            raise ValueError("Inventory not found")
        
        # Create transaction
        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            inventory_id=inventory.id,
            transaction_type='in',
            quantity_change=quantity,
            reason='restock',
        )
        transaction.save()
        
        # Update inventory
        inventory.quantity += quantity
        inventory.last_restocked_at = datetime.utcnow()
        inventory.updated_at = datetime.utcnow()
        inventory.save()
        
        # Resolve low stock alerts
        StockAlert.objects(
            tenant_id=tenant_id,
            inventory_id=inventory.id,
            alert_type__in=['low_stock', 'out_of_stock'],
            is_resolved=False,
        ).update(is_resolved=True, resolved_at=datetime.utcnow())
        
        return transaction

    @staticmethod
    def adjust_inventory(
        inventory_id: str,
        quantity_change: int,
        reason: str,
    ) -> InventoryTransaction:
        """Adjust inventory (for reconciliation or corrections)"""
        tenant_id = get_tenant_id()
        inventory = Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()
        
        if not inventory:
            raise ValueError("Inventory not found")
        
        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(f"Adjustment would result in negative quantity")
        
        # Create transaction
        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            inventory_id=inventory.id,
            transaction_type='adjustment',
            quantity_change=quantity_change,
            reason=reason,
        )
        transaction.save()
        
        # Update inventory
        inventory.quantity = new_quantity
        inventory.updated_at = datetime.utcnow()
        inventory.save()
        
        return transaction

    @staticmethod
    def get_inventory_transactions(
        inventory_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[InventoryTransaction], int]:
        """Get inventory transactions"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id)
        
        if inventory_id:
            query &= Q(inventory_id=inventory_id)
        
        if transaction_type:
            query &= Q(transaction_type=transaction_type)
        
        total = InventoryTransaction.objects(query).count()
        transactions = InventoryTransaction.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(transactions), total

    @staticmethod
    def _create_stock_alert(
        inventory_id: str,
        alert_type: str,
        current_quantity: int,
        threshold: int,
    ) -> StockAlert:
        """Create stock alert"""
        tenant_id = get_tenant_id()
        
        # Check if alert already exists
        existing = StockAlert.objects(
            tenant_id=tenant_id,
            inventory_id=inventory_id,
            alert_type=alert_type,
            is_resolved=False,
        ).first()
        
        if existing:
            return existing
        
        alert = StockAlert(
            tenant_id=tenant_id,
            inventory_id=inventory_id,
            alert_type=alert_type,
            current_quantity=current_quantity,
            threshold=threshold,
        )
        alert.save()
        return alert

    @staticmethod
    def get_stock_alerts(
        is_resolved: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[StockAlert], int]:
        """Get stock alerts"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, is_resolved=is_resolved)
        
        total = StockAlert.objects(query).count()
        alerts = StockAlert.objects(query).order_by('-created_at').skip(skip).limit(limit)
        
        return list(alerts), total

    @staticmethod
    def reconcile_inventory(
        inventory_id: str,
        physical_count: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reconcile inventory with physical count"""
        tenant_id = get_tenant_id()
        inventory = Inventory.objects(tenant_id=tenant_id, id=inventory_id).first()
        
        if not inventory:
            raise ValueError("Inventory not found")
        
        system_count = inventory.quantity
        discrepancy = physical_count - system_count
        
        if discrepancy != 0:
            # Create adjustment transaction
            InventoryService.adjust_inventory(
                inventory_id=inventory_id,
                quantity_change=discrepancy,
                reason=f"reconciliation: {notes or 'physical count'}",
            )
        
        return {
            "inventory_id": str(inventory.id),
            "system_count": system_count,
            "physical_count": physical_count,
            "discrepancy": discrepancy,
            "reconciled_at": datetime.utcnow(),
        }

    @staticmethod
    def get_low_stock_items(skip: int = 0, limit: int = 100) -> tuple[List[Inventory], int]:
        """Get items with low stock"""
        tenant_id = get_tenant_id()
        query = Q(tenant_id=tenant_id, is_active=True)
        
        # Get items where quantity <= reorder_level
        items = Inventory.objects(query)
        low_stock_items = [item for item in items if item.quantity <= item.reorder_level]
        
        total = len(low_stock_items)
        return low_stock_items[skip:skip+limit], total

    @staticmethod
    def get_inventory_value() -> Dict[str, Any]:
        """Calculate total inventory value"""
        tenant_id = get_tenant_id()
        items = Inventory.objects(tenant_id=tenant_id, is_active=True)
        
        total_value = sum(item.quantity * item.unit_cost for item in items)
        total_items = sum(item.quantity for item in items)
        
        return {
            "total_value": total_value,
            "total_items": total_items,
            "item_count": len(list(items)),
        }
