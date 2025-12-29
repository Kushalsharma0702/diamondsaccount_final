// ignore_for_file: constant_identifier_names

class ApiEndpoints {
  // OpenAPI base
  static const String BASE_URL = 'https://7f456a2452e2.ngrok-free.app/api/v1';

  // Auth paths
  static const String REGISTER = '/auth/register';
  static const String LOGIN = '/auth/login';
  static const String REQUEST_OTP = '/auth/request-otp';
  static const String VERIFY_OTP = '/auth/verify-otp';
  static const String ME = '/auth/me';

  // Files paths
  static const String FILES_UPLOAD = '/files/upload';
}
