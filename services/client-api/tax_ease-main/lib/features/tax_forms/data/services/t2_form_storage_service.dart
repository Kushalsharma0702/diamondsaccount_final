import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:logger/logger.dart';
import '../models/t2_form_models.dart';

class T2FormStorageService {
  // New keys for On-Boarding
  static const String _t2FormDataKey = 'T2_ONB_FORM_DATA';
  static const String _t2FormProgressKey = 'T2_ONB_FORM_PROGRESS';
  static const String _t2FormLastSavedKey = 'T2_ONB_FORM_LAST_SAVED';
  static const String _t2FormsListKey = 'T2_ONB_FORMS_LIST';

  static T2FormStorageService? _instance;
  static T2FormStorageService get instance {
    _instance ??= T2FormStorageService._();
    return _instance!;
  }

  final Logger _logger = Logger();

  T2FormStorageService._();

/// Create a new T2 On-Boarding form with unique ID
  T2OnboardingData createNewForm() {
    return T2OnboardingData.newForm();
  }

  /// Save multiple forms to SharedPreferences
Future<bool> saveAllForms(List<T2OnboardingData> forms) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonList = forms.map((form) => form.toJson()).toList();
      final jsonString = json.encode(jsonList);
      
      await prefs.setString(_t2FormsListKey, jsonString);
      return true;
    } catch (e) {
      _logger.e('Error saving T2 forms: $e');
      return false;
    }
  }

/// Load all T2 On-Boarding forms from SharedPreferences
  Future<List<T2OnboardingData>> loadAllForms() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_t2FormsListKey);
      
      if (jsonString == null) {
        // Try to migrate old single form to new format
        final oldForm = await loadT2FormData();
        if (oldForm != null) {
          final migratedForm = oldForm.copyWith(
            id: oldForm.id.isEmpty ? 'T2ONB_${DateTime.now().millisecondsSinceEpoch}' : oldForm.id,
          );
          await saveAllForms([migratedForm]);
          return [migratedForm];
        }
        return [];
      }
      
      final jsonList = json.decode(jsonString) as List;
      return jsonList.map((e) => T2OnboardingData.fromJson(e as Map<String, dynamic>)).toList();
    } catch (e) {
      _logger.e('Error loading T2 forms: $e');
      return [];
    }
  }

  /// Save a specific form (update existing or add new)
Future<bool> saveForm(T2OnboardingData form) async {
    try {
      final forms = await loadAllForms();
      final index = forms.indexWhere((f) => f.id == form.id);
      
      if (index >= 0) {
        // Update existing form
        forms[index] = form;
      } else {
        // Add new form
        forms.add(form);
      }
      
      return await saveAllForms(forms);
    } catch (e) {
      _logger.e('Error saving T2 form: $e');
      return false;
    }
  }

  /// Get a form by ID
Future<T2OnboardingData?> getFormById(String id) async {
    try {
      final forms = await loadAllForms();
      return forms.firstWhere((form) => form.id == id);
    } catch (e) {
      _logger.e('Error getting T2 form by ID: $e');
      return null;
    }
  }

  /// Save T2 form data to SharedPreferences (Legacy method)
Future<bool> saveT2FormData(T2OnboardingData formData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = json.encode(formData.toJson());
      
      await prefs.setString(_t2FormDataKey, jsonString);
      await prefs.setString(_t2FormLastSavedKey, DateTime.now().toIso8601String());
      
      // Calculate and save progress
      final progress = calculateFormProgress(formData);
      await prefs.setDouble(_t2FormProgressKey, progress);
      
      return true;
    } catch (e) {
      _logger.e('Error saving T2 form data: $e');
      return false;
    }
  }

  /// Load T2 form data from SharedPreferences (Legacy method)
Future<T2OnboardingData?> loadT2FormData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_t2FormDataKey);
      
      if (jsonString == null) return null;
      
final jsonData = json.decode(jsonString) as Map<String, dynamic>;
      return T2OnboardingData.fromJson(jsonData);
    } catch (e) {
      _logger.e('Error loading T2 form data: $e');
      return null;
    }
  }

  /// Get form progress percentage (0.0 to 1.0)
  Future<double> getFormProgress() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getDouble(_t2FormProgressKey) ?? 0.0;
    } catch (e) {
      _logger.e('Error getting T2 form progress: $e');
      return 0.0;
    }
  }

  /// Get progress text based on percentage
  String getProgressText(double progress) {
    if (progress <= 0.01) {
      return 'Get Started';
    } else if (progress >= 1.0) {
      return 'Form filled successfully, under review';
    } else {
      // Format as percentage with 0 decimal places
      return '${(progress * 100).toInt()}% Complete';
    }
  }

  /// Get last saved date
  Future<DateTime?> getLastSavedDate() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final dateString = prefs.getString(_t2FormLastSavedKey);
      return dateString != null ? DateTime.parse(dateString) : null;
    } catch (e) {
      _logger.e('Error getting last saved date: $e');
      return null;
    }
  }

  /// Clear all T2 form data
  Future<bool> clearT2FormData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_t2FormDataKey);
      await prefs.remove(_t2FormProgressKey);
      await prefs.remove(_t2FormLastSavedKey);
      return true;
    } catch (e) {
      _logger.e('Error clearing T2 form data: $e');
      return false;
    }
  }

  /// Clear all forms data (including the new forms list)
  Future<bool> clearAllFormsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Clear all T2 form related keys
      await prefs.remove(_t2FormDataKey);
      await prefs.remove(_t2FormProgressKey);
      await prefs.remove(_t2FormLastSavedKey);
      await prefs.remove(_t2FormsListKey);
      
      _logger.i('All T2 forms data cleared successfully');
      return true;
    } catch (e) {
      _logger.e('Error clearing all T2 forms data: $e');
      return false;
    }
  }

  /// Calculate form completion progress based on filled fields
