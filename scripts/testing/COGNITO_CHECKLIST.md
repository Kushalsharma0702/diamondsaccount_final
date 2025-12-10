# Cognito Authentication Setup Checklist

## ✅ Steps to Enable USER_PASSWORD_AUTH in AWS Console

Based on your Cognito console screenshots, follow these steps:

### Step 1: Navigate to App Client
1. Go to AWS Cognito Console: https://console.aws.amazon.com/cognito/v2/idp/user-pools
2. Select region: **Canada (Central)**
3. Click on User Pool: **caxmb4**
4. In left sidebar, click **App clients**
5. Click on: **TaxEaseApp** (Client ID: 504mgtvq1h97vlml90c3iibnt0)

### Step 2: Edit App Client Settings
1. Click the **Edit** button (top right, or "Edit app client information")

### Step 3: Enable Authentication Flow
In the "Authentication flows" section, make sure you **CHECK** the following:

- ✅ **Sign in with username and password: ALLOW_USER_PASSWORD_AUTH**
  - This is REQUIRED for server-side authentication
  - Our FastAPI backend uses this flow

Optional but recommended:
- ✅ Sign in with secure remote password (SRP): ALLOW_USER_SRP_AUTH
- ✅ Get new user tokens from existing authenticated sessions: ALLOW_REFRESH_TOKEN_AUTH

### Step 4: Save Changes
1. Scroll down and click **Save changes**

### Step 5: Verify
After saving, check the "App client information" page:
- Under "Authentication flows", you should see: **Username and password**

If you see this, the flow is enabled! ✅

## 🔍 Current Status Check

From your screenshots, I can see:
- ✅ App Client exists: TaxEaseApp
- ✅ Client ID: 504mgtvq1h97vlml90c3iibnt0
- ⚠️ Need to verify: "Username and password" checkbox is checked

## 🧪 Testing After Enabling

Once you've enabled USER_PASSWORD_AUTH, run:

```bash
# Restart backend to pick up any changes
cd /home/cyberdude/Documents/Projects/CA-final
./MASTER_CONTROL.sh  # Option 1: Start all services

# Or manually restart backend
cd client_side
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)
uvicorn main:app --host 0.0.0.0 --port 8001

# In another terminal, run tests
python3 scripts/testing/test_auth_automated.py
```

## 📋 What Each Flow Does

1. **ALLOW_USER_PASSWORD_AUTH** ✅ REQUIRED
   - Server-side authentication with email/password
   - Used by our FastAPI backend
   - Required for `initiate_auth` with `USER_PASSWORD_AUTH`

2. **ALLOW_USER_SRP_AUTH**
   - Client-side SRP authentication
   - More secure for client applications
   - Optional for our use case

3. **ALLOW_REFRESH_TOKEN_AUTH**
   - Token refresh functionality
   - Usually enabled by default
   - Recommended to keep enabled

4. **ALLOW_ADMIN_USER_PASSWORD_AUTH**
   - Admin operations
   - Optional unless needed for admin functions

## ❌ Common Error Messages

If you see: **"USER_PASSWORD_AUTH flow not enabled for this client"**
- Solution: Enable "Sign in with username and password" checkbox

If you see: **"NotAuthorizedException"**
- This means the flow is enabled but credentials are wrong
- This is actually good - it means authentication is working!

## 🎯 Quick Reference

- **User Pool ID**: ca-central-1_FP2WE41eW
- **User Pool Name**: caxmb4  
- **App Client Name**: TaxEaseApp
- **Client ID**: 504mgtvq1h97vlml90c3iibnt0
- **Required Flow**: ALLOW_USER_PASSWORD_AUTH

