# Google Sign-In Web Configuration Guide

## Quick Setup

To enable Google Sign-In on Flutter Web, you need to configure the Web OAuth Client ID.

## Step 1: Get Your Web Client ID

1. **Go to Firebase Console:**
   - Visit: https://console.firebase.google.com/
   - Select your project: **taxease-ec35f**

2. **Navigate to Authentication Settings:**
   - Click on **Authentication** in the left sidebar
   - Click on **Sign-in method** tab
   - Find **Google** provider (enable it if not already enabled)
   - Click on the **Google** provider to open settings

3. **Copy the Web Client ID:**
   - Look for **Web client ID** in the configuration
   - It will be in format: `XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com`
   - Copy this entire string

## Step 2: Add Client ID to index.html

1. **Open the file:**
   ```
   mobile-app/web/index.html
   ```

2. **Find the meta tag:**
   ```html
   <meta name="google-signin-client_id" content="YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com">
   ```

3. **Replace the placeholder:**
   - Replace `YOUR_WEB_CLIENT_ID_HERE.apps.googleusercontent.com` with your actual Web Client ID
   - Example:
     ```html
     <meta name="google-signin-client_id" content="785722200056-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com">
     ```

4. **Save the file**

## Step 3: Verify Configuration

1. **Restart your Flutter web app:**
   ```bash
   cd mobile-app
   flutter run -d chrome
   ```

2. **Test Google Sign-In:**
   - Navigate to the login page
   - Click "Continue with Google" or "Login with Google (Test)" button
   - Google Sign-In popup should appear (no errors)

## Alternative: Programmatic Configuration

If you prefer to set the client ID programmatically instead of using the meta tag:

1. **Open:**
   ```
   mobile-app/lib/core/firebase/google_sign_in_service.dart
   ```

2. **Find the `_ensureInitialized()` method** (around line 17)

3. **Uncomment and update the `clientId` parameter:**
   ```dart
   _googleSignIn ??= GoogleSignIn(
     scopes: ['email', 'profile'],
     clientId: 'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com', // Your actual client ID
   );
   ```

4. **Remove or comment out the meta tag in `index.html`**

## Troubleshooting

### Error: "ClientID not set"
- **Solution:** Make sure you've added the meta tag in `index.html` or provided `clientId` parameter
- **Solution:** Verify the client ID format is correct (ends with `.apps.googleusercontent.com`)
- **Solution:** Ensure there are no extra spaces or quotes in the meta tag

### Error: "Invalid client ID"
- **Solution:** Double-check you're using the **Web client ID**, not iOS or Android client ID
- **Solution:** Verify the client ID in Firebase Console matches what you entered

### Google Sign-In popup doesn't appear
- **Solution:** Check browser console for errors
- **Solution:** Verify you're testing on an authorized domain (localhost is usually allowed by default)
- **Solution:** In Firebase Console > Authentication > Settings > Authorized domains, ensure your domain is listed

### Still having issues?
1. Check Firebase Console > Authentication > Sign-in method > Google is enabled
2. Verify the Web OAuth client is configured in Google Cloud Console
3. Check browser console (F12) for detailed error messages

## Security Notes

- **Never commit your client ID to public repositories** if it contains sensitive information
- The Web client ID is safe to use in client-side code (it's public)
- OAuth 2.0 secrets should never be exposed to client-side code

## Reference Links

- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Google Sign-In for Web](https://developers.google.com/identity/sign-in/web)
- [Flutter Google Sign-In Plugin](https://pub.dev/packages/google_sign_in)

