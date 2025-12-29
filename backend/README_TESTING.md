# API Testing Guide

## Quick Start

### Option 1: Automated (Start Server + Run Tests)
```bash
cd backend
./start_and_test.sh
```

This will:
1. Start the FastAPI server on port 8001
2. Wait for it to be ready
3. Run all API tests
4. Keep the server running for manual testing

### Option 2: Manual Testing

#### 1. Start the Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### 2. Run Tests (in another terminal)
```bash
python3 backend/test_api.py
```

## Test Coverage

The test script (`backend/test_api.py`) tests the complete user journey:

### ✅ Authentication Flow
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/request-otp` - Request OTP (static: 123456)
- `POST /api/v1/auth/verify-otp` - Verify OTP
- `POST /api/v1/auth/login` - Login and get JWT token

### ✅ Client Operations
- `POST /api/v1/client/add` - Add new client record
- `DELETE /api/v1/client/{client_id}` - Delete client

### ✅ Admin Operations
- `GET /api/v1/admin/clients` - List all clients (visible in admin dashboard)

### ✅ Chat Operations
- `POST /api/v1/chat/send` - Send message (client → admin or admin → client)
- `GET /api/v1/chat/{client_id}` - Get all messages for a client

### ✅ Document Operations
- `POST /api/v1/documents/upload` - Upload document file

### ✅ T1 Form Operations
- `POST /api/v1/client/tax-return` - Submit/update T1 tax form

## Test Output

The script provides color-coded output:
- 🟢 **Green (✓)** - Test passed
- 🔴 **Red (✗)** - Test failed (with error details)
- 🟡 **Yellow (ℹ)** - Informational messages

At the end, you'll see a summary:
```
Test Summary
============================================================
Passed: 12
Failed: 0
Success Rate: 100.0%
```

## Manual Testing with curl

### Register User
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "Test123!",
    "phone": "+1-555-1234"
  }'
```

### Request OTP
```bash
curl -X POST http://localhost:8001/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "purpose": "email_verification"
  }'
```

### Verify OTP (use static code: 123456)
```bash
curl -X POST http://localhost:8001/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "purpose": "email_verification"
  }'
```

### Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

### Add Client
```bash
curl -X POST http://localhost:8001/api/v1/client/add \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1-555-1234",
    "filing_year": 2024
  }'
```

### List Clients (Admin)
```bash
curl http://localhost:8001/api/v1/admin/clients
```

## Testing from Frontend

### Client Dashboard (Flutter)
1. Point `BASE_URL` in `tax_ease_app_client/lib/core/constants/api_endpoints.dart` to:
   ```dart
   static const String BASE_URL = 'http://localhost:8001/api/v1';
   ```
2. Run Flutter app and test registration → OTP → login → add client flow

### Admin Dashboard (React/Next.js)
1. Ensure Vite proxy in `tax-hub-dashboard-admin/vite.config.ts` points to:
   ```typescript
   target: 'http://localhost:8001'
   ```
2. Run admin dashboard and verify clients list shows newly added clients

## Troubleshooting

### Server not starting
- Check if port 8001 is already in use: `lsof -i :8001`
- Check database connection in `.env` file
- View server logs: `tail -f backend/server.log`

### Tests failing
- Ensure server is running: `curl http://localhost:8001/`
- Check database tables exist (users, clients, chat_messages, etc.)
- Verify `.env` has correct database credentials

### Chat messages not appearing
- Ensure `chat_messages` table exists in database
- Check table schema matches expected columns

## Next Steps

After running tests, you can:
1. Test manually via frontend dashboards
2. Use Postman/Thunder Client to test individual endpoints
3. Review test output to identify any bugs
4. Check server logs for detailed error messages
