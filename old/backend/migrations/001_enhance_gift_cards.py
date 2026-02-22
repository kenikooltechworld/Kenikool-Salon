"""
Migration: Enhance Gift Cards Collection
Date: 2024
Description: Add new fields to gift_cards collection for enterprise features:
- delivery_status: Track email/SMS delivery status
- pin: Optional PIN for card protection
- activation_required: Flag for cards requiring activation
- audit_log: Complete audit trail of all operations
- security_flags: Fraud detection flags
Also creates new collections for terms and designs.
"""

from pymongo import MongoClient
from pymongo.errors import OperationFailure
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GiftCardMigration:
    """Migration to enhance gift cards collection"""
    
    def __init__(self, mongodb_url: str, db_name: str):
        """Initialize migration with MongoDB connection details"""
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.gift_cards = self.db.gift_cards
        self.gift_card_terms = self.db.gift_card_terms
        self.gift_card_designs = self.db.gift_card_designs
    
    def run(self) -> dict:
        """Run the migration"""
        try:
            logger.info("Starting gift card schema enhancement migration...")
            
            # Step 1: Add new fields to existing gift cards
            self._enhance_existing_cards()
            
            # Step 2: Create gift_card_terms collection
            self._create_terms_collection()
            
            # Step 3: Create gift_card_designs collection
            self._create_designs_collection()
            
            # Step 4: Create indexes
            self._create_indexes()
            
            logger.info("✅ Migration completed successfully")
            return {
                "success": True,
                "message": "Gift card schema enhanced successfully"
            }
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _enhance_existing_cards(self):
        """Add new fields to existing gift cards"""
        logger.info("Enhancing existing gift cards...")
        
        # Update all existing gift cards with new fields
        result = self.gift_cards.update_many(
            {},
            {
                "$set": {
                    "delivery_status": "pending",
                    "delivery_method": None,
                    "delivery_attempts": 0,
                    "last_delivery_attempt": None,
                    "scheduled_delivery": None,
                    "pin": None,
                    "pin_enabled": False,
                    "activation_required": False,
                    "activated_at": None,
                    "activated_by": None,
                    "terms_version": "1.0",
                    "design_theme": "default",
                    "certificate_url": None,
                    "qr_code_data": None,
                    "security_flags": [],
                    "suspicious_activity_count": 0,
                    "last_balance_check": None,
                    "balance_check_count_today": 0,
                    "audit_log": []
                }
            },
            upsert=False
        )
        
        logger.info(f"Updated {result.modified_count} existing gift cards")
    
    def _create_terms_collection(self):
        """Create gift_card_terms collection with default terms"""
        logger.info("Creating gift_card_terms collection...")
        
        # Check if collection already exists
        if "gift_card_terms" in self.db.list_collection_names():
            logger.info("gift_card_terms collection already exists")
            return
        
        # Create collection with default terms
        default_terms = {
            "version": "1.0",
            "content": """
GIFT CARD TERMS AND CONDITIONS

1. VALIDITY
- Gift cards are valid for 12 months from the date of purchase
- Expired gift cards cannot be redeemed

2. REDEMPTION
- Gift cards can be redeemed for services at our salon
- Gift cards cannot be exchanged for cash
- Partial redemption is allowed

3. TRANSFER
- Gift cards can be transferred to another person
- Transfer is limited to once per card per day

4. REFUNDS
- Refunds are not available for gift card purchases
- Voided cards will be refunded to the original payment method

5. SECURITY
- Keep your gift card number confidential
- Do not share your PIN with anyone
- Report lost or stolen cards immediately

6. LIABILITY
- We are not responsible for lost, stolen, or damaged gift cards
- Gift card balance is non-transferable and cannot be combined with other offers

7. CHANGES
- We reserve the right to modify these terms with 30 days notice
- Continued use of the gift card constitutes acceptance of modified terms
            """,
            "effective_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "created_by": "system",
            "is_active": True
        }
        
        self.gift_card_terms.insert_one(default_terms)
        logger.info("Default terms created")
    
    def _create_designs_collection(self):
        """Create gift_card_designs collection with default templates"""
        logger.info("Creating gift_card_designs collection...")
        
        # Check if collection already exists
        if "gift_card_designs" in self.db.list_collection_names():
            logger.info("gift_card_designs collection already exists")
            return
        
        # Create collection with default design templates
        default_designs = [
            {
                "name": "Classic",
                "theme": "default",
                "template_html": "<div class='gift-card classic'>Classic Design</div>",
                "template_css": ".gift-card.classic { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Christmas",
                "theme": "christmas",
                "template_html": "<div class='gift-card christmas'>🎄 Christmas Special 🎄</div>",
                "template_css": ".gift-card.christmas { background: linear-gradient(135deg, #c41e3a 0%, #165b33 100%); }",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Birthday",
                "theme": "birthday",
                "template_html": "<div class='gift-card birthday'>🎉 Happy Birthday! 🎉</div>",
                "template_css": ".gift-card.birthday { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Valentine",
                "theme": "valentine",
                "template_html": "<div class='gift-card valentine'>💝 With Love 💝</div>",
                "template_css": ".gift-card.valentine { background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%); }",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "name": "Elegant",
                "theme": "elegant",
                "template_html": "<div class='gift-card elegant'>Elegant Gift Card</div>",
                "template_css": ".gift-card.elegant { background: linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%); color: gold; }",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        self.gift_card_designs.insert_many(default_designs)
        logger.info(f"Created {len(default_designs)} default design templates")
    
    def _create_indexes(self):
        """Create indexes for performance optimization"""
        logger.info("Creating indexes...")
        
        # Gift Cards indexes
        self.gift_cards.create_index("card_number", unique=True)
        self.gift_cards.create_index([("tenant_id", 1), ("status", 1)])
        self.gift_cards.create_index([("tenant_id", 1), ("created_at", -1)])
        self.gift_cards.create_index([("tenant_id", 1), ("expires_at", 1)])
        self.gift_cards.create_index("recipient_email", sparse=True)
        self.gift_cards.create_index([("tenant_id", 1), ("delivery_status", 1)])
        self.gift_cards.create_index([("tenant_id", 1), ("balance_check_count_today", 1)])
        self.gift_cards.create_index("security_flags", sparse=True)
        
        # Gift Card Terms indexes
        self.gift_card_terms.create_index([("version", 1)], unique=True)
        self.gift_card_terms.create_index([("is_active", 1)])
        self.gift_card_terms.create_index([("created_at", -1)])
        
        # Gift Card Designs indexes
        self.gift_card_designs.create_index([("theme", 1)], unique=True)
        self.gift_card_designs.create_index([("is_active", 1)])
        self.gift_card_designs.create_index([("created_at", -1)])
        
        logger.info("Indexes created successfully")
    
    def rollback(self) -> dict:
        """Rollback the migration (remove new fields)"""
        try:
            logger.info("Rolling back migration...")
            
            # Remove new fields from gift cards
            self.gift_cards.update_many(
                {},
                {
                    "$unset": {
                        "delivery_status": "",
                        "delivery_method": "",
                        "delivery_attempts": "",
                        "last_delivery_attempt": "",
                        "scheduled_delivery": "",
                        "pin": "",
                        "pin_enabled": "",
                        "activation_required": "",
                        "activated_at": "",
                        "activated_by": "",
                        "terms_version": "",
                        "design_theme": "",
                        "certificate_url": "",
                        "qr_code_data": "",
                        "security_flags": "",
                        "suspicious_activity_count": "",
                        "last_balance_check": "",
                        "balance_check_count_today": "",
                        "audit_log": ""
                    }
                }
            )
            
            # Drop new collections
            self.gift_card_terms.drop()
            self.gift_card_designs.drop()
            
            logger.info("✅ Rollback completed successfully")
            return {
                "success": True,
                "message": "Migration rolled back successfully"
            }
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()


# Standalone function for running migration
def run_migration(mongodb_url: str, db_name: str) -> dict:
    """Run the gift card migration"""
    migration = GiftCardMigration(mongodb_url, db_name)
    try:
        return migration.run()
    finally:
        migration.close()


if __name__ == "__main__":
    # For manual execution
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    mongodb_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("MONGODB_DB_NAME", "kenikool")
    
    if not mongodb_url:
        print("Error: MONGODB_URL not set")
        exit(1)
    
    result = run_migration(mongodb_url, db_name)
    print(result)