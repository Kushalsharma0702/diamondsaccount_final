import 'services/t1_form_storage_service.dart';
import 't1_form_api.dart';
import 'models/t1_form_models_simple.dart';
import '../../../core/logger/app_logger.dart';

/// T1 Form Sync Service
/// Syncs locally saved forms to backend database
class T1FormSyncService {
  T1FormSyncService._(); // Private constructor

  /// Sync all locally saved forms to backend
  /// This ensures forms saved locally are submitted to the database
  static Future<SyncResult> syncAllFormsToBackend() async {
    try {
      AppLogger.info('🔄 Starting sync of locally saved forms to backend...');

      // Load all forms from local storage
      final storageService = T1FormStorageService.instance;
      final localForms = await storageService.loadAllForms();
      
      if (localForms.isEmpty) {
        AppLogger.info('📭 No local forms to sync');
        return SyncResult(
          success: true,
          totalForms: 0,
          syncedForms: 0,
          failedForms: 0,
          errors: [],
        );
      }

      AppLogger.info('📋 Found ${localForms.length} form(s) in local storage');

      int syncedCount = 0;
      int failedCount = 0;
      final List<String> errors = [];

      // Sync each form
      for (final form in localForms) {
        try {
          // Only sync forms that are marked as submitted or have data
          if (form.status == 'submitted' || _hasFormData(form)) {
            AppLogger.info('📤 Syncing form: ${form.id} (Status: ${form.status})');

            // Submit form to backend
            final response = await T1FormApi.submitForm(
              formData: form,
              taxYear: DateTime.now().year,
            );

            if (response['id'] != null) {
              AppLogger.info('✅ Form synced successfully: ${response['id']}');
              
              // Update local form with backend ID if different
              if (response['id'] != form.id) {
                final updatedForm = form.copyWith(id: response['id'].toString());
                await storageService.saveForm(updatedForm);
                AppLogger.info('🔄 Updated local form ID to: ${response['id']}');
              }
              
              syncedCount++;
            } else {
              throw Exception('Backend did not return form ID');
            }
          } else {
            AppLogger.info('⏭️  Skipping form ${form.id} (draft status with no data)');
          }
        } catch (e) {
          AppLogger.error('❌ Failed to sync form ${form.id}: $e');
          failedCount++;
          errors.add('Form ${form.id}: ${e.toString()}');
        }
      }

      AppLogger.info('✅ Sync complete: $syncedCount synced, $failedCount failed');

      return SyncResult(
        success: failedCount == 0,
        totalForms: localForms.length,
        syncedForms: syncedCount,
        failedForms: failedCount,
        errors: errors,
      );
    } catch (e) {
      AppLogger.error('❌ Sync failed: $e');
      return SyncResult(
        success: false,
        totalForms: 0,
        syncedForms: 0,
        failedForms: 0,
        errors: [e.toString()],
      );
    }
  }

  /// Check if form has actual data (not just an empty draft)
  static bool _hasFormData(T1FormData form) {
    // Check if personal info has any data
    final hasPersonalInfo = form.personalInfo.firstName.isNotEmpty ||
        form.personalInfo.lastName.isNotEmpty ||
        form.personalInfo.email.isNotEmpty;

    // Check if any questionnaire fields are answered
    final hasQuestionnaireData = form.hasForeignProperty != null ||
        form.hasMedicalExpenses != null ||
        form.hasCharitableDonations != null ||
        form.isSelfEmployed != null ||
        form.isFirstTimeFiler != null;

    return hasPersonalInfo || hasQuestionnaireData;
  }

  /// Sync a specific form by ID
  static Future<bool> syncFormById(String formId) async {
    try {
      final storageService = T1FormStorageService.instance;
      final form = await storageService.getFormById(formId);
      if (form == null) {
        AppLogger.error('❌ Form not found in local storage: $formId');
        return false;
      }

      AppLogger.info('📤 Syncing form: $formId');
      final response = await T1FormApi.submitForm(
        formData: form,
        taxYear: DateTime.now().year,
      );

      if (response['id'] != null) {
        // Update local form with backend ID if different
        if (response['id'] != form.id) {
          final updatedForm = form.copyWith(id: response['id'].toString());
          await storageService.saveForm(updatedForm);
        }
        AppLogger.info('✅ Form synced successfully: ${response['id']}');
        return true;
      }
      return false;
    } catch (e) {
      AppLogger.error('❌ Failed to sync form $formId: $e');
      return false;
    }
  }
}

/// Result of sync operation
class SyncResult {
  final bool success;
  final int totalForms;
  final int syncedForms;
  final int failedForms;
  final List<String> errors;

  SyncResult({
    required this.success,
    required this.totalForms,
    required this.syncedForms,
    required this.failedForms,
    required this.errors,
  });

  @override
  String toString() {
    return 'SyncResult(success: $success, total: $totalForms, synced: $syncedForms, failed: $failedForms)';
  }
}

