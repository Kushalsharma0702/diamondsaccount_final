# Integration Status & Quick Start Guide

## ✅ Completed Integration Steps

### 1. Local Filesystem Storage
- ✅ Replaced S3Manager with local filesystem storage
- ✅ Files stored in: `client_side/storage/uploads/`
- ✅ File serving endpoint updated to serve local files

### 2. Client Upload → Admin Sync
- ✅ Created `sync_to_admin.py` service to bridge File → Document
- ✅ Automatic sync when file is uploaded
- ✅ Creates Client record in admin DB if doesn't exist (by email)

### 3. Port Configuration
- ✅ Client backend: Port 8001 (was 8000)
- ✅ Admin backend: Port 8002 (was 8000)
- ✅ Flutter app: Updated to use `http://localhost:8001/api/v1`

### 4. File Download
- ✅ Updated download endpoint to serve local files directly

## 🔄 Current Data Flow

```
Flutter App (Port 5173)
  ↓ POST /api/v1/files/upload
Client Backend (Port 8001)
  ↓ Save file to local filesystem
  ↓ Create File record in DB
  ↓ Sync to Admin Backend (async, non-blocking)
Admin Backend (Port 8002)
  ↓ Create/Update Client by email
  ↓ Create Document record
Admin Dashboard (Port 8080)
  ↓ Display documents grouped by client
```

## 🚀 Quick Start

### Prerequisites
- PostgreSQL running on port 5432
- Redis running on port 6379
- Python 3.10+
- Node.js 18+

### Step 1: Start Client Backend
```bash
cd client_side
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taxease_db"
export ADMIN_API_BASE_URL="http://localhost:8002/api/v1"
export STORAGE_BASE_DIR="./storage/uploads"

# Start server on port 8001
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Step 2: Start Admin Backend
```bash
cd tax-hub-dashboard/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/taxhub_db
# REDIS_HOST=localhost
# REDIS_PORT=6379

# Setup database
python setup_database.py

# Create superadmin
python create_superadmin.py

# Start server on port 8002
./start.sh  # or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Step 3: Start Admin Dashboard Frontend
```bash
cd tax-hub-dashboard
npm install
npm run dev  # Runs on port 8080
```

### Step 4: Start Flutter App
```bash
cd frontend/tax_ease-main\ \(1\)/tax_ease-main
flutter pub get
flutter run
```

## 📋 Database Setup

### Client Backend Database
```bash
createdb taxease_db
cd client_side
python -c "from shared.database import Database; import asyncio; asyncio.run(Database.create_tables())"
```

### Admin Backend Database
```bash
createdb taxhub_db
cd tax-hub-dashboard/backend
python setup_database.py
python create_superadmin.py
```

## 🔐 Default Credentials

### Client Backend
- Register new user via `/api/v1/auth/register`
- Login via `/api/v1/auth/login`

### Admin Backend
- Superadmin: `superadmin@taxease.ca` / `demo123`
- Admin: `admin@taxease.ca` / `demo123`
- Or create via: `python create_superadmin.py`

## 📁 File Storage

### Local Storage Structure
```
client_side/
  storage/
    uploads/
      user_{user_id}/
        {timestamp}_{random}.{ext}
```

### Accessing Files
- Download: `GET /api/v1/files/{file_id}/download` (Client backend)
- Files served directly from local filesystem

## 🔄 Sync Mechanism

When a client uploads a file:
1. File saved to local filesystem
2. File record created in client DB
3. Background sync to admin backend:
   - Finds/creates Client by email
   - Creates Document record
   - Links Document to Client

## ⚠️ Known Issues & TODO

### Remaining Tasks
- [ ] Add real-time updates (Redis pub/sub or WebSocket)
- [ ] Add file serving endpoint in admin backend
- [ ] Test end-to-end flow with Flutter app
- [ ] Reorganize folder structure (optional)
- [ ] Add health checks and monitoring

### Notes
- Sync is async and non-blocking (won't fail upload if admin backend is down)
- Client creation uses email as matching key
- Document type auto-detected from filename

## 🐛 Troubleshooting

### Port Conflicts
- Client backend: 8001
- Admin backend: 8002
- Admin dashboard: 8080
- Flutter: Auto-assigned

### Database Connection Issues
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env` files
- Ensure databases exist: `psql -l`

### Redis Issues
- Start Redis: `sudo systemctl start redis` or `docker run -d -p 6379:6379 redis:alpine`
- Check connection: `redis-cli ping`

### File Upload Issues
- Check storage directory exists: `mkdir -p client_side/storage/uploads`
- Check file permissions
- Check file size limits (10MB default)

### Sync Issues
- Check admin backend is running
- Check `ADMIN_API_BASE_URL` environment variable
- Check logs for sync errors

## 📚 API Endpoints

### Client Backend (8001)
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files` - List user files
- `GET /api/v1/files/{id}/download` - Download file

### Admin Backend (8002)
- `GET /api/v1/documents` - List documents
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients` - List clients




