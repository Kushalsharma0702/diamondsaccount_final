import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../data/models/t1_form_models_simple.dart';

class T1QuestionnaireStep extends StatefulWidget {
  final T1FormData formData;
  final Function(T1FormData) onFormDataChanged;
  final VoidCallback onPrevious;
  final VoidCallback onSubmit;

  const T1QuestionnaireStep({
    super.key,
    required this.formData,
    required this.onFormDataChanged,
    required this.onPrevious,
    required this.onSubmit,
  });

  @override
  State<T1QuestionnaireStep> createState() => _T1QuestionnaireStepState();
}

class _T1QuestionnaireStepState extends State<T1QuestionnaireStep> {
  late T1FormData _formData;

  @override
  void initState() {
    super.initState();
    _formData = widget.formData;
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

          // Question 1: Foreign Property
          _buildForeignPropertySection(),
          const SizedBox(height: 24),

          // Question 2: Medical Expenses
          _buildMedicalExpensesSection(),
          const SizedBox(height: 24),

          // Question 3: Charitable Donations
          _buildCharitableDonationsSection(),
          const SizedBox(height: 24),

          // Question 4: Moving Expenses
          _buildMovingExpensesSection(),
          const SizedBox(height: 24),

          // Question 5: Self Employment
          _buildSelfEmploymentSection(),
          const SizedBox(height: 24),

          // Question 6: First Home Buyer
          _buildFirstHomeBuyerSection(),
          const SizedBox(height: 24),

          // Question 7: Property Sale (Long-term)
          _buildPropertySaleLongTermSection(),
          const SizedBox(height: 24),

          // Question 8: Property Sale (Short-term)
          _buildPropertySaleShortTermSection(),
          const SizedBox(height: 24),

          // Question 9: Work From Home
          _buildWorkFromHomeSection(),
          const SizedBox(height: 24),

          // Question 10: Student
          _buildStudentSection(),
          const SizedBox(height: 24),

          // Question 11: Union Member
          _buildUnionMemberSection(),
          const SizedBox(height: 24),

          // Question 12: Daycare Expenses
          _buildDaycareExpensesSection(),
          const SizedBox(height: 24),

          // Question 13: First Time Filer
          _buildFirstTimeFilerSection(),
          const SizedBox(height: 24),

          // Question 14: Other Income
          _buildOtherIncomeSection(),
          const SizedBox(height: 24),

          // Question 15: Professional Dues
          _buildProfessionalDuesSection(),
          const SizedBox(height: 24),

          // Question 16: RRSP/FHSA
          _buildRrspFhsaSection(),
          const SizedBox(height: 24),

          // Question 17: Child Art/Sport
          _buildChildArtSportSection(),
          const SizedBox(height: 24),

          // Question 18: Province Filer
          _buildProvinceFilerSection(),
          const SizedBox(height: 32),

          // Navigation Buttons
          Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ElevatedButton(
                onPressed: widget.onSubmit,
                child: const Text('Submit Form'),
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: widget.onPrevious,
                child: const Text('Previous: Personal Info'),
              ),
            ],
          ),

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
            'Please answer all applicable questions to ensure you don\'t miss any deductions or credits.',
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
    Color? backgroundColor,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: backgroundColor ?? Theme.of(context).cardColor,
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
        Text(
          question,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
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
                onChanged: (value) {
                  // Update foreign property
                },
              ),
              const SizedBox(height: 12),
              _buildTextField(
                label: 'Gross Income',
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  // Update foreign property
                },
              ),
              const SizedBox(height: 12),
              _buildTextField(
                label: 'Country',
                onChanged: (value) {
                  // Update foreign property
                },
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () {
                  // Add foreign property row
                },
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
            onChanged: (date) {
              // Update medical expense
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Patient Name',
            onChanged: (value) {
              // Update medical expense
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update medical expense
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add medical expense row
            },
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
            onChanged: (value) {
              // Update charitable donation
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update charitable donation
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add charitable donation row
            },
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }

  Widget _buildMovingExpensesSection() {
    return _buildSection(
      title: '4. If your province or territory of residence changed in 2023, enter the date of your move. Do you have any moving expenses?',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildDateField(
            label: 'Date of move (if applicable)',
            date: null,
            onChanged: (date) {
              // Update moving expenses
            },
          ),
          const SizedBox(height: 16),
          _buildRadioQuestion(
            question: 'Do you have moving expenses?',
            value: _formData.hasMovingExpenses,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(hasMovingExpenses: value));
            },
            conditionalWidget: _formData.hasMovingExpenses == true
                ? _buildMovingExpensesDetails()
                : null,
          ),
        ],
      ),
    );
  }

  Widget _buildMovingExpensesDetails() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Moving Expense Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '(New address should be at least 40 KM closer to office than old address to claim this)',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Old Address',
            onChanged: (value) {
              // Update moving expenses
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'New Address',
            onChanged: (value) {
              // Update moving expenses
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Air Ticket Cost',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update moving expenses
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Moving Cost',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update moving expenses
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSelfEmploymentSection() {
    return _buildSection(
      title: '5. Are you Self Employed?',
      child: _buildRadioQuestion(
        question: '',
        value: _formData.isSelfEmployed,
        onChanged: (value) {
          _updateFormData(_formData.copyWith(isSelfEmployed: value));
        },
        conditionalWidget: _formData.isSelfEmployed == true
            ? _buildSelfEmploymentDetails()
            : null,
      ),
    );
  }

  Widget _buildSelfEmploymentDetails() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Type of Self-Employment:',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Column(
            children: [
              Row(
                children: [
                  Radio<String>(
                    value: 'uber',
                    groupValue: ((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
                        ? _formData.selfEmployment!.businessTypes.first
                        : ''),
                    onChanged: (value) {
                      _updateFormData(_formData.copyWith(
                        selfEmployment: T1SelfEmployment(businessTypes: value == null || value.isEmpty ? [] : [value]),
                      ));
                    },
                  ),
                  const Expanded(child: Text('Uber/Skip/Doordash')),
                ],
              ),
              Row(
                children: [
                  Radio<String>(
                    value: 'general',
                    groupValue: ((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
                        ? _formData.selfEmployment!.businessTypes.first
                        : ''),
                    onChanged: (value) {
                      _updateFormData(_formData.copyWith(
                        selfEmployment: T1SelfEmployment(businessTypes: value == null || value.isEmpty ? [] : [value]),
                      ));
                    },
                  ),
                  const Expanded(child: Text('General Business')),
                ],
              ),
            ],
          ),
          Row(
            children: [
              Radio<String>(
                value: 'rental',
                groupValue: ((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
                    ? _formData.selfEmployment!.businessTypes.first
                    : ''),
                onChanged: (value) {
                  _updateFormData(_formData.copyWith(
                    selfEmployment: T1SelfEmployment(businessTypes: value == null || value.isEmpty ? [] : [value]),
                  ));
                },
              ),
              const Text('Rental Income'),
            ],
          ),
          // Add specific business type details based on selection
          if (((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
              ? _formData.selfEmployment!.businessTypes.first
              : '') == 'uber') ...[
            const SizedBox(height: 16),
            _buildUberBusinessDetails(),
          ] else if (((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
              ? _formData.selfEmployment!.businessTypes.first
              : '') == 'general') ...[
            const SizedBox(height: 16),
            _buildGeneralBusinessDetails(),
          ] else if (((_formData.selfEmployment?.businessTypes.isNotEmpty ?? false)
              ? _formData.selfEmployment!.businessTypes.first
              : '') == 'rental') ...[
            const SizedBox(height: 16),
            _buildRentalIncomeDetails(),
          ],
        ],
      ),
    );
  }

  Widget _buildUberBusinessDetails() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Uber/Skip/Doordash Income & Expenses',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Statement Details',
          onChanged: (value) {
            // Update uber business
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Basic Income',
          keyboardType: TextInputType.number,
          onChanged: (value) {
            // Update uber business
          },
        ),
      ],
    );
  }

  Widget _buildGeneralBusinessDetails() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'General Business Income & Expenses',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Client Name',
          onChanged: (value) {
            // Update general business
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Business Name',
          onChanged: (value) {
            // Update general business
          },
        ),
      ],
    );
  }

  Widget _buildRentalIncomeDetails() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Rental Income & Expenses',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Property Address',
          onChanged: (value) {
            // Update rental income
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          label: 'Gross Rental Income',
          keyboardType: TextInputType.number,
          onChanged: (value) {
            // Update rental income
          },
        ),
      ],
    );
  }

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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Property Address',
            onChanged: (value) {
              // Update property sale
            },
          ),
          const SizedBox(height: 12),
          _buildDateField(
            label: 'Purchase Date',
            date: null,
            onChanged: (date) {
              // Update property sale
            },
          ),
          const SizedBox(height: 12),
          _buildDateField(
            label: 'Sell Date',
            date: null,
            onChanged: (date) {
              // Update property sale
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Purchase & Sell Expenses',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update property sale
            },
          ),
          if (isLongTerm) ...[
            const SizedBox(height: 12),
            _buildTextField(
              label: 'Capital Gain Earned',
              keyboardType: TextInputType.number,
              onChanged: (value) {
                // Update property sale
              },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Total House Area (Sq.Ft.)',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update work from home
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Work Area (Sq.Ft.)',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update work from home
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Rent/Mortgage Expense',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update work from home
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Utilities Expense',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update work from home
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Institution Name',
            onChanged: (value) {
              // Update union dues
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update union dues
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add union dues row
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Childcare Provider',
            onChanged: (value) {
              // Update daycare expenses
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update daycare expenses
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add daycare expense row
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildDateField(
            label: 'Date of Landing (Individual)',
            date: null,
            onChanged: (date) {
              // Update first time filer
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Income Outside Canada (CAD)',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update first time filer
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
            _buildTextField(
              label: 'Name',
              onChanged: (value) {
                // Update professional dues
              },
            ),
            const SizedBox(height: 12),
            _buildTextField(
              label: 'Organization',
              onChanged: (value) {
                // Update professional dues
              },
            ),
            const SizedBox(height: 12),
            _buildTextField(
              label: 'Amount',
              keyboardType: TextInputType.number,
              onChanged: (value) {
                // Update professional dues
              },
            ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add professional dues row
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        children: [
          _buildTextField(
            label: 'Institute Name',
            onChanged: (value) {
              // Update child art sport
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Description',
            onChanged: (value) {
              // Update child art sport
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update child art sport
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add child art sport row
            },
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
        color: Theme.of(context).brightness == Brightness.dark ? Theme.of(context).colorScheme.surface.withOpacity(0.7) : AppColors.grey50,
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
            onChanged: (value) {
              // Update province filer
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Property Address',
            onChanged: (value) {
              // Update province filer
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Amount Paid',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Update province filer
            },
          ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              // Add province filer row
            },
            icon: const Icon(Icons.add),
            label: const Text('Add Row'),
          ),
        ],
      ),
    );
  }
}
