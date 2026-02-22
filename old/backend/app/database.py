"""
MongoDB database connection using PyMongo (synchronous driver)
"""
from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database manager"""
    
    client: Optional[MongoClient] = None
    db: Optional[PyMongoDatabase] = None
    _initialized: bool = False
    
    @classmethod
    def connect_db(cls):
        """Connect to MongoDB Atlas"""
        try:
            logger.info(f"Connecting to MongoDB Atlas...")
            
            # Simple, secure connection to MongoDB Atlas
            cls.client = MongoClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Test connection with ping
            cls.client.admin.command('ping')
            cls._initialized = True
            
            logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
            
            # Create indexes
            cls.create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            cls._initialized = False
            raise
    
    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        if cls._initialized and cls.client is not None:
            cls.client.close()
            cls._initialized = False
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def create_indexes(cls):
        """Create database indexes for performance"""
        if not cls._initialized:
            return
        
        try:
            # Wrap index creation in try-except to handle conflicts gracefully
            def safe_create_index(collection, keys, **kwargs):
                try:
                    collection.create_index(keys, **kwargs)
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.debug(f"Index already exists: {keys}")
                    else:
                        raise
            
            # Tenants
            safe_create_index(cls.db.tenants, "subdomain", unique=True)
            safe_create_index(cls.db.tenants, "custom_domain", sparse=True)
            
            # Users
            safe_create_index(cls.db.users, "email", unique=True)
            safe_create_index(cls.db.users, "tenant_id")
            
            # Clients
            safe_create_index(cls.db.clients, "tenant_id")
            safe_create_index(cls.db.clients, [("tenant_id", 1), ("phone", 1)], unique=True)
            safe_create_index(cls.db.clients, [("tenant_id", 1), ("last_visit_date", 1)])
            # Dashboard-specific indexes
            safe_create_index(cls.db.clients, [("tenant_id", 1), ("created_at", 1)])
            safe_create_index(cls.db.clients, [("tenant_id", 1), ("segment", 1)])
            
            # Client Analytics
            safe_create_index(cls.db.client_analytics, [("tenant_id", 1), ("client_id", 1)], unique=True)
            safe_create_index(cls.db.client_analytics, "tenant_id")
            safe_create_index(cls.db.client_analytics, [("tenant_id", 1), ("is_at_risk", 1)])
            safe_create_index(cls.db.client_analytics, [("tenant_id", 1), ("churn_risk_score", -1)])
            safe_create_index(cls.db.client_analytics, [("tenant_id", 1), ("lifetime_value", -1)])
            cls.db.client_analytics.create_index([("tenant_id", 1), ("last_visit_date", -1)])
            cls.db.client_analytics.create_index("calculated_at")
            
            # Client Activities
            cls.db.client_activities.create_index("tenant_id")
            cls.db.client_activities.create_index([("tenant_id", 1), ("client_id", 1), ("created_at", -1)])
            cls.db.client_activities.create_index([("tenant_id", 1), ("client_id", 1), ("activity_type", 1)])
            cls.db.client_activities.create_index([("tenant_id", 1), ("created_at", -1)])
            cls.db.client_activities.create_index([("tenant_id", 1), ("created_by", 1)])
            
            # Client Relationships
            cls.db.client_relationships.create_index("tenant_id")
            cls.db.client_relationships.create_index([("tenant_id", 1), ("client_id", 1)])
            cls.db.client_relationships.create_index([("tenant_id", 1), ("related_client_id", 1)])
            cls.db.client_relationships.create_index([("tenant_id", 1), ("relationship_type", 1)])
            cls.db.client_relationships.create_index([("tenant_id", 1), ("client_id", 1), ("related_client_id", 1)], unique=True)
            
            # Services
            cls.db.services.create_index("tenant_id")
            cls.db.services.create_index([("tenant_id", 1), ("is_active", 1)])
            
            # Bookings
            cls.db.bookings.create_index("tenant_id")
            cls.db.bookings.create_index([("tenant_id", 1), ("booking_date", 1)])
            cls.db.bookings.create_index([("tenant_id", 1), ("stylist_id", 1), ("booking_date", 1)])
            cls.db.bookings.create_index([("tenant_id", 1), ("client_id", 1)])
            cls.db.bookings.create_index([("tenant_id", 1), ("status", 1)])
            # Dashboard-specific indexes
            cls.db.bookings.create_index([("tenant_id", 1), ("service_id", 1)])
            cls.db.bookings.create_index([("tenant_id", 1), ("stylist_id", 1)])
            
            # Payments
            cls.db.payments.create_index("tenant_id")
            cls.db.payments.create_index([("tenant_id", 1), ("created_at", 1)])
            cls.db.payments.create_index("transaction_reference")
            cls.db.payments.create_index([("tenant_id", 1), ("status", 1)])
            cls.db.payments.create_index([("tenant_id", 1), ("gateway", 1)])
            cls.db.payments.create_index([("tenant_id", 1), ("booking_id", 1)])
            cls.db.payments.create_index([("tenant_id", 1), ("is_manual", 1)])
            cls.db.payments.create_index([("tenant_id", 1), ("gateway_sync_status", 1)])
            cls.db.payments.create_index("reference", unique=True, sparse=True)
            
            # Payment Refunds
            cls.db.payment_refunds.create_index("tenant_id")
            cls.db.payment_refunds.create_index([("tenant_id", 1), ("payment_id", 1)])
            cls.db.payment_refunds.create_index([("tenant_id", 1), ("created_at", 1)])
            
            # Payment Receipts
            cls.db.payment_receipts.create_index("tenant_id")
            cls.db.payment_receipts.create_index([("tenant_id", 1), ("payment_id", 1)])
            cls.db.payment_receipts.create_index("receipt_number", unique=True)
            
            # Inventory
            cls.db.inventory_products.create_index("tenant_id")
            
            # Reviews
            cls.db.reviews.create_index("tenant_id")
            cls.db.reviews.create_index([("tenant_id", 1), ("stylist_id", 1)])
            
            # Photos
            cls.db.photos.create_index("tenant_id")
            
            # Waitlist
            cls.db.waitlist.create_index("tenant_id")
            
            # POS Transactions - Dashboard-specific indexes
            cls.db.pos_transactions.create_index("tenant_id")
            cls.db.pos_transactions.create_index([("tenant_id", 1), ("created_at", 1)])
            cls.db.pos_transactions.create_index([("tenant_id", 1), ("status", 1)])
            
            # Expenses - Dashboard-specific indexes
            cls.db.expenses.create_index("tenant_id")
            cls.db.expenses.create_index([("tenant_id", 1), ("date", 1)])
            cls.db.expenses.create_index([("tenant_id", 1), ("category", 1)])
            
            # SSL Certificates
            cls.db.ssl_certificates.create_index("tenant_id")
            cls.db.ssl_certificates.create_index([("tenant_id", 1), ("domain", 1)], unique=True)
            cls.db.ssl_certificates.create_index([("tenant_id", 1), ("expires_at", 1)])
            cls.db.ssl_certificates.create_index("domain")
            cls.db.ssl_certificates.create_index("expires_at")
            
            # Branding Versions
            cls.db.branding_versions.create_index("tenant_id")
            cls.db.branding_versions.create_index([("tenant_id", 1), ("created_at", -1)])
            cls.db.branding_versions.create_index([("tenant_id", 1), ("version_number", -1)])
            cls.db.branding_versions.create_index([("tenant_id", 1), ("is_current", 1)])
            
            # Theme Templates
            cls.db.theme_templates.create_index("tenant_id", sparse=True)
            cls.db.theme_templates.create_index("category")
            cls.db.theme_templates.create_index([("is_system", 1), ("category", 1)])
            cls.db.theme_templates.create_index([("tenant_id", 1), ("created_at", -1)], sparse=True)
            cls.db.theme_templates.create_index("name")
            
            # Settings System Collections
            # Sessions
            cls.db.sessions.create_index("user_id")
            cls.db.sessions.create_index("token_hash")
            cls.db.sessions.create_index("expires_at")
            cls.db.sessions.create_index([("user_id", 1), ("expires_at", 1)])
            cls.db.sessions.create_index([("user_id", 1), ("created_at", -1)])
            
            # API Keys
            cls.db.api_keys.create_index("user_id")
            cls.db.api_keys.create_index("key_hash")
            cls.db.api_keys.create_index([("user_id", 1), ("is_active", 1)])
            cls.db.api_keys.create_index([("user_id", 1), ("created_at", -1)])
            cls.db.api_keys.create_index("expires_at", sparse=True)
            
            # User Preferences
            cls.db.user_preferences.create_index("user_id", unique=True)
            cls.db.user_preferences.create_index("tenant_id")
            cls.db.user_preferences.create_index([("tenant_id", 1), ("user_id", 1)], unique=True)
            
            # Privacy Settings
            cls.db.privacy_settings.create_index("user_id", unique=True)
            cls.db.privacy_settings.create_index("tenant_id")
            cls.db.privacy_settings.create_index([("tenant_id", 1), ("user_id", 1)], unique=True)
            
            # Security Logs
            cls.db.security_logs.create_index("user_id")
            cls.db.security_logs.create_index("tenant_id")
            cls.db.security_logs.create_index("timestamp")
            cls.db.security_logs.create_index("event_type")
            cls.db.security_logs.create_index([("user_id", 1), ("timestamp", -1)])
            cls.db.security_logs.create_index([("tenant_id", 1), ("timestamp", -1)])
            cls.db.security_logs.create_index([("user_id", 1), ("event_type", 1)])
            cls.db.security_logs.create_index([("tenant_id", 1), ("event_type", 1)])
            cls.db.security_logs.create_index("flagged", sparse=True)
            
            # Data Exports
            cls.db.data_exports.create_index("user_id")
            cls.db.data_exports.create_index("tenant_id")
            cls.db.data_exports.create_index("status")
            cls.db.data_exports.create_index([("user_id", 1), ("requested_at", -1)])
            cls.db.data_exports.create_index([("tenant_id", 1), ("requested_at", -1)])
            cls.db.data_exports.create_index("expires_at", sparse=True)
            
            # Account Deletions
            cls.db.account_deletions.create_index("user_id")
            cls.db.account_deletions.create_index("tenant_id")
            cls.db.account_deletions.create_index("status")
            cls.db.account_deletions.create_index([("user_id", 1), ("requested_at", -1)])
            cls.db.account_deletions.create_index([("tenant_id", 1), ("requested_at", -1)])
            cls.db.account_deletions.create_index("scheduled_for", sparse=True)
            
            # Package System Collections
            # Package Purchases
            cls.db.package_purchases.create_index([("client_id", 1), ("status", 1)])
            cls.db.package_purchases.create_index([("expiration_date", 1), ("status", 1)])
            cls.db.package_purchases.create_index([("tenant_id", 1), ("purchase_date", -1)])
            cls.db.package_purchases.create_index([("tenant_id", 1), ("client_id", 1), ("status", 1)])
            cls.db.package_purchases.create_index([("package_definition_id", 1), ("status", 1)])
            
            # Service Credits
            cls.db.service_credits.create_index([("purchase_id", 1), ("service_id", 1)])
            cls.db.service_credits.create_index([("purchase_id", 1), ("status", 1)])
            cls.db.service_credits.create_index([("purchase_id", 1), ("remaining_quantity", 1)])
            
            # Redemption Transactions
            cls.db.redemption_transactions.create_index([("purchase_id", 1), ("redemption_date", -1)])
            cls.db.redemption_transactions.create_index([("client_id", 1), ("redemption_date", -1)])
            cls.db.redemption_transactions.create_index("credit_id")
            cls.db.redemption_transactions.create_index([("service_id", 1), ("redemption_date", -1)])
            
            # Package Audit Logs
            cls.db.package_audit_logs.create_index([("entity_id", 1), ("timestamp", -1)])
            cls.db.package_audit_logs.create_index([("tenant_id", 1), ("timestamp", -1)])
            cls.db.package_audit_logs.create_index([("action_type", 1), ("timestamp", -1)])
            cls.db.package_audit_logs.create_index([("tenant_id", 1), ("action_type", 1), ("timestamp", -1)])
            cls.db.package_audit_logs.create_index([("performed_by_user_id", 1), ("timestamp", -1)])
            
            # Gift Cards - Enhanced Schema
            cls.db.gift_cards.create_index("card_number", unique=True)
            cls.db.gift_cards.create_index([("tenant_id", 1), ("status", 1)])
            cls.db.gift_cards.create_index([("tenant_id", 1), ("created_at", -1)])
            cls.db.gift_cards.create_index([("tenant_id", 1), ("expires_at", 1)])
            cls.db.gift_cards.create_index("recipient_email", sparse=True)
            cls.db.gift_cards.create_index([("tenant_id", 1), ("delivery_status", 1)])
            cls.db.gift_cards.create_index([("tenant_id", 1), ("balance_check_count_today", 1)])
            cls.db.gift_cards.create_index("security_flags", sparse=True)
            
            # Gift Card Terms
            cls.db.gift_card_terms.create_index([("version", 1)], unique=True)
            cls.db.gift_card_terms.create_index([("is_active", 1)])
            cls.db.gift_card_terms.create_index([("created_at", -1)])
            
            # Gift Card Designs
            cls.db.gift_card_designs.create_index([("theme", 1)], unique=True)
            cls.db.gift_card_designs.create_index([("is_active", 1)])
            cls.db.gift_card_designs.create_index([("created_at", -1)])
            
            # Membership System Collections
            # Membership Plans
            cls.db.membership_plans.create_index("tenant_id")
            cls.db.membership_plans.create_index([("tenant_id", 1), ("name", 1)], unique=True)
            cls.db.membership_plans.create_index("is_active")
            
            # Membership Subscriptions
            cls.db.membership_subscriptions.create_index("tenant_id")
            cls.db.membership_subscriptions.create_index("client_id")
            cls.db.membership_subscriptions.create_index("plan_id")
            cls.db.membership_subscriptions.create_index("status")
            cls.db.membership_subscriptions.create_index("end_date")
            cls.db.membership_subscriptions.create_index([("tenant_id", 1), ("client_id", 1), ("status", 1)], unique=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    @classmethod
    def get_db(cls) -> PyMongoDatabase:
        """Get database instance"""
        if cls._initialized is False:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        if cls.db is None:
            raise RuntimeError("Database is None")
        return cls.db


# Dependency for FastAPI
def get_database() -> PyMongoDatabase:
    """FastAPI dependency to get database instance"""
    return Database.get_db()


# Alias for backward compatibility
def get_db() -> PyMongoDatabase:
    """FastAPI dependency to get database instance (alias for get_database)"""
    return Database.get_db()


# Module-level db reference for backward compatibility
# Services can use: from app.database import db
# This is a lazy-loaded property that returns Database.db
class _DBProxy:
    """Lazy-loaded proxy for database connection"""
    def __getattr__(self, name):
        if Database.db is None:
            raise RuntimeError("Database not initialized. Call Database.connect_db() first.")
        return getattr(Database.db, name)

db = _DBProxy()
