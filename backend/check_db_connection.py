from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME', 'kenikool-salon')
local_url = os.getenv('DATABASE_URL', 'mongodb://salon_mongodb:27017/kenikool-salon')
atlas_url = os.getenv('DATABASE_URL_ATLAS', 'mongodb+srv://kenikooltechworld_salon:Kenikool_salon@kenikool.jvxeptt.mongodb.net/kenikool-salon?appName=Kenikool')

print("=" * 60)
print("CHECKING DATABASE CONNECTIONS")
print("=" * 60)

# Try local
print("\n1. Trying LOCAL MongoDB (salon_mongodb:27017)...")
try:
    client = MongoClient(local_url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[database_name]
    collections = db.list_collection_names()
    print(f"   ✓ LOCAL MongoDB is CONNECTED")
    print(f"   Database: {database_name}")
    print(f"   Collections: {collections}")
    print(f"   Total collections: {len(collections)}")
except Exception as e:
    print(f"   ✗ LOCAL MongoDB FAILED: {str(e)[:100]}")

# Try Atlas
print("\n2. Trying MONGODB ATLAS...")
try:
    client = MongoClient(atlas_url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[database_name]
    collections = db.list_collection_names()
    print(f"   ✓ MONGODB ATLAS is CONNECTED")
    print(f"   Database: {database_name}")
    print(f"   Collections: {collections}")
    print(f"   Total collections: {len(collections)}")
except Exception as e:
    print(f"   ✗ MONGODB ATLAS FAILED: {str(e)[:100]}")

print("\n" + "=" * 60)
