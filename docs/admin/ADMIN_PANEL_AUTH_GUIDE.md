# Admin Panel Authentication Guide

## ✅ Admin Users Ready!

Default admin users have been created and are ready to use.

## 🔑 Login Credentials

### Superadmin (Full Access)
- **Email:** `superadmin@taxease.ca`
- **Password:** `demo123`
- **Role:** `superadmin`
- **Access:** Full access to all features and settings

### Admin (Limited Access)
- **Email:** `admin@taxease.ca`
- **Password:** `demo123`
- **Role:** `admin`
- **Access:** Permissions defined by superadmin

## 🚀 How to Login

### Option 1: Via Admin Dashboard Web Interface

1. **Start the admin dashboard:**
   ```bash
   cd tax-hub-dashboard
   npm run dev
   ```

2. **Open in browser:**
   - Navigate to: `http://localhost:8080`
   - You'll see the login page

3. **Enter credentials:**
   - Email: `superadmin@taxease.ca`
   - Password: `demo123`
   - Click "Sign In"

4. **Success!** You'll be redirected to the dashboard

### Option 2: Via API

```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@taxease.ca",
    "password": "demo123"
  }'
```

**Response:**
```json
{
  "user": {
    "id": "...",
    "email": "superadmin@taxease.ca",
    "name": "Super Admin",
    "role": "superadmin",
    "permissions": [...]
  },
  "token": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

## 📋 Services & Ports

- **Admin Dashboard Frontend:** `http://localhost:8080`
- **Admin Backend API:** `http://localhost:8002/api/v1`
- **Client Backend API:** `http://localhost:8001/api/v1`

## 🔧 Configuration

### Backend Port
The admin backend runs on port **8002** (configured in `tax-hub-dashboard/backend/start.sh`)

### Frontend API URL
The frontend is configured to use:
- Default: `http://localhost:8000/api/v1` (needs to be updated to 8002)
- Environment variable: `VITE_API_BASE_URL`

### Update Frontend API URL

If the frontend can't connect, check/update the API URL:

1. **Check `.env` file in `tax-hub-dashboard/`:**
   ```bash
   cat tax-hub-dashboard/.env
   ```

2. **Create/Update `.env` file:**
   ```bash
   echo "VITE_API_BASE_URL=http://localhost:8002/api/v1" > tax-hub-dashboard/.env
   ```

3. **Restart frontend:**
   ```bash
   cd tax-hub-dashboard
   npm run dev
   ```

## 🧪 Test Authentication

### Quick Test Script

```bash
# Test login
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@taxease.ca", "password": "demo123"}'
```

### Get Current User

After login, use the access token:

```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:8002/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

## 🔄 Create/Update Admin Users

### Create Default Admins

```bash
cd tax-hub-dashboard/backend
python3 create_default_admin.py
```

### Create Custom Admin

```bash
cd tax-hub-dashboard/backend
python3 create_admin.py \
  <email> \
  <name> \
  <password> \
  <role> \
  [permissions...]

# Example:
python3 create_admin.py \
  "admin2@taxease.ca" \
  "Admin Two" \
  "password123" \
  "admin" \
  "add_edit_client" "view_analytics"
```

## 🔐 Authentication Flow

1. **User enters credentials** on login page
2. **Frontend sends POST** to `/api/v1/auth/login`
3. **Backend validates** credentials and creates JWT tokens
4. **Frontend stores** access token in `localStorage` as `taxease_access_token`
5. **Frontend includes** token in `Authorization: Bearer <token>` header for all requests
6. **Backend validates** token on protected routes

## 🐛 Troubleshooting

### Issue: Login fails with "Incorrect email or password"

**Solutions:**
1. **Verify admin exists:**
   ```bash
   cd tax-hub-dashboard/backend
   python3 create_default_admin.py
   ```

2. **Check backend is running:**
   ```bash
   curl http://localhost:8002/health
   ```

3. **Check credentials are correct:**
   - Email: `superadmin@taxease.ca`
   - Password: `demo123`

### Issue: CORS errors

**Solution:** Backend should have CORS configured. Check `tax-hub-dashboard/backend/app/main.py` includes:
```python
CORSMiddleware(
    allow_origins=["http://localhost:8080", ...],
    ...
)
```

### Issue: Frontend can't connect to backend

**Solutions:**
1. **Check API URL:**
   - Frontend should point to `http://localhost:8002/api/v1`
   - Update `.env` file if needed

2. **Verify backend is running:**
   ```bash
   ps aux | grep "uvicorn.*8002"
   ```

3. **Check port 8002 is accessible:**
   ```bash
   curl http://localhost:8002/health
   ```

### Issue: Token expired

**Solution:** Tokens expire after 15 minutes. Re-login to get a new token. Refresh token can be used to get a new access token.

## 📝 Files Reference

- **Login Page:** `tax-hub-dashboard/src/pages/Login.tsx`
- **Auth Context:** `tax-hub-dashboard/src/contexts/AuthContext.tsx`
- **API Service:** `tax-hub-dashboard/src/services/api.ts`
- **Backend Auth Routes:** `tax-hub-dashboard/backend/app/api/v1/auth.py`
- **Admin Model:** `tax-hub-dashboard/backend/app/models/admin_user.py`

## ✅ Status

- ✅ Admin users created
- ✅ Passwords set to `demo123`
- ✅ Accounts activated
- ✅ Backend authentication working
- ✅ Frontend login page configured

---

**Ready to use!** Login at `http://localhost:8080` with the credentials above.




