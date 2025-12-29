import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:logger/logger.dart';
import '../models/t1_form_models_simple.dart';

class T1FormStorageService {
  static const String _t1FormDataKey = 'T1_FORM_DATA';
  static const String _t1FormProgressKey = 'T1_FORM_PROGRESS';
  static const String _t1FormLastSavedKey = 'T1_FORM_LAST_SAVED';
  static const String _t1FormsListKey = 'T1_FORMS_LIST'; // New key for multiple forms

  static T1FormStorageService? _instance;
  static T1FormStorageService get instance {
    _instance ??= T1FormStorageService._();
    return _instance!;
  }

  final Logger _logger = Logger();

  T1FormStorageService._();

  /// Create a new T1 form with unique ID
  T1FormData createNewForm() {
    final id = 'T1_${DateTime.now().millisecondsSinceEpoch}';
    return T1FormData(
      id: id,
      status: 'draft',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  /// Save multiple forms to SharedPreferences
  Future<bool> saveAllForms(List<T1FormData> forms) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonList = forms.map((form) => form.toJson()).toList();
      final jsonString = json.encode(jsonList);
      
      await prefs.setString(_t1FormsListKey, jsonString);
      return true;
    } catch (e) {
      _logger.e('Error saving T1 forms: $e');
      return false;
    }
  }

