import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../data/models/t1_form_models_simple.dart';

class T1Questionnaire1Step extends StatefulWidget {
  final T1FormData formData;
  final Function(T1FormData) onFormDataChanged;
  final VoidCallback onPrevious;
  final VoidCallback onNext;

  const T1Questionnaire1Step({
    super.key,
    required this.formData,
    required this.onFormDataChanged,
    required this.onPrevious,
    required this.onNext,
  });

  @override
  State<T1Questionnaire1Step> createState() => _T1Questionnaire1StepState();
}

class _T1Questionnaire1StepState extends State<T1Questionnaire1Step> {
  late T1FormData _formData;

  @override
  void initState() {
    super.initState();
    _formData = widget.formData;
  }

  @override
  void didUpdateWidget(T1Questionnaire1Step oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.formData != widget.formData) {
      _formData = widget.formData;
    }
  }

  void _updateFormData(T1FormData newData) {
    setState(() {
      _formData = newData;
    });
    widget.onFormDataChanged(_formData);
  }

  @override
  Widget build(BuildContext context) {
    return ResponsiveContainer(
      padding: EdgeInsets.all(Responsive.responsive(
        context: context,
        mobile: AppDimensions.spacingMd,
        tablet: AppDimensions.spacingLg,
        desktop: AppDimensions.spacingXl,
      )),
      child: SingleChildScrollView(
        physics: const SmoothBouncingScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            _buildHeader(),
            const SizedBox(height: 24),

            // Questions 1-3 (Unchanged)
            _buildForeignPropertySection(),
            const SizedBox(height: 16),

            _buildMedicalExpensesSection(),
            const SizedBox(height: 16),

            _buildCharitableDonationsSection(),
            const SizedBox(height: 16),

            // Question 4: Moving Expenses (Simplified - Only Yes/No)
            _buildMovingExpensesSection(),
            const SizedBox(height: 16),

            // Question 5: Self Employment (Simplified - Yes/No + Checkboxes)
            _buildSelfEmploymentSection(),
            const SizedBox(height: 24),

            // Questions 6-18 continue...
            _buildFirstHomeBuyerSection(),
            const SizedBox(height: 16),

            _buildPropertySaleLongTermSection(),
            const SizedBox(height: 16),

            _buildPropertySaleShortTermSection(),
            const SizedBox(height: 16),

            _buildWorkFromHomeSection(),
            const SizedBox(height: 16),

            _buildStudentSection(),
            const SizedBox(height: 16),

            _buildUnionMemberSection(),
            const SizedBox(height: 16),

            _buildDaycareExpensesSection(),
            const SizedBox(height: 16),

            _buildFirstTimeFilerSection(),
            const SizedBox(height: 16),

            _buildOtherIncomeSection(),
            const SizedBox(height: 16),

            _buildProfessionalDuesSection(),
            const SizedBox(height: 16),

            _buildRrspFhsaSection(),
            const SizedBox(height: 16),

            _buildChildArtSportSection(),
            const SizedBox(height: 16),

            _buildProvinceFilerSection(),
            const SizedBox(height: 32),

            // Navigation Buttons
            _buildNavigationButtons(),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Questionnaire',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Please answer the following questions. Detailed information will be collected in additional steps if applicable.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppColors.grey600,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required Widget child,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Widget _buildRadioQuestion({
    required String question,
    required bool? value,
    required Function(bool?) onChanged,
    Widget? conditionalWidget,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (question.isNotEmpty) ...[
          Text(
            question,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
        ],
        Row(
          children: [
            Radio<bool>(
              value: true,
              groupValue: value,
              onChanged: onChanged,
            ),
            const Text('Yes'),
            const SizedBox(width: 24),
            Radio<bool>(
              value: false,
              groupValue: value,
              onChanged: onChanged,
            ),
            const Text('No'),
          ],
        ),
        if (conditionalWidget != null && value == true) ...[
          const SizedBox(height: 16),
          conditionalWidget,
        ],
      ],
    );
  }

  Widget _buildTextField({
    required String label,
    String? initialValue,
    TextInputType? keyboardType,
    List<TextInputFormatter>? inputFormatters,
    int? maxLines,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      initialValue: initialValue,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      maxLines: maxLines,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
    );
  }

  Widget _buildDateField({
    required String label,
    DateTime? date,
    required Function(DateTime?) onChanged,
  }) {
    return InkWell(
      onTap: () async {
        final pickedDate = await showDatePicker(
          context: context,
          initialDate: date ?? DateTime.now(),
          firstDate: DateTime(1900),
          lastDate: DateTime(2030),
        );
        onChanged(pickedDate);
      },
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          ),
        ),
        child: Text(
          date != null ? '${date.day}/${date.month}/${date.year}' : 'Select Date',
          style: date != null ? null : TextStyle(color: AppColors.grey500),
        ),
      ),
    );
  }

  Widget _buildForeignPropertySection() {
    return _buildSection(
      title: '1. Did taxpayer own specified foreign property at any time in 2023 with a total cost of more than CAN\$100,000?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasForeignProperty,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasForeignProperty: value));
        },
        conditionalWidget: _formData.hasForeignProperty == true
            ? _buildForeignPropertyTable()
            : null,
      ),
    );
  }

  Widget _buildForeignPropertyTable() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Foreign Property Details',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).brightness == Brightness.dark
                ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
                : AppColors.grey50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Theme.of(context).dividerColor),
          ),
          child: Column(
            children: [
              _buildTextField(
                label: 'Investment Details',
                onChanged: (value) {},
              ),
              const SizedBox(height: 12),
              _buildTextField(
                label: 'Gross Income',
                keyboardType: TextInputType.number,
                onChanged: (value) {},
              ),
              const SizedBox(height: 12),
              _buildTextField(
                label: 'Country',
                onChanged: (value) {},
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.add),
                label: const Text('Add Row'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMedicalExpensesSection() {
    return _buildSection(
      title: '2. Do you have any Medical Expenses?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasMedicalExpenses,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasMedicalExpenses: value));
        },
        conditionalWidget: _formData.hasMedicalExpenses == true
            ? _buildMedicalExpensesTable()
            : null,
      ),
    );
  }

  Widget _buildMedicalExpensesTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildDateField(
            label: 'Payment Date',
            date: null,
            onChanged: (date) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Patient Name',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildCharitableDonationsSection() {
    return _buildSection(
      title: '3. Do you have any Charitable Donations?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasCharitableDonations,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasCharitableDonations: value));
        },
        conditionalWidget: _formData.hasCharitableDonations == true
            ? _buildCharitableDonationsTable()
            : null,
      ),
    );
  }

  Widget _buildCharitableDonationsTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Organization Name',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildMovingExpensesSection() {
    return _buildSection(
      title: '4. If your province or territory of residence changed in 2023, do you have any moving expenses?',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildRadioQuestion(
            question: '',
            value: _formData.hasMovingExpenses,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(hasMovingExpenses: value));
            },
          ),
          if (_formData.hasMovingExpenses == true) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.primary.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: AppColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Detailed moving expense information will be collected in Questionnaire 2',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSelfEmploymentSection() {
    return _buildSection(
      title: '5. Are you Self Employed?',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildRadioQuestion(
            question: '',
            value: _formData.isSelfEmployed,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                isSelfEmployed: value,
                selfEmployment: value == true ? const T1SelfEmployment() : null,
              ));
            },
          ),
          if (_formData.isSelfEmployed == true) ...[
            const SizedBox(height: 16),
            Text(
              'Select all that apply:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            CheckboxListTile(
              title: const Text('Uber/Skip/DoorDash'),
              value: _formData.selfEmployment?.businessTypes.contains('uber') ?? false,
              onChanged: (value) {
                final currentTypes = List<String>.from(_formData.selfEmployment?.businessTypes ?? []);
                if (value == true) {
                  if (!currentTypes.contains('uber')) currentTypes.add('uber');
                } else {
                  currentTypes.remove('uber');
                }
                _updateFormData(_formData.copyWith(
                  selfEmployment: T1SelfEmployment(businessTypes: currentTypes),
                ));
              },
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
            ),
            CheckboxListTile(
              title: const Text('General Business'),
              value: _formData.selfEmployment?.businessTypes.contains('general') ?? false,
              onChanged: (value) {
                final currentTypes = List<String>.from(_formData.selfEmployment?.businessTypes ?? []);
                if (value == true) {
                  if (!currentTypes.contains('general')) currentTypes.add('general');
                } else {
                  currentTypes.remove('general');
                }
                _updateFormData(_formData.copyWith(
                  selfEmployment: T1SelfEmployment(businessTypes: currentTypes),
                ));
              },
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
            ),
            CheckboxListTile(
              title: const Text('Rental Income'),
              value: _formData.selfEmployment?.businessTypes.contains('rental') ?? false,
              onChanged: (value) {
                final currentTypes = List<String>.from(_formData.selfEmployment?.businessTypes ?? []);
                if (value == true) {
                  if (!currentTypes.contains('rental')) currentTypes.add('rental');
                } else {
                  currentTypes.remove('rental');
                }
                _updateFormData(_formData.copyWith(
                  selfEmployment: T1SelfEmployment(businessTypes: currentTypes),
                ));
              },
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.primary.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: AppColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Detailed income and expense information will be collected in Questionnaire 2',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  // Remaining sections (6-18) - With original sub-forms
  Widget _buildFirstHomeBuyerSection() {
    return _buildSection(
      title: '6. Did you buy your FIRST HOME in the Tax Year?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.isFirstHomeBuyer,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(isFirstHomeBuyer: value));
        },
      ),
    );
  }

  Widget _buildPropertySaleLongTermSection() {
    return _buildSection(
      title: '7. Did you sell any Residential Property which you hold more than 365 days last year? How much capital gain you earned?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.soldPropertyLongTerm,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(soldPropertyLongTerm: value));
        },
        conditionalWidget: _formData.soldPropertyLongTerm == true
            ? _buildPropertySaleDetails(isLongTerm: true)
            : null,
      ),
    );
  }

  Widget _buildPropertySaleShortTermSection() {
    return _buildSection(
      title: '8. Did you sell any Residential Property which you hold less than 365 days last year? FLIP PROPERTY',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.soldPropertyShortTerm,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(soldPropertyShortTerm: value));
        },
        conditionalWidget: _formData.soldPropertyShortTerm == true
            ? _buildPropertySaleDetails(isLongTerm: false)
            : null,
      ),
    );
  }

  Widget _buildPropertySaleDetails({required bool isLongTerm}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Property Address',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildDateField(
            label: 'Purchase Date',
            date: null,
            onChanged: (date) {},
          ),
          const SizedBox(height: 12),
          _buildDateField(
            label: 'Sell Date',
            date: null,
            onChanged: (date) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Purchase & Sell Expenses',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          if (isLongTerm) ...[
            const SizedBox(height: 12),
            _buildTextField(
              label: 'Capital Gain Earned',
              keyboardType: TextInputType.number,
              onChanged: (value) {},
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildWorkFromHomeSection() {
    return _buildSection(
      title: '9. Did you have any work from home expense in the Tax year? Detailed method, T2200 is required from your employer.',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasWorkFromHomeExpense,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasWorkFromHomeExpense: value));
        },
        conditionalWidget: _formData.hasWorkFromHomeExpense == true
            ? _buildWorkFromHomeDetails()
            : null,
      ),
    );
  }

  Widget _buildWorkFromHomeDetails() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Total House Area (Sq.Ft.)',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Work Area (Sq.Ft.)',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Rent/Mortgage Expense',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Utilities Expense',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
        ],
      ),
    );
  }

  Widget _buildStudentSection() {
    return _buildSection(
      title: '10. Were you a student last year? If yes then we would need T2202A form from your educational institution.',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.wasStudentLastYear,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(wasStudentLastYear: value));
        },
      ),
    );
  }

  Widget _buildUnionMemberSection() {
    return _buildSection(
      title: '11. Are you a member of any union? If yes then, do you have any union dues?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.isUnionMember,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(isUnionMember: value));
        },
        conditionalWidget: _formData.isUnionMember == true
            ? _buildUnionDuesTable()
            : null,
      ),
    );
  }

  Widget _buildUnionDuesTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Institution Name',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildDaycareExpensesSection() {
    return _buildSection(
      title: '12. Do you have Day care expenses for your child?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasDaycareExpenses,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasDaycareExpenses: value));
        },
        conditionalWidget: _formData.hasDaycareExpenses == true
            ? _buildDaycareExpensesTable()
            : null,
      ),
    );
  }

  Widget _buildDaycareExpensesTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Childcare Provider',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildFirstTimeFilerSection() {
    return _buildSection(
      title: '13. Are you a first time filer? If Yes, then please provide the following details.',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.isFirstTimeFiler,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(isFirstTimeFiler: value));
        },
        conditionalWidget: _formData.isFirstTimeFiler == true
            ? _buildFirstTimeFilerDetails()
            : null,
      ),
    );
  }

  Widget _buildFirstTimeFilerDetails() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildDateField(
            label: 'Date of Landing (Individual)',
            date: null,
            onChanged: (date) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Income Outside Canada (CAD)',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
        ],
      ),
    );
  }

  Widget _buildOtherIncomeSection() {
    return _buildSection(
      title: '14. Do you have any other Income in 2023 which does not have T Slips?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasOtherIncome,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasOtherIncome: value));
        },
        conditionalWidget: _formData.hasOtherIncome == true
            ? _buildTextField(
                label: 'Describe the income and amount',
                maxLines: 3,
                initialValue: _formData.otherIncomeDescription,
                onChanged: (value) {
                  _updateFormData(_formData.copyWith(otherIncomeDescription: value));
                },
              )
            : null,
      ),
    );
  }

  Widget _buildProfessionalDuesSection() {
    return _buildSection(
      title: '15. Do you have any Professional Dues, License Fees, Exam fees which you have paid from your pocket for last year?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasProfessionalDues,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasProfessionalDues: value));
        },
        conditionalWidget: _formData.hasProfessionalDues == true
            ? _buildProfessionalDuesTable()
            : null,
      ),
    );
  }

  Widget _buildProfessionalDuesTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Name',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Organization',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildRrspFhsaSection() {
    return _buildSection(
      title: '16. Do you have any RRSP/FHSA Investment? If yes, please provide the slips along with your T Slips.',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasRrspFhsaInvestment,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasRrspFhsaInvestment: value));
        },
      ),
    );
  }

  Widget _buildChildArtSportSection() {
    return _buildSection(
      title: '17. Children\'s Art & Sport Tax Credit - Do you have any receipts for your child\'s Sport/fitness & Art for 2023?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.hasChildArtSportCredit,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(hasChildArtSportCredit: value));
        },
        conditionalWidget: _formData.hasChildArtSportCredit == true
            ? _buildChildArtSportTable()
            : null,
      ),
    );
  }

  Widget _buildChildArtSportTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Institute Name',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Description',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildProvinceFilerSection() {
    return _buildSection(
      title: '18. FOR ONTARIO/ALBERTA/QUEBEC FILER ONLY - Please Provide below details for 2023',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.isProvinceFiler,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(isProvinceFiler: value));
        },
        conditionalWidget: _formData.isProvinceFiler == true
            ? _buildProvinceFilerTable()
            : null,
      ),
    );
  }

  Widget _buildProvinceFilerTable() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          Text(
            'Quebec Filer - Provide RL-31',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 8),
          _buildTextField(
            label: 'Rent or Property Tax',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Property Address',
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {},
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationButtons() {
    final hasMovingExpenses = _formData.hasMovingExpenses ?? false;
    final isSelfEmployed = _formData.isSelfEmployed ?? false;
    final needsAdditionalSteps = hasMovingExpenses || isSelfEmployed;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ElevatedButton(
          onPressed: widget.onNext,
          child: Text(needsAdditionalSteps ? 'Next' : 'Submit Form'),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: widget.onPrevious,
          child: const Text('Previous: Personal Info'),
        ),
      ],
    );
  }
}
