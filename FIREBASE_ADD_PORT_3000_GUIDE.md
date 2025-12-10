# Add Port 3000 to Google Sign-In Authorized Origins

## 🎯 Quick Fix

Google Sign-In requires **exact origin matching**. You must add `http://localhost:3000` to the authorized JavaScript origins in Google Cloud Console.

## 📋 Step-by-Step Instructions

### Method 1: Via Firebase Console (Easiest)

1. **Go to Firebase Console:**
   - https://console.firebase.google.com/
   - Select project: **taxease-ec35f**

2. **Navigate to Authentication:**
   - Click **Authentication** in left sidebar
   - Click **Sign-in method** tab
   - Find **Google** provider
   - Click the **pencil icon** (edit)

3. **Copy Web Client ID:**
   - Copy: `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8.apps.googleusercontent.com`
   - Click on it to open Google Cloud Console

### Method 2: Directly via Google Cloud Console

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/apis/credentials
   - Select project: **taxease-ec35f** (or your Firebase project)

2. **Find OAuth 2.0 Client ID:**
   - Look for: `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8`
   - Type: **Web client** or **Web application**
   - Click **Edit** (pencil icon)

3. **Add Authorized JavaScript origins:**
   - In "Authorized JavaScript origins" section, click **+ ADD URI**
   - Add: `http://localhost:3000`
   - Add: `http://127.0.0.1:3000`
   - Click **Save**

4. **Verify Authorized redirect URIs:**
   - Check "Authorized redirect URIs" section
   - Should include: `http://localhost:3000`
   - If not, add it

### Current Configuration Should Include:

**Authorized JavaScript origins:**
```
http://localhost
http://localhost:8080
http://localhost:3000  ← ADD THIS
http://127.0.0.1:3000  ← ADD THIS (optional but recommended)
```

**Authorized redirect URIs:**
```
http://localhost
http://localhost:8080
http://localhost:3000  ← ADD THIS (if needed)
```

## ✅ Verification

After adding port 3000:

1. **Wait 1-2 minutes** for changes to propagate
2. **Restart Flutter app:**
   ```bash
   ./MASTER_CONTROL.sh
   # Choose option 1 (Start all services)
   ```

3. **Test Google Sign-In:**
   - Go to: http://localhost:3000
   - Click "Continue with Google"
   - Should work! ✅

## 🔍 Why This Happens

- Google OAuth requires **exact origin matching** (protocol + domain + port)
- `http://localhost:3000` ≠ `http://localhost:8080`
- Each port needs to be explicitly authorized
- When running `flutter run -d chrome` directly, it might use a different port that's already authorized

## 📝 Alternative: Use Chrome Port

If you want to avoid this, you can modify `MASTER_CONTROL.sh` to use Chrome directly instead of web-server:

```bash
# In MASTER_CONTROL.sh, change:
flutter run -d web-server --web-port 3000

# To:
flutter run -d chrome --web-port 3000
```

This might use a different OAuth flow, but the **proper fix** is to add port 3000 to authorized origins.

## 🚀 Quick Command to Add Origin

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on the OAuth client ID
3. Add `http://localhost:3000` to authorized origins
4. Save
5. Done! ✅

