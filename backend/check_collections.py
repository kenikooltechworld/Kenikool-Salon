from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME')
database_url = os.getenv('DATABASE_URL')

if not database_url or not database_name:
    raise RuntimeError("DATABASE_URL and DATABASE_NAME are required. Set them in backend/.env")

client = MongoClient(database_url)
database = client[database_name]

collections = database.list_collection_names()
print('Collections in database:')
for col in collections:
    count = database[col].count_documents({})
    print(f'  - {col}: {count} documents')
