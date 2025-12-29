/*
  // Controllers for Corporation Information
  late TextEditingController _businessNumberController;
  late TextEditingController _corporationNameController;
  late TextEditingController _headOfficeAddressController;
  late TextEditingController _headOfficeCityController;
  late TextEditingController _headOfficeProvinceController;
  late TextEditingController _headOfficeCountryController;
  late TextEditingController _headOfficePostalCodeController;

  // Controllers for Mailing Address
  late TextEditingController _mailingAddressController;
  late TextEditingController _mailingCityController;
  late TextEditingController _mailingProvinceController;
  late TextEditingController _mailingCountryController;
  late TextEditingController _mailingPostalCodeController;

  // Controllers for Books and Records
  late TextEditingController _booksAddressController;
  late TextEditingController _booksCityController;
  late TextEditingController _booksProvinceController;
  late TextEditingController _booksCountryController;
  late TextEditingController _booksPostalCodeController;

  // Controllers for Functional Currency
  late TextEditingController _functionalCurrencyController;
  late TextEditingController _countryOfResidenceController;

  // Date variables
  DateTime? _taxYearStart;
  DateTime? _taxYearEnd;
  DateTime? _typeChangeEffectiveDate;
  DateTime? _acquisitionOfControlDate;

  bool _showMailingAddress = false;
  bool _showBooksAndRecords = false;

  @override
  void initState() {
    super.initState();
    _corporationInfo = widget.corporationInfo;
    _taxYearInfo = widget.taxYearInfo;
    _initControllers();
  }

  void _initControllers() {
    // Corporation Info controllers
    _businessNumberController = TextEditingController(text: _corporationInfo.businessNumber);
    _corporationNameController = TextEditingController(text: _corporationInfo.corporationName);
    _headOfficeAddressController = TextEditingController(text: _corporationInfo.headOfficeAddress);
    _headOfficeCityController = TextEditingController(text: _corporationInfo.headOfficeCity);
    _headOfficeProvinceController = TextEditingController(text: _corporationInfo.headOfficeProvince);
    _headOfficeCountryController = TextEditingController(text: _corporationInfo.headOfficeCountry);
    _headOfficePostalCodeController = TextEditingController(text: _corporationInfo.headOfficePostalCode);

    // Mailing Address controllers
    _mailingAddressController = TextEditingController(text: _corporationInfo.mailingAddress ?? '');
    _mailingCityController = TextEditingController(text: _corporationInfo.mailingCity ?? '');
    _mailingProvinceController = TextEditingController(text: _corporationInfo.mailingProvince ?? '');
    _mailingCountryController = TextEditingController(text: _corporationInfo.mailingCountry ?? '');
    _mailingPostalCodeController = TextEditingController(text: _corporationInfo.mailingPostalCode ?? '');

    // Books and Records controllers
    _booksAddressController = TextEditingController(text: _corporationInfo.booksAndRecordsAddress ?? '');
    _booksCityController = TextEditingController(text: _corporationInfo.booksAndRecordsCity ?? '');
    _booksProvinceController = TextEditingController(text: _corporationInfo.booksAndRecordsProvince ?? '');
    _booksCountryController = TextEditingController(text: _corporationInfo.booksAndRecordsCountry ?? '');
    _booksPostalCodeController = TextEditingController(text: _corporationInfo.booksAndRecordsPostalCode ?? '');

    // Tax Year Info controllers
    _functionalCurrencyController = TextEditingController(text: _taxYearInfo.functionalCurrency);
    _countryOfResidenceController = TextEditingController(text: _taxYearInfo.countryOfResidence ?? '');

    // Set dates
    _taxYearStart = _taxYearInfo.taxYearStart;
    _taxYearEnd = _taxYearInfo.taxYearEnd;
    _typeChangeEffectiveDate = _corporationInfo.typeChangeEffectiveDate;
    _acquisitionOfControlDate = _taxYearInfo.acquisitionOfControlDate;

    // Set visibility flags
    _showMailingAddress = _corporationInfo.mailingAddress?.isNotEmpty == true;
    _showBooksAndRecords = _corporationInfo.booksAndRecordsAddress?.isNotEmpty == true;
  }

  @override
  void dispose() {
    _businessNumberController.dispose();
    _corporationNameController.dispose();
    _headOfficeAddressController.dispose();
    _headOfficeCityController.dispose();
    _headOfficeProvinceController.dispose();
    _headOfficeCountryController.dispose();
    _headOfficePostalCodeController.dispose();
    _mailingAddressController.dispose();
    _mailingCityController.dispose();
    _mailingProvinceController.dispose();
    _mailingCountryController.dispose();
    _mailingPostalCodeController.dispose();
    _booksAddressController.dispose();
    _booksCityController.dispose();
    _booksProvinceController.dispose();
    _booksCountryController.dispose();
    _booksPostalCodeController.dispose();
    _functionalCurrencyController.dispose();
    _countryOfResidenceController.dispose();
    super.dispose();
  }

  void _updateCorporationInfo() {
    _corporationInfo = _corporationInfo.copyWith(
      businessNumber: _businessNumberController.text,
      corporationName: _corporationNameController.text,
      headOfficeAddress: _headOfficeAddressController.text,
      headOfficeCity: _headOfficeCityController.text,
      headOfficeProvince: _headOfficeProvinceController.text,
      headOfficeCountry: _headOfficeCountryController.text,
      headOfficePostalCode: _headOfficePostalCodeController.text,
      mailingAddress: _showMailingAddress ? _mailingAddressController.text : null,
      mailingCity: _showMailingAddress ? _mailingCityController.text : null,
      mailingProvince: _showMailingAddress ? _mailingProvinceController.text : null,
      mailingCountry: _showMailingAddress ? _mailingCountryController.text : null,
      mailingPostalCode: _showMailingAddress ? _mailingPostalCodeController.text : null,
      booksAndRecordsAddress: _showBooksAndRecords ? _booksAddressController.text : null,
      booksAndRecordsCity: _showBooksAndRecords ? _booksCityController.text : null,
      booksAndRecordsProvince: _showBooksAndRecords ? _booksProvinceController.text : null,
      booksAndRecordsCountry: _showBooksAndRecords ? _booksCountryController.text : null,
      booksAndRecordsPostalCode: _showBooksAndRecords ? _booksPostalCodeController.text : null,
      typeChangeEffectiveDate: _typeChangeEffectiveDate,
    );

    widget.onCorporationInfoChanged(_corporationInfo);
  }

  void _updateTaxYearInfo() {
    _taxYearInfo = _taxYearInfo.copyWith(
      taxYearStart: _taxYearStart,
      taxYearEnd: _taxYearEnd,
      functionalCurrency: _functionalCurrencyController.text,
      countryOfResidence: _countryOfResidenceController.text.isEmpty ? null : _countryOfResidenceController.text,
      acquisitionOfControlDate: _acquisitionOfControlDate,
    );

    widget.onTaxYearInfoChanged(_taxYearInfo);
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
                    'T2 Corporation Income Tax Return',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Identification and Tax Year Information',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.grey600,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Corporation Identification Section
            _buildSection(
              title: 'Corporation Identification',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTextField(
                    controller: _businessNumberController,
                    label: 'Business Number (BN) *',
                    onChanged: (_) => _updateCorporationInfo(),
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(RegExp(r'[0-9A-Z]')),
                      LengthLimitingTextInputFormatter(15),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _corporationNameController,
                    label: 'Corporation Name *',
                    onChanged: (_) => _updateCorporationInfo(),
                  ),
                  const SizedBox(height: 16),
                  _buildDropdownField(
                    label: 'Type of Corporation *',
                    value: _corporationInfo.typeOfCorporation.isEmpty ? null : _corporationInfo.typeOfCorporation,
                    items: const [
                      DropdownMenuItem(value: 'ccpc', child: Text('Canadian-controlled private corporation (CCPC)')),
                      DropdownMenuItem(value: 'other_private', child: Text('Other private corporation')),
                      DropdownMenuItem(value: 'public', child: Text('Public corporation')),
                      DropdownMenuItem(value: 'controlled_public', child: Text('Corporation controlled by a public corporation')),
                      DropdownMenuItem(value: 'other', child: Text('Other corporation')),
                    ],
                    onChanged: (value) {
                      _corporationInfo = _corporationInfo.copyWith(typeOfCorporation: value ?? '');
                      widget.onCorporationInfoChanged(_corporationInfo);
                      setState(() {});
                    },
                  ),
                  if (_corporationInfo.typeOfCorporation.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _buildDateField(
                      label: 'Type Change Effective Date (if applicable)',
                      date: _typeChangeEffectiveDate,
                      onDateChanged: (date) {
                        setState(() {
                          _typeChangeEffectiveDate = date;
                        });
                        _updateCorporationInfo();
                      },
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Head Office Address Section
            _buildSection(
              title: 'Head Office Address',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTextField(
                    controller: _headOfficeAddressController,
                    label: 'Address *',
                    onChanged: (_) => _updateCorporationInfo(),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: _buildTextField(
                          controller: _headOfficeCityController,
                          label: 'City *',
                          onChanged: (_) => _updateCorporationInfo(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _headOfficeProvinceController,
                          label: 'Province *',
                          onChanged: (_) => _updateCorporationInfo(),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _buildTextField(
                          controller: _headOfficeCountryController,
                          label: 'Country *',
                          onChanged: (_) => _updateCorporationInfo(),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildTextField(
                          controller: _headOfficePostalCodeController,
                          label: 'Postal Code *',
                          onChanged: (_) => _updateCorporationInfo(),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Checkbox(
                        value: _corporationInfo.headOfficeAddressChanged,
                        onChanged: (value) {
                          _corporationInfo = _corporationInfo.copyWith(headOfficeAddressChanged: value ?? false);
                          widget.onCorporationInfoChanged(_corporationInfo);
                          setState(() {});
                        },
                      ),
                      const Expanded(
                        child: Text('Has this address changed since the last time the CRA was notified?'),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Mailing Address Toggle
            Row(
              children: [
                Checkbox(
                  value: _showMailingAddress,
                  onChanged: (value) {
                    setState(() {
                      _showMailingAddress = value ?? false;
                      if (!_showMailingAddress) {
                        _mailingAddressController.clear();
                        _mailingCityController.clear();
                        _mailingProvinceController.clear();
                        _mailingCountryController.clear();
                        _mailingPostalCodeController.clear();
                      }
                    });
                    _updateCorporationInfo();
                  },
                ),
                const Expanded(
                  child: Text('Different mailing address'),
                ),
              ],
            ),

            // Mailing Address Section (Conditional)
            if (_showMailingAddress) ...[
              const SizedBox(height: 16),
              _buildSection(
                title: 'Mailing Address',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildTextField(
                      controller: _mailingAddressController,
                      label: 'Mailing Address',
                      onChanged: (_) => _updateCorporationInfo(),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: _buildTextField(
                            controller: _mailingCityController,
                            label: 'City',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildTextField(
                            controller: _mailingProvinceController,
                            label: 'Province',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildTextField(
                            controller: _mailingCountryController,
                            label: 'Country',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildTextField(
                            controller: _mailingPostalCodeController,
                            label: 'Postal Code',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Checkbox(
                          value: _corporationInfo.mailingAddressChanged,
                          onChanged: (value) {
                            _corporationInfo = _corporationInfo.copyWith(mailingAddressChanged: value ?? false);
                            widget.onCorporationInfoChanged(_corporationInfo);
                            setState(() {});
                          },
                        ),
                        const Expanded(
                          child: Text('Has this address changed since the last time the CRA was notified?'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 20),

            // Books and Records Address Toggle
            Row(
              children: [
                Checkbox(
                  value: _showBooksAndRecords,
                  onChanged: (value) {
                    setState(() {
                      _showBooksAndRecords = value ?? false;
                      if (!_showBooksAndRecords) {
                        _booksAddressController.clear();
                        _booksCityController.clear();
                        _booksProvinceController.clear();
                        _booksCountryController.clear();
                        _booksPostalCodeController.clear();
                      }
                    });
                    _updateCorporationInfo();
                  },
                ),
                const Expanded(
                  child: Text('Different books and records address'),
                ),
              ],
            ),

            // Books and Records Address Section (Conditional)
            if (_showBooksAndRecords) ...[
              const SizedBox(height: 16),
              _buildSection(
                title: 'Location of Books and Records',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildTextField(
                      controller: _booksAddressController,
                      label: 'Books and Records Address',
                      onChanged: (_) => _updateCorporationInfo(),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: _buildTextField(
                            controller: _booksCityController,
                            label: 'City',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildTextField(
                            controller: _booksProvinceController,
                            label: 'Province',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildTextField(
                            controller: _booksCountryController,
                            label: 'Country',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: _buildTextField(
                            controller: _booksPostalCodeController,
                            label: 'Postal Code',
                            onChanged: (_) => _updateCorporationInfo(),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Checkbox(
                          value: _corporationInfo.booksAndRecordsAddressChanged,
                          onChanged: (value) {
                            _corporationInfo = _corporationInfo.copyWith(booksAndRecordsAddressChanged: value ?? false);
                            widget.onCorporationInfoChanged(_corporationInfo);
                            setState(() {});
                          },
                        ),
                        const Expanded(
                          child: Text('Has this address changed since the last time the CRA was notified?'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 24),

            // Tax Year Information Section
            _buildSection(
              title: 'Tax Year Information',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: _buildDateField(
                          label: 'Tax Year Start *',
                          date: _taxYearStart,
                          onDateChanged: (date) {
                            setState(() {
                              _taxYearStart = date;
                            });
                            _updateTaxYearInfo();
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildDateField(
                          label: 'Tax Year End *',
                          date: _taxYearEnd,
                          onDateChanged: (date) {
                            setState(() {
                              _taxYearEnd = date;
                            });
                            _updateTaxYearInfo();
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  _buildRadioSection(
                    title: 'Is the corporation a resident of Canada? *',
                    value: _taxYearInfo.isCanadianResident,
                    onChanged: (value) {
                      _taxYearInfo = _taxYearInfo.copyWith(isCanadianResident: value);
                      widget.onTaxYearInfoChanged(_taxYearInfo);
                      setState(() {});
                    },
                  ),
                  if (!_taxYearInfo.isCanadianResident) ...[
                    const SizedBox(height: 16),
                    _buildTextField(
                      controller: _countryOfResidenceController,
                      label: 'Country of Residence',
                      onChanged: (_) => _updateTaxYearInfo(),
                    ),
                    const SizedBox(height: 16),
                    _buildRadioSection(
                      title: 'Is the non-resident corporation claiming an exemption under an income tax treaty?',
                      value: _taxYearInfo.isClaimingTreatyExemption,
                      onChanged: (value) {
                        _taxYearInfo = _taxYearInfo.copyWith(isClaimingTreatyExemption: value ?? false);
                        widget.onTaxYearInfoChanged(_taxYearInfo);
                        setState(() {});
                      },
                    ),
                  ],
                  const SizedBox(height: 20),
                  _buildRadioSection(
                    title: 'Has there been an acquisition of control resulting in the application of subsection 249(4)?',
                    value: _taxYearInfo.hasAcquisitionOfControl,
                    onChanged: (value) {
                      _taxYearInfo = _taxYearInfo.copyWith(hasAcquisitionOfControl: value ?? false);
                      widget.onTaxYearInfoChanged(_taxYearInfo);
                      setState(() {});
                    },
                  ),
                  if (_taxYearInfo.hasAcquisitionOfControl) ...[
                    const SizedBox(height: 16),
                    _buildDateField(
                      label: 'Date Control was Acquired',
                      date: _acquisitionOfControlDate,
                      onDateChanged: (date) {
                        setState(() {
                          _acquisitionOfControlDate = date;
                        });
                        _updateTaxYearInfo();
                      },
                    ),
                  ],
                  const SizedBox(height: 20),
                  _buildRadioSection(
                    title: 'Is this the first year of filing after incorporation?',
                    value: _taxYearInfo.isFirstYearAfterIncorporation,
                    onChanged: (value) {
                      _taxYearInfo = _taxYearInfo.copyWith(isFirstYearAfterIncorporation: value ?? false);
                      widget.onTaxYearInfoChanged(_taxYearInfo);
                      setState(() {});
                    },
                  ),
                  const SizedBox(height: 16),
                  _buildRadioSection(
                    title: 'Is this the first year of filing after amalgamation?',
                    value: _taxYearInfo.isFirstYearAfterAmalgamation,
                    onChanged: (value) {
                      _taxYearInfo = _taxYearInfo.copyWith(isFirstYearAfterAmalgamation: value ?? false);
                      widget.onTaxYearInfoChanged(_taxYearInfo);
                      setState(() {});
                    },
                  ),
                  const SizedBox(height: 16),
                  if (_taxYearInfo.functionalCurrency.isEmpty) ...[
                    _buildTextField(
                      controller: _functionalCurrencyController,
                      label: 'Functional Currency (if not CAD)',
                      onChanged: (_) => _updateTaxYearInfo(),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 32),

            // Next Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: widget.onNext,
                child: const Text('Next: Income & Deductions'),
              ),
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

  Widget _buildDateField({
    required String label,
    required DateTime? date,
    required Function(DateTime?) onDateChanged,
  }) {
    return InkWell(
      onTap: () async {
        final pickedDate = await showDatePicker(
          context: context,
          initialDate: date ?? DateTime.now(),
          firstDate: DateTime(1900),
          lastDate: DateTime.now().add(const Duration(days: 365)),
        );
        onDateChanged(pickedDate);
      },
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          ),
        ),
        child: Text(
          date != null ? '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}' : 'Select Date',
          style: date != null ? null : TextStyle(color: AppColors.grey500),
        ),
      ),
    );
  }

  Widget _buildRadioSection({
    required String title,
    required bool? value,
    required Function(bool?) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
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
      ],
    );
  }

  Widget _buildDropdownField({
    required String label,
    required String? value,
    required List<DropdownMenuItem<String>> items,
    required Function(String?) onChanged,
  }) {
    return DropdownButtonFormField<String>(
      value: value,
      items: items,
      onChanged: onChanged,
      isExpanded: true, // This prevents overflow by expanding the dropdown
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
    );
  }
*/
