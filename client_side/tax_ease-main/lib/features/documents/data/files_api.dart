import 'dart:io';

import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../../core/network/ui_error.dart';

class FilesApi {
  FilesApi._();

  static Dio _dio() => Dio(
        BaseOptions(
          baseUrl: ApiEndpoints.BASE_URL,
          connectTimeout: const Duration(seconds: 20),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            // Required for ngrok tunnels
            'ngrok-skip-browser-warning': 'true',
            if (ThemeController.authToken != null)
              'Authorization': 'Bearer ${ThemeController.authToken}',
          },
        ),
      );

  /// Upload a file using multipart/form-data to POST /files/upload
  /// Returns the decoded response map on success (201)
  static Future<Map<String, dynamic>> uploadFile({
    required String filePath,
    String fieldName = 'file',
  }) async {
    final file = File(filePath);
    if (!await file.exists()) {
      throw Exception('File does not exist at path: $filePath');
    }

    final fileName = file.uri.pathSegments.isNotEmpty
        ? file.uri.pathSegments.last
        : 'upload.bin';

    final formData = FormData.fromMap({
      fieldName: await MultipartFile.fromFile(
        file.path,
        filename: fileName,
      ),
    });

    try {
      final res = await _dio().post(
        ApiEndpoints.FILES_UPLOAD,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );

      final data = res.data;
      if (data is Map<String, dynamic>) return data;
      if (data is Map) return Map<String, dynamic>.from(data);
      return {'raw': data};
    } on DioException catch (e) {
      final msg = _extractErrorMessage(e);
      throw Exception(msg);
    }
  }

  /// Centralised mapping from DioException to a user-friendly upload error message.
  static String _extractErrorMessage(DioException e) {
    final uiError = mapDioErrorToUIError(e);
    // Customise the default message slightly for the upload context.
    if (uiError.type == UIErrorType.network || uiError.type == UIErrorType.timeout) {
      return 'Upload failed. ${uiError.message}';
    }
    return uiError.message.isNotEmpty ? uiError.message : 'Upload failed. Please try again.';
  }
}
