import 'package:dio/dio.dart';

/// High-level categories for errors that the UI can understand.
enum UIErrorType {
  network,
  timeout,
  server,
  client,
  parsing,
  cancel,
  unknown,
}

/// Normalised error object that can be shown in the UI.
class UIError {
  final UIErrorType type;
  final String message;
  final int? statusCode;

  const UIError({
    required this.type,
    required this.message,
    this.statusCode,
  });
}

/// Helper that maps DioException instances into a UIError.
UIError mapDioErrorToUIError(DioException e) {
  // Try to read a backend message if available.
  String? backendMessage;
  int? statusCode = e.response?.statusCode;

  final data = e.response?.data;
  if (data is Map) {
    // FastAPI returns errors in 'detail' field
    if (data['detail'] != null) {
      backendMessage = data['detail'].toString();
    } 
    // Some APIs may use 'message' field
    else if (data['message'] != null) {
      backendMessage = data['message'].toString();
    }
    // Handle nested error objects
    else if (data['error'] is Map && data['error']['detail'] != null) {
      backendMessage = data['error']['detail'].toString();
    }
  }

  // Timeouts and connection-level problems.
  if (e.type == DioExceptionType.connectionTimeout ||
      e.type == DioExceptionType.sendTimeout ||
      e.type == DioExceptionType.receiveTimeout) {
    return UIError(
      type: UIErrorType.timeout,
      message: backendMessage ??
          'The request timed out. Please check your internet connection and try again.',
      statusCode: statusCode,
    );
  }

  // No response from server at all (offline / DNS / SSL, etc.).
  if (e.type == DioExceptionType.connectionError && e.response == null) {
    return UIError(
      type: UIErrorType.network,
      message: backendMessage ??
          'Unable to connect to the server. Please check your internet connection.',
      statusCode: statusCode,
    );
  }

  // Server responded with a non-2xx status.
  if (e.type == DioExceptionType.badResponse && e.response != null) {
    final sc = statusCode;

    if (sc != null) {
      if (sc >= 500) {
        return UIError(
          type: UIErrorType.server,
          message: backendMessage ??
              'We\'re having trouble on our side (error $sc). Please try again later.',
          statusCode: sc,
        );
      }
      if (sc >= 400 && sc < 500) {
        // Client-side / validation errors.
        String message;
        if (backendMessage != null && backendMessage.isNotEmpty) {
          message = backendMessage;
        } else if (sc == 400) {
          message = 'Invalid request. Please check your input and try again.';
        } else if (sc == 401) {
          message = 'You\'re not authorized. Please sign in again.';
        } else if (sc == 403) {
          message = 'You don\'t have permission to perform this action.';
        } else if (sc == 404) {
          message = 'Requested resource was not found. Please try again.';
        } else if (sc == 422) {
          message = 'Some of the information you entered is not valid. Please review and try again.';
        } else {
          message = 'Request failed (error $sc). Please try again.';
        }

        return UIError(
          type: UIErrorType.client,
          message: message,
          statusCode: sc,
        );
      }
    }

    // Fallback when we have a response but no clear status mapping.
    return UIError(
      type: UIErrorType.unknown,
      message: backendMessage ?? 'Something went wrong while talking to the server. Please try again.',
      statusCode: sc,
    );
  }

  // Request was explicitly cancelled.
  if (e.type == DioExceptionType.cancel) {
    return UIError(
      type: UIErrorType.cancel,
      message: 'Request was cancelled. Please try again.',
      statusCode: statusCode,
    );
  }

  // Other unclassified errors (parsing, unknown, etc.).
  if (e.type == DioExceptionType.unknown) {
    // Some unknown errors are still network-related (e.g. SocketException).
    final msg = e.message ?? '';
    if (msg.contains('SocketException') || msg.contains('Network is unreachable')) {
      return UIError(
        type: UIErrorType.network,
        message: 'No internet connection. Please check your network and try again.',
        statusCode: statusCode,
      );
    }

    return UIError(
      type: UIErrorType.unknown,
      message: backendMessage ?? 'Unexpected error occurred. Please try again.',
      statusCode: statusCode,
    );
  }

  // Final catch-all.
  return UIError(
    type: UIErrorType.unknown,
    message: backendMessage ?? 'Unexpected error occurred. Please try again.',
    statusCode: statusCode,
  );
}
