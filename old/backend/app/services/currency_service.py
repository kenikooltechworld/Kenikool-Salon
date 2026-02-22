"""
Multi-Currency Support Service

Handles currency configuration and exchange rate management including:
- Currency CRUD operations
- Exchange rate management
- Currency conversion calculations
- Exchange gains/losses tracking
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import uuid
import logging

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CurrencyService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.currencies = db.currencies
        self.exchange_rates = db.exchange_rates
        self.journal_entries = db.journal_entries

    def get_currencies(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get currencies with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if active_only:
            query["active"] = True
        
        currencies = list(
            self.currencies.find(query)
            .sort("code", 1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for currency in currencies:
            currency["id"] = str(currency["_id"])
            del currency["_id"]
        
        return currencies

    def create_currency(self, currency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new currency"""
        
        code = currency_data["code"].upper()
        
        # Check if currency code already exists
        existing = self.currencies.find_one({
            "tenant_id": self.tenant_id,
            "code": code
        })
        
        if existing:
            raise ValueError(f"Currency code {code} already exists")
        
        currency_doc = {
            "tenant_id": self.tenant_id,
            "code": code,
            "name": currency_data["name"],
            "symbol": currency_data.get("symbol", code),
            "decimal_places": currency_data.get("decimal_places", 2),
            "is_base_currency": currency_data.get("is_base_currency", False),
            "active": currency_data.get("active", True),
            "created_by": currency_data.get("created_by", "system"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # If this is set as base currency, unset others
        if currency_doc["is_base_currency"]:
            self.currencies.update_many(
                {"tenant_id": self.tenant_id},
                {"$set": {"is_base_currency": False}}
            )
        
        result = self.currencies.insert_one(currency_doc)
        currency_doc["id"] = str(result.inserted_id)
        del currency_doc["_id"]
        
        return currency_doc

    def update_currency(
        self, 
        currency_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing currency"""
        
        update_fields = {}
        
        if "name" in update_data:
            update_fields["name"] = update_data["name"]
        if "symbol" in update_data:
            update_fields["symbol"] = update_data["symbol"]
        if "decimal_places" in update_data:
            update_fields["decimal_places"] = update_data["decimal_places"]
        if "active" in update_data:
            update_fields["active"] = update_data["active"]
        if "is_base_currency" in update_data:
            update_fields["is_base_currency"] = update_data["is_base_currency"]
            
            # If setting as base currency, unset others
            if update_data["is_base_currency"]:
                self.currencies.update_many(
                    {"tenant_id": self.tenant_id, "_id": {"$ne": ObjectId(currency_id)}},
                    {"$set": {"is_base_currency": False}}
                )
        
        update_fields["updated_at"] = datetime.utcnow()
        
        self.currencies.update_one(
            {"_id": ObjectId(currency_id), "tenant_id": self.tenant_id},
            {"$set": update_fields}
        )
        
        return self.get_currency(currency_id)

    def get_currency(self, currency_id: str) -> Dict[str, Any]:
        """Get a specific currency by ID"""
        
        currency = self.currencies.find_one({
            "_id": ObjectId(currency_id),
            "tenant_id": self.tenant_id
        })
        
        if not currency:
            raise ValueError("Currency not found")
        
        currency["id"] = str(currency["_id"])
        del currency["_id"]
        
        return currency

    def get_currency_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get currency by code"""
        
        currency = self.currencies.find_one({
            "tenant_id": self.tenant_id,
            "code": code.upper()
        })
        
        if currency:
            currency["id"] = str(currency["_id"])
            del currency["_id"]
        
        return currency

    def get_base_currency(self) -> Dict[str, Any]:
        """Get the base currency for the tenant"""
        
        base_currency = self.currencies.find_one({
            "tenant_id": self.tenant_id,
            "is_base_currency": True
        })
        
        if not base_currency:
            # If no base currency set, create USD as default
            base_currency_data = {
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "decimal_places": 2,
                "is_base_currency": True,
                "active": True
            }
            return self.create_currency(base_currency_data)
        
        base_currency["id"] = str(base_currency["_id"])
        del base_currency["_id"]
        
        return base_currency

    def create_exchange_rate(self, rate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update an exchange rate"""
        
        from_currency = rate_data["from_currency"]
        to_currency = rate_data["to_currency"]
        rate_date = rate_data["rate_date"]
        rate = rate_data["rate"]
        
        # Check if rate already exists for this date
        existing = self.exchange_rates.find_one({
            "tenant_id": self.tenant_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate_date": rate_date
        })
        
        if existing:
            # Update existing rate
            self.exchange_rates.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "rate": rate,
                        "updated_at": datetime.utcnow(),
                        "updated_by": rate_data.get("created_by", "system")
                    }
                }
            )
            existing["id"] = str(existing["_id"])
            del existing["_id"]
            existing["rate"] = rate
            return existing
        
        # Create new rate
        rate_doc = {
            "tenant_id": self.tenant_id,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "rate_date": rate_date,
            "source": rate_data.get("source", "manual"),
            "created_by": rate_data.get("created_by", "system"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.exchange_rates.insert_one(rate_doc)
        rate_doc["id"] = str(result.inserted_id)
        del rate_doc["_id"]
        
        return rate_doc

    def get_exchange_rate(
        self, 
        from_currency: str, 
        to_currency: str, 
        rate_date: Optional[str] = None
    ) -> float:
        """Get exchange rate between two currencies"""
        
        if from_currency == to_currency:
            return 1.0
        
        if not rate_date:
            rate_date = datetime.now().strftime("%Y-%m-%d")
        
        # Try to find exact rate
        rate_record = self.exchange_rates.find_one(
            {
                "tenant_id": self.tenant_id,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate_date": {"$lte": rate_date}
            },
            sort=[("rate_date", -1)]
        )
        
        if rate_record:
            return rate_record["rate"]
        
        # Try inverse rate
        inverse_rate = self.exchange_rates.find_one(
            {
                "tenant_id": self.tenant_id,
                "from_currency": to_currency,
                "to_currency": from_currency,
                "rate_date": {"$lte": rate_date}
            },
            sort=[("rate_date", -1)]
        )
        
        if inverse_rate:
            return 1.0 / inverse_rate["rate"]
        
        # Default to 1.0 if no rate found
        logger.warning(f"No exchange rate found for {from_currency} to {to_currency} on {rate_date}")
        return 1.0

    def convert_amount(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str, 
        rate_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert amount between currencies"""
        
        if from_currency == to_currency:
            return {
                "original_amount": amount,
                "converted_amount": amount,
                "exchange_rate": 1.0,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate_date": rate_date or datetime.now().strftime("%Y-%m-%d")
            }
        
        exchange_rate = self.get_exchange_rate(from_currency, to_currency, rate_date)
        converted_amount = amount * exchange_rate
        
        return {
            "original_amount": amount,
            "converted_amount": converted_amount,
            "exchange_rate": exchange_rate,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate_date": rate_date or datetime.now().strftime("%Y-%m-%d")
        }

    def calculate_exchange_gain_loss(
        self, 
        original_amount: float,
        original_currency: str,
        original_rate: float,
        current_rate: float,
        base_currency: str
    ) -> Dict[str, Any]:
        """Calculate exchange gain or loss"""
        
        original_base_amount = original_amount * original_rate
        current_base_amount = original_amount * current_rate
        gain_loss = current_base_amount - original_base_amount
        
        return {
            "original_amount": original_amount,
            "original_currency": original_currency,
            "original_rate": original_rate,
            "current_rate": current_rate,
            "base_currency": base_currency,
            "original_base_amount": original_base_amount,
            "current_base_amount": current_base_amount,
            "gain_loss_amount": gain_loss,
            "is_gain": gain_loss > 0
        }

    def create_exchange_gain_loss_entry(
        self, 
        gain_loss_data: Dict[str, Any],
        reference: str = ""
    ) -> Dict[str, Any]:
        """Create journal entry for exchange gain/loss"""
        
        base_currency = self.get_base_currency()
        gain_loss_amount = gain_loss_data["gain_loss_amount"]
        
        if abs(gain_loss_amount) < 0.01:  # No significant gain/loss
            return None
        
        # Get or create exchange gain/loss accounts
        exchange_account_id = self._get_or_create_exchange_account(gain_loss_amount > 0)
        
        # Create journal entry
        entry_data = {
            "tenant_id": self.tenant_id,
            "entry_number": self._get_next_entry_number(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": f"Exchange {'Gain' if gain_loss_amount > 0 else 'Loss'} - {gain_loss_data['original_currency']} to {base_currency['code']}",
            "reference": reference,
            "line_items": [],
            "created_by": "system",
            "created_at": datetime.utcnow()
        }
        
        if gain_loss_amount > 0:  # Gain
            entry_data["line_items"] = [
                {
                    "id": str(uuid.uuid4()),
                    "account_id": exchange_account_id,
                    "debit": 0,
                    "credit": abs(gain_loss_amount),
                    "description": "Exchange gain"
                }
            ]
        else:  # Loss
            entry_data["line_items"] = [
                {
                    "id": str(uuid.uuid4()),
                    "account_id": exchange_account_id,
                    "debit": abs(gain_loss_amount),
                    "credit": 0,
                    "description": "Exchange loss"
                }
            ]
        
        # Calculate totals
        total_debit = sum(item["debit"] for item in entry_data["line_items"])
        total_credit = sum(item["credit"] for item in entry_data["line_items"])
        
        entry_data["total_debit"] = total_debit
        entry_data["total_credit"] = total_credit
        entry_data["balanced"] = abs(total_debit - total_credit) < 0.01
        
        result = self.journal_entries.insert_one(entry_data)
        entry_data["id"] = str(result.inserted_id)
        del entry_data["_id"]
        
        return entry_data

    def get_exchange_rates_history(
        self, 
        from_currency: str, 
        to_currency: str, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get exchange rate history"""
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rates = list(
            self.exchange_rates.find({
                "tenant_id": self.tenant_id,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate_date": {"$gte": start_date}
            }).sort("rate_date", 1)
        )
        
        for rate in rates:
            rate["id"] = str(rate["_id"])
            del rate["_id"]
        
        return rates

    def fetch_live_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """Fetch live exchange rates from external API (optional)"""
        
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "error": "Requests library not available. Install with: pip install requests"
            }
        
        try:
            # Using a free API like exchangerate-api.com
            # Note: In production, you'd want to use a paid service for reliability
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                
                # Store rates in database
                rate_date = datetime.now().strftime("%Y-%m-%d")
                stored_rates = []
                
                for currency_code, rate in rates.items():
                    if currency_code != base_currency:
                        rate_data = {
                            "from_currency": base_currency,
                            "to_currency": currency_code,
                            "rate": rate,
                            "rate_date": rate_date,
                            "source": "api",
                            "created_by": "system"
                        }
                        stored_rate = self.create_exchange_rate(rate_data)
                        stored_rates.append(stored_rate)
                
                return {
                    "success": True,
                    "base_currency": base_currency,
                    "rate_date": rate_date,
                    "rates_count": len(stored_rates),
                    "rates": stored_rates
                }
            
        except Exception as e:
            logger.error(f"Error fetching live exchange rates: {e}")
        
        return {
            "success": False,
            "error": "Failed to fetch live exchange rates"
        }

    def _get_or_create_exchange_account(self, is_gain: bool) -> str:
        """Get or create exchange gain/loss account"""
        
        account_name = "Exchange Gain" if is_gain else "Exchange Loss"
        account_code = "7900" if is_gain else "8900"
        
        # Try to find existing account
        account = self.db.accounts.find_one({
            "tenant_id": self.tenant_id,
            "code": account_code
        })
        
        if account:
            return str(account["_id"])
        
        # Create new account
        account_data = {
            "tenant_id": self.tenant_id,
            "code": account_code,
            "name": account_name,
            "account_type": "revenue" if is_gain else "expense",
            "sub_type": "other_revenue" if is_gain else "operating_expenses",
            "description": f"Automatic account for currency {account_name.lower()}",
            "balance": 0.0,
            "active": True,
            "created_at": datetime.utcnow(),
            "created_by": "system"
        }
        
        result = self.db.accounts.insert_one(account_data)
        return str(result.inserted_id)

    def _get_next_entry_number(self) -> int:
        """Get the next journal entry number"""
        
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        
        return (last_entry.get("entry_number", 0) + 1) if last_entry else 1

    def get_currency_summary(self) -> Dict[str, Any]:
        """Get currency configuration summary"""
        
        total_currencies = self.currencies.count_documents({"tenant_id": self.tenant_id})
        active_currencies = self.currencies.count_documents({
            "tenant_id": self.tenant_id,
            "active": True
        })
        
        base_currency = self.get_base_currency()
        
        # Get recent exchange rates
        recent_rates = list(
            self.exchange_rates.find({"tenant_id": self.tenant_id})
            .sort("created_at", -1)
            .limit(5)
        )
        
        for rate in recent_rates:
            rate["id"] = str(rate["_id"])
            del rate["_id"]
        
        return {
            "total_currencies": total_currencies,
            "active_currencies": active_currencies,
            "base_currency": base_currency,
            "recent_exchange_rates": recent_rates,
            "multi_currency_enabled": total_currencies > 1
        }