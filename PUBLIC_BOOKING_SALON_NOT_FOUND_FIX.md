# Public Booking "Salon Not Found" Fix

## Problem
When accessing the public booking page at `kenzola-salon.localhost:3000`, users were getting a "Salon Not Found" error even though the salon exists in the database.

## Root Causes

### 1. Tenant ID Not Set in Request Scope
**Issue**: The `SubdomainContextMiddleware` was setting `tenant_id` in `request.state`, but downstream middleware and endpoints were reading from `request.scope`.

**Files affected**:
- `backend/app/middleware/subdomain_context.py`
- `backend/app/middleware/tenant_context.py`

**Fix**: Updated both middleware to set `tenant_id` in both `request.state` AND `request.scope`:
```python
request.scope["tenant_id"] = tenant_id_str
```

### 2. Subdomain Not Extracted for Localhost with Subdomains
**Issue**: The subdomain extraction logic didn't handle `kenzola-salon.localhost` correctly. It was checking if hostname starts with "localhost", which failed for `kenzola-salon.localhost`.

**File affected**: `backend/app/middleware/subdomain_context.py`

**Fix**: 
- Changed the check from `hostname.startswith("localhost")` to `hostname_without_port == "localhost"`
- Updated `_extract_subdomain()` to handle localhost subdomains:
  ```python
  if len(parts) == 2:
      if parts[1] == "localhost":
          return parts[0]  # Return subdomain for localhost
      return ""  # No subdomain for regular domains
  ```

### 3. Host Header Lost in Vite Proxy
**Issue**: When Vite proxies requests from `kenzola-salon.localhost:3000` to `http://localhost:8000`, the Host header was being changed to `localhost:8000`, losing the subdomain information.

**File affected**: `salon/vite.config.ts`

**Fix**: 
- Changed `changeOrigin: true` to `changeOrigin: false` to preserve the original Host header
- Updated backend middleware to check `X-Forwarded-Host` header as fallback:
  ```python
  hostname = (
      request.headers.get("x-forwarded-host") or 
      request.headers.get("host", "")
  ).lower()
  ```

### 4. Missing Tenant Fields for Public Booking
**Issue**: The `get_salon_info` endpoint tried to access `description`, `email`, `logo_url`, `primary_color`, and `secondary_color` fields that didn't exist on the Tenant model.

**File affected**: `backend/app/models/tenant.py`

**Fix**: Added missing fields to the Tenant model:
```python
email = StringField(null=True, max_length=255)
description = StringField(null=True, max_length=1000)
logo_url = StringField(null=True, max_length=500)
primary_color = StringField(null=True, max_length=7)  # Hex color code
secondary_color = StringField(null=True, max_length=7)  # Hex color code
```

## Files Modified

1. **backend/app/middleware/subdomain_context.py**
   - Fixed subdomain extraction for localhost
   - Added support for X-Forwarded-Host header
   - Set tenant_id in request.scope

2. **backend/app/middleware/tenant_context.py**
   - Set tenant_id in request.scope for consistency

3. **salon/vite.config.ts**
   - Changed proxy configuration to preserve Host header

4. **backend/app/models/tenant.py**
   - Added email, description, logo_url, primary_color, secondary_color fields

## Testing

To verify the fix works:

1. Ensure a tenant with subdomain "kenzola-salon" exists and is published
2. Access `kenzola-salon.localhost:3000` in your browser
3. The public booking page should load with the salon information

## Subdomain Extraction Examples

After the fix, subdomain extraction works correctly for:
- `acme-salon.kenikool.com` → `acme-salon`
- `kenzola-salon.localhost` → `kenzola-salon`
- `localhost` → (no subdomain, allowed)
- `kenikool.com` → (no subdomain, allowed)
