"""
Fixed Assets Management Service

Handles fixed asset management including:
- Asset CRUD operations
- Depreciation calculations and posting
- Asset disposal
- Depreciation schedules
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import uuid
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class FixedAssetsService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.fixed_assets = db.fixed_assets
        self.depreciation_entries = db.depreciation_entries
        self.asset_disposals = db.asset_disposals
        self.journal_entries = db.journal_entries
        self.accounts = db.accounts

    def get_fixed_assets(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get fixed assets with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        
        assets = list(
            self.fixed_assets.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string and calculate current values
        for asset in assets:
            asset["id"] = str(asset["_id"])
            del asset["_id"]
            
            # Calculate current depreciation and book value
            self._calculate_current_values(asset)
        
        return assets

    def create_fixed_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new fixed asset"""
        
        # Generate asset number
        asset_number = self._get_next_asset_number()
        
        # Calculate monthly depreciation
        monthly_depreciation = self._calculate_monthly_depreciation(asset_data)
        
        asset_doc = {
            "tenant_id": self.tenant_id,
            "asset_number": asset_number,
            "name": asset_data["name"],
            "description": asset_data.get("description"),
            "category": asset_data["category"],
            "purchase_date": asset_data["purchase_date"],
            "purchase_price": float(asset_data["purchase_price"]),
            "salvage_value": float(asset_data.get("salvage_value", 0.0)),
            "useful_life_years": int(asset_data["useful_life_years"]),
            "useful_life_units": asset_data.get("useful_life_units"),
            "depreciation_method": asset_data["depreciation_method"],
            "location": asset_data.get("location"),
            "serial_number": asset_data.get("serial_number"),
            "vendor_id": asset_data.get("vendor_id"),
            "currency_code": asset_data.get("currency_code", "USD"),
            "status": "active",
            "accumulated_depreciation": 0.0,
            "book_value": float(asset_data["purchase_price"]),
            "monthly_depreciation": monthly_depreciation,
            "created_by": asset_data.get("created_by", "system"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.fixed_assets.insert_one(asset_doc)
        asset_doc["id"] = str(result.inserted_id)
        del asset_doc["_id"]
        
        return asset_doc

    def get_fixed_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get a specific fixed asset by ID"""
        
        asset = self.fixed_assets.find_one({
            "_id": ObjectId(asset_id),
            "tenant_id": self.tenant_id
        })
        
        if not asset:
            raise ValueError("Fixed asset not found")
        
        asset["id"] = str(asset["_id"])
        del asset["_id"]
        
        # Calculate current values
        self._calculate_current_values(asset)
        
        # Get depreciation entries
        depreciation_entries = list(
            self.depreciation_entries.find({
                "asset_id": asset_id,
                "tenant_id": self.tenant_id
            }).sort("depreciation_date", 1)
        )
        
        for entry in depreciation_entries:
            entry["id"] = str(entry["_id"])
            del entry["_id"]
        
        asset["depreciation_entries"] = depreciation_entries
        
        return asset

    def update_fixed_asset(
        self, 
        asset_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a fixed asset"""
        
        update_fields = {}
        
        allowed_fields = [
            "name", "description", "category", "location", 
            "serial_number", "status"
        ]
        
        for field in allowed_fields:
            if field in update_data:
                update_fields[field] = update_data[field]
        
        update_fields["updated_at"] = datetime.utcnow()
        
        self.fixed_assets.update_one(
            {"_id": ObjectId(asset_id), "tenant_id": self.tenant_id},
            {"$set": update_fields}
        )
        
        return self.get_fixed_asset(asset_id)

    def post_depreciation(
        self, 
        asset_id: str, 
        depreciation_date: str,
        posted_by: str = "system"
    ) -> Dict[str, Any]:
        """Post depreciation for a specific asset"""
        
        asset = self.get_fixed_asset(asset_id)
        
        if asset["status"] != "active":
            raise ValueError("Cannot depreciate inactive asset")
        
        # Calculate depreciation amount
        depreciation_amount = self._calculate_depreciation_for_period(
            asset, depreciation_date
        )
        
        if depreciation_amount <= 0:
            return {"message": "No depreciation to post", "amount": 0}
        
        # Create depreciation entry
        depreciation_entry = {
            "tenant_id": self.tenant_id,
            "asset_id": asset_id,
            "depreciation_date": depreciation_date,
            "depreciation_amount": depreciation_amount,
            "accumulated_depreciation": asset["accumulated_depreciation"] + depreciation_amount,
            "book_value": asset["book_value"] - depreciation_amount,
            "posted_by": posted_by,
            "created_at": datetime.utcnow()
        }
        
        # Create journal entry for depreciation
        journal_entry_id = self._create_depreciation_journal_entry(
            asset, depreciation_amount, depreciation_date
        )
        
        if journal_entry_id:
            depreciation_entry["journal_entry_id"] = journal_entry_id
        
        # Insert depreciation entry
        result = self.depreciation_entries.insert_one(depreciation_entry)
        depreciation_entry["id"] = str(result.inserted_id)
        del depreciation_entry["_id"]
        
        # Update asset accumulated depreciation and book value
        new_accumulated = asset["accumulated_depreciation"] + depreciation_amount
        new_book_value = asset["purchase_price"] - new_accumulated
        
        # Check if fully depreciated
        status = asset["status"]
        if new_book_value <= asset["salvage_value"]:
            status = "fully_depreciated"
        
        self.fixed_assets.update_one(
            {"_id": ObjectId(asset_id)},
            {
                "$set": {
                    "accumulated_depreciation": new_accumulated,
                    "book_value": new_book_value,
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "asset_id": asset_id,
            "depreciation_amount": depreciation_amount,
            "accumulated_depreciation": new_accumulated,
            "book_value": new_book_value,
            "journal_entry_id": journal_entry_id,
            "depreciation_entry": depreciation_entry
        }

    def dispose_asset(
        self, 
        asset_id: str, 
        disposal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispose of a fixed asset"""
        
        asset = self.get_fixed_asset(asset_id)
        
        if asset["status"] == "disposed":
            raise ValueError("Asset is already disposed")
        
        disposal_price = float(disposal_data["disposal_price"])
        book_value_at_disposal = asset["book_value"]
        gain_loss_amount = disposal_price - book_value_at_disposal
        
        disposal_doc = {
            "tenant_id": self.tenant_id,
            "asset_id": asset_id,
            "disposal_date": disposal_data["disposal_date"],
            "disposal_price": disposal_price,
            "disposal_method": disposal_data["disposal_method"],
            "book_value_at_disposal": book_value_at_disposal,
            "gain_loss_amount": gain_loss_amount,
            "is_gain": gain_loss_amount > 0,
            "notes": disposal_data.get("notes"),
            "disposed_by": disposal_data.get("disposed_by", "system"),
            "created_at": datetime.utcnow()
        }
        
        # Create journal entry for disposal
        journal_entry_id = self._create_disposal_journal_entry(
            asset, disposal_data, gain_loss_amount
        )
        
        if journal_entry_id:
            disposal_doc["journal_entry_id"] = journal_entry_id
        
        # Insert disposal record
        result = self.asset_disposals.insert_one(disposal_doc)
        disposal_doc["id"] = str(result.inserted_id)
        del disposal_doc["_id"]
        
        # Update asset status
        self.fixed_assets.update_one(
            {"_id": ObjectId(asset_id)},
            {
                "$set": {
                    "status": "disposed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return disposal_doc

    def get_depreciation_schedule(
        self, 
        asset_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get depreciation schedule for assets"""
        
        query = {"tenant_id": self.tenant_id, "status": {"$in": ["active", "fully_depreciated"]}}
        
        if asset_id:
            query["_id"] = ObjectId(asset_id)
        if category:
            query["category"] = category
        
        assets = list(self.fixed_assets.find(query))
        schedules = []
        
        for asset in assets:
            asset["id"] = str(asset["_id"])
            del asset["_id"]
            
            schedule = self._generate_depreciation_schedule(asset)
            schedules.append({
                "asset_id": asset["id"],
                "asset_name": asset["name"],
                "schedule": schedule,
                "total_depreciation": asset["purchase_price"] - asset["salvage_value"],
                "remaining_book_value": asset["book_value"]
            })
        
        return schedules

    def post_bulk_depreciation(self, posting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post depreciation for multiple assets"""
        
        asset_ids = posting_data.get("asset_ids")
        depreciation_date = posting_data["depreciation_date"]
        posted_by = posting_data.get("posted_by", "system")
        
        query = {"tenant_id": self.tenant_id, "status": "active"}
        if asset_ids:
            query["_id"] = {"$in": [ObjectId(aid) for aid in asset_ids]}
        
        assets = list(self.fixed_assets.find(query))
        
        posted_count = 0
        total_depreciation_amount = 0.0
        journal_entry_ids = []
        failed_assets = []
        
        for asset in assets:
            try:
                result = self.post_depreciation(
                    str(asset["_id"]), 
                    depreciation_date, 
                    posted_by
                )
                
                if result.get("depreciation_amount", 0) > 0:
                    posted_count += 1
                    total_depreciation_amount += result["depreciation_amount"]
                    if result.get("journal_entry_id"):
                        journal_entry_ids.append(result["journal_entry_id"])
                
            except Exception as e:
                failed_assets.append({
                    "asset_id": str(asset["_id"]),
                    "asset_name": asset["name"],
                    "error": str(e)
                })
        
        return {
            "posted_count": posted_count,
            "total_depreciation_amount": total_depreciation_amount,
            "journal_entry_ids": journal_entry_ids,
            "failed_assets": failed_assets,
            "posting_date": depreciation_date
        }

    def get_assets_summary(self) -> Dict[str, Any]:
        """Get fixed assets summary for the tenant"""
        
        # Get asset counts by status
        pipeline = [
            {"$match": {"tenant_id": self.tenant_id}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_cost": {"$sum": "$purchase_price"},
                "total_accumulated_depreciation": {"$sum": "$accumulated_depreciation"},
                "total_book_value": {"$sum": "$book_value"}
            }}
        ]
        
        status_summary = list(self.fixed_assets.aggregate(pipeline))
        
        # Get category breakdown
        category_pipeline = [
            {"$match": {"tenant_id": self.tenant_id}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "total_cost": {"$sum": "$purchase_price"},
                "total_book_value": {"$sum": "$book_value"}
            }},
            {"$sort": {"total_cost": -1}}
        ]
        
        category_summary = list(self.fixed_assets.aggregate(category_pipeline))
        
        # Calculate totals
        total_assets = self.fixed_assets.count_documents({"tenant_id": self.tenant_id})
        active_assets = self.fixed_assets.count_documents({
            "tenant_id": self.tenant_id,
            "status": "active"
        })
        
        # Get recent depreciation activity
        recent_depreciation = list(
            self.depreciation_entries.find({"tenant_id": self.tenant_id})
            .sort("created_at", -1)
            .limit(5)
        )
        
        for entry in recent_depreciation:
            entry["id"] = str(entry["_id"])
            del entry["_id"]
        
        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "status_breakdown": status_summary,
            "category_breakdown": category_summary,
            "recent_depreciation": recent_depreciation
        }

    def _get_next_asset_number(self) -> str:
        """Generate the next asset number"""
        
        last_asset = self.fixed_assets.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("created_at", -1)]
        )
        
        if last_asset and "asset_number" in last_asset:
            try:
                last_number = int(last_asset["asset_number"].replace("FA", ""))
                return f"FA{last_number + 1:06d}"
            except:
                pass
        
        return "FA000001"

    def _calculate_monthly_depreciation(self, asset_data: Dict[str, Any]) -> float:
        """Calculate monthly depreciation amount"""
        
        purchase_price = float(asset_data["purchase_price"])
        salvage_value = float(asset_data.get("salvage_value", 0.0))
        useful_life_years = int(asset_data["useful_life_years"])
        method = asset_data["depreciation_method"]
        
        depreciable_amount = purchase_price - salvage_value
        
        if method == "straight_line":
            return depreciable_amount / (useful_life_years * 12)
        elif method == "declining_balance":
            # Double declining balance method
            rate = 2.0 / useful_life_years
            return (purchase_price * rate) / 12
        else:
            # Default to straight line
            return depreciable_amount / (useful_life_years * 12)

    def _calculate_current_values(self, asset: Dict[str, Any]) -> None:
        """Calculate current accumulated depreciation and book value"""
        
        # Get all depreciation entries for this asset
        total_depreciation = 0.0
        depreciation_entries = self.depreciation_entries.find({
            "asset_id": asset["id"],
            "tenant_id": self.tenant_id
        })
        
        for entry in depreciation_entries:
            total_depreciation += entry.get("depreciation_amount", 0.0)
        
        asset["accumulated_depreciation"] = total_depreciation
        asset["book_value"] = asset["purchase_price"] - total_depreciation

    def _calculate_depreciation_for_period(
        self, 
        asset: Dict[str, Any], 
        depreciation_date: str
    ) -> float:
        """Calculate depreciation amount for a specific period"""
        
        if asset["book_value"] <= asset["salvage_value"]:
            return 0.0
        
        method = asset["depreciation_method"]
        monthly_depreciation = asset["monthly_depreciation"]
        
        if method == "straight_line":
            # Check if this would exceed salvage value
            remaining_depreciable = asset["book_value"] - asset["salvage_value"]
            return min(monthly_depreciation, remaining_depreciable)
        
        elif method == "declining_balance":
            # Double declining balance
            rate = 2.0 / asset["useful_life_years"]
            monthly_rate = rate / 12
            depreciation = asset["book_value"] * monthly_rate
            
            # Don't depreciate below salvage value
            remaining_depreciable = asset["book_value"] - asset["salvage_value"]
            return min(depreciation, remaining_depreciable)
        
        else:
            # Default to straight line
            remaining_depreciable = asset["book_value"] - asset["salvage_value"]
            return min(monthly_depreciation, remaining_depreciable)

    def _generate_depreciation_schedule(self, asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate future depreciation schedule for an asset"""
        
        schedule = []
        current_book_value = asset["book_value"]
        current_date = datetime.now().date()
        
        # Generate schedule for remaining useful life
        months_remaining = asset["useful_life_years"] * 12
        
        for month in range(months_remaining):
            if current_book_value <= asset["salvage_value"]:
                break
            
            depreciation_amount = self._calculate_depreciation_for_period(
                {**asset, "book_value": current_book_value},
                current_date.strftime("%Y-%m-%d")
            )
            
            if depreciation_amount <= 0:
                break
            
            current_book_value -= depreciation_amount
            
            schedule.append({
                "period": month + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "depreciation_amount": round(depreciation_amount, 2),
                "book_value": round(current_book_value, 2)
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return schedule

    def _create_depreciation_journal_entry(
        self, 
        asset: Dict[str, Any], 
        depreciation_amount: float,
        depreciation_date: str
    ) -> Optional[str]:
        """Create journal entry for depreciation"""
        
        try:
            # Get or create depreciation expense account
            expense_account_id = self._get_or_create_depreciation_account("expense")
            
            # Get or create accumulated depreciation account
            accumulated_account_id = self._get_or_create_depreciation_account("accumulated")
            
            entry_data = {
                "tenant_id": self.tenant_id,
                "entry_number": self._get_next_entry_number(),
                "date": depreciation_date,
                "description": f"Depreciation - {asset['name']}",
                "reference": f"Asset: {asset['asset_number']}",
                "line_items": [
                    {
                        "id": str(uuid.uuid4()),
                        "account_id": expense_account_id,
                        "debit": depreciation_amount,
                        "credit": 0,
                        "description": "Depreciation expense"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "account_id": accumulated_account_id,
                        "debit": 0,
                        "credit": depreciation_amount,
                        "description": "Accumulated depreciation"
                    }
                ],
                "total_debit": depreciation_amount,
                "total_credit": depreciation_amount,
                "balanced": True,
                "created_by": "system",
                "created_at": datetime.utcnow()
            }
            
            result = self.journal_entries.insert_one(entry_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating depreciation journal entry: {e}")
            return None

    def _create_disposal_journal_entry(
        self, 
        asset: Dict[str, Any], 
        disposal_data: Dict[str, Any],
        gain_loss_amount: float
    ) -> Optional[str]:
        """Create journal entry for asset disposal"""
        
        try:
            disposal_price = disposal_data["disposal_price"]
            
            # Get accounts
            cash_account_id = self._get_or_create_account("cash", "Cash", "asset", "cash")
            asset_account_id = self._get_or_create_account("fixed_assets", "Fixed Assets", "asset", "fixed_assets")
            accumulated_account_id = self._get_or_create_depreciation_account("accumulated")
            
            line_items = [
                {
                    "id": str(uuid.uuid4()),
                    "account_id": cash_account_id,
                    "debit": disposal_price,
                    "credit": 0,
                    "description": "Cash received from disposal"
                },
                {
                    "id": str(uuid.uuid4()),
                    "account_id": accumulated_account_id,
                    "debit": asset["accumulated_depreciation"],
                    "credit": 0,
                    "description": "Remove accumulated depreciation"
                },
                {
                    "id": str(uuid.uuid4()),
                    "account_id": asset_account_id,
                    "debit": 0,
                    "credit": asset["purchase_price"],
                    "description": "Remove asset cost"
                }
            ]
            
            # Add gain/loss entry if needed
            if abs(gain_loss_amount) > 0.01:
                gain_loss_account_id = self._get_or_create_gain_loss_account(gain_loss_amount > 0)
                
                if gain_loss_amount > 0:  # Gain
                    line_items.append({
                        "id": str(uuid.uuid4()),
                        "account_id": gain_loss_account_id,
                        "debit": 0,
                        "credit": abs(gain_loss_amount),
                        "description": "Gain on disposal"
                    })
                else:  # Loss
                    line_items.append({
                        "id": str(uuid.uuid4()),
                        "account_id": gain_loss_account_id,
                        "debit": abs(gain_loss_amount),
                        "credit": 0,
                        "description": "Loss on disposal"
                    })
            
            total_debit = sum(item["debit"] for item in line_items)
            total_credit = sum(item["credit"] for item in line_items)
            
            entry_data = {
                "tenant_id": self.tenant_id,
                "entry_number": self._get_next_entry_number(),
                "date": disposal_data["disposal_date"],
                "description": f"Asset Disposal - {asset['name']}",
                "reference": f"Asset: {asset['asset_number']}",
                "line_items": line_items,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "balanced": abs(total_debit - total_credit) < 0.01,
                "created_by": "system",
                "created_at": datetime.utcnow()
            }
            
            result = self.journal_entries.insert_one(entry_data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating disposal journal entry: {e}")
            return None

    def _get_or_create_depreciation_account(self, account_type: str) -> str:
        """Get or create depreciation-related accounts"""
        
        if account_type == "expense":
            account_code = "6200"
            account_name = "Depreciation Expense"
            acc_type = "expense"
            sub_type = "operating_expenses"
        else:  # accumulated
            account_code = "1800"
            account_name = "Accumulated Depreciation"
            acc_type = "asset"
            sub_type = "fixed_assets"
        
        return self._get_or_create_account(account_code, account_name, acc_type, sub_type)

    def _get_or_create_gain_loss_account(self, is_gain: bool) -> str:
        """Get or create gain/loss on disposal account"""
        
        if is_gain:
            account_code = "7800"
            account_name = "Gain on Asset Disposal"
            acc_type = "revenue"
            sub_type = "other_revenue"
        else:
            account_code = "8800"
            account_name = "Loss on Asset Disposal"
            acc_type = "expense"
            sub_type = "operating_expenses"
        
        return self._get_or_create_account(account_code, account_name, acc_type, sub_type)

    def _get_or_create_account(
        self, 
        code: str, 
        name: str, 
        account_type: str, 
        sub_type: str
    ) -> str:
        """Get or create an account"""
        
        account = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "code": code
        })
        
        if account:
            return str(account["_id"])
        
        # Create new account
        account_data = {
            "tenant_id": self.tenant_id,
            "code": code,
            "name": name,
            "account_type": account_type,
            "sub_type": sub_type,
            "description": f"Automatic account for {name.lower()}",
            "balance": 0.0,
            "active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        }
        
        result = self.accounts.insert_one(account_data)
        return str(result.inserted_id)

    def _get_next_entry_number(self) -> int:
        """Get the next journal entry number"""
        
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        
        return (last_entry.get("entry_number", 0) + 1) if last_entry else 1