import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../data/models/t2_form_models.dart';
import '../../data/services/t2_form_storage_service.dart';

class BusinessTaxFormPage extends StatefulWidget {
  final String? formId;
  const BusinessTaxFormPage({super.key, this.formId});

  @override
  State<BusinessTaxFormPage> createState() => _BusinessTaxFormPageState();
}

class _BusinessTaxFormPageState extends State<BusinessTaxFormPage> {
  T2OnboardingData _form = T2OnboardingData.newForm();
  bool _isLoading = true;
  bool _isSaving = false;
  Timer? _autoSaveTimer;

  // Controllers
  final _companyNameCtrl = TextEditingController();
  final _businessNumberCtrl = TextEditingController();
  final _registeredAddressCtrl = TextEditingController();
  final _principalActivityCtrl = TextEditingController();
  final _principalActivityPctCtrl = TextEditingController();
  final _directorFullNameCtrl = TextEditingController();
  final _signingOfficerCtrl = TextEditingController();
  final _signingOfficerPhoneCtrl = TextEditingController();
  final _totalSharesIssuedCtrl = TextEditingController();
  final _totalAmountOfSharesCtrl = TextEditingController();

  // Shareholder 1
  final _sh1NameCtrl = TextEditingController();
  final _sh1CommonPctCtrl = TextEditingController();
  final _sh1PrefPctCtrl = TextEditingController();
  final _sh1SinBnCtrl = TextEditingController();
  // Shareholder 2
  final _sh2NameCtrl = TextEditingController();
  final _sh2CommonPctCtrl = TextEditingController();
  final _sh2PrefPctCtrl = TextEditingController();
  final _sh2SinBnCtrl = TextEditingController();

  DateTime? _incorporationDate;

  // Checklist
  bool _craAuthProvided = false;
  bool _incDocsProvided = false;
  bool _payrollReturned = false;
  bool _prevYearProvided = false;
  bool _franchiseProvided = false;
  bool _isInactive = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _autoSaveTimer?.cancel();
    _companyNameCtrl.dispose();
    _businessNumberCtrl.dispose();
    _registeredAddressCtrl.dispose();
    _principalActivityCtrl.dispose();
    _principalActivityPctCtrl.dispose();
    _directorFullNameCtrl.dispose();
    _signingOfficerCtrl.dispose();
    _signingOfficerPhoneCtrl.dispose();
    _totalSharesIssuedCtrl.dispose();
    _totalAmountOfSharesCtrl.dispose();
    _sh1NameCtrl.dispose();
    _sh1CommonPctCtrl.dispose();
    _sh1PrefPctCtrl.dispose();
    _sh1SinBnCtrl.dispose();
    _sh2NameCtrl.dispose();
    _sh2CommonPctCtrl.dispose();
    _sh2PrefPctCtrl.dispose();
    _sh2SinBnCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    T2OnboardingData? saved;
    if (widget.formId != null) {
      saved = await T2FormStorageService.instance.getFormById(widget.formId!);
    }
    saved ??= T2FormStorageService.instance.createNewForm();
    await T2FormStorageService.instance.saveForm(saved);

