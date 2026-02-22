# Missing Authentication Pages - Implementation Plan

## Overview
Based on the requirements and design documents, the following authentication pages are still needed. All pages must use **httpOnly cookies** for authentication (NOT Bearer tokens or Authorization headers).

## Missing Pages

### 1. Forgot Password Page
**Path:** `salon/src/pages/auth/ForgotPassword.tsx`

**Features:**
- Email input field
- Submit button to request password reset
- Success message showing email sent
- Link back to login
- Error handling for invalid email
- Loading state

**API Endpoint:** `POST /auth/forgot-password`
- Request: `{ email: string }`
- Response: `{ message: string, success: boolean }`

**Technical Details:**
- Send password reset link to email
- Link valid for 1 hour only
- User receives email with reset link

---

### 2. Reset Password Page
**Path:** `salon/src/pages/auth/ResetPassword.tsx`

**Features:**
- Extract reset token from URL query parameter
- New password input with strength indicator
- Confirm password input
- Submit button
- Error handling for invalid/expired token
- Success message with redirect to login
- Loading state

**API Endpoint:** `POST /auth/reset-password`
- Request: `{ token: string, password: string }`
- Response: `{ message: string, success: boolean }`

**Technical Details:**
- Validate token before allowing password change
- Hash new password with bcrypt
- Invalidate all existing sessions after password reset
- Redirect to login after success

---

### 3. MFA Setup Page
**Path:** `salon/src/pages/auth/MFASetup.tsx`

**Features:**
- Display MFA method selection (TOTP or SMS)
- For TOTP:
  - Display QR code
  - Display secret key (for manual entry)
  - Display backup codes
  - Verification code input (6 digits)
  - Confirm button
- For SMS:
  - Phone number input
  - Send OTP button
  - OTP input (6 digits)
  - Confirm button
- Error handling
- Loading states
- Success message with backup codes

**API Endpoints:**
- `POST /auth/mfa/setup` - Initiate MFA setup
  - Request: `{ method: "totp" | "sms", phone?: string }`
  - Response: `{ secret?: string, qr_code?: string, backup_codes?: string[] }`
- `POST /auth/mfa/verify-setup` - Verify MFA setup
  - Request: `{ method: string, code: string }`
  - Response: `{ success: boolean, backup_codes: string[] }`

**Technical Details:**
- Generate TOTP secret using pyotp
- Generate QR code for authenticator apps
- Generate backup codes (10 codes)
- Send SMS OTP via Twilio
- Store MFA settings in User model

---

### 4. MFA Verification Page
**Path:** `salon/src/pages/auth/MFAVerify.tsx`

**Features:**
- Display MFA method (TOTP or SMS)
- 6-digit code input with auto-focus
- Submit button
- "Didn't receive code?" link for SMS
- Resend code button with cooldown
- Error handling
- Loading state
- Backup code option (if available)

**API Endpoint:** `POST /auth/mfa/verify`
- Request: `{ email: string, code: string, method: "totp" | "sms" }`
- Response: `{ success: boolean, message: string }`

**Technical Details:**
- Verify TOTP code using pyotp
- Verify SMS OTP from Redis
- Allow backup codes as fallback
- Return full JWT token on success
- Set httpOnly cookies with tokens

---

### 5. Change Password Page
**Path:** `salon/src/pages/auth/ChangePassword.tsx`

**Features:**
- Current password input
- New password input with strength indicator
- Confirm password input
- Submit button
- Error handling
- Success message
- Loading state
- Redirect to dashboard after success

**API Endpoint:** `POST /auth/change-password`
- Request: `{ current_password: string, new_password: string }`
- Response: `{ message: string, success: boolean }`

**Technical Details:**
- Verify current password
- Validate new password strength
- Hash new password with bcrypt
- Invalidate all existing sessions
- Require re-login after password change

---

### 6. Account Settings/Profile Page
**Path:** `salon/src/pages/auth/AccountSettings.tsx`

**Features:**
- Display current user information
- Edit first name
- Edit last name
- Edit phone number
- Edit email (with verification)
- MFA settings toggle
- Change password link
- Logout button
- Delete account button (with confirmation)
- Loading states
- Success/error messages

