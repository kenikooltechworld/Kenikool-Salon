# PostgreSQL Migration Analysis — KenikoolSalon

## Executive Summary

**Current database**: MongoDB (Atlas)  
**Proposed target**: PostgreSQL  
**Recommendation**: **Do not migrate now.** The project is tightly coupled to MongoDB with no repository abstraction. A full migration would require rewriting ~60 document classes, 55+ service files, and 25+ scripts. Instead: **fix critical bugs first, add a repository layer, and defer migration until it becomes a business necessity.**

---

## 1. Current State Audit

### 1.1 Database Configuration
| Aspect | Detail |
|--------|--------|
| **Type** | MongoDB (Atlas) |
| **ODM** | mongoengine |
| **Connection** | `mongoengine.connect()` with retry logic |
| **Config** | `DATABASE_URL`, `DATABASE_NAME` env vars |
| **Multi-tenancy** | Manual `tenant_id` on every collection |

### 1.2 Model Inventory
- **48 model files** defining **~60 document classes**
- All inherit from `mongoengine.Document` via `BaseDocument`
- Base model provides `tenant_id`, `created_at`, `updated_at` with auto-timestamp

### 1.3 Key MongoDB-Specific Features in Use
| Feature | Usage | Count |
|---------|-------|-------|
| `unique_with` | Compound unique constraints | 7 models |
| `DictField` | Flexible JSON storage | ~15 models |
| `EmbeddedDocument` | Nested line items | 9 embedded classes |
| `DecimalField` | Exact decimal precision | Widespread |
| `ListField` | Arrays of scalars/ObjectIds | Widespread |
| TTL index | Auto-expiry for `temp_registrations` | 1 |
| Aggregation pipelines | Analytics in `owner_dashboard_service.py` | 5 pipelines |
| Raw `bson.ObjectId` | Type-safe ID construction | 80+ files |
| Raw `bson.Decimal128` | Financial precision (`gift_card_service.py`) | 1+ files |
| `pymongo.IndexModel` | Custom index definitions (`service_addon.py`) | 1 file |

### 1.4 Data Access Patterns
- **No repository layer** — services call `Model.objects(Q(...))` directly
- **Tight coupling** — 80+ files import `mongoengine` directly
- **Q-objects** used extensively for complex queries across ~50 service files
- **Raw aggregation** in `owner_dashboard_service.py` using `$match`, `$group`, `$cond`, `$switch`, `$project`, `$divide`, `$subtract`, `$sum`, `$min`

### 1.5 Seeds & Migrations
- **Seeds**: 3 scripts + 1 orchestrator (`seed_pricing_plans.py`, `seed_staff_availability.py`, `seed_test_user.py`, `run_all_seeds.py`)
- **Migrations**: 5 in `backend/migrations/` + ~25 ad-hoc maintenance scripts
- **Index management**: `app/models/indexes.py` + `create_missing_indexes.py`

### 1.6 Critical Bug Found
**Async/Beanie Inconsistency** (High Risk):
- 3 services + 1 route use `await Model.find_one(...)`, `await model.insert()`, `.to_list()` — **Beanie/Motor API**
- Models inherit from `mongoengine.Document` — these methods **do not exist** on mongoengine models
- **Result**: Runtime `AttributeError` when these code paths execute
- Affected files: `gift_card_service.py`, `recommendation_service.py`, `service_package_service.py`, `routes/gift_cards.py`

---

## 2. PostgreSQL Migration: What It Would Take

### 2.1 Estimated Effort
| Component | Effort | Complexity |
|-----------|--------|------------|
| 48 model rewrites | 3–4 weeks | High |
| 55+ service query rewrites | 2–3 weeks | High |
| 5 aggregation pipelines | 1 week | High |
| 25+ migration/seed scripts | 1–2 weeks | Medium |
| Async/Beanie bug fix + rewrite | 3–5 days | Medium |
| Repository layer + interfaces | 1 week | Medium |
| Docker-compose + config updates | 1–2 days | Low |
| **Testing & data validation** | **2–3 weeks** | **High** |
| **Total** | **10–14 weeks** | — |

### 2.2 Technical Challenges

#### 2.2.1 Models
- Every `ObjectIdField` → `UUID` or `String` (or keep `ObjectId` via `sqlalchemy.dialects.postgresql`)
- `DecimalField` → `Numeric(10,2)` with Python `Decimal`
- `DictField` → `JSONB`
- `ListField` → `ARRAY` types or join tables for relationships
- `EmbeddedDocument` → separate tables or `JSONB`
- `unique_with` → composite `UniqueConstraint`
- TTL indexes → `pg_cron` jobs or application-level cleanup

#### 2.2.2 Relationships
- Current: Manual `ObjectIdField` references + application-level joins
- PostgreSQL: Foreign keys with `ON DELETE CASCADE`, `ON UPDATE CASCADE`
- No `$lookup` in current code, but embedded documents become joins

