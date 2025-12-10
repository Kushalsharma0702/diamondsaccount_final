# Google Sign-In Port 3000 Fix

## 🔍 Issue

Google Sign-In works when running Flutter web directly (via `flutter run -d chrome`), but **doesn't work on port 3000** when started via `MASTER_CONTROL.sh`.

## 🔧 Root Cause

Google OAuth requires the **exact origin** (including port) to be added to the **Authorized JavaScript origins** in Google Cloud Console / Firebase Console.

When Flutter runs directly, it likely uses a different port (or the default which is already configured), but port 3000 needs to be explicitly authorized.

## ✅ Solution

### Step 1: Add Port 3000 to Firebase Console

1. **Go to Firebase Console:**
   - https://console.firebase.google.com/
   - Select project: **taxease-ec35f**

2. **Navigate to Authentication → Sign-in method → Google**

3. **Click on Web Client ID:**
   - Web client ID: `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8.apps.googleusercontent.com`

4. **Click "Edit" or go to Google Cloud Console:**
   - This will open Google Cloud Console
   - OR go directly: https://console.cloud.google.com/apis/credentials

5. **Edit the OAuth 2.0 Client ID:**
   - Find the client ID: `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8`
   - Click "Edit" (pencil icon)

6. **Add Authorized JavaScript origins:**
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   ```

7. **Add Authorized redirect URIs (if needed):**
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   ```

8. **Save the changes**

### Step 2: Verify Web Configuration

Ensure `mobile-app/web/index.html` has the correct meta tag:

```html
<meta name="google-signin-client_id" content="785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8.apps.googleusercontent.com">
```

### Step 3: Restart and Test

1. **Restart all services:**
   ```bash
   ./MASTER_CONTROL.sh
   # Choose option 1 (Start all services)
   ```

2. **Test Google Sign-In:**
   - Go to: http://localhost:3000
   - Click "Continue with Google"
   - Should work now! ✅

## 📋 Current Configuration

- **Web Client ID:** `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8.apps.googleusercontent.com`
- **Current Port:** `3000` (via MASTER_CONTROL.sh)
- **Default Flutter Port:** Usually `8080` or random (works because it might be already configured)

## 🔍 Verify Current Authorized Origins

To check what origins are currently authorized:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find client ID: `785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8`
3. Click to view details
4. Check "Authorized JavaScript origins" section

## ⚠️ Important Notes

1. **Changes take effect immediately** - no need to wait
2. **Multiple origins allowed** - you can have both `localhost:3000` and `localhost:8080`
3. **Must include protocol** - `http://` or `https://` is required
4. **No trailing slash** - `http://localhost:3000/` is wrong, use `http://localhost:3000`

## 🧪 Test After Configuration

```bash
# Start services
./MASTER_CONTROL.sh

# Go to browser
http://localhost:3000

# Try Google Sign-In
# Should work now! ✅
```

## 🔧 Alternative: Update MASTER_CONTROL.sh to Use Port 8080

If you prefer to use port 8080 instead (if it's already configured):

```bash
# In MASTER_CONTROL.sh, change:
--web-port 3000
# To:
--web-port 8080
```

But **port 3000** is better because:
- Admin dashboard uses 8080
- Avoids conflicts
- More organized port allocation