**API Endpoints:**
- `GET /auth/me` - Get current user (already exists)
- `PUT /auth/me` - Update user profile
  - Request: `{ first_name?: string, last_name?: string, phone?: string }`
  - Response: `{ user: User, message: string }`
- `POST /auth/change-email` - Change email
  - Request: `{ new_email: string }`
  - Response: `{ message: string, verification_required: boolean }`
- `POST /auth/delete-account` - Delete account
  - Request: `{ password: string }`
  - Response: `{ message: string, success: boolean }`

**Technical Details:**
- Fetch user data on page load
- Update user profile in MongoDB
- Send verification email for email changes
- Require password confirmation for account deletion
- Soft delete user account (mark as deleted)

---

## Cookie-Based Authentication Implementation

### Key Points:
1. **httpOnly Cookies** - Tokens stored in httpOnly cookies (not accessible from JavaScript)
2. **Secure Flag** - Cookies only sent over HTTPS
3. **SameSite** - Set to "Strict" for CSRF protection
4. **Credentials** - Axios configured with `withCredentials: true`
5. **Headers** - Add `X-Tenant-ID` and `X-Session-ID` headers to requests
6. **No Authorization Header** - Don't use `Authorization: Bearer` header

### API Client Configuration:
```typescript
// Already updated in salon/src/lib/utils/api.ts
const client = axios.create({
  withCredentials: true, // Enable cookies
  headers: {
    "Content-Type": "application/json",
  },
});

// Add tenant ID and session ID headers
client.interceptors.request.use((config) => {
  const tenantId = localStorage.getItem("tenantId");
  if (tenantId) {
    config.headers["X-Tenant-ID"] = tenantId;
  }
  
  const sessionId = localStorage.getItem("sessionId");
  if (sessionId) {
    config.headers["X-Session-ID"] = sessionId;
  }
  
  return config;
});
```

### Backend Cookie Setup:
```python
# Already implemented in backend/app/routes/auth.py
response.set_cookie(
    key="access_token",
    value=access_token,
    max_age=auth_service.access_token_expire_minutes * 60,
    secure=True,  # HTTPS only
    httponly=True,  # Not accessible from JavaScript
    samesite="Strict",  # CSRF protection
    path="/",
)
```

---

## Updated App Router

The App.tsx router needs to be updated to include all new routes:

```typescript
<Route path="/auth/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
<Route path="/auth/reset-password" element={<PublicRoute><ResetPassword /></PublicRoute>} />
<Route path="/auth/mfa-setup" element={<ProtectedRoute><MFASetup /></ProtectedRoute>} />
<Route path="/auth/mfa-verify" element={<PublicRoute><MFAVerify /></PublicRoute>} />
<Route path="/auth/change-password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />
<Route path="/auth/account-settings" element={<ProtectedRoute><AccountSettings /></ProtectedRoute>} />
```

---

## Implementation Priority

1. **High Priority** (Required for MVP):
   - Forgot Password
   - Reset Password
   - MFA Verify (for users with MFA enabled)
   - Account Settings

2. **Medium Priority** (Important for security):
   - MFA Setup
   - Change Password

3. **Low Priority** (Nice to have):
   - Account deletion flow

---

## Testing Checklist

- [ ] Login with httpOnly cookies
- [ ] Cookies sent automatically with requests
- [ ] Forgot password email sent
- [ ] Reset password link works
- [ ] MFA setup with TOTP
- [ ] MFA setup with SMS
- [ ] MFA verification on login
- [ ] Change password invalidates sessions
- [ ] Account settings update user profile
- [ ] Logout clears cookies
- [ ] Unauthorized requests redirect to login
- [ ] MFA required redirects to MFA verify

---

## Summary

**Total Missing Pages:** 6
- Forgot Password
- Reset Password
- MFA Setup
- MFA Verify
- Change Password
- Account Settings

**Already Implemented:** 4
- Login (updated for cookies)
- Register
- Verify
- RegisterSuccess

**Total Auth Pages:** 10

All pages must use httpOnly cookies for authentication, not Bearer tokens or Authorization headers.
