#!/usr/bin/env python
"""Direct MongoDB query to check collections."""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment
database_name = os.getenv('DATABASE_NAME', 'kenikool-salon')
database_url = os.getenv('DATABASE_URL', 'mongodb://localhost:27017/')

# Connect to MongoDB
client = MongoClient(database_url)
db = client[database_name]

print("=" * 60)
print("MONGODB COLLECTIONS AND DOCUMENT COUNTS")
print("=" * 60)

collections = db.list_collection_names()
print(f"\nTotal collections: {len(collections)}\n")

for collection_name in sorted(collections):
    collection = db[collection_name]
    count = collection.count_documents({})
    print(f"  {collection_name}: {count} documents")

print("\n" + "=" * 60)
print("CHECKING FOR kenikoolsalon@gmail.com")
print("=" * 60)

# Check temp_registrations
temp_regs = db['temp_registrations'].find({'email': 'kenikoolsalon@gmail.com'})
temp_regs_list = list(temp_regs)
print(f"\ntemp_registrations: {len(temp_regs_list)} found")
if temp_regs_list:
    for doc in temp_regs_list:
        print(f"  - Salon: {doc.get('salon_name')}, Subdomain: {doc.get('subdomain')}")

# Check users
users = db['users'].find({'email': 'kenikoolsalon@gmail.com'})
users_list = list(users)
print(f"\nusers: {len(users_list)} found")
if users_list:
    for doc in users_list:
        print(f"  - Name: {doc.get('first_name')} {doc.get('last_name')}, Status: {doc.get('status')}")

# Check tenants
tenants = db['tenants'].find({'name': {'$regex': 'kenikool', '$options': 'i'}})
tenants_list = list(tenants)
print(f"\ntenants (matching 'kenikool'): {len(tenants_list)} found")
if tenants_list:
    for doc in tenants_list:
        print(f"  - Name: {doc.get('name')}, Subdomain: {doc.get('subdomain')}, Status: {doc.get('status')}")

print("\n" + "=" * 60)