#### 2.2.3 Queries
- `Model.objects(Q(...))` → SQLAlchemy `select().where(and_(...))`
- `.first()` → `.scalar_one_or_none()`
- `.count()` → `func.count()`
- `.skip().limit().order_by()` → `.offset().limit().order_by()`
- `.update()` → `update().where()`
- `.delete()` → `delete().where()`

#### 2.2.4 Aggregation Pipelines
`owner_dashboard_service.py` requires full SQL rewrite:
```python
# MongoDB
db.command({
    '$match': {'tenant_id': tenant_id, 'status': 'completed'},
    '$group': {
        '_id': '$service_id',
        'revenue': {'$sum': '$amount'},
        'count': {'$sum': 1}
    }
})

# PostgreSQL (SQLAlchemy)
stmt = select(
    Appointment.service_id,
    func.sum(Appointment.amount).label('revenue'),
    func.count().label('count')
).where(
    Appointment.tenant_id == tenant_id,
    Appointment.status == 'completed'
).group_by(Appointment.service_id)
```

#### 2.2.5 Multi-Tenancy
- Current: Row-level `tenant_id` filtering
- PostgreSQL options:
  - **Shared database, shared schema** (current pattern, easiest migration)
  - **Schema per tenant** (cleaner isolation, harder migration)
  - **Database per tenant** (maximum isolation, highest ops cost)

---

## 3. Recommended Path Forward

### Phase 0: Stabilize (1–2 weeks) — Do this regardless
1. **Fix async/Beanie bug** — rewrite 4 files to use mongoengine properly or convert to sync
2. **Add repository interfaces** — define abstract base classes for each domain
3. **Add SQLModel/SQLAlchemy** to `requirements.txt` alongside mongoengine (no code changes yet)
4. **Set up PostgreSQL in docker-compose** (run alongside MongoDB, unused)

### Phase 1: Dual-Write (2–3 weeks)
- Create PostgreSQL models + repositories for **one simple domain** (e.g., `PricingPlan`)
- Write to both MongoDB and PostgreSQL
- Read from PostgreSQL only (feature-flagged)

### Phase 2: Domain-by-Domain Migration (6–8 weeks)
Migrate one bounded context at a time:
1. PricingPlan, VideoTestimonial, BookingActivity
2. Service, ServiceCategory, ServiceAddon
3. Customer, Staff, User, Role
4. Appointment, TimeSlot, Availability
5. Payment, Invoice, Receipt, Transaction
6. Notification, Membership, GiftCard
7. Resource, Inventory, Commission
8. Owner dashboard analytics

### Phase 3: Cutover (1 week)
- Stop writing to MongoDB
- Validate data consistency
- Remove mongoengine

### Phase 4: Cleanup (1 week)
- Remove MongoDB from docker-compose
- Remove migration scripts
- Update documentation

---

## 4. Why Not Migrate Now?

1. **No pressing pain**: MongoDB works for this app's current needs
2. **High cost, low urgency**: 10–14 weeks of engineering for architectural improvement, not user-facing features
3. **Active codebase**: 50+ models and 55+ services are changing — migrating stable code is easier
4. **Async bug needs fixing anyway**: That bug blocks production reliability regardless of database
5. **Team velocity**: Full migration would dominate the roadmap for months

**Better strategy**: Fix the async bug, add repository abstraction, set up PostgreSQL alongside, and migrate incrementally when:
- A specific domain needs complex SQL queries/reporting
- Team is ready to invest 3+ months
- MongoDB costs or limitations become blockers

---

## 5. PostgreSQL Advantages for This Project

| Area | Benefit |
|------|---------|
| **Financial data** | ACID transactions for payments, invoices, receipts |
| **Inventory** | Row-level locking prevents overselling |
| **Reporting** | SQL `GROUP BY` / window functions for analytics |
| **Relationships** | Foreign keys ensure referential integrity |
| **Migrations** | Alembic tracks schema changes declaratively |
| **Tooling** | pgAdmin, Supabase, PostgREST, Hasura |
| **Typing** | Strong schema enforcement at DB level |

---

## 6. Risks of Migration

| Risk | Mitigation |
|------|------------|
| Data loss during migration | Dual-write + read replica validation |
| Performance regression | Load test PostgreSQL with production data shape |
| Broken queries | Comprehensive integration test suite |
| Long downtime | Blue-green deployment with feature flags |
| Team knowledge gap | SQLAlchemy training + pair programming |

---

## 7. Decision Matrix

| Scenario | Action |
|----------|--------|
| Startup / MVP phase | **Stay on MongoDB** — speed to market matters |
| Hitting MongoDB limits (data size, query complexity) | **Start Phase 1** (dual-write) |
| Need complex financial/reporting queries | **Migrate financial domains first** |
| Team comfortable with SQL | **Full migration feasible** |
| Production data at risk from async bug | **Fix bug immediately** |

---

*Document generated: 2026-09-17*
