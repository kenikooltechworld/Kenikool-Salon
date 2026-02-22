"""
Commission Admin API

Admin endpoints for managing commissions, viewing analytics, and generating reports.
Requires admin authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import csv
from io import StringIO

from app.database import Database
from app.services.commission_service import CommissionService
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/commissions", tags=["admin-commissions"])


# ============================================================================
# Pydantic Models
# ============================================================================

class CommissionRateUpdate(BaseModel):
    """Update commission rates"""
    commission_rate: float  # 0-100
    referral_commission_rate: float  # 0-100


class CommissionTransaction(BaseModel):
    """Commission transaction"""
    _id: str
    tenant_id: str
    booking_id: str
    booking_reference: str
    amount: float
    commission_rate: float
    commission_amount: float
    platform_fee: float
    net_amount: float
    status: str
    created_at: str


class CommissionDashboard(BaseModel):
    """Commission dashboard metrics"""
    total_commission: float
    commission_today: float
    commission_this_week: float
    commission_this_month: float
    total_bookings: int
    average_commission_per_booking: float
    top_salons: list
    commission_by_status: dict


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/dashboard", response_model=CommissionDashboard)
async def get_commission_dashboard(
    current_user = Depends(get_current_user)
):
    """
    Get commission dashboard metrics
    
    Requires admin authentication
    """
    try:
        # Check admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        db = Database.get_db()
        commission_service = CommissionService(db)
        
        # Get metrics
        metrics = await commission_service.get_dashboard_metrics()
        
        return CommissionDashboard(
            total_commission=metrics.get("total_commission", 0),
            commission_today=metrics.get("commission_today", 0),
            commission_this_week=metrics.get("commission_this_week", 0),
            commission_this_month=metrics.get("commission_this_month", 0),
            total_bookings=metrics.get("total_bookings", 0),
            average_commission_per_booking=metrics.get("average_commission_per_booking", 0),
            top_salons=metrics.get("top_salons", []),
            commission_by_status=metrics.get("commission_by_status", {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting commission dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
async def get_commission_transactions(
    tenant_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """
    Get paginated commission transactions
    
    Supports filtering by tenant, date range, and status
    """
    try:
        # Check admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        db = Database.get_db()
        
        query = {}
        
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        if date_from and date_to:
            query["created_at"] = {
                "$gte": datetime.fromisoformat(date_from),
                "$lte": datetime.fromisoformat(date_to)
            }
        
        if status:
            query["status"] = status
        
        transactions = list(
            db.commission_transactions.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for transaction in transactions:
            transaction["_id"] = str(transaction["_id"])
        
        total = db.commission_transactions.count_documents(query)
        
        return {
            "transactions": transactions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting commission transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rates/{tenant_id}")
async def update_commission_rates(
    tenant_id: str,
    rates: CommissionRateUpdate,
    current_user = Depends(get_current_user)
):
    """
    Update commission rates for a salon
    
    Requires admin authentication
    """
    try:
        # Check admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate rates
        if not (0 <= rates.commission_rate <= 100):
            raise HTTPException(status_code=400, detail="Commission rate must be between 0 and 100")
        
        if not (0 <= rates.referral_commission_rate <= 100):
            raise HTTPException(status_code=400, detail="Referral commission rate must be between 0 and 100")
        
        db = Database.get_db()
        
        # Update tenant commission rates
        result = db.tenants.update_one(
            {"_id": tenant_id},
            {
                "$set": {
                    "commission_rate": rates.commission_rate / 100,  # Convert to decimal
                    "referral_commission_rate": rates.referral_commission_rate / 100,
                    "commission_updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Log the change
        db.commission_audit_log.insert_one({
            "tenant_id": tenant_id,
            "updated_by": current_user.get("_id"),
            "old_commission_rate": None,  # TODO: Get old rate
            "new_commission_rate": rates.commission_rate / 100,
            "old_referral_rate": None,  # TODO: Get old rate
            "new_referral_rate": rates.referral_commission_rate / 100,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "message": "Commission rates updated successfully",
            "tenant_id": tenant_id,
            "commission_rate": rates.commission_rate,
            "referral_commission_rate": rates.referral_commission_rate
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating commission rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_commission_report(
    date_from: str,
    date_to: str,
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user = Depends(get_current_user)
):
    """
    Export commission report
    
    Supports CSV and JSON formats
    """
    try:
        # Check admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        db = Database.get_db()
        
        # Get transactions for date range
        transactions = list(
            db.commission_transactions.find({
                "created_at": {
                    "$gte": datetime.fromisoformat(date_from),
                    "$lte": datetime.fromisoformat(date_to)
                }
            }).sort("created_at", -1)
        )
        
        if format == "csv":
            # Generate CSV
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "booking_reference",
                    "tenant_id",
                    "amount",
                    "commission_rate",
                    "commission_amount",
                    "platform_fee",
                    "net_amount",
                    "status",
                    "created_at"
                ]
            )
            
            writer.writeheader()
            for transaction in transactions:
                writer.writerow({
                    "booking_reference": transaction.get("booking_reference"),
                    "tenant_id": transaction.get("tenant_id"),
                    "amount": transaction.get("amount"),
                    "commission_rate": transaction.get("commission_rate"),
                    "commission_amount": transaction.get("commission_amount"),
                    "platform_fee": transaction.get("platform_fee"),
                    "net_amount": transaction.get("net_amount"),
                    "status": transaction.get("status"),
                    "created_at": transaction.get("created_at")
                })
            
            return {
                "format": "csv",
                "data": output.getvalue(),
                "filename": f"commission_report_{date_from}_to_{date_to}.csv"
            }
        
        else:  # JSON format
            # Convert ObjectId to string
            for transaction in transactions:
                transaction["_id"] = str(transaction["_id"])
            
            return {
                "format": "json",
                "data": transactions,
                "filename": f"commission_report_{date_from}_to_{date_to}.json"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting commission report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salons/{tenant_id}/summary")
async def get_salon_commission_summary(
    tenant_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get commission summary for a specific salon
    """
    try:
        # Check admin role
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        db = Database.get_db()
        
        # Get salon info
        salon = db.tenants.find_one({"_id": tenant_id})
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        
        # Get commission transactions
        transactions = list(
            db.commission_transactions.find({"tenant_id": tenant_id})
        )
        
        # Calculate summary
        total_commission = sum(t.get("commission_amount", 0) for t in transactions)
        total_platform_fee = sum(t.get("platform_fee", 0) for t in transactions)
        total_net = sum(t.get("net_amount", 0) for t in transactions)
        
        # Group by status
        by_status = {}
        for transaction in transactions:
            status = transaction.get("status", "unknown")
            if status not in by_status:
                by_status[status] = 0
            by_status[status] += transaction.get("commission_amount", 0)
        
        return {
            "tenant_id": tenant_id,
            "salon_name": salon.get("name"),
            "commission_rate": salon.get("commission_rate", 0.10),
            "total_transactions": len(transactions),
            "total_commission": total_commission,
            "total_platform_fee": total_platform_fee,
            "total_net": total_net,
            "by_status": by_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting salon commission summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