    _applyToControllers(saved);
    setState(() {
      _form = saved!;
      _isLoading = false;
    });
  }

  void _applyToControllers(T2OnboardingData f) {
    _companyNameCtrl.text = f.companyName;
    _businessNumberCtrl.text = f.businessNumber;
    _registeredAddressCtrl.text = f.registeredAddress;
    _principalActivityCtrl.text = f.principalActivity;
    _principalActivityPctCtrl.text = f.principalActivityPercentage.toString();
    _directorFullNameCtrl.text = f.directorFullName;
    _signingOfficerCtrl.text = f.signingOfficerFullNameAndPosition;
    _signingOfficerPhoneCtrl.text = f.signingOfficerPhone;
    _totalSharesIssuedCtrl.text = f.totalSharesIssued.toString();
    _totalAmountOfSharesCtrl.text = f.totalAmountOfShares.toString();
    _incorporationDate = f.incorporationDate;
    _craAuthProvided = f.craAuthorizationProvided;
    _incDocsProvided = f.incorporationDocsProvided;
    _payrollReturned = f.payrollEnrollmentReturned;
    _prevYearProvided = f.previousYearRecordsProvided;
    _franchiseProvided = f.franchiseDocsProvided;
    _isInactive = f.isInactive;
    // shareholders
    if (f.shareholders.isNotEmpty) {
      final s = f.shareholders[0];
      _sh1NameCtrl.text = s.name;
      _sh1CommonPctCtrl.text = s.commonSharesPercent.toString();
      _sh1PrefPctCtrl.text = s.preferenceSharesPercent.toString();
      _sh1SinBnCtrl.text = s.sinOrBn;
    }
    if (f.shareholders.length > 1) {
      final s = f.shareholders[1];
      _sh2NameCtrl.text = s.name;
      _sh2CommonPctCtrl.text = s.commonSharesPercent.toString();
      _sh2PrefPctCtrl.text = s.preferenceSharesPercent.toString();
      _sh2SinBnCtrl.text = s.sinOrBn;
    }
  }

  void _updateAndAutosave() {
    final shareholders = <T2ShareholderInfo>[];
    if (_sh1NameCtrl.text.isNotEmpty || _sh1SinBnCtrl.text.isNotEmpty) {
      shareholders.add(T2ShareholderInfo(
        name: _sh1NameCtrl.text,
        commonSharesPercent: double.tryParse(_sh1CommonPctCtrl.text) ?? 0,
        preferenceSharesPercent: double.tryParse(_sh1PrefPctCtrl.text) ?? 0,
        sinOrBn: _sh1SinBnCtrl.text,
      ));
    }
    if (_sh2NameCtrl.text.isNotEmpty || _sh2SinBnCtrl.text.isNotEmpty) {
      shareholders.add(T2ShareholderInfo(
        name: _sh2NameCtrl.text,
        commonSharesPercent: double.tryParse(_sh2CommonPctCtrl.text) ?? 0,
        preferenceSharesPercent: double.tryParse(_sh2PrefPctCtrl.text) ?? 0,
        sinOrBn: _sh2SinBnCtrl.text,
      ));
    }

    _form = _form.copyWith(
      companyName: _companyNameCtrl.text,
      businessNumber: _businessNumberCtrl.text,
      registeredAddress: _registeredAddressCtrl.text,
      incorporationDate: _incorporationDate,
      isInactive: _isInactive,
      principalActivity: _principalActivityCtrl.text,
      principalActivityPercentage: int.tryParse(_principalActivityPctCtrl.text) ?? 0,
      directorFullName: _directorFullNameCtrl.text,
      signingOfficerFullNameAndPosition: _signingOfficerCtrl.text,
      signingOfficerPhone: _signingOfficerPhoneCtrl.text,
      totalSharesIssued: int.tryParse(_totalSharesIssuedCtrl.text) ?? 0,
      totalAmountOfShares: double.tryParse(_totalAmountOfSharesCtrl.text) ?? 0.0,
      shareholders: shareholders,
      craAuthorizationProvided: _craAuthProvided,
      incorporationDocsProvided: _incDocsProvided,
      payrollEnrollmentReturned: _payrollReturned,
      previousYearRecordsProvided: _prevYearProvided,
      franchiseDocsProvided: _franchiseProvided,
    );

    _autoSaveTimer?.cancel();
    _autoSaveTimer = Timer(const Duration(milliseconds: 1200), () async {
      await T2FormStorageService.instance.saveForm(_form);
    });
    setState(() {});
  }

  Future<void> _save() async {
    if (_isSaving) return;
    setState(() => _isSaving = true);
    try {
      await T2FormStorageService.instance.saveForm(_form);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [Icon(Icons.check_circle, color: Colors.white), SizedBox(width: 8), Text('Form saved')],
          ),
          backgroundColor: AppColors.success,
          duration: const Duration(seconds: 2),
        ),
      );
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  Future<void> _submit() async {
    _form = _form.copyWith(status: 'submitted');
    await _save();
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        icon: Icon(Icons.check_circle, color: AppColors.success, size: 64),
        title: const Text('Form Submitted Successfully!'),
        content: const Text('Your T2 Business On-Boarding has been saved and is now under review.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.go('/tax-forms/filled-forms?refresh=true');
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('On-Boarding Details'),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => context.go('/tax-forms/filled-forms'),
          ),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('On-Boarding Details'),
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
              child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.screenPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _section(
              context,
              'Checklist',
              Column(children: [
                _checkbox('CRA authorization of business account provided', _craAuthProvided, (v) { _craAuthProvided = v ?? false; _updateAndAutosave(); }),
                _checkbox('Incorporation documents provided', _incDocsProvided, (v) { _incDocsProvided = v ?? false; _updateAndAutosave(); }),
                _checkbox('Payroll enrollment form returned for all employees', _payrollReturned, (v) { _payrollReturned = v ?? false; _updateAndAutosave(); }),
                _checkbox('Previous years T2 returns & last FS provided', _prevYearProvided, (v) { _prevYearProvided = v ?? false; _updateAndAutosave(); }),
                _checkbox('Franchise documents provided (if applicable)', _franchiseProvided, (v) { _franchiseProvided = v ?? false; _updateAndAutosave(); }),
              ]),
            ),
            const SizedBox(height: 16),

            _section(
              context,
              'Company Details',
              Column(children: [
                _text('Company Name', _companyNameCtrl),
                const SizedBox(height: 12),
                _text('Business Number', _businessNumberCtrl, inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9A-Za-z-]'))], maxLength: 20),
                const SizedBox(height: 12),
                _text('Registered Address', _registeredAddressCtrl, maxLines: 2),
                const SizedBox(height: 12),
                _dateField(context, 'Incorporation Date', _incorporationDate, (d) { _incorporationDate = d; _updateAndAutosave(); }),
                const SizedBox(height: 12),
                _checkbox('Is the corporation inactive?', _isInactive, (v) { _isInactive = v ?? false; _updateAndAutosave(); }),
                const SizedBox(height: 12),
                _text('Principal Activity', _principalActivityCtrl),
                const SizedBox(height: 12),
                _text('Principal Activity Percentage', _principalActivityPctCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly], suffixText: '%'),
                const SizedBox(height: 12),
                _text('Director – Last Name & First Name', _directorFullNameCtrl),
                const SizedBox(height: 12),
                _text('Authorized Signing officer – Full Name & Position', _signingOfficerCtrl),
                const SizedBox(height: 12),
                _text('Phone no. of Authorized Signing officer', _signingOfficerPhoneCtrl, keyboardType: TextInputType.phone),
                const SizedBox(height: 12),
                _text('Total No. of Shares issued', _totalSharesIssuedCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly]),
                const SizedBox(height: 12),
                _text('Total amount of Shares', _totalAmountOfSharesCtrl, keyboardType: const TextInputType.numberWithOptions(decimal: true)),
              ]),
            ),
            const SizedBox(height: 16),

            _section(
              context,
              'Shareholders',
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Share Holder 1', style: TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                _text('Name', _sh1NameCtrl),
                const SizedBox(height: 8),
                _text('Percentage of Common Shares', _sh1CommonPctCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly], suffixText: '%'),
                const SizedBox(height: 8),
                _text('Percentage of Preference Shares', _sh1PrefPctCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly], suffixText: '%'),
                const SizedBox(height: 8),
                _text('SIN / BN', _sh1SinBnCtrl),
                const SizedBox(height: 16),
                const Text('Share Holder 2', style: TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                _text('Name', _sh2NameCtrl),
                const SizedBox(height: 8),
                _text('Percentage of Common Shares', _sh2CommonPctCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly], suffixText: '%'),
                const SizedBox(height: 8),
                _text('Percentage of Preference Shares', _sh2PrefPctCtrl, keyboardType: TextInputType.number, inputFormatters: [FilteringTextInputFormatter.digitsOnly], suffixText: '%'),
                const SizedBox(height: 8),
                _text('SIN / BN', _sh2SinBnCtrl),
              ]),
            ),

            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _submit,
                icon: const Icon(Icons.check),
                label: const Text('Submit'),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _section(BuildContext context, String title, Widget child) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        child,
      ]),
    );
  }

  Widget _text(String label, TextEditingController c,
      {TextInputType? keyboardType,
      List<TextInputFormatter>? inputFormatters,
      String? suffixText,
      int maxLines = 1,
      int? maxLength}) {
    return TextFormField(
      controller: c,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      maxLines: maxLines,
      maxLength: maxLength,
      onChanged: (_) => _updateAndAutosave(),
      decoration: InputDecoration(
        labelText: label,
        suffixText: suffixText,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
      ),
    );
  }

  Widget _checkbox(String label, bool value, ValueChanged<bool?> onChanged) {
    return Row(children: [
      Checkbox(value: value, onChanged: (v) { onChanged(v); }),
      Expanded(child: Text(label)),
    ]);
  }

  Widget _dateField(BuildContext context, String label, DateTime? date, ValueChanged<DateTime?> onChanged) {
    return InkWell(
      onTap: () async {
        final picked = await showDatePicker(
          context: context,
          initialDate: date ?? DateTime.now(),
          firstDate: DateTime(1900),
          lastDate: DateTime.now().add(const Duration(days: 3650)),
        );
        onChanged(picked);
      },
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
        ),
        child: Text(date != null
            ? '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}'
            : 'Select Date',
        ),
      ),
    );
  }
}
