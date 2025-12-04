# 🎯 Complete Test Setup - Ready to Go!

## ✅ Everything is Configured

### Database
- ✅ **Both backends use the same database**: `taxease_db`
- ✅ Client Backend: Uses `taxease_db` 
- ✅ Admin Backend: Updated to use `taxease_db` (was `taxhub_db`)

### Services
- ✅ Client Backend: Port 8001
- ✅ Admin Backend: Port 8002
- ✅ Admin Dashboard: Port 8080
- ✅ Ngrok: Will expose port 8001

### Scripts Created
- ✅ `start-all-services.sh` - Start all services
- ✅ `start-ngrok.sh` - Start ngrok tunnel
- ✅ `stop-all-services.sh` - Stop all services
- ✅ `update-flutter-url.sh` - Update Flutter API URL
- ✅ `build-flutter-apk.sh` - Build Flutter APK
- ✅ `QUICK_TEST_START.sh` - Master startup script
- ✅ `check-database-connection.sh` - Check database

## 🚀 Quick Start - 3 Commands

### Option 1: Automatic (Recommended)

```bash
# Start everything automatically
./QUICK_TEST_START.sh
```

This will:
1. Start all services
2. Start ngrok
3. Update Flutter app URL
4. Show you all URLs

### Option 2: Manual Step-by-Step

```bash
# Step 1: Start all services
./start-all-services.sh

# Step 2: Start ngrok (in separate terminal)
./start-ngrok.sh

# Step 3: Update Flutter URL (use ngrok URL from step 2)
./update-flutter-url.sh ngrok https://xxxx.ngrok.io

# Step 4: Build APK
./build-flutter-apk.sh
```

## 📋 Detailed Steps

### 1. Check Database

```bash
# Check database connection
./check-database-connection.sh
```

### 2. Start All Services

```bash
# Start client backend, admin backend, and admin dashboard
./start-all-services.sh
```

