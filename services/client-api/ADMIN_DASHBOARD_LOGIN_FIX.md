# Admin Dashboard Login Fix - Complete Guide

## Problem Analysis

The login issue was caused by:
1. **Missing Server**: Admin dashboard HTML was being served directly without a backend proxy
2. **API Endpoint Mismatch**: Frontend was making requests to `/admin/api/v1/...` but had no proxy
3. **CORS Issues**: No proper CORS configuration for cross-origin requests
4. **Authentication**: Frontend was using local authentication instead of backend API

## Solution Implemented

### 1. Admin Dashboard Server (`serve_admin_dashboard.py`)
- Created a Python HTTP server that:
  - Serves static files (HTML, CSS, JS) from `admin-dashboard` directory
  - Proxies `/admin/api/*` requests to the admin backend on port 8002
  - Handles CORS headers properly
  - Supports all HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS)

### 2. Backend API Integration
- Updated `script.js` to use real backend authentication
- Added token-based authentication with JWT
- Implemented automatic token refresh
- Added fallback to local authentication for development

### 3. CORS Configuration
- Properly configured CORS middleware in admin backend
- Added development mode with permissive CORS
- Configured allowed origins for production

## How to Use

### Step 1: Start the Admin Backend (Port 8002)

```bash
cd /home/cyberdude/Documents/Projects/CA-final/services/admin-api
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Step 2: Start the Admin Dashboard Server (Port 8080)

```bash
cd /home/cyberdude/Documents/Projects/CA-final/services/client-api
./start_admin_dashboard.sh
```

Or manually:
```bash
python3 serve_admin_dashboard.py
```

### Step 3: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8080
```

### Login Credentials

**Superadmin (Backend)**:
- Email: `superadmin@taxease.ca`
- Password: `demo123`

**Demo Credentials (Fallback)**:
- Superadmin: `superadmin@diamonds.com` / `admin123`
- Admin: `admin@diamonds.com` / `admin123`

## Architecture

```
┌─────────────────┐
│   Browser       │
│  (localhost:    │
│      8080)      │
└────────┬────────┘
         │
         │ HTTP Requests
         │
         ▼
┌─────────────────────────────────┐
│  Admin Dashboard Server         │
│  (serve_admin_dashboard.py)     │
│  Port: 8080                     │
│                                 │
│  - Serves static files          │
│  - Proxies API requests         │
│  - Handles CORS                 │
└────────┬───────────────┬────────┘
         │               │
         │ Static        │ API Proxy
         │ Files         │ /admin/api/*
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │  Admin Backend  │
         │      │  (FastAPI)      │
         │      │  Port: 8002     │
         │      │                 │
         │      │  - Auth API     │
         │      │  - T1 Forms API │
         │      │  - Files API    │
         │      │  - Clients API  │
         │      └────────┬────────┘
         │               │
         │               │
         │               ▼
         │      ┌─────────────────┐
         │      │   PostgreSQL    │
         │      │   Database      │
         │      └─────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Static Files                   │
│  - diamonds-admin.html          │
│  - script.js                    │
│  - styles.css                   │
└─────────────────────────────────┘
```

## API Endpoints

All API endpoints are proxied through the admin dashboard server:

### Authentication
- `POST /admin/api/v1/auth/login` - Admin login
- `POST /admin/api/v1/auth/refresh` - Refresh access token

### T1 Forms
- `GET /admin/api/v1/t1-forms` - List T1 forms
- `GET /admin/api/v1/t1-forms/{form_id}/detailed` - Get detailed form with files

### Files
- `GET /admin/api/v1/files` - List files
- `GET /admin/api/v1/files/{file_id}/metadata` - Get file metadata
- `GET /admin/api/v1/files/{file_id}/download` - Download file

### Clients
- `GET /admin/api/v1/clients` - List clients
- `GET /admin/api/v1/clients/{client_id}` - Get client details

## Troubleshooting

### Issue: Cannot connect to admin backend

**Solution**: Make sure the admin backend is running:
```bash
cd services/admin-api
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Issue: Port 8080 already in use

**Solution**: Kill the process using port 8080:
```bash
lsof -ti:8080 | xargs kill -9
```

Or use a different port by modifying `serve_admin_dashboard.py`:
```python
PORT = 8081  # Change to any available port
```

### Issue: CORS errors in browser console

**Solution**: 
1. Check that `ENVIRONMENT=development` is set in `.env`
2. Verify CORS_ORIGINS includes `http://localhost:8080`
3. Restart the admin backend after changes

### Issue: 401 Unauthorized errors

**Solution**:
1. Login again to get a fresh token
2. Check that the admin user exists in the database
3. Verify SECRET_KEY is set correctly in `.env`

### Issue: Database connection errors

**Solution**:
1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check DATABASE_URL in `.env` is correct
3. Ensure database `taxease_db` exists

## Testing

### Test Login
```bash
curl -X POST http://localhost:8080/admin/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@taxease.ca", "password": "demo123"}'
```

### Test API with Token
```bash
TOKEN="your-access-token-here"
curl http://localhost:8080/admin/api/v1/clients \
  -H "Authorization: Bearer $TOKEN"
```

## Features

✅ Real backend authentication with JWT tokens
✅ Automatic token refresh
✅ CORS handling for cross-origin requests
✅ API request proxying
✅ Static file serving
✅ Development and production modes
✅ Fallback to local authentication for testing
✅ Proper error handling and logging

## Security Notes

### Development
- Uses permissive CORS for localhost
- Includes demo credentials for testing
- Detailed error messages in console

### Production
- Set `ENVIRONMENT=production` in `.env`
- Change default admin passwords
- Use strong SECRET_KEY (min 32 characters)
- Configure specific CORS origins
- Use HTTPS for all communications
- Enable rate limiting
- Implement proper session management

## Additional Configuration

### Custom Port
Edit `serve_admin_dashboard.py`:
```python
PORT = 8081  # Your custom port
```

### Custom Admin Backend URL
Edit `serve_admin_dashboard.py`:
```python
ADMIN_API_URL = "http://your-backend-url:port"
```

### Environment Variables
Create or edit `.env` in `services/admin-api/`:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
ADMIN_EMAIL=your-admin@email.com
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:8080,http://yourdomain.com
ENVIRONMENT=development
```

## Files Modified

1. `/services/client-api/serve_admin_dashboard.py` - New server
2. `/services/client-api/start_admin_dashboard.sh` - Start script
3. `/services/client-api/admin-dashboard/script.js` - Backend integration
4. `/services/admin-api/.env` - Environment configuration
5. `/services/admin-api/app/main.py` - CORS configuration (already done)
6. `/services/admin-api/app/middleware/cors_middleware.py` - CORS middleware (already done)

## Success Indicators

When everything is working correctly, you should see:

1. **Admin Dashboard Server Log**:
```
🚀 Admin Dashboard Server Starting...
📁 Serving from: /path/to/admin-dashboard
🌐 Dashboard URL: http://localhost:8080
🔗 API Proxy: http://localhost:8002
✅ Server running on port 8080
```

2. **Successful Login**:
   - No CORS errors in browser console
   - Successful redirect to dashboard
   - User info displayed in header

3. **API Requests**:
   - Successful data loading
   - No 401/403 errors
   - Proper file categorization

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all services are running
3. Check browser console for errors
4. Check server logs for detailed error messages
