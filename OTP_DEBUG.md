# OTP Debugging Guide

## Current Issue

The test shows the backend is returning:
```json
{"detail":"Invalid or expired OTP"}
```

But the code should return:
```json
{"detail":"Invalid or expired OTP. Use '123456' for testing."}
```

This means the backend hasn't reloaded with the new code yet.

## Solutions

### Solution 1: Restart the Backend Manually

```bash
# Stop the backend
pkill -f "uvicorn main:app.*8001"

# Start it again
cd client_side
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Solution 2: Use the Restart Script

```bash
./restart-client-backend.sh
```

### Solution 3: Touch the File to Trigger Reload

If uvicorn is running with `--reload`, touching the file should trigger a reload:

```bash
touch client_side/main.py
```

## Verify the Fix

After restarting, test again:

```bash
./test_otp.sh
```

Expected response:
```json
{"message":"OTP verified successfully","success":true}
```

## Check Backend Logs

```bash
# If running in foreground, you'll see logs directly
# If running in background, check:
tail -f logs/client_backend.log
```

Look for:
```
OTP verification attempt for test@example.com: code='123456', purpose=email_verification, developer_otp='123456'
✅ Developer OTP matched!
✅ OTP verified (developer bypass)
```

## Common Issues

1. **Backend not reloaded** - Most common issue. Restart the backend.
2. **Wrong DEVELOPER_OTP value** - Check with:
   ```bash
   cd client_side && python3 -c "from shared.utils import DEVELOPER_OTP; print(DEVELOPER_OTP)"
   ```
3. **Code comparison failing** - Check the logs for the normalized code values.


