# Multi-Browser Session Fix - Complete Solution (Updated)

## Problem Summary

When opening a second browser on the same `localhost:3000` port while already logged in on another browser, the second browser would get stuck in an infinite redirect loop with continuous 401 errors:

```
[TenantContext] Final - tenant_id: None, user_id: None
GET /api/v1/auth/me - 401
Cannot log audit event without tenant_id
```

## Root Cause Analysis

The issue had **two parts**:

### Part 1: Middleware Cookie Extraction (FIXED)
The backend middleware was trying to extract `tenant_id` and `user_id` from separate cookies instead of from the JWT token:
- Cookies are **per-browser**, not per-domain
- Browser B has no cookies (it's a fresh browser instance)
- Middleware couldn't find `tenant_id` or `user_id` in cookies → returned 401

**Solution**: Updated `tenant_context.py` to extract `tenant_id` and `user_id` from the JWT token payload instead of relying on separate cookies.

### Part 2: Frontend 401 Redirect Loop (FIXED)
The API client's response interceptor was causing an infinite redirect loop using `window.location.href`:
- Browser B calls `/auth/me` during initialization → gets 401
- API interceptor saw 401 → redirected to `/auth/login` with `window.location.href` (hard redirect, bypasses React Router)
- But `useInitializeAuth` was still running → called `/auth/me` again
- Got 401 again → redirected again → **infinite loop**

**Solution**: 
1. Deferred 401 handling until after auth initialization completes
2. Replaced `window.location.href` with React Router's `useNavigate` for proper SPA navigation
3. Used a callback pattern to communicate between API interceptor and React Router

## Implementation Details

### Backend Changes: `backend/app/middleware/tenant_context.py`

The middleware now:
1. First tries to extract `tenant_id` and `user_id` from JWT token in `access_token` cookie
2. Falls back to separate cookies if JWT extraction fails
3. Properly handles both authenticated and unauthenticated requests

```python
# Extract from JWT token first
if access_token:
    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if not tenant_id:
            tenant_id = payload.get("tenant_id")
        if not user_id:
            user_id = payload.get("sub")
    except JWTError as e:
        logger.warning(f"Failed to decode JWT token: {e}")

# Fallback to cookies
if not tenant_id:
    tenant_id = request.cookies.get("tenant_id")
if not user_id:
    user_id = request.cookies.get("user_id")
```

### Frontend Changes: `salon/src/lib/utils/api.ts`

The API client now:
1. **Does NOT redirect on 401 during initialization**
2. Uses a callback pattern to communicate with React Router
3. Prevents redirect loops by deferring 401 handling

```typescript
// Store for navigation callback (set by App component)
let navigationCallback: ((path: string) => void) | null = null;

export function setNavigationCallback(callback: (path: string) => void) {
  navigationCallback = callback;
}

// In response interceptor:
if (error.response?.status === 401) {
  localStorage.removeItem("tenantId");
  
  // Use navigation callback if available (set after auth initialization)
  if (navigationCallback) {
    navigationCallback("/auth/login");
  }
}
```

### Frontend Changes: `salon/src/App.tsx`

The AppContent component now:
1. Waits for auth initialization to complete
2. Sets up a navigation callback using React Router's `useNavigate` **after** initialization
3. Only redirects to login if user is actually unauthenticated
4. Uses proper SPA navigation instead of hard redirects

```typescript
function AppContent() {
  const { isLoading } = useInitializeAuth();
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  // Setup navigation callback after auth initialization
  React.useEffect(() => {
    if (!isLoading) {
      const { setNavigationCallback } = require("@/lib/utils/api");
      
      setNavigationCallback((path: string) => {
        // Only redirect if user is not authenticated
        if (!user) {
          navigate(path);
        }
      });
    }
  }, [isLoading, user, navigate]);
```

## How It Works Now

### Scenario: Browser A logged in, Browser B opens

1. **Browser B loads** → `useInitializeAuth` runs
2. **Calls `/auth/me`** → No cookies in Browser B → Backend returns 401
3. **API interceptor catches 401** → Checks if `navigationCallback` exists
   - It doesn't exist yet (still initializing) → Does nothing
4. **`useInitializeAuth` catches error** → Sets user to null gracefully
5. **Initialization completes** → `AppContent` sets up `navigationCallback` with `useNavigate`
6. **User sees login page** (not redirect loop)
7. **User logs in on Browser B** → Gets new cookies and JWT token
8. **Browser B now works independently** with its own session

### Scenario: User gets 401 after initialization (token expired)

1. **User makes API call** → Token expired → Backend returns 401
2. **API interceptor catches 401** → Calls `navigationCallback`
3. **Callback uses `navigate()` from React Router** → Navigates to `/auth/login`
4. **User sees login page** (clean SPA navigation, no hard redirect)

## Key Improvements

✅ **Multi-browser support**: Each browser can have its own independent session
✅ **No redirect loops**: 401 handling is deferred until after initialization
✅ **React Router integration**: Uses `useNavigate` instead of `window.location.href`
✅ **Proper SPA navigation**: Maintains React Router state and history
✅ **Graceful degradation**: Unauthenticated users see login page, not errors
✅ **JWT-based context**: Tenant context extracted from JWT, not separate cookies
✅ **Proper error handling**: Middleware logs JWT decode failures but continues

## Testing

To verify the fix works:

1. **Browser A**: Log in successfully
2. **Browser B**: Open same `localhost:3000` in a different browser
3. **Expected**: Browser B shows login page (not redirect loop)
4. **Browser B**: Log in with same or different account
5. **Expected**: Both browsers work independently with their own sessions
6. **Token expiry**: Wait for token to expire or manually expire it
7. **Expected**: Clean redirect to login page using React Router navigation

## Files Modified

- `backend/app/middleware/tenant_context.py` - JWT token extraction
- `salon/src/lib/utils/api.ts` - Callback-based 401 handling with React Router integration
- `salon/src/App.tsx` - Navigation callback setup using `useNavigate`
