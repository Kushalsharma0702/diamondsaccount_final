# Debugging Authentication Issue

## Problem
Authentication with demo credentials is not working.

## Backend Test (Direct)
✅ Backend login works when tested directly with curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@taxease.ca","password":"demo123"}'
```

## Potential Issues

### 1. CORS Configuration
- Frontend is running on port **8080**
- Backend CORS needs to allow this origin
- **Fixed**: Added port 8080 to CORS_ORIGINS

### 2. Frontend API Configuration
- Check `.env` file has: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- Frontend needs to be restarted after .env changes

### 3. Network/CORS Errors
Check browser console (F12) for:
- CORS errors
- Network request failures
- 401/403 errors

## Testing Steps

1. **Test from browser console**:
```javascript
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'superadmin@taxease.ca',
    password: 'demo123'
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

2. **Check browser Network tab**:
- Open DevTools (F12)
- Go to Network tab
- Try to login
- Check the login request:
  - Status code
  - Response body
  - CORS headers

3. **Check backend logs**:
```bash
tail -f tax-hub-dashboard/backend/backend.log
```

## Common Fixes

1. **Restart frontend** after .env changes:
```bash
pkill -f vite
cd tax-hub-dashboard
npm run dev
```

2. **Restart backend** after CORS changes:
```bash
pkill -f uvicorn
cd tax-hub-dashboard/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. **Clear browser cache/localStorage**:
- Open DevTools (F12)
- Application tab
- Clear Local Storage
- Try login again

## Expected Response

Successful login should return:
```json
{
  "user": {
    "id": "...",
    "email": "superadmin@taxease.ca",
    "name": "Super Admin",
    "role": "superadmin",
    ...
  },
  "token": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 86400
  }
}
```

## Next Steps

1. Check browser console for errors
2. Verify CORS headers in network request
3. Check backend is running and accepting requests
4. Verify API base URL in frontend .env






