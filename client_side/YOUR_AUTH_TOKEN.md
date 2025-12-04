# 🔑 Your Authentication Token - Quick Reference

**Generated:** November 13, 2025  
**Status:** ✅ Active and Valid

---

## 🎯 Your JWT Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8
```

**⏰ Valid for:** 15 minutes (until ~05:54 UTC)

---

## 📋 Test Account Credentials

| Field | Value |
|-------|-------|
| Email | `test_1763013147@example.com` |
| Password | `SecureTestPass123!` |

---

## 🚀 How to Use in Different Tools

### 1. Postman

1. Open any request in Postman
2. Go to **Authorization** tab
3. Select **Type:** `Bearer Token`
4. Paste the token in the **Token** field:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8
```

**OR** set it as a collection/environment variable:
- Variable name: `access_token`
- Variable value: (paste token above)
- Then use: `{{access_token}}` in Authorization

---

### 2. curl Command

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8"
```

---

### 3. JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/v1/t1-forms/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8',
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data);
```

---

### 4. Python/Requests

```python
import requests

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/v1/auth/me', headers=headers)
print(response.json())
```

---

### 5. Flutter/Dart

```dart
import 'package:http/http.dart' as http;

final response = await http.get(
  Uri.parse('http://localhost:8000/api/v1/auth/me'),
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8',
    'Content-Type': 'application/json',
  },
);

print(response.body);
```

---

## 🧪 Quick Test Commands

### Test 1: Get Your Profile
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8"
```

**Expected Response:**
```json
{
  "id": "a8fb8ab8-4ba4-4b9e-b709-3d66ce1f1476",
  "email": "test_1763013147@example.com",
  "first_name": "Test",
  "last_name": "User",
  "phone": "+14165550100",
  "email_verified": false,
  "created_at": "2025-11-13T05:39:07.123Z"
}
```

---

### Test 2: Setup Encryption
```bash
curl -X POST http://localhost:8000/api/v1/encryption/setup \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8" \
  -H "Content-Type: application/json" \
  -d '{"password": "T1TestPassword123!"}'
```

---

### Test 3: Create T1 Form
```bash
curl -X POST http://localhost:8000/api/v1/t1-forms/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOGZiOGFiOC00YmE0LTRiOWUtYjcwOS0zZDY2Y2UxZjE0NzYiLCJlbWFpbCI6InRlc3RfMTc2MzAxMzE0N0BleGFtcGxlLmNvbSIsImV4cCI6MTc2MzAxNDA0OCwidHlwZSI6ImFjY2VzcyJ9.6hUS7YhBw7WeA-Na4SDCgcgp8GHXC8r0Z0H6iNfYkk8" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "draft",
    "personalInfo": {
      "firstName": "Jane",
      "lastName": "Doe",
      "sin": "123456789",
      "dateOfBirth": "1990-05-20",
      "address": "123 Main St, Toronto, ON",
      "phoneNumber": "+14165550123",
      "email": "jane@example.com",
      "maritalStatus": "single"
    },
    "hasForeignProperty": false,
    "hasMedicalExpenses": true,
    "isFirstTimeFiler": true
  }'
```

---

## 🔄 Token Expired? Generate New One

If your token expires (after 15 minutes), login again:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_1763013147@example.com",
    "password": "SecureTestPass123!"
  }'
```

**Or create a new user:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myemail@example.com",
    "password": "SecurePass123!",
    "first_name": "Your",
    "last_name": "Name",
    "phone": "+14165550100",
    "accept_terms": true
  }'
```

Then login with your credentials.

---

## ❌ Common Errors and Solutions

### Error: "Not authenticated"
**Cause:** Missing or invalid token  
**Solution:** Copy the full token including all characters, ensure no extra spaces

### Error: "Token has expired"
**Cause:** Token older than 15 minutes  
**Solution:** Login again to get a new token

### Error: "Invalid token"
**Cause:** Token was copied incorrectly  
**Solution:** Make sure you copied the ENTIRE token (it's very long)

### Error: "Missing Authorization header"
**Cause:** Header not set correctly  
**Solution:** Ensure header is exactly:
```
Authorization: Bearer <token>
```
Note: There's a space between "Bearer" and the token!

---

## 📊 API Endpoints You Can Test

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/me` | Get your profile |
| POST | `/api/v1/encryption/setup` | Setup encryption |
| POST | `/api/v1/t1-forms/` | Create T1 form |
| GET | `/api/v1/t1-forms/` | List your forms |
| GET | `/api/v1/t1-forms/{id}` | Get specific form |
| PUT | `/api/v1/t1-forms/{id}` | Update form |
| DELETE | `/api/v1/t1-forms/{id}` | Delete form |

---

## 🌐 API Documentation

**Interactive Swagger UI:**  
http://localhost:8000/docs

In Swagger:
1. Click "Authorize" button (🔒 icon at top)
2. Paste your token
3. Click "Authorize"
4. Now you can test all endpoints interactively!

---

## 💾 Save This Information

**Recommended:** Save this token in:
- Postman environment variable
- Your code configuration
- A secure note (temporarily)

**Security Note:** Tokens expire after 15 minutes. This is normal security practice.

---

**Status:** ✅ Token is active and verified  
**Next Step:** Use this token in your API requests!
