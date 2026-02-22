"""
Supplier Service - Handles supplier management and performance tracking
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from ..models.supplier import Supplier


class SupplierService:
    """Service for managing suppliers"""

    def __init__(self, db):
        self.db = db
        self.collection = db["suppliers"]
        # Create indexes
        self.collection.create_index("tenant_id")
        self.collection.create_index([("tenant_id", 1), ("name", 1)])

    async def create_supplier(
        self,
        tenant_id: str,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        contact_person: Optional[str] = None,
        payment_terms: Optional[str] = None,
    ) -> Supplier:
        """Create a new supplier"""
        supplier_data = {
            "tenant_id": tenant_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "country": country,
            "contact_person": contact_person,
            "payment_terms": payment_terms,
            "is_active": True,
            "total_orders": 0,
            "on_time_deliveries": 0,
            "on_time_delivery_rate": 0.0,
            "average_delivery_days": 0.0,
            "total_spent": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(supplier_data)
        supplier_data["_id"] = result.inserted_id

        return Supplier(**supplier_data)

    async def get_supplier(self, tenant_id: str, supplier_id: str) -> Optional[Supplier]:
        """Get a supplier by ID"""
        supplier = await self.collection.find_one({
            "_id": ObjectId(supplier_id),
            "tenant_id": tenant_id,
        })
        return Supplier(**supplier) if supplier else None

    async def get_suppliers(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Supplier], int]:
        """Get suppliers for a tenant"""
        query = {"tenant_id": tenant_id}
        if is_active is not None:
            query["is_active"] = is_active

        total_count = await self.collection.count_documents(query)

        suppliers = await self.collection.find(query).skip(skip).limit(limit).to_list(
            length=limit
        )

        return (
            [Supplier(**s) for s in suppliers],
            total_count,
        )

    async def update_supplier(
        self,
        tenant_id: str,
        supplier_id: str,
        **kwargs,
    ) -> Optional[Supplier]:
        """Update a supplier"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(supplier_id),
                "tenant_id": tenant_id,
            },
            {"$set": update_data},
            return_document=True,
        )

        return Supplier(**result) if result else None

    async def delete_supplier(self, tenant_id: str, supplier_id: str) -> bool:
        """Soft delete a supplier (mark as inactive)"""
        result = await self.collection.update_one(
            {
                "_id": ObjectId(supplier_id),
                "tenant_id": tenant_id,
            },
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return result.modified_count > 0

    async def update_performance_metrics(
        self,
        tenant_id: str,
        supplier_id: str,
        total_orders: int,
        on_time_deliveries: int,
        average_delivery_days: float,
        total_spent: float,
    ) -> Optional[Supplier]:
        """Update supplier performance metrics"""
        on_time_rate = (
            (on_time_deliveries / total_orders * 100)
            if total_orders > 0
            else 0.0
        )

        return await self.update_supplier(
            tenant_id=tenant_id,
            supplier_id=supplier_id,
            total_orders=total_orders,
            on_time_deliveries=on_time_deliveries,
            on_time_delivery_rate=on_time_rate,
            average_delivery_days=average_delivery_days,
            total_spent=total_spent,
            last_order_date=datetime.utcnow(),
        )
