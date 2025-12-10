# 🧪 Complete Test Setup - Ready to Run!

## 🎯 What's Been Set Up

### ✅ Database Unification
- **Both backends now use the same database**: `taxease_db`
- Client Backend: Uses existing `taxease_db`
- Admin Backend: Updated to use `taxease_db` (changed from `taxhub_db`)

### ✅ Services Configuration
- **Client Backend**: Port 8001
- **Admin Backend**: Port 8002  
- **Admin Dashboard**: Port 8080
- **Ngrok**: Will expose port 8001 for mobile access

### ✅ Integration Features
- **Local Filesystem Storage**: Files saved to `client_side/storage/uploads/`
- **Auto-Sync**: Files automatically sync to admin backend
- **Client Creation**: Admin clients created automatically from user email
- **Document Mapping**: Files mapped to admin documents

## 🚀 Quick Start - 3 Commands

### Step 1: Start All Services + Ngrok

```bash
./QUICK_TEST_START.sh
```

This will:
- ✅ Start client backend (port 8001)
- ✅ Start admin backend (port 8002)
- ✅ Start admin dashboard (port 8080)
- ✅ Start ngrok tunnel
- ✅ Update Flutter app URL automatically

**Copy the ngrok URL that's displayed!**

### Step 2: Build Flutter APK

```bash
./build-flutter-apk.sh
```

This will create the APK at:
```
frontend/tax_ease-main (1)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

### Step 3: Install & Test

```bash
# Install on device
adb install frontend/tax_ease-main\ \(1\)/tax_ease-main/build/app/outputs/flutter-apk/app-release.apk
```

Or transfer the APK file to your device and install manually.

## 📋 Manual Step-by-Step (If Needed)

### 1. Start All Services

```bash
./start-all-services.sh
```

Wait for all services to start (you'll see ✅ messages).

### 2. Start Ngrok (New Terminal)

```bash
./start-ngrok.sh
```

**Copy the ngrok URL** (e.g., `https://abcd1234.ngrok.io`)

### 3. Update Flutter URL

```bash
./update-flutter-url.sh ngrok https://your-ngrok-url.ngrok.io
```

### 4. Build APK

```bash
./build-flutter-apk.sh
```

## 🧪 Testing Steps

### Upload File from Flutter

1. Open Flutter app on device
2. Register/Login with email (e.g., `test@example.com`)
3. Go to Documents/Upload
4. Select and upload a file
5. Wait for success message

### Check Admin Dashboard

1. Open: http://localhost:8080
2. Login:
   - Email: `superadmin@taxease.ca`
   - Password: `demo123`
3. Go to **Documents** page
4. You should see:
   - Client card with your email
   - File listed under the client
   - Click to expand and see details

### Check Database

```bash
# Connect to database
psql -U postgres -d taxease_db

# Check uploaded file
SELECT id, original_filename, file_type, upload_status, created_at 
FROM files 
ORDER BY created_at DESC 
LIMIT 5;

# Check client created
SELECT id, name, email, status 
FROM clients 
ORDER BY created_at DESC 
LIMIT 5;

# Check document created
SELECT d.id, d.name, d.type, d.status, c.name as client_name
FROM documents d
JOIN clients c ON d.client_id = c.id
ORDER BY d.created_at DESC
LIMIT 5;
```

## 🔍 Verification Checklist

After uploading a file:

- [ ] ✅ File in database (`files` table)
- [ ] ✅ File saved to filesystem (`client_side/storage/uploads/`)
- [ ] ✅ Client created in admin DB (`clients` table)
- [ ] ✅ Document created in admin DB (`documents` table)
- [ ] ✅ Document visible in admin dashboard
- [ ] ✅ File grouped under correct client card

## 🛑 Stop Everything

```bash
./stop-all-services.sh
```

## 📊 Service URLs

| Service | URL |
|---------|-----|
| Client Backend | http://localhost:8001 |
| Client Backend Docs | http://localhost:8001/docs |
| Admin Backend | http://localhost:8002 |
| Admin Backend Docs | http://localhost:8002/docs |
| Admin Dashboard | http://localhost:8080 |
| Ngrok Dashboard | http://localhost:4040 |

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check ports
lsof -i :8001
lsof -i :8002
lsof -i :8080

# Kill if needed
kill -9 $(lsof -ti:8001)
```

### Database Issues
```bash
# Check database
./check-database-connection.sh

# Create if needed
createdb -U postgres taxease_db
```

### Ngrok Not Working
```bash
# Check ngrok
curl http://localhost:4040/api/tunnels

# View dashboard
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
```

## ✅ Success!

You've successfully tested when:
1. ✅ File uploaded from Flutter
2. ✅ File appears in admin dashboard
3. ✅ Database shows all records
4. ✅ File exists in filesystem

---

**Ready? Run `./QUICK_TEST_START.sh` now!** 🚀




