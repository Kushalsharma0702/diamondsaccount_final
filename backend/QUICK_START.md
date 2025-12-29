# 🚀 Quick Start - Test Everything

## Prerequisites Check

1. **PostgreSQL is running**
   ```bash
   psql -U postgres -c "SELECT version();"
   ```

2. **Database exists**
   ```bash
   psql -U postgres -l | grep CA_Project
   ```

3. **Python dependencies installed**
   ```bash
   cd backend && pip install -r requirements.txt
   ```

## Step-by-Step Testing

### 1. Configure Database (if not already done)

Create/update `.env` file at project root:
```bash
cat > .env << 'EOL'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=CA_Project
DB_USER=postgres
DB_PASSWORD=your_actual_password
JWT_SECRET_KEY=test-secret-key-12345
EOL
```

### 2. Start Backend Server

```bash
cd /home/cyberdude/Documents/Projects/CA-final
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
```

Keep this terminal open. In another terminal:

### 3. Run Full Test Suite

```bash
cd /home/cyberdude/Documents/Projects/CA-final
python3 backend/test_api.py
```

## What Gets Tested

✅ **Complete User Journey:**
1. New user registers → stored in `users` table
2. User requests OTP → static code `123456` issued
3. User verifies OTP → email marked as verified
4. User logs in → receives JWT token
5. User adds client record → visible in admin panel
6. Admin lists all clients → sees new client
7. Client sends chat message → stored in `chat_messages`
8. Admin sends reply → stored in `chat_messages`
9. Client uploads document → saved to `storage/uploads/`
10. Client submits T1 form → stored in `tax_returns` table
11. Client deletes their record → removed from `clients` table

## Expected Test Results

If everything works:
```
Test Summary
============================================================
Passed: 12
Failed: 0
Success Rate: 100.0%
```

If database connection fails:
- Check `.env` file has correct credentials
- Verify PostgreSQL is running
- Check database name is correct

## Manual Testing URLs

Once server is running, test in browser or Postman:

- Health: http://localhost:8001/
- API Docs: http://localhost:8001/docs (FastAPI auto-generated)
- Register: POST http://localhost:8001/api/v1/auth/register
- List Clients: GET http://localhost:8001/api/v1/admin/clients

## Frontend Integration

### Flutter Client
Update `tax_ease_app_client/lib/core/constants/api_endpoints.dart`:
```dart
static const String BASE_URL = 'http://localhost:8001/api/v1';
```

### Admin Dashboard
Update `tax-hub-dashboard-admin/vite.config.ts` proxy:
```typescript
target: 'http://localhost:8001'
```
