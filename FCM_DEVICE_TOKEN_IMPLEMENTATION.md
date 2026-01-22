# FCM Device Token Registration - Implementation Complete

## ✅ Implementation Summary

The FCM device token registration endpoint has been successfully implemented in your backend API (port 8001).

## 📋 What Was Implemented

### 1. Database Model
**File:** `database/schemas_v2.py`

Added `NotificationDeviceToken` model with:
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `token`: FCM device token (unique, indexed)
- `platform`: Enum (android, ios, web, macos, windows, linux)
- `device_id`: Optional stable device identifier
- `is_active`: Boolean flag for soft delete
- `app_version`, `locale`: Optional metadata
- `created_at`, `updated_at`, `last_seen_at`: Timestamps

### 2. Pydantic Schemas
**File:** `backend/app/schemas/notifications.py`

Created schemas:
- `DeviceTokenRegister`: Request schema for registration
- `DeviceTokenResponse`: Response schema
- `DeviceTokenList`: List response schema
- `DevicePlatform`: Platform enum

### 3. API Endpoints
**File:** `backend/app/routes_v2/notifications.py`

Implemented three endpoints:

#### POST `/api/v1/notifications/device-tokens`
- **Purpose:** Register or update FCM device token
- **Auth:** Required (JWT Bearer token)
- **Request Body:**
  ```json
  {
    "token": "fcm_device_token_string",
    "platform": "android|ios|web|macos|windows|linux",
    "device_id": "optional-device-id",
    "app_version": "1.0.0",
    "locale": "en_US"
  }
  ```
- **Response:** 200 OK with token details
- **Behavior:**
  - If token exists: Updates it and sets `is_active = true`
  - If token is new: Creates new record
  - Always updates `last_seen_at` timestamp

#### GET `/api/v1/notifications/device-tokens`
- **Purpose:** List all active device tokens for authenticated user
- **Auth:** Required
- **Response:** List of tokens with metadata

#### DELETE `/api/v1/notifications/device-tokens/{token_id}`
- **Purpose:** Deactivate a device token (soft delete)
- **Auth:** Required
- **Response:** 204 No Content on success

### 4. Main App Integration
**File:** `backend/app/main.py`

- Imported notifications router
- Registered with `/api/v1` prefix

## 🚀 How to Deploy

### Step 1: Run Database Migration

```bash
cd /home/cyberdude/Documents/Projects/CA-final
python add_device_tokens_table.py
```

This will create the `notification_device_tokens` table in your PostgreSQL database.

### Step 2: Start Backend API

```bash
cd /home/cyberdude/Documents/Projects/CA-final/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 3: Verify API Documentation

Open your browser and visit:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

You should see the new `/api/v1/notifications/device-tokens` endpoints.

## 🧪 Testing

### Option 1: Run Test Script

```bash
python test_device_token_api.py
```

**Note:** Update `TEST_USER` credentials in the script first.

### Option 2: Manual Testing with curl

```bash
# 1. Login to get access token
ACCESS_TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.access_token')

# 2. Register device token
curl -X POST http://localhost:8001/api/v1/notifications/device-tokens \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fcm_test_token_12345",
    "platform": "android",
    "device_id": "device-001"
  }'

# 3. List device tokens
curl -X GET http://localhost:8001/api/v1/notifications/device-tokens \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Option 3: Test via Swagger UI

1. Go to http://localhost:8001/docs
2. Click "Authorize" and enter your JWT token
3. Test the endpoints under "notifications" section

## 📱 Flutter App Integration

Your Flutter app should call this endpoint like this:

```dart
// In your NotificationService
Future<void> syncTokenWithBackend() async {
  final fcmToken = await FirebaseMessaging.instance.getToken();
  if (fcmToken == null) return;

  final response = await http.post(
    Uri.parse('${ApiEndpoints.BASE_URL}/notifications/device-tokens'),
    headers: {
      'Authorization': 'Bearer ${authToken}',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'token': fcmToken,
      'platform': Platform.isAndroid ? 'android' : 'ios',
      'device_id': await _getDeviceId(),
      'app_version': packageInfo.version,
      'locale': Platform.localeName,
    }),
  );
}
```

## 🔐 Security Features

✅ **Authentication Required:** All endpoints require valid JWT token  
✅ **User Isolation:** Users can only access their own tokens  
✅ **Token Uniqueness:** Enforced at database level  
✅ **Soft Delete:** Tokens are deactivated, not deleted  
✅ **Input Validation:** Pydantic schemas validate all inputs  

## 📊 Database Schema

```sql
CREATE TABLE notification_device_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(500) NOT NULL UNIQUE,
    platform VARCHAR(50) NOT NULL,
    device_id VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    app_version VARCHAR(50),
    locale VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_device_token_user_active ON notification_device_tokens(user_id, is_active);
CREATE INDEX idx_device_token_token ON notification_device_tokens(token);
```

## 🎯 Next Steps

To complete the FCM integration, you'll need to implement:

### 1. FCM Sender Service
Create a service to send notifications via FCM HTTP v1 API:
- Set up Google service account credentials
- Implement OAuth2 token acquisition
- Create function to send messages to device tokens

### 2. Domain Event Handlers
Add notification triggers for:
- Filing submitted → Notify user
- Payment requested → Notify user
- Document upload requested → Notify user
- Filing status changed → Notify user

### 3. Token Cleanup
Create a scheduled job to:
- Deactivate tokens that return FCM errors (NOT_FOUND, UNREGISTERED)
- Remove old inactive tokens (e.g., older than 90 days)

## 📚 Reference Files

- **FCM Backend Guide:** `/home/cyberdude/Documents/Projects/CA-final/fcm-backend-guide.txt`
- **Database Schema:** `/home/cyberdude/Documents/Projects/CA-final/database/schemas_v2.py`
- **API Route:** `/home/cyberdude/Documents/Projects/CA-final/backend/app/routes_v2/notifications.py`
- **Schemas:** `/home/cyberdude/Documents/Projects/CA-final/backend/app/schemas/notifications.py`

## ✅ Implementation Checklist

- [x] Database model created
- [x] Pydantic schemas defined
- [x] API endpoints implemented
- [x] Routes registered in main app
- [x] Migration script created
- [x] Test script created
- [x] Documentation completed
- [ ] Database migration run
- [ ] API tested and verified
- [ ] Flutter app integrated
- [ ] FCM sender service implemented
- [ ] Domain event handlers added

## 🔧 Troubleshooting

### Issue: Table doesn't exist
**Solution:** Run the migration script: `python add_device_tokens_table.py`

### Issue: 401 Unauthorized
**Solution:** Make sure you're passing a valid JWT token in the Authorization header

### Issue: Token already exists for different user
**Solution:** The endpoint automatically reassigns tokens to the current user

### Issue: Platform validation error
**Solution:** Use one of: android, ios, web, macos, windows, linux (lowercase)

---

**Status:** ✅ Ready for testing and deployment  
**Last Updated:** January 22, 2026
