import 'package:firebase_auth/firebase_auth.dart';
import '../logger/app_logger.dart';

/// Firebase Core Service
/// Handles Firebase initialization and provides access to Firebase Auth instance
/// 
/// This service works ALONGSIDE the existing SES-based OTP flow.
/// Both authentication methods can be used independently.
class FirebaseService {
  static FirebaseAuth? _auth;
  static bool _initialized = false;

  /// Initialize Firebase service
  /// Note: Firebase.initializeApp() must be called in main.dart first
  /// This method sets up service instances and should be called after Firebase.initializeApp()
  static Future<void> initialize() async {
    if (_initialized) {
      AppLogger.info('Firebase service already initialized');
      return;
    }

    try {
      // Firebase.initializeApp() should already be called in main.dart
      // This just sets up our service instances
      _auth = FirebaseAuth.instance;

      _initialized = true;
      AppLogger.info('Firebase service initialized successfully');
    } catch (e) {
      AppLogger.error('Failed to initialize Firebase service: $e');
      // Don't throw - allow app to continue without Firebase
      // This ensures existing Cognito/SES flow still works
    }
  }

  /// Get Firebase Auth instance
  static FirebaseAuth? get auth => _auth;

  /// Check if Firebase is initialized
  static bool get isInitialized => _initialized;

  /// Check if user is currently logged in
  static bool get isLoggedIn => _auth?.currentUser != null;

  /// Get current Firebase user
  static User? getCurrentUser() {
    return _auth?.currentUser;
  }

  /// Get current user's ID token
  /// Refreshes token if needed
  static Future<String?> getIdToken({bool forceRefresh = false}) async {
    if (_auth?.currentUser == null) return null;
    try {
      return await _auth!.currentUser?.getIdToken(forceRefresh);
    } catch (e) {
      AppLogger.error('Failed to get ID token: $e');
      return null;
    }
  }

  /// Sign out from Firebase
  /// Note: This only signs out from Firebase, not from Google Sign-In
  /// Use GoogleSignInService.signOut() for Google Sign-In logout
  static Future<void> signOut() async {
    if (_auth != null) {
      await _auth!.signOut();
      AppLogger.info('Signed out from Firebase');
    }
  }
}
