// ignore_for_file: constant_identifier_names

class ApiEndpoints {
  // OpenAPI base
  // Use localhost for client backend (port 8001)
  // For production, update this to your production API URL
  static const String BASE_URL = 'http://localhost:8001/api/v1';

          // Auth paths
          static const String REGISTER = '/auth/register';
          static const String LOGIN = '/auth/login';
          static const String REQUEST_OTP = '/auth/request-otp';
          static const String VERIFY_OTP = '/auth/verify-otp';
          static const String REFRESH_TOKEN = '/auth/refresh';
          static const String ME = '/auth/me';
  
  // Firebase Authentication paths (work alongside existing Cognito/SES flow)
  static const String FIREBASE_REGISTER = '/auth/firebase-register';
  static const String FIREBASE_LOGIN = '/auth/firebase-login';
  static const String GOOGLE_LOGIN = '/auth/google-login';

  // Files paths
  static const String FILES_UPLOAD = '/files/upload';
  
  // Tax Forms paths
  static const String T1_PERSONAL_CREATE = '/tax/t1-personal';
  static const String T1_PERSONAL_GET = '/tax/t1-personal';
  static const String T1_PERSONAL_GET_BY_ID = '/tax/t1-personal'; // Use with /{id}
  static const String T1_PERSONAL_UPDATE = '/tax/t1-personal'; // Use with /{id}
}
