// MongoDB initialization script
db = db.getSiblingDB('salon_saas');

// Create collections with indexes for better performance
db.createCollection('users');
db.createCollection('tenants');
db.createCollection('bookings');
db.createCollection('services');
db.createCollection('clients');
db.createCollection('staff');
db.createCollection('payments');
db.createCollection('inventory');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "tenant_id": 1 });
db.tenants.createIndex({ "domain": 1 }, { unique: true });
db.bookings.createIndex({ "tenant_id": 1, "date": 1 });
db.bookings.createIndex({ "client_id": 1 });
db.bookings.createIndex({ "staff_id": 1 });
db.services.createIndex({ "tenant_id": 1 });
db.clients.createIndex({ "tenant_id": 1, "email": 1 });
db.staff.createIndex({ "tenant_id": 1, "email": 1 });
db.payments.createIndex({ "tenant_id": 1, "created_at": 1 });
db.inventory.createIndex({ "tenant_id": 1 });

print('Database initialized successfully');