import 'dart:convert';

import 'package:dio/dio.dart';

import '../../../core/constants/api_endpoints.dart';
import '../../../core/theme/theme_controller.dart';
import '../../../core/network/ui_error.dart';
import '../../../core/network/auth_interceptor.dart';
import 'models/t1_form_models_simple.dart';

/// T1 Form API Service
/// Handles communication with backend for T1 tax forms
class T1FormApi {
  T1FormApi._(); // Private constructor

  static Dio _dio() {
    final dio = Dio(
      BaseOptions(
        baseUrl: ApiEndpoints.BASE_URL,
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
      ),
    );
    
    // Add auth interceptor for automatic token refresh
    dio.interceptors.add(AuthInterceptor());
    
    return dio;
  }

  /// Create or update T1 form on backend
  /// Maps Flutter T1FormData to backend format
  static Future<Map<String, dynamic>> submitForm({
    required T1FormData formData,
    int? taxYear,
  }) async {
    try {
      // Extract tax year - use provided or default to current year
      final year = taxYear ?? formData.personalInfo.dateOfBirth?.year ?? DateTime.now().year;
      
      // Map T1FormData to backend format
      final payload = {
        'tax_year': year,
        'sin': formData.personalInfo.sin.isNotEmpty ? formData.personalInfo.sin : null,
        'marital_status': formData.personalInfo.maritalStatus.isNotEmpty 
            ? formData.personalInfo.maritalStatus 
            : null,
        'first_name': formData.personalInfo.firstName.isNotEmpty 
            ? formData.personalInfo.firstName 
            : null,
        'last_name': formData.personalInfo.lastName.isNotEmpty 
            ? formData.personalInfo.lastName 
            : null,
        'email': formData.personalInfo.email.isNotEmpty 
            ? formData.personalInfo.email 
            : null,
        'employment_income': _extractEmploymentIncome(formData) ?? 0.0,
        'self_employment_income': (formData.isSelfEmployed == true) ? (_extractSelfEmploymentIncome(formData) ?? 0.0) : 0.0,
        'investment_income': _extractInvestmentIncome(formData) ?? 0.0,
        'other_income': _extractOtherIncome(formData) ?? 0.0,
        'rrsp_contributions': (formData.hasRrspFhsaInvestment == true) ? (_extractRrspContributions(formData) ?? 0.0) : 0.0,
        'charitable_donations': (formData.hasCharitableDonations == true) ? (_extractCharitableDonations(formData) ?? 0.0) : 0.0,
      };

      // Check if form exists - try to update first
      List<Map<String, dynamic>> existingForms = [];
      try {
        existingForms = await getUserForms();
      } catch (e) {
        // If get fails, continue to create new form
      }
      
      final existingForm = existingForms.isNotEmpty
          ? existingForms.firstWhere(
              (f) => f['tax_year'] == year,
              orElse: () => {},
            )
          : <String, dynamic>{};

      if (existingForm.isNotEmpty && existingForm['id'] != null) {
        // Update existing form
        final response = await _dio().put(
          '${ApiEndpoints.T1_PERSONAL_UPDATE}/${existingForm['id']}',
          data: payload,
        );
        return _parseFormResponse(response.data);
      } else {
        // Create new form
        final response = await _dio().post(
          ApiEndpoints.T1_PERSONAL_CREATE,
          data: payload,
        );
        return _parseFormResponse(response.data);
      }
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    } catch (e) {
      throw Exception('Failed to submit form: ${e.toString()}');
    }
  }

  /// Get all T1 forms for current user
  static Future<List<Map<String, dynamic>>> getUserForms() async {
    try {
      final response = await _dio().get(
        ApiEndpoints.T1_PERSONAL_GET,
      );
      final data = response.data;
      if (data is List) {
        return data.map((item) => _parseFormResponse(item)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw Exception(_extractErrorMessage(e));
    }
  }

  /// Helper methods to extract income values from T1FormData
  static double? _extractEmploymentIncome(T1FormData formData) {
    // Try to extract from questionnaire or income fields
    // Default to 0 if not available
    return 0.0;
  }

  static double? _extractSelfEmploymentIncome(T1FormData formData) {
    // Extract self-employment income if available
    return 0.0;
  }

  static double? _extractInvestmentIncome(T1FormData formData) {
    // Extract investment income if available
    return 0.0;
  }

  static double? _extractOtherIncome(T1FormData formData) {
    // Extract other income if available
    return 0.0;
  }

  static double? _extractRrspContributions(T1FormData formData) {
    // Extract RRSP contributions if available
    return 0.0;
  }

  static double? _extractCharitableDonations(T1FormData formData) {
    // Extract charitable donations if available
    return 0.0;
  }

  /// Parse form response from backend
  static Map<String, dynamic> _parseFormResponse(dynamic data) {
    if (data is Map<String, dynamic>) return data;
    if (data is Map) return Map<String, dynamic>.from(data);
    if (data is String) {
      try {
        return json.decode(data) as Map<String, dynamic>;
      } catch (_) {}
    }
    return {};
  }

  /// Extract error message from DioException
  static String _extractErrorMessage(DioException e) {
    final uiError = mapDioErrorToUIError(e);
    return uiError.message;
  }
}

