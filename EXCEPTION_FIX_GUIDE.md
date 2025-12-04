# 🔧 Fix: "Exception please check your input and try again"

## Problem
Getting an exception error when uploading files or making authenticated requests.

## Common Causes & Solutions

### 1. Backend Not Restarted After Changes

**Solution:** Restart the client backend

```bash
# Stop existing backend
pkill -f "uvicorn.*8001"

# Start backend
cd client_side
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Token Not Being Sent Correctly

**Check:** Make sure your Flutter app or API client sends the Authorization header:

```
Authorization: Bearer <your_token>
```

**Example for Flutter:**
```dart
var request = http.MultipartRequest(
  'POST',
  Uri.parse('$baseUrl/api/v1/files/upload'),
);

// IMPORTANT: Add this header
request.headers['Authorization'] = 'Bearer $accessToken';

request.files.add(
  await http.MultipartFile.fromPath('file', filePath),
);
```

### 3. Token Expired

**Solution:** Tokens expire after 15 minutes. Re-login to get a new token:

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Developer@aurocode.app",
    "password": "Developer@123"
  }'
```

### 4. Invalid Token Format

**Check:** Token should be in format:
```
Bearer <token>
```
- Must have space after "Bearer"
- Must not have quotes around token
- Token should start with `eyJ...` (JWT format)

### 5. CORS Issues

**Check:** Make sure CORS allows Authorization header. It's already configured, but verify:

```python
# client_side/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # This allows Authorization header
)
```

## Debugging Steps

### Step 1: Check Backend is Running

```bash
curl http://localhost:8001/health
```

Should return:
```json
{"status": "healthy"}
```

### Step 2: Test Authentication

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "Developer@aurocode.app", "password": "Developer@123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Test auth
curl -X GET http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

If this fails, the token is invalid or expired.

### Step 3: Test File Upload

```bash
# Create test file
echo "Test content" > /tmp/test.pdf

# Upload with token
curl -X POST http://localhost:8001/api/v1/files/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test.pdf"
```

### Step 4: Check Backend Logs

```bash
# Check for errors in backend output
# Look for:
# - Authentication errors
# - Token validation errors
# - Import errors
# - Database connection errors
```

## Quick Fix Checklist

- [ ] Backend restarted after auth.py changes
- [ ] Token is valid (not expired)
- [ ] Authorization header format is correct: `Bearer <token>`
- [ ] Token is being sent in the request
- [ ] User account is active
- [ ] Backend is running on port 8001
- [ ] Database connection is working

## Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Not authenticated" | No token or invalid format | Add Authorization header |
| "Token expired" | Token older than 15 min | Re-login |
| "Invalid token" | Token format wrong | Check token format |
| "User not found" | User deleted | Create user account |
| "Inactive user" | Account disabled | Enable user account |

## Still Not Working?

1. **Check backend logs** for detailed error messages
2. **Verify token** by testing `/api/v1/auth/me` endpoint
3. **Check file format** - must be: pdf, jpg, jpeg, png, doc, docx, xls, xlsx
4. **Check file size** - max 10MB

## Status

✅ **Authentication code is fixed and ready!**
- Request parameter added
- Token extraction works for multipart requests
- Better error messages

**Action Required:** Restart backend to apply changes!

---

**Need Help?** Check backend logs for specific error messages.