  /// Load all T1 forms from SharedPreferences
  Future<List<T1FormData>> loadAllForms() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_t1FormsListKey);
      
      if (jsonString == null) {
        // Try to migrate old single form to new format
        final oldForm = await loadT1FormData();
        if (oldForm != null) {
          final migratedForm = oldForm.copyWith(
            id: oldForm.id.isEmpty ? 'T1_${DateTime.now().millisecondsSinceEpoch}' : oldForm.id,
          );
          await saveAllForms([migratedForm]);
          return [migratedForm];
        }
        return [];
      }
      
      final jsonList = json.decode(jsonString) as List;
      return jsonList.map((json) => T1FormData.fromJson(json)).toList();
    } catch (e) {
      _logger.e('Error loading T1 forms: $e');
      return [];
    }
  }

  /// Save a specific form (update existing or add new)
  Future<bool> saveForm(T1FormData form) async {
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
      _logger.e('Error saving form: $e');
      return false;
    }
  }

  /// Get a form by ID
  Future<T1FormData?> getFormById(String id) async {
    try {
      final forms = await loadAllForms();
      return forms.firstWhere((form) => form.id == id);
    } catch (e) {
      _logger.e('Error getting form by ID: $e');
      return null;
    }
  }

  /// Save T1 form data to SharedPreferences
  Future<bool> saveT1FormData(T1FormData formData) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = json.encode(formData.toJson());
      
      await prefs.setString(_t1FormDataKey, jsonString);
      await prefs.setString(_t1FormLastSavedKey, DateTime.now().toIso8601String());
      
      // Calculate and save progress
      final progress = calculateFormProgress(formData);
      await prefs.setDouble(_t1FormProgressKey, progress);
      
      return true;
    } catch (e) {
      _logger.e('Error saving T1 form data: $e');
      return false;
    }
  }

  /// Load T1 form data from SharedPreferences
  Future<T1FormData?> loadT1FormData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_t1FormDataKey);
      
      if (jsonString == null) return null;
      
      final jsonData = json.decode(jsonString) as Map<String, dynamic>;
      return T1FormData.fromJson(jsonData);
    } catch (e) {
      _logger.e('Error loading T1 form data: $e');
      return null;
    }
  }

  /// Get form progress percentage (0.0 to 1.0)
  Future<double> getFormProgress() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getDouble(_t1FormProgressKey) ?? 0.0;
    } catch (e) {
      _logger.e('Error getting form progress: $e');
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
      final dateString = prefs.getString(_t1FormLastSavedKey);
      return dateString != null ? DateTime.parse(dateString) : null;
    } catch (e) {
      _logger.e('Error getting last saved date: $e');
      return null;
    }
  }

  /// Clear all T1 form data
  Future<bool> clearT1FormData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_t1FormDataKey);
      await prefs.remove(_t1FormProgressKey);
      await prefs.remove(_t1FormLastSavedKey);
      return true;
    } catch (e) {
      _logger.e('Error clearing T1 form data: $e');
      return false;
    }
  }

  /// Clear all forms data (including the new forms list)
  Future<bool> clearAllFormsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Clear all T1 form related keys
      await prefs.remove(_t1FormDataKey);
      await prefs.remove(_t1FormProgressKey);
      await prefs.remove(_t1FormLastSavedKey);
      await prefs.remove(_t1FormsListKey);
      
      _logger.i('All forms data cleared successfully');
      return true;
    } catch (e) {
      _logger.e('Error clearing all forms data: $e');
      return false;
    }
  }

  /// Calculate form completion progress based on filled fields
  double calculateFormProgress(T1FormData formData) {
    int totalFields = 0;
    int filledFields = 0;

    // Personal Info (Weight: 40%)
    final personalInfoFields = _getPersonalInfoProgress(formData.personalInfo);
    totalFields += personalInfoFields['total']!;
    filledFields += personalInfoFields['filled']!;

    // Questionnaire sections (Weight: 60%)
    // Simplified progress calculation for questionnaire
    totalFields += 18; // One field per question (18 questions total)
    
    // Count answered questions
    if (formData.hasForeignProperty != null) filledFields++;
    if (formData.hasMedicalExpenses != null) filledFields++;
    if (formData.hasCharitableDonations != null) filledFields++;
    if (formData.hasMovingExpenses != null) filledFields++;
    if (formData.isSelfEmployed != null) filledFields++;
    if (formData.isFirstHomeBuyer != null) filledFields++;
    if (formData.soldPropertyLongTerm != null) filledFields++;
    if (formData.soldPropertyShortTerm != null) filledFields++;
    if (formData.hasWorkFromHomeExpense != null) filledFields++;
    if (formData.wasStudentLastYear != null) filledFields++;
    if (formData.isUnionMember != null) filledFields++;
    if (formData.hasDaycareExpenses != null) filledFields++;
    if (formData.isFirstTimeFiler != null) filledFields++;
    if (formData.hasOtherIncome != null) filledFields++;
    if (formData.hasProfessionalDues != null) filledFields++;
    if (formData.hasRrspFhsaInvestment != null) filledFields++;
    if (formData.hasChildArtSportCredit != null) filledFields++;
    if (formData.isProvinceFiler != null) filledFields++;
    
    // Give extra weight to details if they exist
    if (formData.hasForeignProperty == true && formData.foreignProperties.isNotEmpty) {
      totalFields += 3;
      filledFields += 3;
    }

    if (totalFields == 0) return 0.0;
    return filledFields / totalFields;
  }

  Map<String, int> _getPersonalInfoProgress(T1PersonalInfo personalInfo) {
    int total = 0;
    int filled = 0;

    // Required fields
    total += 7; // firstName, lastName, sin, dateOfBirth, address, phoneNumber, email
    if (personalInfo.firstName.isNotEmpty) filled++;
    if (personalInfo.lastName.isNotEmpty) filled++;
    if (personalInfo.sin.isNotEmpty) filled++;
    if (personalInfo.dateOfBirth != null) filled++;
    if (personalInfo.address.isNotEmpty) filled++;
    if (personalInfo.phoneNumber.isNotEmpty) filled++;
    if (personalInfo.email.isNotEmpty) filled++;

    // Canadian citizenship
    total += 1;
    if (personalInfo.isCanadianCitizen != null) filled++;

    // Marital status
    total += 1;
    if (personalInfo.maritalStatus.isNotEmpty) filled++;

    // Spouse info (if married/common-law)
    if (personalInfo.maritalStatus == 'married' || personalInfo.maritalStatus == 'common-law') {
      total += 4; // spouse firstName, lastName, sin, dateOfBirth
      if (personalInfo.spouseInfo != null) {
        if (personalInfo.spouseInfo!.firstName.isNotEmpty) filled++;
        if (personalInfo.spouseInfo!.lastName.isNotEmpty) filled++;
        if (personalInfo.spouseInfo!.sin.isNotEmpty) filled++;
        if (personalInfo.spouseInfo!.dateOfBirth != null) filled++;
      }
    }

    // Children (each child adds weight)
    for (final child in personalInfo.children) {
      total += 4; // firstName, lastName, sin, dateOfBirth
      if (child.firstName.isNotEmpty) filled++;
      if (child.lastName.isNotEmpty) filled++;
      if (child.sin.isNotEmpty) filled++;
      if (child.dateOfBirth != null) filled++;
    }

    return {'total': total, 'filled': filled};
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
      _logger.e('Error getting progress status: $e');
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'lastSaved': null,
        'isComplete': false,
      };
    }
  }
}