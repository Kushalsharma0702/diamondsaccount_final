import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../data/models/t1_form_models_simple.dart';

class T1PersonalInfoStep extends StatefulWidget {
  final T1PersonalInfo personalInfo;
  final Function(T1PersonalInfo) onPersonalInfoChanged;
  final VoidCallback onNext;

  const T1PersonalInfoStep({
    super.key,
    required this.personalInfo,
    required this.onPersonalInfoChanged,
    required this.onNext,
  });

  @override
  State<T1PersonalInfoStep> createState() => _T1PersonalInfoStepState();
}

class _T1PersonalInfoStepState extends State<T1PersonalInfoStep> {
  late T1PersonalInfo _personalInfo;

  // Controllers for Individual
  late TextEditingController _firstNameController;
  late TextEditingController _middleNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _sinController;
  late TextEditingController _addressController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;

  // Controllers for Spouse
  late TextEditingController _spouseFirstNameController;
  late TextEditingController _spouseMiddleNameController;
  late TextEditingController _spouseLastNameController;
  late TextEditingController _spouseSinController;

  // Date variables
  DateTime? _dateOfBirth;
  DateTime? _spouseDateOfBirth;

  @override
  void initState() {
    super.initState();
    _personalInfo = widget.personalInfo;
    _initControllers();
  }

  void _initControllers() {
    _firstNameController = TextEditingController(text: _personalInfo.firstName);
    _middleNameController = TextEditingController(text: _personalInfo.middleName ?? '');
    _lastNameController = TextEditingController(text: _personalInfo.lastName);
    _sinController = TextEditingController(text: _personalInfo.sin);
    _addressController = TextEditingController(text: _personalInfo.address);
    _phoneController = TextEditingController(text: _personalInfo.phoneNumber);
    _emailController = TextEditingController(text: _personalInfo.email);

    _spouseFirstNameController = TextEditingController(text: _personalInfo.spouseInfo?.firstName ?? '');
    _spouseMiddleNameController = TextEditingController(text: _personalInfo.spouseInfo?.middleName ?? '');
    _spouseLastNameController = TextEditingController(text: _personalInfo.spouseInfo?.lastName ?? '');
    _spouseSinController = TextEditingController(text: _personalInfo.spouseInfo?.sin ?? '');

    _dateOfBirth = _personalInfo.dateOfBirth;
    _spouseDateOfBirth = _personalInfo.spouseInfo?.dateOfBirth;
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _middleNameController.dispose();
    _lastNameController.dispose();
    _sinController.dispose();
    _addressController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _spouseFirstNameController.dispose();
    _spouseMiddleNameController.dispose();
    _spouseLastNameController.dispose();
    _spouseSinController.dispose();
    super.dispose();
  }

  void _updatePersonalInfo() {
    T1SpouseInfo? spouseInfo;
    if (_personalInfo.maritalStatus == 'married' || _personalInfo.maritalStatus == 'common-law') {
      spouseInfo = T1SpouseInfo(
        firstName: _spouseFirstNameController.text,
        middleName: _spouseMiddleNameController.text.isEmpty ? null : _spouseMiddleNameController.text,
        lastName: _spouseLastNameController.text,
        sin: _spouseSinController.text,
        dateOfBirth: _spouseDateOfBirth,
      );
    }

    _personalInfo = _personalInfo.copyWith(
      firstName: _firstNameController.text,
      middleName: _middleNameController.text.isEmpty ? null : _middleNameController.text,
      lastName: _lastNameController.text,
      sin: _sinController.text,
      dateOfBirth: _dateOfBirth,
      address: _addressController.text,
      phoneNumber: _phoneController.text,
      email: _emailController.text,
      spouseInfo: spouseInfo,
    );

    widget.onPersonalInfoChanged(_personalInfo);
  }

  void _addChild() {
    final newChildren = List<T1ChildInfo>.from(_personalInfo.children);
    newChildren.add(const T1ChildInfo());
    _personalInfo = _personalInfo.copyWith(children: newChildren);
    widget.onPersonalInfoChanged(_personalInfo);
    setState(() {});
  }

  void _removeChild(int index) {
    final newChildren = List<T1ChildInfo>.from(_personalInfo.children);
    newChildren.removeAt(index);
    _personalInfo = _personalInfo.copyWith(children: newChildren);
    widget.onPersonalInfoChanged(_personalInfo);
    setState(() {});
  }