double calculateFormProgress(T2OnboardingData formData) {
    int totalFields = 0;
    int filledFields = 0;

// Checklist items (Weight: 25%)
    totalFields += 5;
    if (formData.craAuthorizationProvided) filledFields++;
    if (formData.incorporationDocsProvided) filledFields++;
    if (formData.payrollEnrollmentReturned) filledFields++;
    if (formData.previousYearRecordsProvided) filledFields++;
    if (formData.franchiseDocsProvided) filledFields++;

    // Company details (Weight: 60%)
    totalFields += 12; // companyName, businessNumber, address, incorporationDate, isInactive, principalActivity, principalActivityPercentage, director, signingOfficer, signingOfficerPhone, totalSharesIssued, totalAmountOfShares
    if (formData.companyName.isNotEmpty) filledFields++;
    if (formData.businessNumber.isNotEmpty) filledFields++;
    if (formData.registeredAddress.isNotEmpty) filledFields++;
    if (formData.incorporationDate != null) filledFields++;
    if (formData.isInactive) filledFields++; // counts as answered
    if (formData.principalActivity.isNotEmpty) filledFields++;
    if (formData.principalActivityPercentage > 0) filledFields++;
    if (formData.directorFullName.isNotEmpty) filledFields++;
    if (formData.signingOfficerFullNameAndPosition.isNotEmpty) filledFields++;
    if (formData.signingOfficerPhone.isNotEmpty) filledFields++;
    if (formData.totalSharesIssued > 0) filledFields++;
    if (formData.totalAmountOfShares > 0) filledFields++;

    // Shareholders (Weight: 15%)
    totalFields += 4; // At least one shareholder with name and percentages
    if (formData.shareholders.isNotEmpty) {
      final sh = formData.shareholders.first;
      if (sh.name.isNotEmpty) filledFields++;
      if (sh.commonSharesPercent > 0) filledFields++;
      if (sh.preferenceSharesPercent > 0) filledFields++;
      if (sh.sinOrBn.isNotEmpty) filledFields++;
    }

    if (totalFields == 0) return 0.0;
    return filledFields / totalFields;
  }


  /// Check if form is complete (100% filled)
  Future<bool> isFormComplete() async {
    final progress = await getFormProgress();
    return progress >= 1.0;
  }

  /// Get progress status text based on percentage
  String getProgressStatusText(double progress) {
    if (progress == 0.0) {
      return 'Get Started';
    } else if (progress >= 1.0) {
      return 'Form filled successfully, under review';
    } else {
      return '${(progress * 100).round()}% form filled';
    }
  }

  /// Get progress status for dashboard based on multiple forms
  Future<Map<String, dynamic>> getProgressStatus() async {
    try {
      final forms = await loadAllForms();
      
      // If no forms exist, show "Get Started"
      if (forms.isEmpty) {
        return {
          'progress': 0.0,
          'progressText': 'Get Started',
          'lastSaved': null,
          'isComplete': false,
        };
      }
      
      // Separate forms by status
      final draftForms = forms.where((f) => f.status == 'draft').toList();
      final submittedForms = forms.where((f) => f.status == 'submitted').toList();
      
      // If all forms are submitted, show "under review"
      if (draftForms.isEmpty && submittedForms.isNotEmpty) {
        final mostRecent = submittedForms.reduce((a, b) => 
          (a.updatedAt ?? DateTime(0)).isAfter(b.updatedAt ?? DateTime(0)) ? a : b);
        
        return {
          'progress': 1.0,
          'progressText': 'Form submitted, under review',
          'lastSaved': mostRecent.updatedAt,
          'isComplete': true,
        };
      }
      
      // If there are draft forms, show progress of most recent draft
      if (draftForms.isNotEmpty) {
        final mostRecentDraft = draftForms.reduce((a, b) => 
          (a.updatedAt ?? DateTime(0)).isAfter(b.updatedAt ?? DateTime(0)) ? a : b);
        
        final progress = calculateFormProgress(mostRecentDraft);
        
        return {
          'progress': progress,
          'progressText': getProgressStatusText(progress),
          'lastSaved': mostRecentDraft.updatedAt,
          'isComplete': progress >= 1.0,
        };
      }
      
      // Fallback (shouldn't reach here)
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'lastSaved': null,
        'isComplete': false,
      };
    } catch (e) {
      _logger.e('Error getting T2 progress status: $e');
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'lastSaved': null,
        'isComplete': false,
      };
    }
  }
}