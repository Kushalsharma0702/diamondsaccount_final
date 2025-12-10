import 'dart:convert';
import 'package:dio/dio.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/ui_error.dart';
import 'auth_api.dart'; // For AuthResult

/// OTP API Service for Firebase-based Authentication Flow
/// 
/// This service handles the OTP flow that works AFTER Firebase authentication:
/// 1. User authenticates with Firebase → Gets Firebase ID token
/// 2. Send Firebase ID token to backend → Backend verifies token → Generates OTP → Sends via SES
/// 3. User enters OTP → Backend verifies OTP → Returns backend JWT
/// 
/// This works ALONGSIDE existing Cognito/SES OTP flow - both can coexist
class OtpApiService {
  OtpApiService._();

  static Dio _dio() => Dio(
        BaseOptions(
          baseUrl: ApiEndpoints.BASE_URL,
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 20),
          headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true',
          },
        ),
      );

  /// Request OTP after Firebase authentication
  /// Sends Firebase ID token to backend, backend verifies it and sends OTP via AWS SES
  /// 
  /// [firebaseIdToken] - Firebase ID token from Firebase authentication
  /// [email] - User's email (can be extracted from Firebase token, but sent for convenience)
  /// 
  /// Returns success message if OTP was sent
  static Future<void> requestOtpWithFirebase({
    required String firebaseIdToken,
    required String email,
  }) async {
    try {
      await _dio().post(
        ApiEndpoints.REQUEST_OTP,
        data: {
          'firebase_id_token': firebaseIdToken,
          'email': email,
          'purpose': 'email_verification',
        },
      );
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Verify OTP and get backend JWT token
  /// Verifies the OTP code and returns backend JWT token for session management
  /// 
  /// [firebaseIdToken] - Firebase ID token (for additional verification)
  /// [email] - User's email
  /// [otpCode] - 6-digit OTP code entered by user
  /// 
  /// Returns backend JWT token string
  static Future<String> verifyOtpAndGetToken({
    required String firebaseIdToken,
    required String email,
    required String otpCode,
  }) async {
    try {
      final response = await _dio().post(
        ApiEndpoints.VERIFY_OTP,
        data: {
          'firebase_id_token': firebaseIdToken,
          'email': email,
          'code': otpCode,
          'purpose': 'email_verification',
        },
      );

      final data = response.data;
      
      // Backend should return: { "success": true, "token": "<jwt>", "refresh_token": "<jwt>" }
      if (data is Map) {
        final token = data['token']?.toString();
        if (token != null && token.isNotEmpty) {
          return token;
        }
      }
      
      throw Exception('No token received from server');
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Verify OTP and get full auth result (including refresh token)
  static Future<AuthResult> verifyOtpWithFirebase({
    required String email,
    required String otpCode,
    required String purpose,
    required String firebaseIdToken,
  }) async {
    try {
      final res = await _dio().post(
        ApiEndpoints.VERIFY_OTP,
        data: {
          'email': email,
          'code': otpCode,
          'purpose': purpose,
          'firebase_id_token': firebaseIdToken,
        },
      );
      // Backend returns: { "success": true, "token": "...", "refresh_token": "..." }
      final data = res.data;
      if (data is Map) {
        return AuthResult(
          token: data['token']?.toString(),
          refreshToken: data['refresh_token']?.toString(),
          displayName: null,
          filingType: null,
        );
      }
      throw Exception('Unexpected response format');
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Extract error message from DioException
  static String _extractErrorMessage(DioException e) {
    final uiError = mapDioErrorToUIError(e);
    return uiError.message;
  }

  /// Extract error message from DioException
  static String _extractErrorMessage(DioException e) {
    final uiError = mapDioErrorToUIError(e);
    return uiError.message;
  }
}