  void _updateChild(int index, T1ChildInfo childInfo) {
    final newChildren = List<T1ChildInfo>.from(_personalInfo.children);
    newChildren[index] = childInfo;
    _personalInfo = _personalInfo.copyWith(children: newChildren);
    widget.onPersonalInfoChanged(_personalInfo);
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
                  'Personal Information',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'PLEASE READ AND FILL ENTIRE SHEET SO YOU DON\'T MISS OUT ANY CREDITS OR DEDUCTIONS',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.grey600,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Individual Information Section
          _buildSection(
            title: 'Individual Information',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Name as per SIN Document',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                _buildTextField(
                  controller: _firstNameController,
                  label: 'First Name *',
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 16),
                _buildTextField(
                  controller: _middleNameController,
                  label: 'Middle Name',
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 16),
                _buildTextField(
                  controller: _lastNameController,
                  label: 'Last Name *',
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 20),
                _buildTextField(
                  controller: _sinController,
                  label: 'SIN (Individual) *',
                  keyboardType: TextInputType.number,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(9),
                  ],
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 16),
                _buildDateField(
                  label: 'Date of Birth *',
                  date: _dateOfBirth,
                  onDateChanged: (date) {
                    setState(() {
                      _dateOfBirth = date;
                    });
                    _updatePersonalInfo();
                  },
                ),
                const SizedBox(height: 20),
                _buildTextField(
                  controller: _addressController,
                  label: 'Current Address with Postal Code *',
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 20),
                _buildTextField(
                  controller: _phoneController,
                  label: 'Phone Number *',
                  keyboardType: TextInputType.phone,
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 16),
                _buildTextField(
                  controller: _emailController,
                  label: 'Email *',
                  keyboardType: TextInputType.emailAddress,
                  onChanged: (_) => _updatePersonalInfo(),
                ),
                const SizedBox(height: 20),
                _buildRadioSection(
                  title: 'Are you a Canadian Citizen? *',
                  value: _personalInfo.isCanadianCitizen,
                  onChanged: (value) {
                    _personalInfo = _personalInfo.copyWith(isCanadianCitizen: value);
                    widget.onPersonalInfoChanged(_personalInfo);
                    setState(() {});
                  },
                ),
                const SizedBox(height: 20),
                _buildDropdownField(
                  label: 'Marital Status *',
                  value: _personalInfo.maritalStatus.isEmpty ? null : _personalInfo.maritalStatus,
                  items: const [
                    DropdownMenuItem(value: 'single', child: Text('Single')),
                    DropdownMenuItem(value: 'married', child: Text('Married')),
                    DropdownMenuItem(value: 'common-law', child: Text('Common-Law')),
                    DropdownMenuItem(value: 'separated', child: Text('Separated')),
                    DropdownMenuItem(value: 'divorced', child: Text('Divorced')),
                    DropdownMenuItem(value: 'widowed', child: Text('Widowed')),
                  ],
                  onChanged: (value) {
                    _personalInfo = _personalInfo.copyWith(maritalStatus: value ?? '');
                    widget.onPersonalInfoChanged(_personalInfo);
                    setState(() {});
                  },
                ),
              ],
            ),
          ),

          // Spouse Information Section (Conditional)
          if (_personalInfo.maritalStatus == 'married' || _personalInfo.maritalStatus == 'common-law') ...[
            const SizedBox(height: 24),
            _buildSection(
              title: 'Spouse Information',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Name as per SIN Document (Spouse)',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildTextField(
                    controller: _spouseFirstNameController,
                    label: 'First Name *',
                    onChanged: (_) => _updatePersonalInfo(),
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _spouseMiddleNameController,
                    label: 'Middle Name',
                    onChanged: (_) => _updatePersonalInfo(),
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _spouseLastNameController,
                    label: 'Last Name *',
                    onChanged: (_) => _updatePersonalInfo(),
                  ),
                  const SizedBox(height: 16),
                  _buildTextField(
                    controller: _spouseSinController,
                    label: 'SIN (Spouse) *',
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(9),
                    ],
                    onChanged: (_) => _updatePersonalInfo(),
                  ),
                  const SizedBox(height: 16),
                  _buildDateField(
                    label: 'Date of Birth *',
                    date: _spouseDateOfBirth,
                    onDateChanged: (date) {
                      setState(() {
                        _spouseDateOfBirth = date;
                      });
                      _updatePersonalInfo();
                    },
                  ),
                ],
              ),
            ),
          ],

          // Children Section
          const SizedBox(height: 24),
          _buildSection(
            title: 'Children Details',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ...List.generate(_personalInfo.children.length, (index) {
                  return _buildChildSection(
                    index: index,
                    child: _personalInfo.children[index],
                    onChildChanged: (childInfo) => _updateChild(index, childInfo),
                    onRemove: () => _removeChild(index),
                  );
                }),
                const SizedBox(height: 16),
                OutlinedButton.icon(
                  onPressed: _addChild,
                  icon: const Icon(Icons.add),
                  label: const Text('Add Another Child'),
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          // Next Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: widget.onNext,
              child: const Text('Next: Questionnaire'),
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
          lastDate: DateTime.now(),
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
          date != null ? '${date.day}/${date.month}/${date.year}' : 'Select Date',
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
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
    );
  }

  Widget _buildChildSection({
    required int index,
    required T1ChildInfo child,
    required Function(T1ChildInfo) onChildChanged,
    required VoidCallback onRemove,
  }) {
    final firstNameController = TextEditingController(text: child.firstName);
    final middleNameController = TextEditingController(text: child.middleName ?? '');
    final lastNameController = TextEditingController(text: child.lastName);
    final sinController = TextEditingController(text: child.sin);

    void updateChild() {
      onChildChanged(T1ChildInfo(
        firstName: firstNameController.text,
        middleName: middleNameController.text.isEmpty ? null : middleNameController.text,
        lastName: lastNameController.text,
        sin: sinController.text,
        dateOfBirth: child.dateOfBirth,
      ));
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Child ${index + 1} Details',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.delete, color: Colors.red),
                onPressed: onRemove,
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildTextField(
            controller: firstNameController,
            label: 'First Name',
            onChanged: (_) => updateChild(),
          ),
          const SizedBox(height: 16),
          _buildTextField(
            controller: middleNameController,
            label: 'Middle Name',
            onChanged: (_) => updateChild(),
          ),
          const SizedBox(height: 16),
          _buildTextField(
            controller: lastNameController,
            label: 'Last Name',
            onChanged: (_) => updateChild(),
          ),
          const SizedBox(height: 16),
          _buildTextField(
            controller: sinController,
            label: 'SIN',
            keyboardType: TextInputType.number,
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(9),
            ],
            onChanged: (_) => updateChild(),
          ),
          const SizedBox(height: 16),
          _buildDateField(
            label: 'Date of Birth',
            date: child.dateOfBirth,
            onDateChanged: (date) {
              onChildChanged(child.copyWith(dateOfBirth: date));
            },
          ),
        ],
      ),
    );
  }
}