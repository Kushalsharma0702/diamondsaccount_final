import 'dart:convert';

import 'package:dio/dio.dart';

import '../../../core/constants/api_endpoints.dart';
import '../../../core/theme/theme_controller.dart';
import '../../../core/network/ui_error.dart';

class AuthResult {
  final String? token; // access_token
  final String? refreshToken;
  final String? displayName;
  final String? filingType; // e.g., T1/T2 if provided by backend

  AuthResult({this.token, this.refreshToken, this.displayName, this.filingType});
}

class UserProfile {
  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final String? phone;
  final bool emailVerified;
  final bool isActive;
  final String? createdAt;
  final String? updatedAt;

  UserProfile({
    required this.id,
    required this.email,
    this.firstName,
    this.lastName,
    this.phone,
    required this.emailVerified,
    required this.isActive,
    this.createdAt,
    this.updatedAt,
  });

  String get fullName {
    final f = (firstName ?? '').trim();
    final l = (lastName ?? '').trim();
    final combined = ('$f $l').trim();
    if (combined.isEmpty) return email.split('@').first;
    return combined;
  }

  String get initials {
    final f = (firstName ?? '').trim();
    final l = (lastName ?? '').trim();
    if (f.isEmpty && l.isEmpty) return email.isNotEmpty ? email[0].toUpperCase() : 'U';
    if (l.isEmpty) return f.substring(0, 1).toUpperCase();
    return (f.substring(0, 1) + l.substring(0, 1)).toUpperCase();
  }

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: (json['id'] ?? '').toString(),
      email: (json['email'] ?? '').toString(),
      firstName: json['first_name']?.toString(),
      lastName: json['last_name']?.toString(),
      phone: json['phone']?.toString(),
      emailVerified: (json['email_verified'] == true),
      isActive: (json['is_active'] == true),
      createdAt: json['created_at']?.toString(),
      updatedAt: json['updated_at']?.toString(),
    );
  }
}

class AuthApi {
  AuthApi._();

  static Dio _dio() => Dio(
        BaseOptions(
          baseUrl: ApiEndpoints.BASE_URL,
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 20),
          headers: {
            'Content-Type': 'application/json',
            // Bypass ngrok browser interstitial for API calls
            'ngrok-skip-browser-warning': 'true',
            if (ThemeController.authToken != null)
              'Authorization': 'Bearer ${ThemeController.authToken}',
          },
        ),
      );

  /// Register user (email verification via OTP follows).
  static Future<void> register({
    required String email,
    required String firstName,
    required String lastName,
    required String password,
    String? phone,
    required bool acceptTerms,
  }) async {
    try {
      await _dio().post(
        ApiEndpoints.REGISTER,
        data: {
          'email': email,
          'first_name': firstName,
          'last_name': lastName,
          'phone': phone,
          'password': password,
          'accept_terms': acceptTerms,
        },
      );
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Attempt login; returns tokens according to docs.
  static Future<AuthResult> login({required String email, required String password}) async {
    try {
      final res = await _dio().post(
        ApiEndpoints.LOGIN,
        data: {
          'email': email,
          'password': password,
        },
      );
      final data = res.data;
      return _parseAuthResult(data);
    } on DioException catch (e) {
      final message = _extractErrorMessage(e);
      throw Exception(message);
    }
  }

  /// Request an OTP for email verification or password reset
  static Future<void> requestOtp({
    required String email,
    required String purpose, // 'email_verification' | 'password_reset'
  }) async {
    try {
      await _dio().post(
        ApiEndpoints.REQUEST_OTP,
        data: {
          'email': email,
          'purpose': purpose,
        },
      );
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Verify an OTP code
  static Future<void> verifyOtp({
    required String email,
    required String code,
    required String purpose,
  }) async {
    try {
      await _dio().post(
        ApiEndpoints.VERIFY_OTP,
        data: {
          'email': email,
          'code': code,
          'purpose': purpose,
        },
      );
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// GET /auth/me - fetch current user's profile.
  static Future<UserProfile> getCurrentUser() async {
    try {
      final res = await _dio().get(ApiEndpoints.ME);
      final data = res.data;
      if (data is Map<String, dynamic>) return UserProfile.fromJson(data);
      if (data is Map) return UserProfile.fromJson(Map<String, dynamic>.from(data));
      if (data is String) {
        try {
          final parsed = json.decode(data) as Map<String, dynamic>;
          return UserProfile.fromJson(parsed);
        } catch (_) {}
      }
      throw Exception('Unexpected response format');
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  // ========================================
  // FIREBASE AUTHENTICATION METHODS
  // These work alongside existing Cognito/SES OTP flow
  // ========================================

  /// Register user with Firebase Email/Password
  /// Then exchange Firebase ID token for backend JWT
  /// 
  /// IMPORTANT: Call FirebaseService.createUserWithEmailAndPassword() first
  /// to get the Firebase ID token, then pass it here.
  static Future<AuthResult> registerWithFirebase({
    required String email,
    required String firstName,
    required String lastName,
    required String firebaseIdToken,
    String? phone,
    required bool acceptTerms,
  }) async {
    try {
      final res = await _dio().post(
        ApiEndpoints.FIREBASE_REGISTER,
        data: {
          'email': email,
          'first_name': firstName,
          'last_name': lastName,
          'phone': phone,
          'accept_terms': acceptTerms,
          'firebase_id_token': firebaseIdToken,
        },
      );
      return _parseAuthResult(res.data);
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Login with Firebase ID token
  /// Exchanges Firebase ID token for backend JWT tokens
  static Future<AuthResult> loginWithFirebase({
    required String firebaseIdToken,
  }) async {
    try {
      final res = await _dio().post(
        ApiEndpoints.FIREBASE_LOGIN,
        data: {
          'firebase_id_token': firebaseIdToken,
        },
      );
      return _parseAuthResult(res.data);
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Login with Google Sign-In (Firebase)
  /// Exchanges Firebase ID token for backend JWT tokens
  static Future<AuthResult> loginWithGoogle({
    required String firebaseIdToken,
  }) async {
    try {
      final res = await _dio().post(
        ApiEndpoints.GOOGLE_LOGIN,
        data: {
          'firebase_id_token': firebaseIdToken,
        },
      );
      return _parseAuthResult(res.data);
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  static AuthResult _parseAuthResult(dynamic data) {
    // Docs:
    // { "access_token": "...", "refresh_token": "...", "token_type": "Bearer", "expires_in": 0 }
    dynamic root = data;
    if (data is String) {
      try { root = json.decode(data); } catch (_) {}
    }

    String? token;
    String? refreshToken;
    String? name;
    String? filingType;

    if (root is Map) {
      token = (root['access_token'] ?? root['token'])?.toString();
      refreshToken = (root['refresh_token'])?.toString();

      final user = (root['user'] ?? root['data']?['user']) as Map?;
      name = (user?['name'] ?? user?['fullName'] ?? user?['first_name'] ?? user?['firstName'])?.toString();
      filingType = (user?['filingType'] ?? user?['filing_type'])?.toString();
    }

    return AuthResult(
      token: token,
      refreshToken: refreshToken,
      displayName: name,
      filingType: filingType,
    );
  }

  /// Centralised mapping from DioException to a user-friendly error message.
  ///
  /// This uses [UIError] so the UI can distinguish between network/server/client issues
  /// if needed, while still returning a simple message for existing callers.
  static String _extractErrorMessage(DioException e) {
    final uiError = mapDioErrorToUIError(e);
    return uiError.message;
  }
}
