"""
Seed marketplace services into the database
"""

from app.database import Database
from datetime import datetime
import uuid

def seed_marketplace_services():
    """Seed marketplace services"""
    
    db = Database.get_db()
    
    # Sample marketplace services
    services = [
        {
            "_id": str(uuid.uuid4()),
            "name": "Email Marketing Pro",
            "description": "Advanced email marketing and automation platform for salons",
            "category": "Marketing",
            "icon": "https://via.placeholder.com/100?text=Email",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=Email+Dashboard",
                "https://via.placeholder.com/400x300?text=Email+Templates"
            ],
            "features": [
                "Email campaign management",
                "Automated workflows",
                "A/B testing",
                "Analytics and reporting",
                "Template library"
            ],
            "pricing": {
                "type": "paid",
                "basePrice": 29.99,
                "currency": "USD",
                "billingCycle": "monthly",
                "features": [
                    {
                        "name": "Starter",
                        "price": 29.99,
                        "features": ["Up to 5,000 contacts", "Basic templates"]
                    },
                    {
                        "name": "Professional",
                        "price": 79.99,
                        "features": ["Up to 50,000 contacts", "Advanced templates", "Automation"]
                    }
                ]
            },
            "rating": 4.8,
            "reviewCount": 245,
            "developer": "EmailPro Inc",
            "version": "2.1.0",
            "status": "active",
            "documentation": "https://docs.emailpro.com",
            "supportUrl": "https://support.emailpro.com",
            "regions": ["US", "CA", "UK", "AU"],
            "supportedLanguages": ["en", "es", "fr"],
            "requirements": {
                "minPlan": "professional",
                "requiredFeatures": ["email"]
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "SMS Blast",
            "description": "Send bulk SMS messages to your clients",
            "category": "Communication",
            "icon": "https://via.placeholder.com/100?text=SMS",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=SMS+Dashboard"
            ],
            "features": [
                "Bulk SMS sending",
                "Scheduled messages",
                "Delivery tracking",
                "Message templates",
                "Two-way messaging"
            ],
            "pricing": {
                "type": "freemium",
                "basePrice": 0,
                "currency": "USD",
                "billingCycle": "monthly",
                "features": [
                    {
                        "name": "Free",
                        "price": 0,
                        "features": ["100 SMS/month", "Basic templates"]
                    },
                    {
                        "name": "Pro",
                        "price": 49.99,
                        "features": ["Unlimited SMS", "Advanced features"]
                    }
                ]
            },
            "rating": 4.5,
            "reviewCount": 189,
            "developer": "SMS Blast Ltd",
            "version": "1.8.2",
            "status": "active",
            "documentation": "https://docs.smsblast.io",
            "supportUrl": "https://support.smsblast.io",
            "regions": ["US", "CA", "UK"],
            "supportedLanguages": ["en"],
            "requirements": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "Google Analytics Integration",
            "description": "Track salon website analytics and visitor behavior",
            "category": "Analytics",
            "icon": "https://via.placeholder.com/100?text=Analytics",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=Analytics+Dashboard"
            ],
            "features": [
                "Website traffic tracking",
                "Visitor behavior analysis",
                "Conversion tracking",
                "Custom reports",
                "Real-time data"
            ],
            "pricing": {
                "type": "free",
                "basePrice": 0,
                "currency": "USD",
                "features": []
            },
            "rating": 4.9,
            "reviewCount": 512,
            "developer": "Google",
            "version": "4.0.0",
            "status": "active",
            "documentation": "https://support.google.com/analytics",
            "supportUrl": "https://support.google.com/analytics",
            "regions": ["US", "CA", "UK", "AU", "EU"],
            "supportedLanguages": ["en", "es", "fr", "de"],
            "requirements": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "Stripe Payment Gateway",
            "description": "Accept credit card payments securely",
            "category": "Payments",
            "icon": "https://via.placeholder.com/100?text=Stripe",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=Payment+Dashboard"
            ],
            "features": [
                "Credit card processing",
                "Recurring billing",
                "Fraud detection",
                "Multi-currency support",
                "Detailed reporting"
            ],
            "pricing": {
                "type": "paid",
                "basePrice": 0,
                "currency": "USD",
                "features": [
                    {
                        "name": "Pay-as-you-go",
                        "price": 0,
                        "features": ["2.9% + $0.30 per transaction"]
                    }
                ]
            },
            "rating": 4.7,
            "reviewCount": 1203,
            "developer": "Stripe Inc",
            "version": "3.5.0",
            "status": "active",
            "documentation": "https://stripe.com/docs",
            "supportUrl": "https://support.stripe.com",
            "regions": ["US", "CA", "UK", "EU", "AU"],
            "supportedLanguages": ["en"],
            "requirements": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "Zapier Automation",
            "description": "Connect your salon software with 1000+ apps",
            "category": "Automation",
            "icon": "https://via.placeholder.com/100?text=Zapier",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=Zapier+Dashboard"
            ],
            "features": [
                "1000+ app integrations",
                "Workflow automation",
                "Data synchronization",
                "Conditional logic",
                "Error handling"
            ],
            "pricing": {
                "type": "freemium",
                "basePrice": 0,
                "currency": "USD",
                "billingCycle": "monthly",
                "features": [
                    {
                        "name": "Free",
                        "price": 0,
                        "features": ["100 tasks/month", "Basic zaps"]
                    },
                    {
                        "name": "Professional",
                        "price": 19.99,
                        "features": ["Unlimited tasks", "Advanced features"]
                    }
                ]
            },
            "rating": 4.6,
            "reviewCount": 876,
            "developer": "Zapier Inc",
            "version": "2.3.1",
            "status": "active",
            "documentation": "https://zapier.com/help",
            "supportUrl": "https://zapier.com/help",
            "regions": ["US", "CA", "UK", "EU"],
            "supportedLanguages": ["en"],
            "requirements": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "Slack Integration",
            "description": "Get salon notifications in Slack",
            "category": "Communication",
            "icon": "https://via.placeholder.com/100?text=Slack",
            "screenshots": [
                "https://via.placeholder.com/400x300?text=Slack+Integration"
            ],
            "features": [
                "Real-time notifications",
                "Booking alerts",
                "Team messaging",
                "Custom workflows",
                "Message formatting"
            ],
            "pricing": {
                "type": "free",
                "basePrice": 0,
                "currency": "USD",
                "features": []
            },
            "rating": 4.8,
            "reviewCount": 654,
            "developer": "Slack Technologies",
            "version": "1.2.0",
            "status": "active",
            "documentation": "https://api.slack.com",
            "supportUrl": "https://slack.com/help",
            "regions": ["US", "CA", "UK", "EU"],
            "supportedLanguages": ["en"],
            "requirements": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert services
    try:
        result = db.marketplace_services.insert_many(services)
        print(f"✅ Inserted {len(result.inserted_ids)} marketplace services")
        return result.inserted_ids
    except Exception as e:
        print(f"❌ Error inserting marketplace services: {e}")
        return []


if __name__ == "__main__":
    Database.connect_db()
    seed_marketplace_services()
    print("✅ Marketplace services seeded successfully")
