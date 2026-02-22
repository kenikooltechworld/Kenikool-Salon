#!/usr/bin/env python3
"""
Script to add sample salon data to the database for marketplace testing
"""
import os
import sys
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings

def add_sample_salons():
    """Add sample salon data to MongoDB"""
    try:
        # Connect to MongoDB
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB_NAME]
        
        print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
        # Sample salons data
        sample_salons = [
            {
                "name": "Glam Hair Studio",
                "description": "Premium hair styling and beauty services",
                "location": {
                    "latitude": 6.5244,
                    "longitude": 3.3792,
                    "address": "123 Lekki Phase 1, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 801 234 5678",
                "email": "info@glamhair.com",
                "rating": 4.8,
                "review_count": 156,
                "image_url": "https://via.placeholder.com/400x300?text=Glam+Hair+Studio",
                "services_count": 12,
                "staff_count": 8,
                "is_verified": True,
                "starting_price": 5000,
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Beauty Haven Salon",
                "description": "Full-service beauty salon with experienced stylists",
                "location": {
                    "latitude": 6.5200,
                    "longitude": 3.3850,
                    "address": "456 Victoria Island, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 802 345 6789",
                "email": "contact@beautyhaven.com",
                "rating": 4.6,
                "review_count": 98,
                "image_url": "https://via.placeholder.com/400x300?text=Beauty+Haven",
                "services_count": 15,
                "staff_count": 10,
                "is_verified": True,
                "starting_price": 4500,
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Elegant Nails & Spa",
                "description": "Nail art, spa treatments, and relaxation services",
                "location": {
                    "latitude": 6.5150,
                    "longitude": 3.3900,
                    "address": "789 Ikoyi, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 803 456 7890",
                "email": "bookings@elegantnails.com",
                "rating": 4.7,
                "review_count": 124,
                "image_url": "https://via.placeholder.com/400x300?text=Elegant+Nails",
                "services_count": 20,
                "staff_count": 12,
                "is_verified": True,
                "starting_price": 3500,
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Prestige Hair Lounge",
                "description": "Luxury hair care and styling for all hair types",
                "location": {
                    "latitude": 6.5300,
                    "longitude": 3.3700,
                    "address": "321 Banana Island, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 804 567 8901",
                "email": "hello@prestigehair.com",
                "rating": 4.9,
                "review_count": 203,
                "image_url": "https://via.placeholder.com/400x300?text=Prestige+Hair",
                "services_count": 18,
                "staff_count": 14,
                "is_verified": True,
                "starting_price": 6000,
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Urban Beauty Bar",
                "description": "Modern salon with trendy styles and expert colorists",
                "location": {
                    "latitude": 6.5100,
                    "longitude": 3.3950,
                    "address": "654 Ajah, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 805 678 9012",
                "email": "style@urbanbeauty.com",
                "rating": 4.5,
                "review_count": 87,
                "image_url": "https://via.placeholder.com/400x300?text=Urban+Beauty",
                "services_count": 16,
                "staff_count": 9,
                "is_verified": True,
                "starting_price": 4000,
                "created_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Radiant Skin & Beauty",
                "description": "Skincare, facials, and beauty treatments",
                "location": {
                    "latitude": 6.5250,
                    "longitude": 3.3800,
                    "address": "987 Surulere, Lagos",
                    "city": "Lagos",
                    "state": "Lagos"
                },
                "phone": "+234 806 789 0123",
                "email": "glow@radiantskin.com",
                "rating": 4.7,
                "review_count": 142,
                "image_url": "https://via.placeholder.com/400x300?text=Radiant+Skin",
                "services_count": 14,
                "staff_count": 7,
                "is_verified": True,
                "starting_price": 5500,
                "created_at": datetime.utcnow(),
                "is_active": True
            }
        ]
        
        # Check if salons collection exists and has data
        existing_count = db.salons.count_documents({})
        print(f"Existing salons in database: {existing_count}")
        
        if existing_count == 0:
            # Insert sample salons
            result = db.salons.insert_many(sample_salons)
            print(f"✅ Added {len(result.inserted_ids)} sample salons to the database")
            
            # Print inserted IDs
            for i, salon_id in enumerate(result.inserted_ids):
                print(f"   - {sample_salons[i]['name']}: {salon_id}")
        else:
            print("⚠️  Database already has salons. Skipping insertion.")
            print("   To add more salons, delete existing ones first or modify this script.")
        
        client.close()
        print("✅ Sample salons added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding sample salons: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_sample_salons()
