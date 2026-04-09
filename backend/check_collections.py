from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME', 'kenikool-salon')
database_url = os.getenv('DATABASE_URL', 'mongodb://localhost:27017/kenikool-salon')

client = MongoClient(database_url)
database = client[database_name]

collections = database.list_collection_names()
print('Collections in database:')
for col in collections:
    count = database[col].count_documents({})
    print(f'  - {col}: {count} documents')
