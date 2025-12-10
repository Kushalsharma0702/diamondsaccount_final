# 🚀 START TESTING - Complete Setup Ready!

## ✅ Everything is Configured!

### Database
- ✅ **Both backends use the same database**: `taxease_db`
- ✅ Client Backend: `postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db`
- ✅ Admin Backend: Updated to use `taxease_db`

### Services & Ports
- ✅ Client Backend: **Port 8001**
- ✅ Admin Backend: **Port 8002**
- ✅ Admin Dashboard: **Port 8080**
- ✅ Ngrok: Will expose port 8001

### Integration Features
- ✅ Local filesystem storage (`client_side/storage/uploads/`)
- ✅ Auto-sync (File → Document)
- ✅ Client creation from email
- ✅ Ngrok tunnel setup
- ✅ Flutter URL auto-update

## 🎯 3-STEP QUICK START

### Step 1: Start Everything

```bash
./RUN_TEST_NOW.sh
```

This will:
- ✅ Start client backend (port 8001)
- ✅ Start admin backend (port 8002)
- ✅ Start admin dashboard (port 8080)
- ✅ Start ngrok tunnel
- ✅ Update Flutter app with ngrok URL
- ✅ Show all URLs and next steps

**Copy the ngrok URL from the output!**

### Step 2: Build Flutter APK

```bash
./build-flutter-apk.sh
```

APK location:
```
frontend/tax_ease-main (1)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

### Step 3: Install & Test

```bash
# Install on Android device
adb install frontend/tax_ease-main\ \(1\)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

Or transfer APK file to device and install manually.

## 🧪 Test Workflow

### 1. Upload File from Flutter
- Open Flutter app
- Register/Login (e.g., `test@example.com`)
- Upload a file
- Wait for success message

### 2. Check Admin Dashboard
- Open: http://localhost:8080
- Login: `superadmin@taxease.ca` / `demo123`
- Go to Documents page
- See file under client card

### 3. Check Database
```bash
psql -U postgres -d taxease_db

# Check uploaded file
SELECT id, original_filename, file_type, upload_status, created_at 
FROM files ORDER BY created_at DESC LIMIT 5;

# Check client created
SELECT id, name, email, status FROM clients ORDER BY created_at DESC LIMIT 5;

# Check document created
SELECT d.id, d.name, d.type, d.status, c.name as client_name
FROM documents d JOIN clients c ON d.client_id = c.id
ORDER BY d.created_at DESC LIMIT 5;
```

## 📋 All Available Scripts

| Script | Purpose |
|--------|---------|
| `RUN_TEST_NOW.sh` | **Master script - starts everything** |
| `start-all-services.sh` | Start all services (without ngrok) |
| `start-ngrok.sh` | Start ngrok tunnel only |
| `stop-all-services.sh` | Stop all services |
| `update-flutter-url.sh` | Update Flutter API URL manually |
| `build-flutter-apk.sh` | Build Flutter APK |
| `check-database-connection.sh` | Check database setup |

## 🔍 Verification Checklist

After uploading a file:

- [ ] ✅ File in database (`files` table)
- [ ] ✅ File saved to filesystem (`client_side/storage/uploads/`)
- [ ] ✅ Client created (`clients` table)
- [ ] ✅ Document created (`documents` table)
- [ ] ✅ Document visible in admin dashboard
- [ ] ✅ File grouped under correct client card

## 📊 Service URLs

After starting services:

- Client Backend: http://localhost:8001
- Client Backend Docs: http://localhost:8001/docs
- Admin Backend: http://localhost:8002
- Admin Backend Docs: http://localhost:8002/docs
- Admin Dashboard: http://localhost:8080
- Ngrok Dashboard: http://localhost:4040

## 🛑 Stop Everything

```bash
./stop-all-services.sh
```

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check ports
lsof -i :8001
lsof -i :8002
lsof -i :8080

# Kill processes
kill -9 $(lsof -ti:8001)
kill -9 $(lsof -ti:8002)
kill -9 $(lsof -ti:8080)
```

### Database Issues
```bash
# Check database
./check-database-connection.sh

# Create database if needed
createdb -U postgres taxease_db
```

### Ngrok Issues
```bash
# Check ngrok status
curl http://localhost:4040/api/tunnels

# View ngrok dashboard
open http://localhost:4040
```

### Flutter Build Issues
```bash
cd frontend/tax_ease-main\ \(1\)/tax_ease-main
flutter clean
flutter pub get
flutter build apk --release
```

## 📝 Logs

All logs are in: `logs/`

```bash
# Watch logs
tail -f logs/client-backend.log
tail -f logs/admin-backend.log
tail -f logs/admin-dashboard.log
```

## 🎉 Ready to Test!

**Run this command to start everything:**

```bash
./RUN_TEST_NOW.sh
```

Then:
1. Build APK: `./build-flutter-apk.sh`
2. Install on device
3. Upload a file
4. Check admin dashboard!

---

**All systems are ready! 🚀**