Wait for all services to be ready (you'll see ✅ messages).

### 3. Start Ngrok Tunnel

In a **new terminal**:

```bash
./start-ngrok.sh
```

This will:
- Start ngrok tunnel
- Display the public URL (e.g., `https://abcd1234.ngrok.io`)
- Save URL to `/tmp/ngrok_url.txt`

**Copy the ngrok URL!**

### 4. Update Flutter App

```bash
# Update Flutter app with ngrok URL
./update-flutter-url.sh ngrok https://your-ngrok-url.ngrok.io
```

Or manually edit:
- File: `frontend/tax_ease-main (1)/tax_ease-main/lib/core/constants/api_endpoints.dart`
- Set: `BASE_URL = 'https://your-ngrok-url.ngrok.io/api/v1'`

### 5. Build Flutter APK

```bash
# Build the APK (this takes a few minutes)
./build-flutter-apk.sh
```

APK location:
```
frontend/tax_ease-main (1)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

### 6. Install APK on Device

```bash
# Connect Android device via USB
adb devices

# Install APK
adb install frontend/tax_ease-main\ \(1\)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

Or transfer APK file to device and install manually.

## 🧪 Testing Workflow

### Test File Upload

1. **Open Flutter App** on your device
2. **Login/Register**:
   - Register a new user with email (e.g., `test@example.com`)
   - Or login with existing credentials
3. **Upload File**:
   - Go to Documents/Upload section
   - Select a file (PDF, image, etc.)
   - Upload the file
   - Wait for success message

### Verify in Admin Dashboard

1. **Open Admin Dashboard**: http://localhost:8080
2. **Login**:
   - Email: `superadmin@taxease.ca`
   - Password: `demo123`
3. **Check Documents Page**:
   - Go to "Documents" in sidebar
   - You should see a client card with your email
   - File should be listed under the client
   - Click to expand and see file details

### Check Database

```bash
# Connect to database
psql -U postgres -d taxease_db

# Check uploaded file
SELECT id, original_filename, file_type, upload_status, created_at 
FROM files 
ORDER BY created_at DESC 
LIMIT 5;

# Check client created in admin
SELECT id, name, email, status 
FROM clients 
ORDER BY created_at DESC 
LIMIT 5;

# Check document created
SELECT d.id, d.name, d.type, d.status, c.name as client_name, d.created_at
FROM documents d
JOIN clients c ON d.client_id = c.id
ORDER BY d.created_at DESC
LIMIT 5;
```

## 📊 Service Status

After starting services, check:

| Service | URL | Status Check |
|---------|-----|--------------|
| Client Backend | http://localhost:8001 | `curl http://localhost:8001/health` |
| Admin Backend | http://localhost:8002 | `curl http://localhost:8002/health` |
| Admin Dashboard | http://localhost:8080 | Open in browser |
| Ngrok | https://xxxx.ngrok.io | `curl http://localhost:4040/api/tunnels` |

## 🔍 Verification Checklist

After uploading a file from Flutter app:

- [ ] ✅ File appears in client backend database (`files` table)
- [ ] ✅ File saved to `client_side/storage/uploads/user_{user_id}/`
- [ ] ✅ Client record created in admin database (`clients` table)
- [ ] ✅ Document record created in admin database (`documents` table)
- [ ] ✅ Document visible in admin dashboard Documents page
- [ ] ✅ File grouped under correct client card
- [ ] ✅ Database shows correct relationships

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using the ports
lsof -i :8001  # Client backend
lsof -i :8002  # Admin backend  
lsof -i :8080  # Admin dashboard

# Kill processes if needed
kill -9 $(lsof -ti:8001)
kill -9 $(lsof -ti:8002)
kill -9 $(lsof -ti:8080)
```

### Database Not Found

```bash
# Create database
createdb -U postgres taxease_db

# Or check connection
./check-database-connection.sh
```

### Ngrok Not Working

```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# View ngrok dashboard
open http://localhost:4040  # or visit in browser

# Get URL manually
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool
```

### Flutter Build Issues

```bash
cd frontend/tax_ease-main\ \(1\)/tax_ease-main

# Clean and rebuild
flutter clean
flutter pub get
flutter build apk --release
```

### File Upload Fails

1. Check client backend logs: `tail -f logs/client-backend.log`
2. Check ngrok is accessible from device (open URL in device browser)
3. Check file size (max 10MB)
4. Check file type (PDF, JPG, PNG, DOC, DOCX, XLS, XLSX)

### Files Not Appearing in Admin

1. Check admin backend is running: `curl http://localhost:8002/health`
2. Check sync logs in client backend
3. Check admin backend logs: `tail -f logs/admin-backend.log`
4. Verify client was created: Check `clients` table in database

## 📝 Logs Location

All logs are in: `/home/cyberdude/Documents/Projects/CA-final/logs/`

- `client-backend.log` - Client backend logs
- `admin-backend.log` - Admin backend logs
- `admin-dashboard.log` - Admin dashboard logs

View logs:
```bash
# Watch client backend logs
tail -f logs/client-backend.log

# Watch admin backend logs
tail -f logs/admin-backend.log
```

## 🛑 Stop Everything

```bash
# Stop all services
./stop-all-services.sh
```

## 🎯 Success Criteria

Test is successful when:

1. ✅ File uploaded from Flutter app on device
2. ✅ File appears in admin dashboard under Documents
3. ✅ File grouped under correct client card
4. ✅ Database shows:
   - File record in `files` table
   - Client record in `clients` table  
   - Document record in `documents` table
5. ✅ File exists in filesystem: `client_side/storage/uploads/`

## 🚀 Ready to Test!

Run this command to start everything:

```bash
./QUICK_TEST_START.sh
```

Then:
1. Build APK: `./build-flutter-apk.sh`
2. Install on device
3. Upload a file
4. Check admin dashboard!

---

**All scripts are ready! Start testing! 🎉**


