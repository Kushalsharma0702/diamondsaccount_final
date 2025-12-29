/*
class _T2IncomeDeductionsStepState extends State<T2IncomeDeductionsStep> {
  late T2TaxableIncomeInfo _taxableIncomeInfo;
  late T2FormData _formData;

  // Controllers for income and deductions
  late TextEditingController _netIncomeController;
  late TextEditingController _charitableDonationsController;
  late TextEditingController _culturalGiftsController;
  late TextEditingController _ecologicalGiftsController;
  late TextEditingController _taxableDividendsController;
  late TextEditingController _partVITaxController;
  late TextEditingController _nonCapitalLossesController;
  late TextEditingController _netCapitalLossesController;
  late TextEditingController _restrictedFarmLossesController;
  late TextEditingController _farmLossesController;
  late TextEditingController _limitedPartnershipLossesController;
  late TextEditingController _restrictedInterestExpensesController;
  late TextEditingController _taxableCapitalGainsController;
  late TextEditingController _prospectorSharesController;
  late TextEditingController _employerDeductionController;
  late TextEditingController _section110AdditionsController;

  // Controllers for additional information
  late TextEditingController _principalProduct1Controller;
  late TextEditingController _principalProduct1PercentageController;
  late TextEditingController _principalProduct2Controller;
  late TextEditingController _principalProduct2PercentageController;
  late TextEditingController _principalProduct3Controller;
  late TextEditingController _principalProduct3PercentageController;

  @override
  void initState() {
    super.initState();
    _taxableIncomeInfo = widget.taxableIncomeInfo;
    _formData = widget.formData;
    _initControllers();
  }

  void _initControllers() {
    // Income and deductions controllers
    _netIncomeController = TextEditingController(text: _taxableIncomeInfo.netIncomeOrLoss.toString());
    _charitableDonationsController = TextEditingController(text: _taxableIncomeInfo.charitableDonations.toString());
    _culturalGiftsController = TextEditingController(text: _taxableIncomeInfo.culturalGifts.toString());
    _ecologicalGiftsController = TextEditingController(text: _taxableIncomeInfo.ecologicalGifts.toString());
    _taxableDividendsController = TextEditingController(text: _taxableIncomeInfo.taxableDividendsDeductible.toString());
    _partVITaxController = TextEditingController(text: _taxableIncomeInfo.partVITaxDeduction.toString());
    _nonCapitalLossesController = TextEditingController(text: _taxableIncomeInfo.nonCapitalLosses.toString());
    _netCapitalLossesController = TextEditingController(text: _taxableIncomeInfo.netCapitalLosses.toString());
    _restrictedFarmLossesController = TextEditingController(text: _taxableIncomeInfo.restrictedFarmLosses.toString());
    _farmLossesController = TextEditingController(text: _taxableIncomeInfo.farmLosses.toString());
    _limitedPartnershipLossesController = TextEditingController(text: _taxableIncomeInfo.limitedPartnershipLosses.toString());
    _restrictedInterestExpensesController = TextEditingController(text: _taxableIncomeInfo.restrictedInterestExpenses.toString());
    _taxableCapitalGainsController = TextEditingController(text: _taxableIncomeInfo.taxableCapitalGains.toString());
    _prospectorSharesController = TextEditingController(text: _taxableIncomeInfo.prospectorShares.toString());
    _employerDeductionController = TextEditingController(text: _taxableIncomeInfo.employerDeductionNonQualified.toString());
    _section110AdditionsController = TextEditingController(text: _taxableIncomeInfo.section110Additions.toString());

    // Additional information controllers
    _principalProduct1Controller = TextEditingController(text: _formData.principalProduct1);
    _principalProduct1PercentageController = TextEditingController(text: _formData.principalProduct1Percentage.toString());
    _principalProduct2Controller = TextEditingController(text: _formData.principalProduct2);
    _principalProduct2PercentageController = TextEditingController(text: _formData.principalProduct2Percentage.toString());
    _principalProduct3Controller = TextEditingController(text: _formData.principalProduct3);
    _principalProduct3PercentageController = TextEditingController(text: _formData.principalProduct3Percentage.toString());
  }

  @override
  void dispose() {
    _netIncomeController.dispose();
    _charitableDonationsController.dispose();
    _culturalGiftsController.dispose();
    _ecologicalGiftsController.dispose();
    _taxableDividendsController.dispose();
    _partVITaxController.dispose();
    _nonCapitalLossesController.dispose();
    _netCapitalLossesController.dispose();
    _restrictedFarmLossesController.dispose();
    _farmLossesController.dispose();
    _limitedPartnershipLossesController.dispose();
    _restrictedInterestExpensesController.dispose();
    _taxableCapitalGainsController.dispose();
    _prospectorSharesController.dispose();
    _employerDeductionController.dispose();
    _section110AdditionsController.dispose();
    _principalProduct1Controller.dispose();
    _principalProduct1PercentageController.dispose();
    _principalProduct2Controller.dispose();
    _principalProduct2PercentageController.dispose();
    _principalProduct3Controller.dispose();
    _principalProduct3PercentageController.dispose();
    super.dispose();
  }

  void _updateTaxableIncome() {
    _taxableIncomeInfo = _taxableIncomeInfo.copyWith(
      netIncomeOrLoss: double.tryParse(_netIncomeController.text) ?? 0.0,
      charitableDonations: double.tryParse(_charitableDonationsController.text) ?? 0.0,
      culturalGifts: double.tryParse(_culturalGiftsController.text) ?? 0.0,
      ecologicalGifts: double.tryParse(_ecologicalGiftsController.text) ?? 0.0,
      taxableDividendsDeductible: double.tryParse(_taxableDividendsController.text) ?? 0.0,
      partVITaxDeduction: double.tryParse(_partVITaxController.text) ?? 0.0,
      nonCapitalLosses: double.tryParse(_nonCapitalLossesController.text) ?? 0.0,
      netCapitalLosses: double.tryParse(_netCapitalLossesController.text) ?? 0.0,
      restrictedFarmLosses: double.tryParse(_restrictedFarmLossesController.text) ?? 0.0,
      farmLosses: double.tryParse(_farmLossesController.text) ?? 0.0,
      limitedPartnershipLosses: double.tryParse(_limitedPartnershipLossesController.text) ?? 0.0,
      restrictedInterestExpenses: double.tryParse(_restrictedInterestExpensesController.text) ?? 0.0,
      taxableCapitalGains: double.tryParse(_taxableCapitalGainsController.text) ?? 0.0,
      prospectorShares: double.tryParse(_prospectorSharesController.text) ?? 0.0,
      employerDeductionNonQualified: double.tryParse(_employerDeductionController.text) ?? 0.0,
      section110Additions: double.tryParse(_section110AdditionsController.text) ?? 0.0,
    );

    widget.onTaxableIncomeChanged(_taxableIncomeInfo);
    setState(() {}); // Refresh to show calculated taxable income
  }

  void _updateFormData() {
    _formData = _formData.copyWith(
      principalProduct1: _principalProduct1Controller.text,
      principalProduct1Percentage: int.tryParse(_principalProduct1PercentageController.text) ?? 0,
      principalProduct2: _principalProduct2Controller.text,
      principalProduct2Percentage: int.tryParse(_principalProduct2PercentageController.text) ?? 0,
      principalProduct3: _principalProduct3Controller.text,
      principalProduct3Percentage: int.tryParse(_principalProduct3PercentageController.text) ?? 0,
    );

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
            Container(
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
                    'Taxable Income Calculation',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Enter your corporation\'s income and deductions for the tax year',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.grey600,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Net Income Section
            _buildSection(
              title: 'Net Income (Loss) for Income Tax Purposes',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Enter the net income or loss from Schedule 1, financial statements, or GIFI',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _netIncomeController,
                    label: 'Net Income (Loss) *',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Deductions Section
            _buildSection(
              title: 'Deductions',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildCurrencyField(
                    controller: _charitableDonationsController,
                    label: 'Charitable Donations from Schedule 2',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _culturalGiftsController,
                    label: 'Cultural Gifts from Schedule 2',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _ecologicalGiftsController,
                    label: 'Ecological Gifts from Schedule 2',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _taxableDividendsController,
                    label: 'Taxable Dividends Deductible (sections 112/113)',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _partVITaxController,
                    label: 'Part VI.1 Tax Deduction',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Losses Section
            _buildSection(
              title: 'Losses from Previous Tax Years',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildCurrencyField(
                    controller: _nonCapitalLossesController,
                    label: 'Non-Capital Losses from Schedule 4',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _netCapitalLossesController,
                    label: 'Net Capital Losses from Schedule 4',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _restrictedFarmLossesController,
                    label: 'Restricted Farm Losses from Schedule 4',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _farmLossesController,
                    label: 'Farm Losses from Schedule 4',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _limitedPartnershipLossesController,
                    label: 'Limited Partnership Losses from Schedule 4',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _restrictedInterestExpensesController,
                    label: 'Restricted Interest and Financing Expenses',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Other Deductions Section
            _buildSection(
              title: 'Other Items',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildCurrencyField(
                    controller: _taxableCapitalGainsController,
                    label: 'Taxable Capital Gains (from central credit union)',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _prospectorSharesController,
                    label: 'Prospector\'s and Grubstaker\'s Shares',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _employerDeductionController,
                    label: 'Employer Deduction for Non-Qualified Securities',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                  const SizedBox(height: 16),
                  _buildCurrencyField(
                    controller: _section110AdditionsController,
                    label: 'Section 110.5 Additions',
                    onChanged: (_) => _updateTaxableIncome(),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Calculated Taxable Income
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(AppDimensions.spacingMd),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
                border: Border.all(color: AppColors.primary),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Calculated Taxable Income',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '\$${_taxableIncomeInfo.taxableIncome.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'This amount will be used for tax calculation',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Principal Business Activity Section
            _buildSection(
              title: 'Principal Products or Services',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Specify the principal products mined, manufactured, sold, constructed, or services provided',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: _buildTextField(
                          controller: _principalProduct1Controller,
                          label: 'Product/Service 1 *',
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _principalProduct1PercentageController,
                          label: 'Percentage *',
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(3),
                          ],
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: _buildTextField(
                          controller: _principalProduct2Controller,
                          label: 'Product/Service 2',
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _principalProduct2PercentageController,
                          label: 'Percentage',
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(3),
                          ],
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: _buildTextField(
                          controller: _principalProduct3Controller,
                          label: 'Product/Service 3',
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _principalProduct3PercentageController,
                          label: 'Percentage',
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(3),
                          ],
                          onChanged: (_) => _updateFormData(),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Additional Information Section with Conditional Sub-forms
            _buildSection(
              title: 'Additional Corporation Questions',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildRadioQuestionWithConditional(
                    title: 'Did the corporation use International Financial Reporting Standards (IFRS)?',
                    value: _formData.usesIFRS,
                    onChanged: (value) {
                      _formData = _formData.copyWith(usesIFRS: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.usesIFRS == true ? _buildIFRSDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'Is the corporation inactive?',
                    value: _formData.isInactive,
                    onChanged: (value) {
                      _formData = _formData.copyWith(isInactive: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.isInactive == true ? _buildInactiveDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'Did the corporation meet the definition of substantive CCPC under subsection 248(1)?',
                    value: _formData.meetsSubstantiveCCPC,
                    onChanged: (value) {
                      _formData = _formData.copyWith(meetsSubstantiveCCPC: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.meetsSubstantiveCCPC == true ? _buildSubstantiveCCPCDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'Did the corporation immigrate to Canada during the tax year?',
                    value: _formData.immigratedToCanada,
                    onChanged: (value) {
                      _formData = _formData.copyWith(immigratedToCanada: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.immigratedToCanada == true ? _buildImmigrationDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'Did the corporation emigrate from Canada during the tax year?',
                    value: _formData.emigratedFromCanada,
                    onChanged: (value) {
                      _formData = _formData.copyWith(emigratedFromCanada: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.emigratedFromCanada == true ? _buildEmigrationDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'Do you want to be considered as a quarterly instalment remitter if you are eligible?',
                    value: _formData.wantsQuarterlyInstallments,
                    onChanged: (value) {
                      _formData = _formData.copyWith(wantsQuarterlyInstallments: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.wantsQuarterlyInstallments == true ? _buildQuarterlyInstallmentDetails() : null,
                  ),
                  const SizedBox(height: 24),
                  _buildRadioQuestionWithConditional(
                    title: 'If the corporation\'s major business activity is construction, did you have any subcontractors?',
                    value: _formData.hasSubcontractors,
                    onChanged: (value) {
                      _formData = _formData.copyWith(hasSubcontractors: value);
                      widget.onFormDataChanged(_formData);
                      setState(() {});
                    },
                    conditionalWidget: _formData.hasSubcontractors == true ? _buildSubcontractorDetails() : null,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // Action Buttons - Vertical Layout
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ElevatedButton(
                  onPressed: widget.onSubmit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                    ),
                    elevation: 2,
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.send, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Submit T2 Form',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: widget.onPrevious,
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                    ),
                    side: BorderSide(color: AppColors.grey400),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.arrow_back, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Previous: Identification',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
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

  Widget _buildSection({required String title, required Widget child}) {
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
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    TextInputType? keyboardType,
    List<TextInputFormatter>? inputFormatters,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
    );
  }

  Widget _buildCurrencyField({
    required TextEditingController controller,
    required String label,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      inputFormatters: [
        FilteringTextInputFormatter.allow(RegExp(r'[0-9.-]')),
      ],
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: label,
        prefixText: '\$ ',
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
    );
  }


  Widget _buildRadioQuestionWithConditional({
    required String title,
    required bool? value,
    required Function(bool?) onChanged,
    Widget? conditionalWidget,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
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

  Widget _buildConditionalContainer({required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark 
            ? Theme.of(context).colorScheme.surface.withOpacity(0.7)
            : AppColors.grey50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: child,
    );
  }

  // Conditional Sub-forms
  Widget _buildIFRSDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'IFRS Implementation Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Year IFRS was first adopted',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Handle IFRS adoption year
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'External auditor name',
            onChanged: (value) {
              // Handle auditor info
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Impact on opening retained earnings (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle IFRS impact
            },
          ),
        ],
      ),
    );
  }

  Widget _buildInactiveDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Inactive Corporation Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'An inactive corporation is one that does not carry on business and has no income.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Date business operations ceased',
            onChanged: (value) {
              // Handle cessation date
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Reason for inactivity',
            onChanged: (value) {
              // Handle reason
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Expected date to resume operations (if any)',
            onChanged: (value) {
              // Handle resume date
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSubstantiveCCPCDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Substantive CCPC Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'A substantive CCPC is a Canadian-controlled private corporation throughout the year.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Primary business activity',
            onChanged: (value) {
              // Handle business activity
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Number of full-time employees',
            keyboardType: TextInputType.number,
            onChanged: (value) {
              // Handle employee count
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Total assets (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle total assets
            },
          ),
        ],
      ),
    );
  }

  Widget _buildImmigrationDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Corporation Immigration Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Date of immigration to Canada',
            onChanged: (value) {
              // Handle immigration date
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Previous country of incorporation',
            onChanged: (value) {
              // Handle previous country
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Fair market value of assets at immigration (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle asset value
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Income earned outside Canada (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle foreign income
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEmigrationDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Corporation Emigration Details',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Date of emigration from Canada',
            onChanged: (value) {
              // Handle emigration date
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'New country of residence',
            onChanged: (value) {
              // Handle new country
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Fair market value of assets at emigration (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle asset value
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Deemed disposition proceeds (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle disposition proceeds
            },
          ),
        ],
      ),
    );
  }

  Widget _buildQuarterlyInstallmentDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quarterly Installment Information',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Corporations may be eligible for quarterly installments instead of monthly.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Previous year taxable income (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle previous taxable income
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Two years ago taxable income (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle two years ago income
            },
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: TextEditingController(),
            label: 'Estimated current year taxable income (CAD)',
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (value) {
              // Handle estimated income
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSubcontractorDetails() {
    return _buildConditionalContainer(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Subcontractor Information',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Provide details about subcontractors used in construction activities.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          _buildSubcontractorTable(),
        ],
      ),
    );
  }

  Widget _buildSubcontractorTable() {
    return Column(
      children: [
        _buildTextField(
          controller: TextEditingController(),
          label: 'Subcontractor Business Name',
          onChanged: (value) {
            // Handle subcontractor name
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          controller: TextEditingController(),
          label: 'Business Number (if available)',
          onChanged: (value) {
            // Handle business number
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          controller: TextEditingController(),
          label: 'Total Amount Paid (CAD)',
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          onChanged: (value) {
            // Handle amount paid
          },
        ),
        const SizedBox(height: 12),
        _buildTextField(
          controller: TextEditingController(),
          label: 'Services Provided',
          onChanged: (value) {
            // Handle services
          },
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () {
            // Add another subcontractor row
          },
          icon: const Icon(Icons.add),
          label: const Text('Add Another Subcontractor'),
        ),
      ],
    );
  }
*/
