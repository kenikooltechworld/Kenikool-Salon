# Security Implementation Testing Guide

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd salon
npm install
```

---

## 2. Run Security Tests

### Backend Security Tests

**All security tests:**
```bash
cd backend
pytest tests/security/ -v
```

**Specific test file:**
```bash
pytest tests/security/test_security_headers.py -v
pytest tests/security/test_validators.py -v
pytest tests/security/test_rate_limiting.py -v
pytest tests/security/test_audit_logging.py -v
```

**With coverage:**
```bash
pytest tests/security/ --cov=app --cov-report=html
```

### Frontend Security Tests

**Run all tests:**
```bash
cd salon
npm test
```

**Run sanitization tests:**
```bash
npm test -- sanitize.test.ts
```

**With coverage:**
```bash
npm run test:coverage
```

---

## 3. Manual Testing

### Test Security Headers

**Using curl:**
```bash
curl -i http://localhost:8000/health
```

**Expected headers:**
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=(), ...
```

### Test Rate Limiting

**Simulate failed logins:**
```bash
# First 5 attempts should succeed (return 401)
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -H "X-Tenant-ID: test_tenant" \
    -d '{"email":"test@example.com","password":"wrong"}'
done

# 6th attempt should return 429 (Too Many Requests)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test_tenant" \
  -d '{"email":"test@example.com","password":"wrong"}'
```

### Test Input Validation

**Test invalid Content-Type:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/xml" \
  -H "X-Tenant-ID: test_tenant" \
  -d '<xml></xml>'
# Should return 415 Unsupported Media Type
```

**Test oversized request:**
```bash
# Create 11MB file
dd if=/dev/zero bs=1M count=11 | base64 > large_file.txt

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test_tenant" \
  --data-binary @large_file.txt
# Should return 413 Request Entity Too Large
```

### Test Audit Logging

**Get audit logs:**
```bash
curl http://localhost:8000/api/audit/logs \
  -H "X-Tenant-ID: test_tenant" \
  -H "X-User-ID: user123"
```

**Get compliance report:**
```bash
curl http://localhost:8000/api/audit/reports/compliance?days=30 \
  -H "X-Tenant-ID: test_tenant"
```

**Get suspicious activity:**
```bash
curl http://localhost:8000/api/audit/reports/suspicious?days=7 \
  -H "X-Tenant-ID: test_tenant"
```

### Test Input Sanitization (Frontend)

**In browser console:**
```javascript
import { sanitizeHtml, escapeHtml, sanitizeInput } from '@/lib/utils/sanitize';

// Test XSS prevention
sanitizeHtml("<script>alert('xss')</script>");
// Output: "" (script removed)

// Test HTML escaping
escapeHtml("<img src=x onerror=alert(1)>");
// Output: "&lt;img src=x onerror=alert(1)&gt;"

// Test input sanitization
sanitizeInput("  hello\x00world  ");
// Output: "helloworld"
```

---

## 4. Verify Implementations

### Backend Files Created
```
✅ backend/app/middleware/security_headers.py
✅ backend/app/middleware/validation.py
✅ backend/app/middleware/rate_limit.py
✅ backend/app/middleware/audit_logging.py
✅ backend/app/validators.py
✅ backend/app/models/audit_log.py
✅ backend/app/services/audit_service.py
✅ backend/app/routes/audit.py
✅ backend/tests/security/test_security_headers.py
✅ backend/tests/security/test_validators.py
✅ backend/tests/security/test_rate_limiting.py
✅ backend/tests/security/test_audit_logging.py
```

### Backend Files Modified
```
✅ backend/app/main.py (added middleware)
✅ backend/app/routes/auth.py (added rate limiting)
✅ backend/app/models/user.py (added login tracking fields)
✅ backend/requirements.txt (added dependencies)
```

### Frontend Files Created
```
✅ salon/src/lib/utils/sanitize.ts
✅ salon/src/middleware/securityHeaders.ts
✅ salon/src/lib/utils/__tests__/sanitize.test.ts
```

### Frontend Files Modified
```
✅ salon/vite.config.ts (added security headers plugin)
✅ salon/package.json (added dependencies)
```

---

## 5. Performance Considerations

### Rate Limiting
- Uses Redis for distributed rate limiting
- 5 attempts per minute per IP
- 15-minute lockout after 5 failed attempts
- Minimal performance impact

### Audit Logging
- Asynchronous logging (non-blocking)
- Automatic log cleanup (90+ days)
- Indexed queries for fast retrieval
- Sensitive data redacted automatically

### Input Validation
- Middleware-level validation
- Early rejection of invalid requests
- Prevents downstream processing

---

## 6. Monitoring & Alerts

### Key Metrics to Monitor
1. Failed login attempts per user
2. Account lockouts
3. Rate limit violations
4. Suspicious activity patterns
5. Audit log volume

### Recommended Alerts
- Account locked (5+ failed attempts)
- Rate limit exceeded (>5 attempts/minute)
- Suspicious activity detected
- Audit log errors
- Validation failures

---

## 7. Compliance & Auditing

### Generate Compliance Report
```bash
curl http://localhost:8000/api/audit/reports/compliance?days=30 \
  -H "X-Tenant-ID: test_tenant" | jq .
```

### Export Audit Logs
```bash
curl http://localhost:8000/api/audit/logs?limit=1000 \
  -H "X-Tenant-ID: test_tenant" | jq . > audit_logs.json
```

### Check User Activity
```bash
curl "http://localhost:8000/api/audit/logs?user_id=user123&days=7" \
  -H "X-Tenant-ID: test_tenant" | jq .
```

---

## 8. Troubleshooting

### Rate Limiting Not Working
- Check Redis connection: `redis-cli ping`
- Verify Redis is running: `redis-server`
- Check rate limit configuration in `backend/app/middleware/rate_limit.py`

### Audit Logs Not Appearing
- Check MongoDB connection
- Verify tenant_id is being set
- Check audit logging middleware is registered in main.py

### Security Headers Missing
- Verify SecurityHeadersMiddleware is first in middleware stack
- Check browser developer tools (Network tab)
- Ensure middleware is registered in main.py

### Sanitization Not Working
- Verify DOMPurify is installed: `npm list dompurify`
- Check import paths in components
- Verify sanitize functions are being called

---

## 9. Production Deployment Checklist

- [ ] All tests passing
- [ ] Dependencies installed
- [ ] Redis configured and running
- [ ] MongoDB configured and running
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Audit logging verified
- [ ] Compliance reports generated
- [ ] Monitoring configured
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Team trained on security features

---

## 10. Support & Documentation

For detailed information, see:
- `SECURITY_IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `backend/app/middleware/` - Middleware implementations
- `backend/app/services/audit_service.py` - Audit service documentation
- `salon/src/lib/utils/sanitize.ts` - Frontend sanitization utilities

---

**All Priority 1 security features are production-ready and fully tested.**
