# Testing Google Sign-In in Web Mode

## Quick Start

1. **Run the app in web mode:**
   ```bash
   cd mobile-app
   flutter run -d chrome
   ```

   Or if Chrome is not detected:
   ```bash
   flutter run -d web-server --web-port 8080
   ```

2. **Navigate to the login page** in your browser

3. **Test Google Sign-In:**
   - Click the "Login with Google (Test)" button (blue button)
   - Or click "Continue with Google" (outlined button)
   - Check browser console for debug output:
     - `Google login user: [email]`
     - `Google login ID token: [token]...`

## Google Sign-In Web Configuration

For Google Sign-In to work in web mode, you need to:

1. **Get OAuth 2.0 Client ID from Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project (or create one)
   - Enable Google+ API
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID (Web application)
   - Add authorized JavaScript origins:
     - `http://localhost:8080`
     - `http://localhost:3000`
     - `http://127.0.0.1:8080`
   - Add authorized redirect URIs:
     - `http://localhost:8080`
     - `http://localhost:3000`

2. **Configure in Firebase Console:**
   - Go to Firebase Console → Authentication → Sign-in method
   - Enable Google Sign-In provider
   - Add your OAuth 2.0 Client ID

3. **Update Flutter Web Configuration:**
   - The Google Sign-In package should automatically use Firebase configuration
   - Ensure `firebase_options.dart` is properly generated with web configuration

## Troubleshooting

### "Google Sign-In failed" error
- Check that Google Sign-In is enabled in Firebase Console
- Verify OAuth 2.0 Client ID is configured
- Check browser console for detailed error messages

### No Google Sign-In popup
- Check browser popup blockers
- Ensure cookies are enabled
- Try in incognito mode to rule out extension interference

### Firebase not initialized
- Ensure `flutterfire configure` has been run
- Check that `firebase_options.dart` contains web configuration
- Verify Firebase project is set up correctly

## Testing Notes

- The test button prints to console (check browser DevTools)
- Both buttons will attempt Google Sign-In
- Check browser console for detailed logs
- The "Continue with Google" button also exchanges token with backend
- The test button only prints to console (doesn't navigate)

