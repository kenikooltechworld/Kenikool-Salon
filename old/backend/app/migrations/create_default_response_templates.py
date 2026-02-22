"""
Migration script to create default response templates for all tenants
"""
from datetime import datetime
from pymongo import MongoClient
import os

def create_default_templates():
    """Create default response templates"""
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    db = client.get_database()
    
    # Default templates
    default_templates = [
        {
            "name": "Thank You - Positive Review",
            "category": "positive",
            "text": "Thank you so much for taking the time to leave us a wonderful review! We're thrilled that you had such a great experience. Your kind words mean the world to us, and we look forward to seeing you again soon!",
            "is_default": True
        },
        {
            "name": "Appreciation - Positive Review",
            "category": "positive",
            "text": "We truly appreciate your positive feedback! It's wonderful to know that our team provided you with excellent service. Thank you for choosing us, and we can't wait to welcome you back!",
            "is_default": True
        },
        {
            "name": "We're Sorry - Negative Review",
            "category": "negative",
            "text": "We're truly sorry to hear that your experience didn't meet your expectations. Your feedback is invaluable to us, and we'd like the opportunity to make things right. Please contact us directly so we can address your concerns.",
            "is_default": True
        },
        {
            "name": "Improvement Commitment - Negative Review",
            "category": "negative",
            "text": "Thank you for your honest feedback. We take your concerns seriously and are committed to improving our service. We'd appreciate the chance to discuss this further and ensure your next visit is exceptional.",
            "is_default": True
        },
        {
            "name": "Neutral Response",
            "category": "neutral",
            "text": "Thank you for your review. We appreciate your feedback and are always looking for ways to enhance our services. If you have any specific suggestions, please feel free to reach out to us directly.",
            "is_default": True
        }
    ]
    
    # Get all tenants
    tenants = db.tenants.find({})
    
    for tenant in tenants:
        tenant_id = str(tenant["_id"])
        
        # Check if templates already exist for this tenant
        existing_count = db.review_templates.count_documents({"tenant_id": tenant_id})
        
        if existing_count == 0:
            # Insert default templates for this tenant
            templates_to_insert = []
            for template in default_templates:
                template_data = {
                    "tenant_id": tenant_id,
                    "name": template["name"],
                    "category": template["category"],
                    "text": template["text"],
                    "is_default": template["is_default"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                templates_to_insert.append(template_data)
            
            db.review_templates.insert_many(templates_to_insert)
            print(f"Created {len(templates_to_insert)} default templates for tenant {tenant_id}")
        else:
            print(f"Templates already exist for tenant {tenant_id}")
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    create_default_templates()
