# Integration Analysis Summary

## 📋 Existing Code Structure

### 1. Client-Side Backend (`/client_side`)
**Entry Point**: `main.py` (FastAPI app, port 8000 by default)
**File Upload Logic**: 
- Route: `POST /api/v1/files/upload` (line 727)
- Service: `services/file/main.py` (standalone microservice)
- Storage: Currently uses `S3Manager` but upload is disabled (line 785: `success = True`)
- Database: PostgreSQL with `File` model in `shared/models.py`
- Auth: JWT-based with `User` model
- Upload Location: Files stored with `s3_key` format: `user_{user_id}/{unique_filename}`

**Key Files**:
- `main.py` - Main FastAPI app (1646 lines)
- `services/file/main.py` - File service microservice (309 lines)
- `shared/models.py` - Database models (User, File, T1PersonalForm, etc.)
- `shared/utils.py` - S3Manager class (uses boto3, but needs local filesystem)

### 2. Admin Dashboard Backend (`/tax-hub-dashboard/backend`)
**Entry Point**: `app/main.py` (FastAPI app, port 8000)
**Document Management**:
- Route: `GET /api/v1/documents` (line 21 in `app/api/v1/documents.py`)
- Model: `Document` model in `app/models/document.py`
- Linked to: `Client` model (admin-side clients)
- Auth: Admin JWT with role-based access
- Database: Separate PostgreSQL instance

**Key Files**:
- `app/main.py` - Admin FastAPI app
- `app/api/v1/documents.py` - Document routes
- `app/models/document.py` - Document model (linked to Client)
- `app/models/client.py` - Client model (admin-side)

### 3. Flutter Mobile App (`/frontend/tax_ease-main`)
**API Configuration**: 
- `lib/core/constants/api_endpoints.dart` - Base URL: `https://7f456a2452e2.ngrok-free.app/api/v1` (needs localhost)
- `lib/features/documents/data/files_api.dart` - File upload client
- Upload Route: `POST /files/upload`

**Key Files**:
- `lib/core/constants/api_endpoints.dart` - API base URL
- `lib/features/documents/data/files_api.dart` - File upload implementation
- `lib/features/auth/data/auth_api.dart` - Authentication

## 🔌 Integration Points Needed

### Missing Connections:
1. **Client Upload → Admin View**: 
   - Client-side `File` model (user uploads) needs to sync with admin-side `Document` model
   - Currently separate databases/models

2. **Storage**: 
   - S3Manager is disabled, needs local filesystem storage
   - Files should be stored in `/storage/uploads/` directory

3. **User ↔ Client Mapping**:
   - Client-side `User` (from `client_side/shared/models.py`) needs to map to admin-side `Client` (from `tax-hub-dashboard/backend/app/models/client.py`)
   - Same person, different models

4. **Real-time Updates**:
   - No WebSocket/SSE implementation found
   - Admin needs to see new uploads immediately
   - Can use Redis pub/sub or polling

5. **API URLs**:
   - Flutter app uses ngrok URL (needs localhost)
   - Two separate backends on same port conflict

## 🏗️ Reorganization Plan

### Target Structure:
```
/app
  /backend_client      ← from /client_side (rename main.py, keep all logic)
  /backend_admin       ← from /tax-hub-dashboard/backend
  /admin_dashboard     ← from /tax-hub-dashboard/src (React frontend)
  /mobile_client       ← from /frontend/tax_ease-main
  /shared              ← merge shared utilities
  /storage             ← new local upload directory
  /migrations          ← database migrations
  /docs                ← existing docs
```

## ✅ Action Items

1. **Replace S3 with Local Storage**
   - Modify `S3Manager` to use local filesystem
   - Store files in `/app/storage/uploads/user_{user_id}/`
   - Update file paths in database

2. **Bridge User ↔ Client Models**
   - Create mapping table or sync logic
   - When user uploads file, create corresponding Client document entry
   - Use email as matching key

3. **Connect APIs**
   - Client backend: Port 8001
   - Admin backend: Port 8002
   - Update Flutter base URL to `http://localhost:8001/api/v1`

4. **Real-time Updates**
   - Use Redis pub/sub for file upload events
   - Admin polls or subscribes to new document events

5. **Fix File Serving**
   - Admin backend needs to serve files from storage directory
   - Add file download endpoint

## 🚨 Critical Notes

- **DO NOT** rewrite upload logic - it already works
- **DO NOT** change database schemas unless absolutely necessary
- **DO** preserve all existing business logic
- **DO** use existing authentication patterns
- **DO** maintain existing API contracts

## 🔄 Data Flow After Integration

```
Flutter App → POST /api/v1/files/upload (port 8001)
  ↓
Client Backend → Save file locally + Create File record
  ↓
Sync/Notify → Redis event or direct DB sync
  ↓
Admin Backend → Create Document record + Link to Client
  ↓
Admin Dashboard → Display in Documents page
```


