"""Test MongoDB Atlas connection."""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_atlas_connection():
    """Test connection to MongoDB Atlas."""
    
    # Get connection string from environment
    atlas_url = os.getenv(
        'DATABASE_URL_ATLAS',
        'mongodb+srv://kenikooltechworld_salon:Kenikool_salon@kenikool.jvxeptt.mongodb.net/kenikool-salon?appName=Kenikool'
    )
    
    print(f"Testing connection to MongoDB Atlas...")
    print(f"Connection string: {atlas_url[:50]}...")
    
    try:
        # Create client with short timeout
        client = MongoClient(
            atlas_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB Atlas!")
        
        # List databases
        dbs = client.list_database_names()
        print(f"✓ Available databases: {dbs}")
        
        # Check if our database exists
        db_name = 'kenikool-salon'
        if db_name in dbs:
            print(f"✓ Database '{db_name}' exists")
            
            # List collections
            db = client[db_name]
            collections = db.list_collection_names()
            print(f"✓ Collections in '{db_name}': {collections}")
        else:
            print(f"⚠ Database '{db_name}' does not exist yet (will be created on first write)")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"✗ Connection timeout - Cannot reach MongoDB Atlas")
        print(f"  Error: {e}")
        print("\nPossible causes:")
        print("  1. Network connectivity issues")
        print("  2. MongoDB Atlas IP whitelist (add 0.0.0.0/0 to allow all IPs)")
        print("  3. Incorrect credentials")
        return False
        
    except ConnectionFailure as e:
        print(f"✗ Connection failed")
        print(f"  Error: {e}")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    test_atlas_connection()
