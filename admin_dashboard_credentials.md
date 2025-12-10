# Admin Dashboard Login Credentials

## ✅ Verified Working Credentials

### Superadmin (Full Access)
- **Email:** `superadmin@taxease.ca`
- **Password:** `demo123`
- **Role:** superadmin
- **Status:** ✅ Active and verified

### Admin (Standard Access)
- **Email:** `admin@taxease.ca`
- **Password:** `demo123`
- **Role:** admin
- **Status:** ✅ Active and verified

## 🌐 Access URLs

- **Frontend (Admin Dashboard):** http://localhost:8080
- **Backend API:** http://localhost:8002/api/v1
- **API Documentation:** http://localhost:8002/docs

## ✅ Verification

Both credentials have been tested and are working correctly:
- Backend login API returns valid tokens
- Passwords match database hashes
- Accounts are active

## 🔄 If Login Still Fails

If you're still getting "incorrect credentials" error:

1. **Clear Browser Cache:**
   - Open Developer Tools (F12)
   - Go to Application/Storage tab
   - Clear localStorage and cookies
   - Refresh the page

2. **Check Browser Console:**
   - Open Developer Tools (F12)
   - Go to Console tab
   - Look for any error messages
   - Check Network tab for failed API calls

3. **Verify Backend Connection:**
   - Open http://localhost:8002/docs
   - Try the `/api/v1/auth/login` endpoint directly
   - Use Postman or curl to test

4. **Reset Password (if needed):**
   ```bash
   cd admin-dashboard/backend
   source venv/bin/activate
   python3 create_default_admin.py
   ```

## 📝 Important Notes

- **Email Domain:** Must use `.ca` (not `.com`)
- **Case Sensitive:** Email is case-insensitive, password is case-sensitive
- **Backend Port:** 8002 (not 8080 - that's frontend)
- **Frontend Port:** 8080

## 🧪 Test Login via API

```bash
curl -X POST "http://localhost:8002/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@taxease.ca","password":"demo123"}'
```

This should return a JSON response with user info and tokens.

