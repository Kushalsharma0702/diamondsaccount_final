import 'package:dio/dio.dart';
import '../theme/theme_controller.dart';
import '../constants/api_endpoints.dart';

/// Dio interceptor for automatic token refresh
/// Handles 401 errors by refreshing the access token and retrying the request
class AuthInterceptor extends Interceptor {
  static bool _isRefreshing = false;
  static final List<_PendingRequest> _pendingRequests = [];

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add auth token to request if available
    if (ThemeController.authToken != null && ThemeController.authToken!.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer ${ThemeController.authToken}';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Only handle 401 errors (unauthorized)
    if (err.response?.statusCode == 401) {
      final requestOptions = err.requestOptions;

      // If we're already refreshing, queue this request
      if (_isRefreshing) {
        return _queueRequest(requestOptions, handler);
      }

      // Check if we have a refresh token
      final refreshToken = ThemeController.refreshToken;
      if (refreshToken == null || refreshToken.isEmpty) {
        // No refresh token - user needs to log in again
        await _handleTokenExpired(handler, err);
        return;
      }

      // Attempt to refresh the token
      _isRefreshing = true;
      try {
        final newToken = await _refreshAccessToken(refreshToken);
        
        if (newToken != null) {
          // Update stored token
          await ThemeController.setAuthToken(newToken);
          
          // Retry the original request with new token
          final opts = Options(
            method: requestOptions.method,
            headers: requestOptions.headers,
          );
          opts.headers!['Authorization'] = 'Bearer $newToken';
          
          final response = await Dio().fetch(requestOptions..headers = opts.headers);
          
          // Process all pending requests
          _processPendingRequests(newToken);
          
          handler.resolve(response);
        } else {
          // Refresh failed - user needs to log in again
          await _handleTokenExpired(handler, err);
        }
      } catch (e) {
        // Refresh failed - user needs to log in again
        await _handleTokenExpired(handler, err);
      } finally {
        _isRefreshing = false;
      }
    } else {
      // Not a 401 error - pass through
      handler.next(err);
    }
  }

  /// Queue a request to be retried after token refresh
  void _queueRequest(RequestOptions options, ErrorInterceptorHandler handler) {
    _pendingRequests.add(_PendingRequest(options, handler));
  }

  /// Process all pending requests with new token
  Future<void> _processPendingRequests(String newToken) async {
    final requests = List<_PendingRequest>.from(_pendingRequests);
    _pendingRequests.clear();

    for (final pending in requests) {
      try {
        final opts = Options(
          method: pending.options.method,
          headers: pending.options.headers,
        );
        opts.headers!['Authorization'] = 'Bearer $newToken';
        
        final response = await Dio().fetch(pending.options..headers = opts.headers);
        pending.handler.resolve(response);
      } catch (e) {
        pending.handler.reject(DioException(
          requestOptions: pending.options,
          error: e,
        ));
      }
    }
  }

  /// Refresh the access token using refresh token
  Future<String?> _refreshAccessToken(String refreshToken) async {
    try {
      final dio = Dio(BaseOptions(
        baseUrl: ApiEndpoints.BASE_URL,
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
      ));

      final response = await dio.post(
        ApiEndpoints.REFRESH_TOKEN,
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final newAccessToken = data['access_token']?.toString() ?? 
                              data['token']?.toString();
        final newRefreshToken = data['refresh_token']?.toString();
        
        // Update refresh token if provided
        if (newRefreshToken != null) {
          await ThemeController.setRefreshToken(newRefreshToken);
        }
        
        return newAccessToken;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Handle token expiration - clear auth and throw error
  Future<void> _handleTokenExpired(ErrorInterceptorHandler handler, DioException originalError) async {
    await ThemeController.clearAuth();
    
    // Create a more user-friendly error
    final error = DioException(
      requestOptions: originalError.requestOptions,
      response: originalError.response,
      type: DioExceptionType.badResponse,
      error: 'Your session has expired. Please log in again.',
    );
    
    handler.reject(error);
  }
}

/// Helper class to store pending requests
class _PendingRequest {
  final RequestOptions options;
  final ErrorInterceptorHandler handler;

  _PendingRequest(this.options, this.handler);
}

