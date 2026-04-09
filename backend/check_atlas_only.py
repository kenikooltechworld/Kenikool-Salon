from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME', 'kenikool-salon')
atlas_url = os.getenv('DATABASE_URL_ATLAS', 'mongodb+srv://kenikooltechworld_salon:Kenikool_salon@kenikool.jvxeptt.mongodb.net/kenikool-salon?appName=Kenikool')

print("Connecting to MONGODB ATLAS...")
try:
    client = MongoClient(atlas_url, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    
    # Check the configured database
    print(f"\nChecking '{database_name}' database:")
    db = client[database_name]
    cols = db.list_collection_names()
    print(f"  Collections: {cols}")
    for col in cols:
        count = db[col].count_documents({})
        print(f"    - {col}: {count} documents")
        
except Exception as e:
    print(f"ERROR: {e}")
