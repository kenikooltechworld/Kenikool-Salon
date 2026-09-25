from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME')
atlas_url = os.getenv('DATABASE_URL')

if not atlas_url or not database_name:
    raise RuntimeError("DATABASE_URL and DATABASE_NAME are required. Set them in backend/.env")

print("=" * 60)
print("CHECKING MONGODB ATLAS CONNECTION")
print("=" * 60)

# Try Atlas
print(f"\nConnecting to MongoDB Atlas: {database_name}...")
try:
    client = MongoClient(atlas_url, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[database_name]
    collections = db.list_collection_names()
    print(f"   [OK] MONGODB ATLAS is CONNECTED")
    print(f"   Database: {database_name}")
    print(f"   Collections: {collections}")
    print(f"   Total collections: {len(collections)}")
except Exception as e:
    print(f"   [FAIL] MONGODB ATLAS FAILED: {str(e)[:100]}")

print("\n" + "=" * 60)
