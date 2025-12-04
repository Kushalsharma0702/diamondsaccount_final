# 🧪 End-to-End Test Setup Guide

## ✅ Configuration Complete

### Database Unification
- ✅ Both backends now use the same database: `taxease_db`
- ✅ Client Backend: Uses existing database connection
- ✅ Admin Backend: Updated to use `taxease_db` instead of `taxhub_db`

### Port Configuration
- ✅ Client Backend: Port 8001
- ✅ Admin Backend: Port 8002  
- ✅ Admin Dashboard: Port 8080
- ✅ Ngrok: Will expose port 8001

## 🚀 Quick Start - Complete Test Setup

### Step 1: Start All Services

```bash
# Start all services (client backend, admin backend, admin dashboard)
./start-all-services.sh
```

This will:
- Start client backend on port 8001
- Start admin backend on port 8002
- Start admin dashboard on port 8080
- Show you service URLs

### Step 2: Start Ngrok Tunnel

```bash
# Start ngrok tunnel for client backend
./start-ngrok.sh
```

Ngrok will:
- Expose your client backend publicly
- Display the public URL (e.g., `https://xxxx.ngrok.io`)
- Save the URL to `/tmp/ngrok_url.txt`

**Copy the ngrok URL!** You'll need it for the Flutter app.

### Step 3: Update Flutter App with Ngrok URL

```bash
# Update Flutter app to use ngrok URL
./update-flutter-url.sh ngrok https://xxxx.ngrok.io
```

Or manually edit:
- File: `frontend/tax_ease-main (1)/tax_ease-main/lib/core/constants/api_endpoints.dart`
- Change: `BASE_URL` to your ngrok URL + `/api/v1`

### Step 4: Build Flutter APK

```bash
# Build the APK
./build-flutter-apk.sh
```

This will:
- Clean previous builds
- Get dependencies
- Build release APK
- Show you the APK location

APK will be at:
```
frontend/tax_ease-main (1)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

### Step 5: Install APK on Device

```bash
# Connect your Android device via USB
# Enable USB debugging
adb devices  # Check device is connected

# Install APK
adb install frontend/tax_ease-main\ \(1\)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

Or transfer the APK to your device and install manually.

## 📋 Service URLs

After starting all services:

| Service | URL | Description |
|---------|-----|-------------|
| Client Backend | http://localhost:8001 | Client API (also exposed via ngrok) |
| Client Backend Docs | http://localhost:8001/docs | Swagger documentation |
| Admin Backend | http://localhost:8002 | Admin API |
| Admin Backend Docs | http://localhost:8002/docs | Swagger documentation |
| Admin Dashboard | http://localhost:8080 | React admin dashboard |
| Ngrok Dashboard | http://localhost:4040 | View ngrok requests |

## 🧪 Testing Workflow

### 1. Upload File from Flutter App

1. Open the Flutter app on your device
2. Login or register a new account
3. Navigate to Documents/Upload section
4. Select and upload a file
5. Wait for upload confirmation

### 2. Check Admin Dashboard

1. Open http://localhost:8080 in your browser
2. Login with admin credentials:
   - Superadmin: `superadmin@taxease.ca` / `demo123`
   - Admin: `admin@taxease.ca` / `demo123`
3. Go to Documents page
4. You should see:
   - Client card with the uploaded file
   - File listed under the client
   - File metadata (name, type, status)

### 3. Check Database

```bash
# Connect to database
psql -U postgres -d taxease_db

# Check users (client-side)
SELECT id, email, first_name, last_name FROM users;

# Check files (client-side)
SELECT id, user_id, original_filename, file_type, upload_status, created_at 
FROM files 
ORDER BY created_at DESC 
LIMIT 10;

# Check clients (admin-side)
SELECT id, name, email, status FROM clients;

# Check documents (admin-side)
SELECT d.id, d.name, d.type, d.status, c.name as client_name, d.created_at
FROM documents d
JOIN clients c ON d.client_id = c.id
ORDER BY d.created_at DESC
LIMIT 10;
```

## 🔍 Verification Checklist

After uploading a file, verify:

- [ ] File appears in client backend database (`files` table)
- [ ] File is saved to local filesystem (`client_side/storage/uploads/`)
- [ ] Client record created in admin database (`clients` table)
- [ ] Document record created in admin database (`documents` table)
- [ ] Document appears in admin dashboard
- [ ] File can be downloaded from admin dashboard
- [ ] Database shows correct relationships

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
lsof -i :8001  # Client backend
lsof -i :8002  # Admin backend
lsof -i :8080  # Admin dashboard

# Kill processes on ports if needed
kill -9 $(lsof -ti:8001)
kill -9 $(lsof -ti:8002)
kill -9 $(lsof -ti:8080)
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
psql -U postgres -l | grep taxease_db

# Create database if needed
createdb -U postgres taxease_db
```

### Ngrok Not Working

```bash
# Check ngrok is running
curl http://localhost:4040/api/tunnels

# Get ngrok URL manually
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'

# Check ngrok logs
cat /tmp/ngrok.log
```

### Flutter Build Fails

```bash
# Clean and rebuild
cd frontend/tax_ease-main\ \(1\)/tax_ease-main
flutter clean
flutter pub get
flutter build apk --release
```

### File Upload Fails

1. Check client backend logs: `tail -f logs/client-backend.log`
2. Check ngrok is accessible: Open ngrok URL in browser
3. Check file size (max 10MB default)
4. Check file type (allowed: pdf, jpg, jpeg, png, doc, docx, xls, xlsx)

### Sync Not Working

1. Check admin backend is running: `curl http://localhost:8002/health`
2. Check sync service logs in client backend
3. Verify `ADMIN_API_BASE_URL` environment variable
4. Check admin backend logs: `tail -f logs/admin-backend.log`

## 📊 Database Schema

Both backends use the same database (`taxease_db`) with these tables:

### Client-Side Tables
- `users` - Client users
- `files` - Uploaded files
- `t1_personal_forms` - Tax forms
- `refresh_tokens` - Auth tokens
- `otps` - OTP codes

### Admin-Side Tables
- `admin_users` - Admin/superadmin users
- `clients` - Client records (synced from users)
- `documents` - Document records (synced from files)
- `payments` - Payment records
- `audit_logs` - Activity logs

### Relationship
- Client `User.email` → Admin `Client.email`
- Client `File.user_id` → Admin `Document.client_id` (via email lookup)

## 🛑 Stop All Services

```bash
# Stop all services
./stop-all-services.sh
```

This will:
- Stop all backends
- Stop admin dashboard
- Stop ngrok tunnel
- Clean up PID files

## 📝 Logs Location

All logs are stored in: `/home/cyberdude/Documents/Projects/CA-final/logs/`

- `client-backend.log` - Client backend logs
- `admin-backend.log` - Admin backend logs
- `admin-dashboard.log` - Admin dashboard logs
- `*.pid` - Process IDs

## ✅ Success Criteria

You've successfully completed the test when:

1. ✅ File uploaded from Flutter app
2. ✅ File appears in admin dashboard
3. ✅ File can be viewed/downloaded from admin dashboard
4. ✅ Database shows correct records in both `files` and `documents` tables
5. ✅ Client record created in admin database
6. ✅ File exists in local filesystem

## 🎯 Next Steps

After successful testing:

1. Add real-time updates (WebSocket/SSE)
2. Enhance error handling
3. Add file preview in admin dashboard
4. Add more document metadata
5. Optimize sync performance

---

**Ready to test? Run `./start-all-services.sh` and follow the steps above!** 🚀


