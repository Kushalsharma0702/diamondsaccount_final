# Missing Form Issue - jijaji@gmail.com

## Problem
User `jijaji@gmail.com` filled a T1 form but it's not appearing in the admin dashboard.

## Root Cause
1. **User doesn't exist in database** - The user was never registered in the system
2. **Form only saved locally** - Form was saved in Flutter SharedPreferences but NOT submitted to backend
3. **API endpoint issue** - Was using expired ngrok URL instead of localhost

## Why Forms Aren't Submitted

Forms require **authentication** to submit:
- Backend endpoint `/api/v1/tax/t1-personal` requires `get_current_user` dependency
- If user isn't logged in or JWT token is invalid, submission fails
- Form is saved locally (SharedPreferences) but not in database

## Solution

### For Existing User (jijaji@gmail.com):

1. **User must be registered first:**
   ```bash
   # Check if user exists
   # If not, user needs to register/login through the app
   ```

2. **User must submit the form:**
   - Form must be in "submitted" status (not just "draft")
   - Form submission calls `T1FormApi.submitForm()` which POSTs to backend
   - Backend creates entry in `t1_personal_forms` table

3. **Fix API endpoint:**
   - ✅ Updated `api_endpoints.dart` to use `http://localhost:8001` instead of ngrok
   - ✅ Form submission now uses correct endpoint

### Steps to Fix:

1. **Check if user is logged in:**
   - User must have valid JWT token
   - Token stored in SharedPreferences as `auth_token`

2. **Ensure backend is running:**
   ```bash
   # Backend should be on http://localhost:8001
   curl http://localhost:8001/api/v1/health
   ```

3. **Submit the form:**
   - User needs to open the filled form
   - Click "Submit Form" button
   - Form will be sent to backend API

4. **Verify in database:**
   ```sql
   SELECT * FROM users WHERE email = 'jijaji@gmail.com';
   SELECT * FROM t1_personal_forms WHERE user_id = (SELECT id FROM users WHERE email = 'jijaji@gmail.com');
   ```

## Current Status

- ✅ API endpoint fixed (localhost instead of ngrok)
- ✅ Form submission code is correct
- ❌ User `jijaji@gmail.com` doesn't exist in database
- ❌ No forms in database for this email

## Next Steps

1. User needs to **register/login** with `jijaji@gmail.com`
2. User needs to **fill and submit** the form again (or resubmit existing local form)
3. Form will then appear in admin dashboard

## Testing

To test form submission:
```bash
# 1. Login as user
# 2. Fill T1 form
# 3. Click "Submit Form"
# 4. Check database:
python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check():
    engine = create_async_engine('postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db')
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        result = await session.execute(text(\"SELECT * FROM t1_personal_forms ORDER BY created_at DESC LIMIT 5\"))
        for row in result:
            print(row)
    await engine.dispose()

asyncio.run(check())
"
```

