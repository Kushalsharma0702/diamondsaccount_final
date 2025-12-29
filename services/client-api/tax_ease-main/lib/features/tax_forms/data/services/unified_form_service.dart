import '../models/t1_form_models_simple.dart';
import '../models/t2_form_models.dart';
import 't1_form_storage_service.dart';
import 't2_form_storage_service.dart';

/// Combined form data for unified progress tracking
class CombinedFormProgress {
  final String formId;
  final String formType; // 'T1' or 'T2'
  final String status;
  final DateTime? updatedAt;
  final double progress;
  final T1FormData? t1Form;
final T2OnboardingData? t2Form;

  CombinedFormProgress({
    required this.formId,
    required this.formType,
    required this.status,
    this.updatedAt,
    required this.progress,
    this.t1Form,
    this.t2Form,
  });
}

/// Unified service to handle both T1 and T2 forms for dashboard progress tracking
class UnifiedFormService {
  static UnifiedFormService? _instance;
  static UnifiedFormService get instance {
    _instance ??= UnifiedFormService._();
    return _instance!;
  }

  UnifiedFormService._();

  /// Get unified progress status for dashboard
  Future<Map<String, dynamic>> getUnifiedProgressStatus() async {
    try {
      // Load both T1 and T2 forms
      final t1Forms = await T1FormStorageService.instance.loadAllForms();
      final t2Forms = await T2FormStorageService.instance.loadAllForms();

      // Convert to combined format
      final List<CombinedFormProgress> allForms = [];
      
      // Add T1 forms
      for (final form in t1Forms) {
        allForms.add(CombinedFormProgress(
          formId: form.id,
          formType: 'T1',
          status: form.status,
          updatedAt: form.updatedAt,
          progress: T1FormStorageService.instance.calculateFormProgress(form),
          t1Form: form,
        ));
      }
      
      // Add T2 forms
      for (final form in t2Forms) {
        allForms.add(CombinedFormProgress(
          formId: form.id,
          formType: 'T2',
          status: form.status,
          updatedAt: form.updatedAt,
          progress: T2FormStorageService.instance.calculateFormProgress(form),
          t2Form: form,
        ));
      }

      // If no forms exist, show "Get Started"
      if (allForms.isEmpty) {
        return {
          'progress': 0.0,
          'progressText': 'Get Started',
          'formType': null,
          'lastSaved': null,
          'isComplete': false,
        };
      }

      // Separate forms by status
      final draftForms = allForms.where((f) => f.status == 'draft').toList();
      final submittedForms = allForms.where((f) => f.status == 'submitted').toList();

      // If all forms are submitted, show "under review" for most recent
      if (draftForms.isEmpty && submittedForms.isNotEmpty) {
        final mostRecent = submittedForms.reduce((a, b) => 
          (a.updatedAt ?? DateTime(0)).isAfter(b.updatedAt ?? DateTime(0)) ? a : b);

        return {
          'progress': 1.0,
          'progressText': '${mostRecent.formType} Form submitted, under review',
          'formType': mostRecent.formType,
          'lastSaved': mostRecent.updatedAt,
          'isComplete': true,
        };
      }

      // If there are draft forms, show progress of most recent draft
      if (draftForms.isNotEmpty) {
        final mostRecentDraft = draftForms.reduce((a, b) => 
          (a.updatedAt ?? DateTime(0)).isAfter(b.updatedAt ?? DateTime(0)) ? a : b);

        final progress = mostRecentDraft.progress;
        final progressText = _getProgressText(progress, mostRecentDraft.formType);

        return {
          'progress': progress,
          'progressText': progressText,
          'formType': mostRecentDraft.formType,
          'lastSaved': mostRecentDraft.updatedAt,
          'isComplete': progress >= 1.0,
          'formId': mostRecentDraft.formId,
        };
      }

      // Fallback (shouldn't reach here)
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'formType': null,
        'lastSaved': null,
        'isComplete': false,
      };
    } catch (e) {
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'formType': null,
        'lastSaved': null,
        'isComplete': false,
      };
    }
  }

  /// Get form counts for both T1 and T2 forms
  Future<Map<String, dynamic>> getFormCounts() async {
    try {
      final t1Forms = await T1FormStorageService.instance.loadAllForms();
      final t2Forms = await T2FormStorageService.instance.loadAllForms();

      int submittedCount = 0;
      int draftsCount = 0;
      int t1Count = 0;
      int t2Count = 0;

      // Count T1 forms
      for (final form in t1Forms) {
        t1Count++;
        if (form.status == 'submitted') {
          submittedCount++;
        } else if (form.status == 'draft') {
          draftsCount++;
        }
      }

      // Count T2 forms
      for (final form in t2Forms) {
        t2Count++;
        if (form.status == 'submitted') {
          submittedCount++;
        } else if (form.status == 'draft') {
          draftsCount++;
        }
      }

      return {
        'submitted': submittedCount,
        'drafts': draftsCount,
        't1Count': t1Count,
        't2Count': t2Count,
        'total': t1Count + t2Count,
      };
    } catch (e) {
      return {
        'submitted': 0,
        'drafts': 0,
        't1Count': 0,
        't2Count': 0,
        'total': 0,
      };
    }
  }

  /// Navigate to the most recent draft form
  String getMostRecentFormRoute() {
    // This method would be called after getting the progress status
    // Implementation depends on how you want to handle navigation
    return '/tax-forms/filled-forms';
  }

  String _getProgressText(double progress, String formType) {
    if (progress <= 0.01) {
      return 'Get Started with $formType';
    } else if (progress >= 1.0) {
      return '$formType Form completed, ready to submit';
    } else {
      return '$formType Form ${(progress * 100).toInt()}% Complete';
    }
  }
}