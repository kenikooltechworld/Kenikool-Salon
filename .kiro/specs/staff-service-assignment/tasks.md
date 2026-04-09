# Staff Service Assignment Feature - Implementation Tasks

## Task List

### Phase 1: Backend Model & API Updates

- [ ] 1.1 Update Staff model with service_ids field
  - Add `service_ids: List[ObjectId]` field to Staff model
  - Set default to empty list
  - Add field to Staff schema

- [ ] 1.2 Create database index for service_ids
  - Create compound index on (tenant_id, service_ids)
  - Verify index creation

- [ ] 1.3 Update staff creation endpoint
  - Accept service_ids in request body
  - Validate service IDs exist and belong to tenant
  - Save service_ids with staff record

- [ ] 1.4 Update staff update endpoint
  - Accept service_ids in request body
  - Validate service IDs exist and belong to tenant
  - Update service_ids in staff record

- [ ] 1.5 Update staff list endpoint
  - Add service_id query parameter for filtering
  - Filter staff by service_ids array
  - Return filtered results

- [ ] 1.6 Update public staff endpoint
  - Add service_id query parameter (required)
  - Filter by service_ids, is_available_for_public_booking, status
  - Return only public fields

### Phase 2: Frontend Form Updates

- [ ] 2.1 Update Staff type definition
  - Add service_ids?: string[] field
  - Update type exports

- [ ] 2.2 Update StaffForm component
  - Add service_ids to form state
  - Add services state for available services
  - Add useEffect to fetch services on mount
  - Add handleServiceToggle function

- [ ] 2.3 Add Services section to form UI
  - Display after Roles section
  - Show checkboxes for each service
  - Display "No services available" message if empty
  - Pre-populate with existing service_ids when editing

- [ ] 2.4 Update form submission
  - Include service_ids in form data
  - Send service_ids to API

- [ ] 2.5 Test form functionality
  - Create staff with services
  - Edit staff services
  - Verify services persist

### Phase 3: Data Migration

- [ ] 3.1 Create migration script
  - Get all published services with allow_public_booking = True
  - For each staff with is_available_for_public_booking = True
  - Add service IDs to service_ids array
  - Log migration results

- [ ] 3.2 Make migration idempotent
  - Check if service_ids already populated
  - Skip if already migrated
  - Safe to run multiple times

- [ ] 3.3 Test migration
  - Run on test database
  - Verify all staff updated correctly
  - Verify no data loss

- [ ] 3.4 Run migration on production
  - Backup staff collection
  - Execute migration script
  - Verify results

### Phase 4: Public Booking Integration

- [ ] 4.1 Update StaffSelector component
  - Verify it filters by service_id
  - Verify empty state displays correctly
  - Verify toast notification shows

- [ ] 4.2 Test public booking flow
  - Select service in booking wizard
  - Verify staff list shows only assigned staff
  - Verify empty state if no staff assigned

- [ ] 4.3 Test empty state UX
  - Verify helpful message displays
  - Verify action buttons work
  - Verify toast notification appears

### Phase 5: Testing & Validation

- [ ] 5.1 Unit tests - Backend
  - Test staff creation with services
  - Test staff update with services
  - Test staff filtering by service
  - Test public staff filtering

- [ ] 5.2 Unit tests - Frontend
  - Test service toggle handler
  - Test service list rendering
  - Test empty state display
  - Test form submission

- [ ] 5.3 Integration tests
  - Test end-to-end staff creation with services
  - Test end-to-end staff editing with services
  - Test public booking staff filtering
  - Test empty state in public booking

- [ ] 5.4 Property-based tests
  - Test service assignment persistence
  - Test public booking filtering correctness
  - Test service filtering accuracy
  - Test migration data integrity

### Phase 6: Documentation & Deployment

- [ ] 6.1 Update API documentation
  - Document service_ids field
  - Document service_id query parameter
  - Document filtering behavior

- [ ] 6.2 Update user documentation
  - Document how to assign services to staff
  - Document how to edit staff services
  - Document public booking staff filtering

- [ ] 6.3 Create deployment guide
  - Document migration steps
  - Document rollback procedure
  - Document verification steps

- [ ] 6.4 Deploy to production
  - Run migration script
  - Deploy backend changes
  - Deploy frontend changes
  - Verify functionality

## Acceptance Criteria

### Feature Completion
- ✓ Staff can have services assigned during creation
- ✓ Staff can have services updated during editing
- ✓ Services are displayed as checkboxes in forms
- ✓ Multiple services can be selected per staff
- ✓ Service assignments persist correctly
- ✓ Public booking filters staff by service
- ✓ Empty state displays when no staff assigned
- ✓ Toast notification shows for empty state
- ✓ Migration populates existing staff with services
- ✓ All tests pass

### Performance
- ✓ Staff filtering by service completes in < 500ms
- ✓ Service list loads in < 1s
- ✓ Form submission completes in < 2s

### Quality
- ✓ No TypeScript errors
- ✓ No console errors
- ✓ All tests passing
- ✓ Code follows project conventions
- ✓ Documentation is complete

## Dependencies

- Staff model must be updated first
- Database index must be created before migration
- Backend API must be updated before frontend
- Migration must run before public booking testing

## Estimated Timeline

- Phase 1: 2-3 hours
- Phase 2: 2-3 hours
- Phase 3: 1-2 hours
- Phase 4: 1-2 hours
- Phase 5: 2-3 hours
- Phase 6: 1-2 hours

**Total**: 9-15 hours

## Notes

- All changes maintain backward compatibility
- Migration is safe and idempotent
- No breaking changes to existing APIs
- Existing staff without services will work normally
- Public booking will show empty state if no staff assigned
