"""
Purchase Order Service - Handles purchase order management
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from ..models.purchase_order import (
    PurchaseOrder,
    POStatus,
    POLineItem,
)


class PurchaseOrderService:
    """Service for managing purchase orders"""

    def __init__(self, db):
        self.db = db
        self.collection = db["purchase_orders"]
        # Create indexes
        self.collection.create_index("tenant_id")
        self.collection.create_index("po_number")
        self.collection.create_index([("tenant_id", 1), ("status", 1)])
        self.collection.create_index([("tenant_id", 1), ("supplier_id", 1)])

    async def generate_po_number(self, tenant_id: str) -> str:
        """Generate a unique PO number"""
        # Get the last PO number for this tenant
        last_po = await self.collection.find_one(
            {"tenant_id": tenant_id},
            sort=[("created_at", -1)],
        )

        if last_po and "po_number" in last_po:
            # Extract number from last PO
            last_number = int(last_po["po_number"].split("-")[-1])
            next_number = last_number + 1
        else:
            next_number = 1

        year = datetime.utcnow().year
        return f"PO-{year}-{next_number:04d}"

    async def create_purchase_order(
        self,
        tenant_id: str,
        supplier_id: str,
        supplier_name: str,
        line_items: List[Dict[str, Any]],
        created_by: str,
        expected_delivery_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        tax_amount: float = 0.0,
        shipping_cost: float = 0.0,
    ) -> PurchaseOrder:
        """Create a new purchase order"""
        po_number = await self.generate_po_number(tenant_id)

        # Calculate totals
        subtotal = sum(item["total_price"] for item in line_items)
        total_amount = subtotal + tax_amount + shipping_cost

        po_data = {
            "tenant_id": tenant_id,
            "po_number": po_number,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "status": POStatus.DRAFT.value,
            "line_items": line_items,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "total_amount": total_amount,
            "expected_delivery_date": expected_delivery_date,
            "notes": notes,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(po_data)
        po_data["_id"] = result.inserted_id

        return PurchaseOrder(**po_data)

    async def get_purchase_order(
        self,
        tenant_id: str,
        po_id: str,
    ) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID"""
        po = await self.collection.find_one({
            "_id": ObjectId(po_id),
            "tenant_id": tenant_id,
        })
        return PurchaseOrder(**po) if po else None

    async def get_purchase_orders(
        self,
        tenant_id: str,
        status: Optional[POStatus] = None,
        supplier_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[PurchaseOrder], int]:
        """Get purchase orders with optional filtering"""
        query = {"tenant_id": tenant_id}
        if status:
            query["status"] = status.value
        if supplier_id:
            query["supplier_id"] = supplier_id

        total_count = await self.collection.count_documents(query)

        pos = await self.collection.find(query).sort(
            "created_at", -1
        ).skip(skip).limit(limit).to_list(length=limit)

        return (
            [PurchaseOrder(**po) for po in pos],
            total_count,
        )

    async def update_purchase_order(
        self,
        tenant_id: str,
        po_id: str,
        **kwargs,
    ) -> Optional[PurchaseOrder]:
        """Update a purchase order"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(po_id),
                "tenant_id": tenant_id,
            },
            {"$set": update_data},
            return_document=True,
        )

        return PurchaseOrder(**result) if result else None

    async def send_purchase_order(
        self,
        tenant_id: str,
        po_id: str,
    ) -> Optional[PurchaseOrder]:
        """Mark PO as sent"""
        return await self.update_purchase_order(
            tenant_id=tenant_id,
            po_id=po_id,
            status=POStatus.SENT.value,
            sent_at=datetime.utcnow(),
        )

    async def receive_purchase_order(
        self,
        tenant_id: str,
        po_id: str,
        received_items: Optional[Dict[str, int]] = None,
    ) -> Optional[PurchaseOrder]:
        """Mark PO as received (fully or partially)"""
        po = await self.get_purchase_order(tenant_id, po_id)
        if not po:
            return None

        # Update line items with received quantities
        if received_items:
            for item in po.line_items:
                if item.product_id in received_items:
                    item.quantity_received = received_items[item.product_id]

        # Determine status
        all_received = all(
            item.quantity_received == item.quantity_ordered
            for item in po.line_items
        )
        status = POStatus.RECEIVED if all_received else POStatus.PARTIAL

        return await self.update_purchase_order(
            tenant_id=tenant_id,
            po_id=po_id,
            status=status.value,
            received_at=datetime.utcnow(),
            line_items=[item.dict() for item in po.line_items],
        )

    async def cancel_purchase_order(
        self,
        tenant_id: str,
        po_id: str,
    ) -> Optional[PurchaseOrder]:
        """Cancel a purchase order"""
        return await self.update_purchase_order(
            tenant_id=tenant_id,
            po_id=po_id,
            status=POStatus.CANCELLED.value,
        )
