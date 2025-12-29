# Backend Setup & Testing Guide

## ✅ What's Been Created

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app with all routes
│   ├── database.py          # DB connection (needs .env config)
│   ├── auth/                # JWT, OTP, password hashing
│   ├── routes/              # All API endpoints
│   │   ├── auth.py          # Register, login, OTP
│   │   ├── client.py         # Add/delete client
│   │   ├── admin.py         # List clients
│   │   ├── chat.py          # Chat messaging
│   │   ├── documents.py     # Document upload
│   │   └── t1.py            # T1 form submission
│   └── services/            # (Placeholder for future services)
├── test_api.py              # Comprehensive test script
├── start_and_test.sh        # Auto-start server + run tests
├── run_tests.sh             # Run tests only (server must be running)
└── requirements.txt         # Python dependencies
```

### All Endpoints Implemented

**Auth:**
- ✅ `POST /api/v1/auth/register` - Register user (stores in `users` table)
- ✅ `POST /api/v1/auth/login` - Login (returns JWT)
- ✅ `POST /api/v1/auth/request-otp` - Request OTP (static: 123456)
- ✅ `POST /api/v1/auth/verify-otp` - Verify OTP (accepts 123456)

**Client:**
- ✅ `POST /api/v1/client/add` - Add client record
- ✅ `DELETE /api/v1/client/{client_id}` - Delete client

**Admin:**
- ✅ `GET /api/v1/admin/clients` - List all clients

**Chat:**
- ✅ `POST /api/v1/chat/send` - Send message (client ↔ admin)
- ✅ `GET /api/v1/chat/{client_id}` - Get messages

**Documents:**
- ✅ `POST /api/v1/documents/upload` - Upload file

**T1 Forms:**
- ✅ `POST /api/v1/client/tax-return` - Submit/update T1 form

## ⚠️ Configuration Required

### 1. Database Connection

The backend needs a `.env` file at the project root with:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=CA_Project
DB_USER=postgres
DB_PASSWORD=your_actual_password
```

**To find your database credentials:**
- Check existing `.env` files in the project
- Or check `services/client-api` or `services/admin-api` for their DB config
- Or check PostgreSQL directly: `psql -U postgres -l` to list databases

### 2. Database Tables

Ensure these tables exist in `CA_Project` database:
- `users` (from `database/schemas.py`)
- `clients` (from `database/schemas.py`)
- `admins` (from `database/schemas.py`)
- `admin_client_map` (from `database/schemas.py`)
- `tax_returns` (from `database/schemas.py`)
- `documents` (from `database/schemas.py`)
- `chat_messages` (may need to be created - see below)
- `otps` (from `database/schemas.py`)
- `refresh_tokens` (from `database/schemas.py`)

**To create missing tables:**
```bash
python database/schemas.py
```

**To create `chat_messages` table (if missing):**
```sql
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    sender_role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_by_client BOOLEAN DEFAULT FALSE,
    read_by_admin BOOLEAN DEFAULT FALSE
);
```

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Database
```bash
# Create/update .env file at project root
cat > .env << EOL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=CA_Project
DB_USER=postgres
DB_PASSWORD=your_password_here
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
STORAGE_PATH=./storage/uploads
MAX_FILE_SIZE_MB=10
EOL
```

### Step 3: Start Server
```bash
# Option A: Automated (starts server + runs tests)
./backend/start_and_test.sh

# Option B: Manual
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001
```

### Step 4: Run Tests
```bash
# If server is already running
./backend/run_tests.sh

# Or directly
python3 backend/test_api.py
```

## 🧪 Testing

The test script (`backend/test_api.py`) will:

1. ✅ Check server health
2. ✅ Test registration → OTP → login flow
3. ✅ Test client add operation
4. ✅ Test admin listing clients
5. ✅ Test chat (client → admin, admin → client)
6. ✅ Test document upload
7. ✅ Test T1 form submission
8. ✅ Test client delete

**Expected Output:**
- Green ✓ = Test passed
- Red ✗ = Test failed (check error message)
- Yellow ℹ = Info message

## 🐛 Current Issues to Fix

1. **Database Connection**: Update `.env` with correct PostgreSQL credentials
2. **Chat Table**: Ensure `chat_messages` table exists (create manually if needed)
3. **Import Paths**: All imports use `from database import ...` which should work if `database/` is in Python path

## 📝 Next Steps After Setup

1. Run test script to verify all endpoints work
2. Test from Flutter client app (point to `http://localhost:8001/api/v1`)
3. Test from admin dashboard (ensure Vite proxy points to port 8001)
4. Report any bugs found during testing

## 🔍 Debugging

### Check Server Logs
```bash
tail -f backend/server.log
```

### Test Individual Endpoints
```bash
# Health check
curl http://localhost:8001/

# Register
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"John","last_name":"Doe","password":"Test123!"}'
```

### Check Database Connection
```bash
psql -U postgres -d CA_Project -c "SELECT COUNT(*) FROM users;"
```
