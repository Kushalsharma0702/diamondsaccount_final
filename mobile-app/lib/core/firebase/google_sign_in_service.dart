import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'firebase_service.dart';
import 'firebase_auth_service.dart';
import '../logger/app_logger.dart';

/// Google Sign-In Service (via Firebase)
/// Handles Google Sign-In authentication flow
/// 
/// This service works ALONGSIDE the existing SES-based OTP flow.
/// Both authentication methods can be used independently.
class GoogleSignInService {
  static GoogleSignIn? _googleSignIn;

  /// Initialize Google Sign-In
  /// Should be called after Firebase initialization
  /// 
  /// For web: The client ID is read from the meta tag in index.html:
  /// <meta name="google-signin-client_id" content="YOUR_CLIENT_ID">
  /// 
  /// Alternatively, you can pass the clientId parameter directly:
  /// GoogleSignIn(clientId: 'YOUR_CLIENT_ID.apps.googleusercontent.com')
  static void _ensureInitialized() {
    // Explicitly set clientId for web to ensure it works on all ports
    // This overrides the meta tag approach but ensures consistency
    _googleSignIn ??= GoogleSignIn(
      scopes: ['email', 'profile'],
      // Explicitly set client ID for web compatibility across all ports
      // Web Client ID from Firebase Console
      clientId: '785722200056-fovkr26n2b7p80mju8otg2gqcqn2v8d8.apps.googleusercontent.com',
    );
  }

  /// Sign in with Google
  /// Returns Firebase User and ID token for backend verification
  /// 
  /// Returns null if user cancels the sign-in process
  /// Throws exception if sign-in fails
  static Future<FirebaseAuthResult?> signInWithGoogle() async {
    if (!FirebaseService.isInitialized || FirebaseService.auth == null) {
      throw Exception('Firebase not initialized. Please ensure Firebase is configured.');
    }

    _ensureInitialized();

    try {
      // Trigger the Google Sign-In flow
      final GoogleSignInAccount? googleUser = await _googleSignIn!.signIn();

      // User cancelled the sign-in
      if (googleUser == null) {
        AppLogger.info('Google Sign-In was cancelled by user');
        return null;
      }

      AppLogger.info('Google Sign-In account selected: ${googleUser.email}');

      // Obtain the auth details from the request
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // Create a new credential for Firebase
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Sign in to Firebase with the Google credential
      final userCredential = await FirebaseService.auth!.signInWithCredential(credential);
      final idToken = await userCredential.user?.getIdToken();

      AppLogger.info('User signed in with Google: ${userCredential.user?.email}');

      return FirebaseAuthResult(
        user: userCredential.user,
        idToken: idToken,
        emailVerified: userCredential.user?.emailVerified ?? true, // Google accounts are pre-verified
      );
    } on FirebaseAuthException catch (e) {
      AppLogger.error('Firebase Auth error during Google Sign-In: ${e.code} - ${e.message}');
      throw _handleFirebaseAuthException(e);
    } catch (e) {
      AppLogger.error('Google Sign-In error: $e');
      
      // Handle specific Google Sign-In errors
      final errorMessage = e.toString().toLowerCase();
      
      if (errorMessage.contains('sign_in_canceled') || 
          errorMessage.contains('cancelled') ||
          errorMessage.contains('cancel')) {
        return null; // User cancelled - return null instead of throwing
      }
      
      if (errorMessage.contains('network')) {
        throw Exception('Network error during Google Sign-In. Please check your internet connection.');
      }
      
      throw Exception('Google Sign-In failed: ${e.toString()}');
    }
  }

  /// Sign out from Google Sign-In
  /// This signs out from both Google Sign-In and Firebase
  static Future<void> signOut() async {
    _ensureInitialized();
    
    try {
      // Sign out from Google
      if (_googleSignIn != null) {
        await _googleSignIn!.signOut();
        AppLogger.info('Signed out from Google Sign-In');
      }
      
      // Also sign out from Firebase
      await FirebaseService.signOut();
    } catch (e) {
      AppLogger.error('Error during Google Sign-In sign out: $e');
      // Continue even if sign out fails partially
    }
  }

  /// Get ID token for current user
  /// This is a convenience method that delegates to FirebaseService
  static Future<String?> getIdToken({bool forceRefresh = false}) async {
    return await FirebaseService.getIdToken(forceRefresh: forceRefresh);
  }

  /// Handle Firebase Auth exceptions during Google Sign-In
  static Exception _handleFirebaseAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'account-exists-with-different-credential':
        return Exception('An account already exists with the same email address but different sign-in credentials.');
      case 'invalid-credential':
        return Exception('The credential received is malformed or has expired.');
      case 'operation-not-allowed':
        return Exception('Google Sign-In is not enabled. Please contact support.');
      case 'user-disabled':
        return Exception('This user account has been disabled.');
      case 'user-not-found':
        return Exception('No user found with this credential.');
      case 'wrong-password':
        return Exception('Invalid credential provided.');
      case 'invalid-verification-code':
        return Exception('Invalid verification code.');
      case 'invalid-verification-id':
        return Exception('Invalid verification ID.');
      case 'network-request-failed':
        return Exception('Network error. Please check your internet connection.');
      default:
        AppLogger.error('Unhandled Firebase Auth error during Google Sign-In: ${e.code} - ${e.message}');
        return Exception('Google Sign-In failed: ${e.message ?? e.code}');
    }
  }
}

