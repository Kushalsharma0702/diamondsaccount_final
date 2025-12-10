# Scripts Directory

This directory contains all project scripts organized by functionality.

## 📁 Directory Structure

### `/setup`
Setup and deployment scripts:
- `start-all-services.sh` - Start all backend services
- `stop-all-services.sh` - Stop all services
- `start-ngrok.sh` - Start ngrok tunnel
- `build-flutter-apk.sh` - Build Flutter APK
- `restart-*.sh` - Restart specific services
- `update-flutter-url.sh` - Update Flutter API URL

### `/testing`
Testing and verification scripts:
- `test_*.sh` - Various test scripts
- `check_*.sh` - Health check scripts
- `QUICK_TEST_START.sh` - Quick test setup
- `RUN_TEST_NOW.sh` - Complete test runner
- `diagnose_upload_error.sh` - Error diagnostics

### `/maintenance`
Maintenance and utility scripts:
- `sync_*.py` - Database sync scripts
- `check_t1_forms.py` - T1 form checker

### `/deployment`
Deployment scripts (currently empty, reserved for future use)

---

## 🚀 Quick Start Scripts

### Start All Services
```bash
./scripts/setup/start-all-services.sh
```

### Run Tests
```bash
./scripts/testing/RUN_TEST_NOW.sh
```

### Start Ngrok Tunnel
```bash
./scripts/setup/start-ngrok.sh
```

---

## 📝 Script Categories

**Setup Scripts** (`/setup`):
- Service management (start/stop/restart)
- Environment setup
- Build scripts

**Testing Scripts** (`/testing`):
- API testing
- Health checks
- Diagnostic tools

**Maintenance Scripts** (`/maintenance`):
- Database sync
- Data validation
- Cleanup utilities

---

## ⚠️ Usage Notes

- All scripts should be run from the project root directory
- Check script permissions: `chmod +x scripts/**/*.sh`
- Review script contents before executing
- Some scripts require environment variables to be set

---

## 🔧 Making Scripts Executable

```bash
chmod +x scripts/**/*.sh
chmod +x scripts/**/*.py
```



