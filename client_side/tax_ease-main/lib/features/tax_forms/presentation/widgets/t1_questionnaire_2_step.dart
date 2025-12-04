import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../data/models/t1_form_models_simple.dart';

/// Detail page types for Questionnaire 2 sections
enum T1DetailStepType {
  movingExpenses,
  uberSkipDoordash,
  generalBusiness,
  rentalIncome,
}

class T1Questionnaire2Step extends StatefulWidget {
  final T1DetailStepType stepType;
  final T1FormData formData;
  final Function(T1FormData) onFormDataChanged;
  final VoidCallback onPrevious;
  final VoidCallback onPrimary;
  final String primaryButtonLabel;
  final String? previousStepTitle;

  const T1Questionnaire2Step({
    super.key,
    required this.stepType,
    required this.formData,
    required this.onFormDataChanged,
    required this.onPrevious,
    required this.onPrimary,
    required this.primaryButtonLabel,
    this.previousStepTitle,
  });

  @override
  State<T1Questionnaire2Step> createState() => _T1Questionnaire2StepState();
}

class _T1Questionnaire2StepState extends State<T1Questionnaire2Step> {
  late T1FormData _formData;

  @override
  void initState() {
    super.initState();
    _formData = widget.formData;
  }

  @override
  void didUpdateWidget(T1Questionnaire2Step oldWidget) {
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
    // Build a single detailed section based on the configured step type
    Widget detailSection;
    switch (widget.stepType) {
      case T1DetailStepType.movingExpenses:
        detailSection = _buildMovingExpenseDetails();
        break;
      case T1DetailStepType.uberSkipDoordash:
        detailSection = _buildUberBusinessDetails();
        break;
      case T1DetailStepType.generalBusiness:
        detailSection = _buildGeneralBusinessDetails();
        break;
      case T1DetailStepType.rentalIncome:
        detailSection = _buildRentalIncomeDetails();
        break;
    }

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

            detailSection,
            const SizedBox(height: 24),

            // Navigation Buttons
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ElevatedButton(
                  onPressed: widget.onPrimary,
                  child: Text(widget.primaryButtonLabel),
                ),
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: widget.onPrevious,
                  child: Text(
                    widget.previousStepTitle != null
                        ? 'Previous: ${widget.previousStepTitle}'
                        : 'Previous',
                  ),
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
    String title;
    String? subtitle;

    switch (widget.stepType) {
      case T1DetailStepType.movingExpenses:
        title = 'Moving Expenses';
        subtitle =
            'Provide detailed moving expense information for you and/or your spouse.';
        break;
      case T1DetailStepType.uberSkipDoordash:
        title = 'Uber/Skip/DoorDash Details';
        subtitle =
            'Provide income and expense details for ride-sharing or food delivery.';
        break;
      case T1DetailStepType.generalBusiness:
        title = 'General Business Details';
        subtitle = 'Provide income and expense details for your business.';
        break;
      case T1DetailStepType.rentalIncome:
        title = 'Rental Income Details';
        subtitle = 'Provide income and expense details for your rental properties.';
        break;
    }

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
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 4),
            Text(
              subtitle!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.grey600,
                  ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    String? subtitle,
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
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.grey600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Widget _buildTextField({
    required String label,
    String? initialValue,
    TextInputType? keyboardType,
    List<TextInputFormatter>? inputFormatters,
    String? prefix,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      initialValue: initialValue,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        prefixText: prefix,
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
          firstDate: DateTime(2020),
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

  // ========== MOVING EXPENSE DETAILS ==========
  Widget _buildMovingExpenseDetails() {
    final selectedIndividual = _formData.movingExpenseForIndividual ?? false;
    final selectedSpouse = _formData.movingExpenseForSpouse ?? false;
    final individualExpense = _formData.movingExpenseIndividual ?? const T1MovingExpense();
    final spouseExpense = _formData.movingExpenseSpouse ?? const T1MovingExpense();

    return _buildSection(
      title: 'Moving Expense Details',
      subtitle: 'New address should be at least 40 KM closer to office than old address to claim this',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Selection checkboxes
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            controlAffinity: ListTileControlAffinity.leading,
            title: const Text('Individual'),
            value: selectedIndividual,
            onChanged: (val) {
              _updateFormData(_formData.copyWith(
                movingExpenseForIndividual: val,
                movingExpenseIndividual: (val ?? false)
                    ? (_formData.movingExpenseIndividual ?? const T1MovingExpense())
                    : _formData.movingExpenseIndividual,
              ));
            },
          ),
          if (selectedIndividual) ...[
            _buildMovingExpenseSubform(
              'Individual',
              individualExpense,
              (updated) => _updateFormData(_formData.copyWith(movingExpenseIndividual: updated)),
            ),
            const SizedBox(height: 16),
          ],
          CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            controlAffinity: ListTileControlAffinity.leading,
            title: const Text('Spouse'),
            value: selectedSpouse,
            onChanged: (val) {
              _updateFormData(_formData.copyWith(
                movingExpenseForSpouse: val,
                movingExpenseSpouse: (val ?? false)
                    ? (_formData.movingExpenseSpouse ?? const T1MovingExpense())
                    : _formData.movingExpenseSpouse,
              ));
            },
          ),
          if (selectedSpouse)
            _buildMovingExpenseSubform(
              'Spouse',
              spouseExpense,
              (updated) => _updateFormData(_formData.copyWith(movingExpenseSpouse: updated)),
            ),
        ],
      ),
    );
  }

  Widget _buildMovingExpenseSubform(
    String who,
    T1MovingExpense movingExpense,
    ValueChanged<T1MovingExpense> onChanged,
  ) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$who Sub Form',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Old Address',
            initialValue: movingExpense.oldAddress,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(oldAddress: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'New Address',
            initialValue: movingExpense.newAddress,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(newAddress: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Distance from old address to new office (KM)',
            initialValue: movingExpense.distanceFromOldToNew,
            keyboardType: TextInputType.number,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(distanceFromOldToNew: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Distance from new address to new office (KM)',
            initialValue: movingExpense.distanceFromNewToOffice,
            keyboardType: TextInputType.number,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(distanceFromNewToOffice: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Air ticket cost / Travelling cost',
            initialValue: movingExpense.airTicketCost > 0 ? movingExpense.airTicketCost.toString() : '',
            keyboardType: TextInputType.number,
prefix: '\$ ',
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              onChanged(movingExpense.copyWith(airTicketCost: double.tryParse(value) ?? 0));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Movers and packers',
            initialValue: movingExpense.moversAndPackers > 0 ? movingExpense.moversAndPackers.toString() : '',
            keyboardType: TextInputType.number,
prefix: '\$ ',
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              onChanged(movingExpense.copyWith(moversAndPackers: double.tryParse(value) ?? 0));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Meals and other cost',
            initialValue: movingExpense.mealsAndOtherCost > 0 ? movingExpense.mealsAndOtherCost.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              onChanged(movingExpense.copyWith(mealsAndOtherCost: double.tryParse(value) ?? 0));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Any other cost',
            initialValue: movingExpense.anyOtherCost > 0 ? movingExpense.anyOtherCost.toString() : '',
            keyboardType: TextInputType.number,
prefix: '\$ ',
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              onChanged(movingExpense.copyWith(anyOtherCost: double.tryParse(value) ?? 0));
            },
          ),
          const SizedBox(height: 16),
          _buildDateField(
            label: 'Date of travel from old address to new address',
            date: movingExpense.dateOfTravel,
            onChanged: (date) {
              onChanged(movingExpense.copyWith(dateOfTravel: date));
            },
          ),
          const SizedBox(height: 16),
          _buildDateField(
            label: 'Date of joining the company',
            date: movingExpense.dateOfJoining,
            onChanged: (date) {
              onChanged(movingExpense.copyWith(dateOfJoining: date));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Name of the company',
            initialValue: movingExpense.companyName,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(companyName: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Address of new employer',
            initialValue: movingExpense.newEmployerAddress,
            onChanged: (value) {
              onChanged(movingExpense.copyWith(newEmployerAddress: value));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Gross income earned in this company during tax year after moving (CAD)',
            initialValue: movingExpense.grossIncomeAfterMoving > 0 ? movingExpense.grossIncomeAfterMoving.toString() : '',
            keyboardType: TextInputType.number,
prefix: '\$ ',
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              onChanged(movingExpense.copyWith(grossIncomeAfterMoving: double.tryParse(value) ?? 0));
            },
          ),
        ],
      ),
    );
  }

  // ========== UBER/SKIP/DOORDASH BUSINESS DETAILS ==========
  Widget _buildUberBusinessDetails() {
    final uberBusiness = _formData.selfEmployment?.uberBusiness ?? const T1UberBusiness();

    return _buildSection(
      title: 'Uber/Skip/DoorDash Income & Expenses',
      subtitle: 'Income from ride-sharing or food delivery services',
      child: Column(
        children: [
          _buildTextField(
            label: 'Uber/Skip/Uber Eats statement',
            initialValue: uberBusiness.uberSkipStatement,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(uberSkipStatement: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Business (HST) number',
            initialValue: uberBusiness.businessHstNumber,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(businessHstNumber: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'HST access code',
            initialValue: uberBusiness.hstAccessCode,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(hstAccessCode: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'HST filing period',
            initialValue: uberBusiness.hstFillingPeriod,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(hstFillingPeriod: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Income',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Income',
            initialValue: uberBusiness.income > 0 ? uberBusiness.income.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(income: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Total KM travelled as per statement',
            initialValue: uberBusiness.totalKmForUberSkip > 0 ? uberBusiness.totalKmForUberSkip.toString() : '',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(totalKmForUberSkip: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Total official KM driven',
            initialValue: uberBusiness.totalOfficialKmDriven > 0 ? uberBusiness.totalOfficialKmDriven.toString() : '',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(totalOfficialKmDriven: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Total KM driven entire year',
            initialValue: uberBusiness.totalKmDrivenEntireYear > 0 ? uberBusiness.totalKmDrivenEntireYear.toString() : '',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(totalKmDrivenEntireYear: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Expenses',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Business number / vehicle registration expense',
            initialValue: uberBusiness.businessNumberVehicleRegistration > 0 ? uberBusiness.businessNumberVehicleRegistration.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(businessNumberVehicleRegistration: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Meals',
            initialValue: uberBusiness.meals > 0 ? uberBusiness.meals.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(meals: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Telephone',
            initialValue: uberBusiness.telephone > 0 ? uberBusiness.telephone.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(telephone: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Parking fees',
            initialValue: uberBusiness.parkingFees > 0 ? uberBusiness.parkingFees.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(parkingFees: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Cleaning expenses',
            initialValue: uberBusiness.cleaningExpenses > 0 ? uberBusiness.cleaningExpenses.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(cleaningExpenses: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Safety inspection',
            initialValue: uberBusiness.safetyInspection > 0 ? uberBusiness.safetyInspection.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(safetyInspection: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Winter tire change',
            initialValue: uberBusiness.winterTireChange > 0 ? uberBusiness.winterTireChange.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(winterTireChange: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Oil change and other maintenance',
            initialValue: uberBusiness.oilChangeAndMaintenance > 0 ? uberBusiness.oilChangeAndMaintenance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(oilChangeAndMaintenance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Depreciation',
            initialValue: uberBusiness.depreciation > 0 ? uberBusiness.depreciation.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(depreciation: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Insurance on vehicle',
            initialValue: uberBusiness.insuranceOnVehicle > 0 ? uberBusiness.insuranceOnVehicle.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(insuranceOnVehicle: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Gas',
            initialValue: uberBusiness.gas > 0 ? uberBusiness.gas.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(gas: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Financing cost - interest paid on installment',
            initialValue: uberBusiness.financingCostInterest > 0 ? uberBusiness.financingCostInterest.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(financingCostInterest: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Lease cost (if car is on lease)',
            initialValue: uberBusiness.leaseCost > 0 ? uberBusiness.leaseCost.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(leaseCost: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Any other Uber/Skip related expense',
            initialValue: uberBusiness.otherExpense > 0 ? uberBusiness.otherExpense.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  uberBusiness: uberBusiness.copyWith(otherExpense: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
        ],
      ),
    );
  }

  // ========== GENERAL BUSINESS DETAILS ==========
  Widget _buildGeneralBusinessDetails() {
    final generalBusiness = _formData.selfEmployment?.generalBusiness ?? const T1GeneralBusiness();

    return _buildSection(
      title: 'General Business Income & Expenses',
      subtitle: 'Self-employment or freelance business income',
      child: Column(
        children: [
          _buildTextField(
            label: 'Client Name',
            initialValue: generalBusiness.clientName,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(clientName: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Business Name',
            initialValue: generalBusiness.businessName,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(businessName: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Income',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Sales, commissions, or fees (including HST)',
            initialValue: generalBusiness.salesCommissionsFees > 0 ? generalBusiness.salesCommissionsFees.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(salesCommissionsFees: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Minus HST collected',
            initialValue: generalBusiness.minusHstCollected > 0 ? generalBusiness.minusHstCollected.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(minusHstCollected: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Gross income',
            initialValue: generalBusiness.grossIncome > 0 ? generalBusiness.grossIncome.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(grossIncome: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Costs of goods sold',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Opening inventory',
            initialValue: generalBusiness.openingInventory > 0 ? generalBusiness.openingInventory.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(openingInventory: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Purchases during the year',
            initialValue: generalBusiness.purchasesDuringYear > 0 ? generalBusiness.purchasesDuringYear.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(purchasesDuringYear: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Subcontracts',
            initialValue: generalBusiness.subcontracts > 0 ? generalBusiness.subcontracts.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(subcontracts: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Direct wage costs',
            initialValue: generalBusiness.directWageCosts > 0 ? generalBusiness.directWageCosts.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(directWageCosts: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other costs',
            initialValue: generalBusiness.otherCosts > 0 ? generalBusiness.otherCosts.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(otherCosts: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Minus: purchase returns',
            initialValue: generalBusiness.purchaseReturns > 0 ? generalBusiness.purchaseReturns.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(purchaseReturns: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Business Expenses',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Advertising',
            initialValue: generalBusiness.advertising > 0 ? generalBusiness.advertising.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(advertising: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Meals & entertainment',
            initialValue: generalBusiness.mealsEntertainment > 0 ? generalBusiness.mealsEntertainment.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(mealsEntertainment: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Bad debts',
            initialValue: generalBusiness.badDebts > 0 ? generalBusiness.badDebts.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(badDebts: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Insurance',
            initialValue: generalBusiness.insurance > 0 ? generalBusiness.insurance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(insurance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Interest',
            initialValue: generalBusiness.interest > 0 ? generalBusiness.interest.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(interest: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Fees, licenses, dues',
            initialValue: generalBusiness.feesLicensesDues > 0 ? generalBusiness.feesLicensesDues.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(feesLicensesDues: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Office expenses',
            initialValue: generalBusiness.officeExpenses > 0 ? generalBusiness.officeExpenses.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(officeExpenses: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Supplies',
            initialValue: generalBusiness.supplies > 0 ? generalBusiness.supplies.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(supplies: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Legal, accounting, and professional fees',
            initialValue: generalBusiness.legalAccountingFees > 0 ? generalBusiness.legalAccountingFees.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(legalAccountingFees: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Management & administration',
            initialValue: generalBusiness.managementAdministration > 0 ? generalBusiness.managementAdministration.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(managementAdministration: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Office rent',
            initialValue: generalBusiness.officeRent > 0 ? generalBusiness.officeRent.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(officeRent: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Maintenance & repairs',
            initialValue: generalBusiness.maintenanceRepairs > 0 ? generalBusiness.maintenanceRepairs.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(maintenanceRepairs: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Salaries, wages, benefits',
            initialValue: generalBusiness.salariesWagesBenefits > 0 ? generalBusiness.salariesWagesBenefits.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(salariesWagesBenefits: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Property tax',
            initialValue: generalBusiness.propertyTax > 0 ? generalBusiness.propertyTax.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(propertyTax: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Travel',
            initialValue: generalBusiness.travel > 0 ? generalBusiness.travel.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(travel: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Telephone and utilities',
            initialValue: generalBusiness.telephoneUtilities > 0 ? generalBusiness.telephoneUtilities.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(telephoneUtilities: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Fuel costs (non-motor vehicle)',
            initialValue: generalBusiness.fuelCosts > 0 ? generalBusiness.fuelCosts.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(fuelCosts: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Delivery, freight, express',
            initialValue: generalBusiness.deliveryFreightExpress > 0 ? generalBusiness.deliveryFreightExpress.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(deliveryFreightExpress: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expense 1',
            initialValue: generalBusiness.otherExpense1 > 0 ? generalBusiness.otherExpense1.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(otherExpense1: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expense 2',
            initialValue: generalBusiness.otherExpense2 > 0 ? generalBusiness.otherExpense2.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(otherExpense2: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expense 3',
            initialValue: generalBusiness.otherExpense3 > 0 ? generalBusiness.otherExpense3.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(otherExpense3: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Office-in-house expenses',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Area of home used for business',
            initialValue: generalBusiness.areaOfHomeForBusiness,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(areaOfHomeForBusiness: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Total area of home',
            initialValue: generalBusiness.totalAreaOfHome,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(totalAreaOfHome: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Heat',
            initialValue: generalBusiness.heat > 0 ? generalBusiness.heat.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(heat: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Electricity',
            initialValue: generalBusiness.electricity > 0 ? generalBusiness.electricity.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(electricity: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Insurance',
            initialValue: generalBusiness.houseInsurance > 0 ? generalBusiness.houseInsurance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(houseInsurance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Maintenance & repairs',
            initialValue: generalBusiness.homeMaintenance > 0 ? generalBusiness.homeMaintenance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(homeMaintenance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Mortgage interest',
            initialValue: generalBusiness.mortgageInterest > 0 ? generalBusiness.mortgageInterest.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(mortgageInterest: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Property taxes',
            initialValue: generalBusiness.propertyTaxes > 0 ? generalBusiness.propertyTaxes.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(propertyTaxes: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'House rent',
            initialValue: generalBusiness.houseRent > 0 ? generalBusiness.houseRent.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(houseRent: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expense 1',
            initialValue: generalBusiness.homeOtherExpense1 > 0 ? generalBusiness.homeOtherExpense1.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(homeOtherExpense1: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expense 2',
            initialValue: generalBusiness.homeOtherExpense2 > 0 ? generalBusiness.homeOtherExpense2.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(homeOtherExpense2: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Motor vehicle expenses',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Kilometers driven to earn business income',
            initialValue: generalBusiness.kmDrivenForBusiness > 0 ? generalBusiness.kmDrivenForBusiness.toString() : '',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(kmDrivenForBusiness: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Total kilometers driven in tax year',
            initialValue: generalBusiness.totalKmDrivenInYear > 0 ? generalBusiness.totalKmDrivenInYear.toString() : '',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(totalKmDrivenInYear: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Fuel',
            initialValue: generalBusiness.vehicleFuel > 0 ? generalBusiness.vehicleFuel.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(vehicleFuel: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Insurance',
            initialValue: generalBusiness.vehicleInsurance > 0 ? generalBusiness.vehicleInsurance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(vehicleInsurance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'License and registration',
            initialValue: generalBusiness.licenseRegistration > 0 ? generalBusiness.licenseRegistration.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(licenseRegistration: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Maintenance & repairs',
            initialValue: generalBusiness.vehicleMaintenance > 0 ? generalBusiness.vehicleMaintenance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(vehicleMaintenance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Business parking',
            initialValue: generalBusiness.businessParking > 0 ? generalBusiness.businessParking.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(businessParking: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other (specify)',
            initialValue: generalBusiness.vehicleOtherExpense > 0 ? generalBusiness.vehicleOtherExpense.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(vehicleOtherExpense: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Leasing or finance payments',
            initialValue: generalBusiness.leasingFinancePayments > 0 ? generalBusiness.leasingFinancePayments.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  generalBusiness: generalBusiness.copyWith(leasingFinancePayments: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
        ],
      ),
    );
  }


  // ========== RENTAL INCOME DETAILS ==========
  Widget _buildRentalIncomeDetails() {
    final rentalIncome = _formData.selfEmployment?.rentalIncome ?? const T1RentalIncome();

    return _buildSection(
      title: 'Rental Income & Expenses',
      subtitle: 'Income from rental properties',
      child: Column(
        children: [
          _buildTextField(
            label: 'Property Address with postal code',
            initialValue: rentalIncome.propertyAddress,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(propertyAddress: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Co-owner / Partner 1',
            initialValue: rentalIncome.coOwnerPartner1,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(coOwnerPartner1: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Co-owner / Partner 2',
            initialValue: rentalIncome.coOwnerPartner2,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(coOwnerPartner2: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Co-owner / Partner 3',
            initialValue: rentalIncome.coOwnerPartner3,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(coOwnerPartner3: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Number of units',
            initialValue: rentalIncome.numberOfUnits > 0 ? rentalIncome.numberOfUnits.toString() : '',
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(numberOfUnits: int.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Income',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Gross rental income',
            initialValue: rentalIncome.grossRentalIncome > 0 ? rentalIncome.grossRentalIncome.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(grossRentalIncome: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Any government income relating to rental',
            initialValue: rentalIncome.anyGovtIncomeRelatingToRental > 0 ? rentalIncome.anyGovtIncomeRelatingToRental.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(anyGovtIncomeRelatingToRental: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'Expenses',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Personal use portion (if sharing house with tenants)',
            initialValue: rentalIncome.personalUsePortion,
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(personalUsePortion: value),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'House insurance',
            initialValue: rentalIncome.houseInsurance > 0 ? rentalIncome.houseInsurance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(houseInsurance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Mortgage interest',
            initialValue: rentalIncome.mortgageInterest > 0 ? rentalIncome.mortgageInterest.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(mortgageInterest: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Property taxes',
            initialValue: rentalIncome.propertyTaxes > 0 ? rentalIncome.propertyTaxes.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(propertyTaxes: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Utilities (if any)',
            initialValue: rentalIncome.utilities > 0 ? rentalIncome.utilities.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(utilities: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Management / admin fees',
            initialValue: rentalIncome.managementAdminFees > 0 ? rentalIncome.managementAdminFees.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(managementAdminFees: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Repair and maintenance',
            initialValue: rentalIncome.repairAndMaintenance > 0 ? rentalIncome.repairAndMaintenance.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(repairAndMaintenance: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Cleaning expense',
            initialValue: rentalIncome.cleaningExpense > 0 ? rentalIncome.cleaningExpense.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(cleaningExpense: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Motor vehicle expenses',
            initialValue: rentalIncome.motorVehicleExpenses > 0 ? rentalIncome.motorVehicleExpenses.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(motorVehicleExpenses: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Legal and professional fees',
            initialValue: rentalIncome.legalProfessionalFees > 0 ? rentalIncome.legalProfessionalFees.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(legalProfessionalFees: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Advertising and promotion',
            initialValue: rentalIncome.advertisingPromotion > 0 ? rentalIncome.advertisingPromotion.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(advertisingPromotion: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Other expenses',
            initialValue: rentalIncome.otherExpense > 0 ? rentalIncome.otherExpense.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(otherExpense: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          Text(
            'CCA/Depreciation',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            label: 'Purchase price',
            initialValue: rentalIncome.purchasePrice > 0 ? rentalIncome.purchasePrice.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(purchasePrice: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildDateField(
            label: 'Purchase date',
            date: rentalIncome.purchaseDate,
            onChanged: (date) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(purchaseDate: date),
                ),
              ));
            },
          ),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'Addition/deletion in property amount',
            initialValue: rentalIncome.additionDeletionAmount > 0 ? rentalIncome.additionDeletionAmount.toString() : '',
            keyboardType: TextInputType.number,
            prefix: '\$ ',
            onChanged: (value) {
              _updateFormData(_formData.copyWith(
                selfEmployment: _formData.selfEmployment?.copyWith(
                  rentalIncome: rentalIncome.copyWith(additionDeletionAmount: double.tryParse(value) ?? 0),
                ),
              ));
            },
          ),
        ],
      ),
    );
  }
}
