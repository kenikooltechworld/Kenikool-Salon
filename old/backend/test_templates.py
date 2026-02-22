#!/usr/bin/env python3
"""
Test booking templates
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Database
from bson import ObjectId

Database.connect_db()
db = Database.get_db()

# Check templates in database
templates = list(db.booking_templates.find({'tenant_id': ObjectId('507f1f77bcf86cd799439011')}))
print(f'Found {len(templates)} templates in database')

for template in templates:
    print(f'- {template["name"]} (ID: {template["_id"]})')
    print(f'  Description: {template.get("description", "N/A")}')
    print(f'  Category: {template.get("category", "N/A")}')
    print(f'  Duration: {template.get("duration", "N/A")} minutes')
    print(f'  Price: ${template.get("pricing", 0):.2f}')
    print(f'  Services: {len(template.get("services", []))} service(s)')
    print()

Database.close_db()