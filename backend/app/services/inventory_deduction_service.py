"""Service for managing inventory deduction in POS transactions."""

from typing import List, Optional
from bson import ObjectId
from app.models.inventory import Inventory, InventoryTransaction
from app.models.transaction import TransactionItem


class InventoryDeductionService:
    """Service for inventory deduction and management."""

    @staticmethod
    def deduct_inventory(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        items: List[TransactionItem],
    ) -> bool:
        """
        Deduct inventory for transaction items.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            items: List of TransactionItem objects

        Returns:
            True if successful, raises exception otherwise

        Raises:
            ValueError: If inventory is insufficient
        """
        # First, check availability for all items
        for item in items:
            if item.item_type == "product":
                inventory = Inventory.objects(
                    tenant_id=tenant_id,
                    name=item.item_name
                ).first()

                if not inventory or inventory.quantity < item.quantity:
                    raise ValueError(
                        f"Insufficient inventory for product {item.item_name}. "
                        f"Available: {inventory.quantity if inventory else 0}, "
                        f"Requested: {item.quantity}"
                    )

        # Deduct inventory for all items
        for item in items:
            if item.item_type == "product":
                inventory = Inventory.objects(
                    tenant_id=tenant_id,
                    name=item.item_name
                ).first()

                if inventory:
                    # Deduct inventory
                    inventory.quantity -= item.quantity
                    inventory.save()

                    # Create inventory transaction record
                    transaction = InventoryTransaction(
                        tenant_id=tenant_id,
                        inventory_id=inventory.id,
                        transaction_type="out",
                        quantity_change=-item.quantity,
                        reason="POS Sale",
                        reference_id=transaction_id,
                        reference_type="transaction",
                    )
                    transaction.save()

                    # Check for low stock
                    if inventory.quantity <= inventory.reorder_level:
                        InventoryDeductionService.generate_low_stock_alert(
                            tenant_id, inventory.id
                        )

        return True

    @staticmethod
    def restore_inventory(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
    ) -> bool:
        """
        Restore inventory when transaction is refunded.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID

        Returns:
            True if successful
        """
        # Find all inventory transactions for this transaction
        transactions = InventoryTransaction.objects(
            tenant_id=tenant_id,
            reference_id=transaction_id,
            reference_type="transaction",
            transaction_type="out"
        )

        for inv_transaction in transactions:
            # Reverse the transaction
            inventory = Inventory.objects(
                tenant_id=tenant_id,
                id=inv_transaction.inventory_id
            ).first()

            if inventory:
                # Restore inventory (reverse the negative quantity)
                inventory.quantity -= inv_transaction.quantity_change  # quantity_change is negative
                inventory.save()

                # Create reverse transaction record
                reverse_transaction = InventoryTransaction(
                    tenant_id=tenant_id,
                    inventory_id=inventory.id,
                    transaction_type="in",
                    quantity_change=-inv_transaction.quantity_change,  # Positive quantity for refund
                    reason="POS Refund",
                    reference_id=transaction_id,
                    reference_type="transaction",
                )
                reverse_transaction.save()

        return True

    @staticmethod
    def check_inventory_availability(
        tenant_id: ObjectId,
        product_id: ObjectId,
        quantity: int,
    ) -> bool:
        """
        Check if inventory is available for a product.

        Args:
            tenant_id: Tenant ID
            product_id: Product ID
            quantity: Quantity to check

        Returns:
            True if available, False otherwise
        """
        inventory = Inventory.objects(
            tenant_id=tenant_id,
            id=product_id
        ).first()

        if not inventory:
            return False

        return inventory.quantity >= quantity

    @staticmethod
    def generate_low_stock_alert(
        tenant_id: ObjectId,
        inventory_id: ObjectId,
    ) -> None:
        """
        Generate low stock alert for a product.

        Args:
            tenant_id: Tenant ID
            inventory_id: Inventory ID
        """
        from app.models.inventory import StockAlert

        inventory = Inventory.objects(
            tenant_id=tenant_id,
            id=inventory_id
        ).first()

        if inventory:
            # Check if alert already exists
            existing_alert = StockAlert.objects(
                tenant_id=tenant_id,
                inventory_id=inventory_id,
                alert_type="low_stock",
                is_resolved=False
            ).first()

            if not existing_alert:
                # Create new alert
                alert = StockAlert(
                    tenant_id=tenant_id,
                    inventory_id=inventory_id,
                    alert_type="low_stock",
                    current_quantity=inventory.quantity,
                    threshold=inventory.reorder_level,
                )
                alert.save()

    @staticmethod
    def get_inventory_status(
        tenant_id: ObjectId,
        inventory_id: ObjectId,
    ) -> Optional[dict]:
        """
        Get inventory status for a product.

        Args:
            tenant_id: Tenant ID
            inventory_id: Inventory ID

        Returns:
            Dictionary with inventory status or None if not found
        """
        inventory = Inventory.objects(
            tenant_id=tenant_id,
            id=inventory_id
        ).first()

        if not inventory:
            return None

        return {
            "inventory_id": str(inventory_id),
            "name": inventory.name,
            "quantity": inventory.quantity,
            "reorder_level": inventory.reorder_level,
            "is_low_stock": inventory.quantity <= inventory.reorder_level,
        }
