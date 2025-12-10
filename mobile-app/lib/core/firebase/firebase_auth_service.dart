import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_service.dart';
import '../logger/app_logger.dart';

/// Firebase Email/Password Authentication Service
/// Handles email/password registration and login
/// 
/// This service works ALONGSIDE the existing SES-based OTP flow.
/// Both authentication methods can be used independently.
class FirebaseAuthService {
  /// Register user with email and password
  /// Creates user in Firebase and automatically sends verification email
  /// Returns Firebase User and ID token for backend verification
  static Future<FirebaseAuthResult> registerWithEmail({
    required String email,
    required String password,
  }) async {
    if (!FirebaseService.isInitialized || FirebaseService.auth == null) {
      throw Exception('Firebase not initialized');
    }

    try {
      final userCredential = await FirebaseService.auth!.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      // Send email verification automatically
      await userCredential.user?.sendEmailVerification();
      AppLogger.info('Email verification sent to: $email');

      // Get ID token for backend verification
      final idToken = await userCredential.user?.getIdToken();

      return FirebaseAuthResult(
        user: userCredential.user,
        idToken: idToken,
        emailVerified: userCredential.user?.emailVerified ?? false,
      );
    } on FirebaseAuthException catch (e) {
      throw _handleFirebaseAuthException(e);
    }
  }

  /// Login with email and password
  /// Returns Firebase User and ID token for backend verification
  static Future<FirebaseAuthResult> loginWithEmail({
    required String email,
    required String password,
  }) async {
    if (!FirebaseService.isInitialized || FirebaseService.auth == null) {
      throw Exception('Firebase not initialized');
    }

    try {
      final userCredential = await FirebaseService.auth!.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      final idToken = await userCredential.user?.getIdToken();

      AppLogger.info('User logged in via Firebase: $email');
      return FirebaseAuthResult(
        user: userCredential.user,
        idToken: idToken,
        emailVerified: userCredential.user?.emailVerified ?? false,
      );
    } on FirebaseAuthException catch (e) {
      throw _handleFirebaseAuthException(e);
    }
  }

  /// Send email verification to current user
  /// Throws exception if no user is signed in
  static Future<void> sendEmailVerification() async {
    final user = FirebaseService.getCurrentUser();
    if (user == null) {
      throw Exception('No user signed in. Please log in first.');
    }

    try {
      await user.sendEmailVerification();
      AppLogger.info('Email verification sent to: ${user.email}');
    } on FirebaseAuthException catch (e) {
      throw _handleFirebaseAuthException(e);
    }
  }

  /// Resend email verification
  /// Same as sendEmailVerification() but with a clearer method name
  static Future<void> resendVerification() async {
    await sendEmailVerification();
  }

  /// Get ID token for current user
  /// This is a convenience method that delegates to FirebaseService
  static Future<String?> getIdToken({bool forceRefresh = false}) async {
    return await FirebaseService.getIdToken(forceRefresh: forceRefresh);
  }

  /// Handle Firebase Auth exceptions and convert to user-friendly messages
  static Exception _handleFirebaseAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'weak-password':
        return Exception('The password provided is too weak. Please use a stronger password.');
      case 'email-already-in-use':
        return Exception('An account already exists with that email address.');
      case 'invalid-email':
        return Exception('The email address is invalid. Please check and try again.');
      case 'user-disabled':
        return Exception('This user account has been disabled. Please contact support.');
      case 'user-not-found':
        return Exception('No user found with this email address.');
      case 'wrong-password':
        return Exception('Incorrect password. Please try again.');
      case 'requires-recent-login':
        return Exception('Please log out and log back in to perform this action.');
      case 'operation-not-allowed':
        return Exception('This operation is not allowed. Please contact support.');
      case 'too-many-requests':
        return Exception('Too many requests. Please try again later.');
      case 'network-request-failed':
        return Exception('Network error. Please check your internet connection.');
      default:
        AppLogger.error('Unhandled Firebase Auth error: ${e.code} - ${e.message}');
        return Exception('Authentication failed: ${e.message ?? e.code}');
    }
  }
}

/// Result of Firebase authentication operations
class FirebaseAuthResult {
  final User? user;
  final String? idToken;
  final bool emailVerified;

  FirebaseAuthResult({
    required this.user,
    required this.idToken,
    required this.emailVerified,
  });

  String? get email => user?.email;
  String? get uid => user?.uid;
  String? get displayName => user?.displayName;
  String? get photoUrl => user?.photoURL;
}

