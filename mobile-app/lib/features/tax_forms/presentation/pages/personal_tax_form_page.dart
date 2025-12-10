import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../data/models/t1_form_models_simple.dart';
import '../../data/services/t1_form_storage_service.dart';
import '../../data/t1_form_api.dart';
import '../widgets/t1_personal_info_step.dart';
import '../widgets/t1_questionnaire_1_step.dart';
import '../widgets/t1_questionnaire_2_step.dart';
import '../widgets/t1_form_progress_bar.dart';

class PersonalTaxFormPage extends StatefulWidget {
  final String? formId;
  
  const PersonalTaxFormPage({super.key, this.formId});

  @override
  State<PersonalTaxFormPage> createState() => _PersonalTaxFormPageState();
}

class _PersonalTaxFormPageState extends State<PersonalTaxFormPage>
    with TickerProviderStateMixin {
  late PageController _pageController;
  late AnimationController _progressController;
  late AnimationController _slideController;
  
  int _currentStep = 0;
  
  /// Dynamic list of step titles shown in the top bar.
  /// Always starts with:
  /// 0: Personal Info
  /// 1: Questionnaire
  /// Followed by optional detail pages in this order:
  /// - Uber/Skip/DoorDash
  /// - Rental Income
  /// - General Business
  /// - Moving Expenses
  List<String> _stepTitles = const [];

  /// Detail steps corresponding to indices >= 2 in [_stepTitles].
  List<T1DetailStepType> _detailSteps = const [];
  
  T1FormData _formData = const T1FormData.empty();
  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    _progressController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _slideController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    
    _loadFormData();
  }

  @override
  void dispose() {
    _autoSaveTimer?.cancel();
    _pageController.dispose();
    _progressController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  Future<void> _loadFormData() async {
    T1FormData? savedData;
    
    if (widget.formId != null) {
      // Load specific form by ID
      savedData = await T1FormStorageService.instance.getFormById(widget.formId!);
    }
    
    if (savedData == null) {
      // Create a new form if no existing form found
      savedData = T1FormStorageService.instance.createNewForm();
      // Save the new form immediately
      await T1FormStorageService.instance.saveForm(savedData);
    }
    
    setState(() {
      _formData = savedData!;
      _isLoading = false;
      _rebuildSteps();
    });
  }

  Future<void> _saveFormData() async {
    if (_isSaving) return;
    
    setState(() {
      _isSaving = true;
    });
    
    try {
      final success = await T1FormStorageService.instance.saveForm(_formData);
      
      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 8),
                Text('Form saved successfully'),
              ],
            ),
            backgroundColor: AppColors.success,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error, color: Colors.white),
                const SizedBox(width: 8),
                Text('Error saving form: $e'),
              ],
            ),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      setState(() {
        _isSaving = false;
      });
    }
  }

  void _rebuildSteps() {
    final hasMovingExpenses = _formData.hasMovingExpenses ?? false;
    final isSelfEmployed = _formData.isSelfEmployed ?? false;
    final businessTypes = _formData.selfEmployment?.businessTypes ?? <String>[];

    final detailSteps = <T1DetailStepType>[];
    final titles = <String>['Personal Info', 'Questionnaire'];

    if (isSelfEmployed && businessTypes.contains('uber')) {
      detailSteps.add(T1DetailStepType.uberSkipDoordash);
      titles.add('Uberskip/Doordash');
    }
    if (isSelfEmployed && businessTypes.contains('rental')) {
      detailSteps.add(T1DetailStepType.rentalIncome);
      titles.add('Rental Income');
    }
    if (isSelfEmployed && businessTypes.contains('general')) {
      detailSteps.add(T1DetailStepType.generalBusiness);
      titles.add('General Business');
    }
    if (hasMovingExpenses) {
      detailSteps.add(T1DetailStepType.movingExpenses);
      titles.add('Moving Expenses');
    }

    _detailSteps = detailSteps;
    _stepTitles = titles;

    if (_stepTitles.isEmpty) {
      _currentStep = 0;
      _progressController.animateTo(0.0);
      return;
    }

    if (_currentStep >= _stepTitles.length) {
      _currentStep = _stepTitles.length - 1;
    }

    _updateProgress();
  }

  void _updateProgress() {
    if (_stepTitles.length <= 1) {
      _progressController.animateTo(0.0);
    } else {
      _progressController.animateTo(_currentStep / (_stepTitles.length - 1));
    }
  }

  void _nextStep() {
    if (_stepTitles.isEmpty) return;

    // If this is the last step, submitting the form instead of navigating forward
    if (_currentStep >= _stepTitles.length - 1) {
      _submitForm();
      return;
    }

    setState(() {
      _currentStep++;
    });
    _pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
    _updateProgress();
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
      _updateProgress();
    }
  }

  Future<void> _submitForm() async {
    try {
      // Show loading indicator
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Submitting form to database...')),
        );
      }

      // Submit to backend API FIRST - this saves the form directly to database
      // Don't save locally first - database is the source of truth
      try {
        final backendResponse = await T1FormApi.submitForm(
          formData: _formData,
          taxYear: DateTime.now().year, // Use current year
        );
        
        if (backendResponse['id'] == null) {
          throw Exception('Backend did not return form ID');
        }
        
        // Update form status to submitted and sync with backend response
        _formData = _formData.copyWith(
          status: 'submitted',
          id: backendResponse['id'].toString(),
        );
        
        // Save locally only AFTER successful database submission (for offline viewing)
        await _saveFormData();
        
        print('✅ Form submitted to database: ${backendResponse['id']}');
        
      } catch (e) {
        // If database submission fails, show error and don't mark as submitted
        print('❌ Failed to submit form to database: $e');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to submit form: ${e.toString()}. Please try again.'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
        // Don't proceed to success dialog if submission failed
        setState(() => _isLoading = false);
        return;
      }
      
      if (mounted) {
        // Show success dialog
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            icon: Icon(
              Icons.check_circle,
              color: AppColors.success,
              size: 64,
            ),
            title: const Text('Form Submitted Successfully!'),
            content: const Text(
              'Your T1 Personal Tax form has been saved and is now under review. '
              'You can continue to edit the form until the filing deadline.',
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  context.go('/tax-forms/filled-forms?refresh=true'); // Navigate with refresh parameter
                },
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error submitting form: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  void _updateFormData(T1FormData newData) {
    setState(() {
      _formData = newData;
      _rebuildSteps();
    });
    // Auto-save the form data when it changes
    _autoSaveFormData();
  }

  // Debounced auto-save to avoid excessive saves
  Timer? _autoSaveTimer;
  void _autoSaveFormData() {
    _autoSaveTimer?.cancel();
    _autoSaveTimer = Timer(const Duration(milliseconds: 1500), () {
      _performAutoSave();
    });
  }

  Future<void> _performAutoSave() async {
    if (!mounted) return;
    
    try {
      await T1FormStorageService.instance.saveForm(_formData);
      // Silent auto-save, no user notification
    } catch (e) {
      // Only log error, don't show user notification for auto-save failures
      debugPrint('Auto-save failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('T1 Personal Tax Form'),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => context.go('/tax-forms/filled-forms'),
          ),
        ),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('T1 Personal Tax Form'),
        centerTitle: true,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/tax-forms/filled-forms'),
        ),
        actions: [
          if (_isSaving)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          // Progress Bar
          Container(
            color: Theme.of(context).cardColor,
            padding: const EdgeInsets.all(AppDimensions.spacingMd),
            child: Column(
              children: [
                T1FormProgressBar(
                  currentStep: _currentStep,
                  totalSteps: _stepTitles.length,
                  controller: _progressController,
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: List.generate(_stepTitles.length, (index) {
                    final isActive = index == _currentStep;
                    return Flexible(
                      child: Text(
                        _stepTitles[index],
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                          color: isActive ? AppColors.primary : AppColors.grey500,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    );
                  }),
                ),
              ],
            ),
          ),
          // Form Content
          Expanded(
            child: PageView(
              controller: _pageController,
              onPageChanged: (index) {
                setState(() {
                  _currentStep = index;
                });
                _updateProgress();
              },
              children: List.generate(_stepTitles.length, (index) {
                // Step 0: Personal Information
                if (index == 0) {
                  return T1PersonalInfoStep(
                    personalInfo: _formData.personalInfo,
                    onPersonalInfoChanged: (personalInfo) {
                      _updateFormData(_formData.copyWith(personalInfo: personalInfo));
                    },
                    onNext: _nextStep,
                  );
                }

                // Step 1: Questionnaire (basic questions)
                if (index == 1) {
                  return T1Questionnaire1Step(
                    formData: _formData,
                    onFormDataChanged: _updateFormData,
                    onPrevious: _previousStep,
                    onNext: _nextStep,
                  );
                }

                // Subsequent steps: detailed sections (Uber, Rental, General Business, Moving)
                final detailIndex = index - 2;
                if (detailIndex < 0 || detailIndex >= _detailSteps.length) {
                  // Fallback to an empty container if something goes out of sync
                  return const SizedBox.shrink();
                }

                final detailType = _detailSteps[detailIndex];
                final isLastStep = index == _stepTitles.length - 1;
                final String primaryLabel = isLastStep
                    ? 'Submit Form'
                    : 'Next: ${_stepTitles[index + 1]}';
                final String previousTitle = _stepTitles[index - 1];

                return T1Questionnaire2Step(
                  stepType: detailType,
                  formData: _formData,
                  onFormDataChanged: _updateFormData,
                  onPrevious: _previousStep,
                  onPrimary: isLastStep ? _submitForm : _nextStep,
                  primaryButtonLabel: primaryLabel,
                  previousStepTitle: previousTitle,
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}
