from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    InventoryTransactionCreate, InventoryTransactionResponse, StockAlertResponse,
    InventoryReconciliationRequest, InventoryReconciliationResponse,
    InventoryValueResponse,
)
from app.services.inventory_service import InventoryService
from app.decorators.tenant_isolated import tenant_isolated

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", response_model=InventoryResponse)
@tenant_isolated
async def create_inventory(data: InventoryCreate):
    """Create new inventory item"""
    try:
        inventory = InventoryService.create_inventory(
            name=data.name,
            sku=data.sku,
            quantity=data.quantity,
            reorder_level=data.reorder_level,
            unit_cost=data.unit_cost,
            unit=data.unit,
            category=data.category,
            supplier_id=data.supplier_id,
            expiry_date=data.expiry_date,
            notes=data.notes,
        )
        return InventoryResponse.from_orm(inventory)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{inventory_id}", response_model=InventoryResponse)
@tenant_isolated
async def get_inventory(inventory_id: str):
    """Get inventory by ID"""
    inventory = InventoryService.get_inventory(inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return InventoryResponse.from_orm(inventory)


@router.get("", response_model=dict)
@tenant_isolated
async def list_inventory(
    category: Optional[str] = Query(None),
    is_active: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List inventory items"""
    items, total = InventoryService.list_inventory(
        category=category,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [InventoryResponse.from_orm(item) for item in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.put("/{inventory_id}", response_model=InventoryResponse)
@tenant_isolated
async def update_inventory(inventory_id: str, data: InventoryUpdate):
    """Update inventory item"""
    try:
        inventory = InventoryService.update_inventory(
            inventory_id=inventory_id,
            **data.dict(exclude_unset=True),
        )
        return InventoryResponse.from_orm(inventory)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{inventory_id}/deduct", response_model=InventoryTransactionResponse)
@tenant_isolated
async def deduct_inventory(
    inventory_id: str,
    data: InventoryTransactionCreate,
):
    """Deduct inventory"""
    try:
        transaction = InventoryService.deduct_inventory(
            inventory_id=inventory_id,
            quantity=data.quantity,
            reason=data.reason,
            reference_id=data.reference_id,
            reference_type=data.reference_type or "appointment",
        )
        return InventoryTransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{inventory_id}/restock", response_model=InventoryTransactionResponse)
@tenant_isolated
async def restock_inventory(
    inventory_id: str,
    data: InventoryTransactionCreate,
):
    """Restock inventory"""
    try:
        transaction = InventoryService.restock_inventory(
            inventory_id=inventory_id,
            quantity=data.quantity,
        )
        return InventoryTransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{inventory_id}/adjust", response_model=InventoryTransactionResponse)
@tenant_isolated
async def adjust_inventory(
    inventory_id: str,
    data: InventoryTransactionCreate,
):
    """Adjust inventory"""
    try:
        transaction = InventoryService.adjust_inventory(
            inventory_id=inventory_id,
            quantity_change=data.quantity if data.reason.startswith('+') else -data.quantity,
            reason=data.reason,
        )
        return InventoryTransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/list", response_model=dict)
@tenant_isolated
async def get_transactions(
    inventory_id: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get inventory transactions"""
    transactions, total = InventoryService.get_inventory_transactions(
        inventory_id=inventory_id,
        transaction_type=transaction_type,
        skip=skip,
        limit=limit,
    )
    return {
        "transactions": [InventoryTransactionResponse.from_orm(t) for t in transactions],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/{inventory_id}/reconcile", response_model=InventoryReconciliationResponse)
@tenant_isolated
async def reconcile_inventory(
    inventory_id: str,
    data: InventoryReconciliationRequest,
):
    """Reconcile inventory with physical count"""
    try:
        result = InventoryService.reconcile_inventory(
            inventory_id=inventory_id,
            physical_count=data.physical_count,
            notes=data.notes,
        )
        return InventoryReconciliationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/alerts/list", response_model=dict)
@tenant_isolated
async def get_stock_alerts(
    is_resolved: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get stock alerts"""
    alerts, total = InventoryService.get_stock_alerts(
        is_resolved=is_resolved,
        skip=skip,
        limit=limit,
    )
    return {
        "alerts": [StockAlertResponse.from_orm(alert) for alert in alerts],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/low-stock/list", response_model=dict)
@tenant_isolated
async def get_low_stock_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get low stock items"""
    items, total = InventoryService.get_low_stock_items(skip=skip, limit=limit)
    return {
        "items": [InventoryResponse.from_orm(item) for item in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/value/summary", response_model=InventoryValueResponse)
@tenant_isolated
async def get_inventory_value():
    """Get total inventory value"""
    return InventoryService.get_inventory_value()
