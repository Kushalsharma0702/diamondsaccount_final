// T2 Business On-Boarding Data Models (derived from assets/on-boarding/business_onboarding.csv)

class T2ShareholderInfo {
  final String name;
  final double commonSharesPercent;
  final double preferenceSharesPercent;
  final String sinOrBn;

  const T2ShareholderInfo({
    this.name = '',
    this.commonSharesPercent = 0.0,
    this.preferenceSharesPercent = 0.0,
    this.sinOrBn = '',
  });

  factory T2ShareholderInfo.fromJson(Map<String, dynamic> json) => T2ShareholderInfo(
        name: json['name'] ?? '',
        commonSharesPercent: (json['commonSharesPercent'] ?? 0.0).toDouble(),
        preferenceSharesPercent: (json['preferenceSharesPercent'] ?? 0.0).toDouble(),
        sinOrBn: json['sinOrBn'] ?? '',
      );

  Map<String, dynamic> toJson() => {
        'name': name,
        'commonSharesPercent': commonSharesPercent,
        'preferenceSharesPercent': preferenceSharesPercent,
        'sinOrBn': sinOrBn,
      };

  T2ShareholderInfo copyWith({
    String? name,
    double? commonSharesPercent,
    double? preferenceSharesPercent,
    String? sinOrBn,
  }) =>
      T2ShareholderInfo(
        name: name ?? this.name,
        commonSharesPercent: commonSharesPercent ?? this.commonSharesPercent,
        preferenceSharesPercent: preferenceSharesPercent ?? this.preferenceSharesPercent,
        sinOrBn: sinOrBn ?? this.sinOrBn,
      );
}

class T2OnboardingData {
  final String id;
  final String status; // 'draft', 'submitted'
  final DateTime? createdAt;
  final DateTime? updatedAt;

  // Checklist items
  final bool craAuthorizationProvided;
  final bool incorporationDocsProvided;
  final bool payrollEnrollmentReturned;
  final bool previousYearRecordsProvided; // Previous years T2 & FS
  final bool franchiseDocsProvided;

  // Company details
  final String companyName;
  final String businessNumber;
  final String registeredAddress;
  final DateTime? incorporationDate;
  final bool isInactive;
  final String principalActivity;
  final int principalActivityPercentage; // 0-100
  final String directorFullName; // Last Name & First Name
  final String signingOfficerFullNameAndPosition;
  final String signingOfficerPhone;
  final int totalSharesIssued;
  final double totalAmountOfShares;

  // Shareholders (support up to 2 as per CSV, but store list)
  final List<T2ShareholderInfo> shareholders;

  const T2OnboardingData({
    this.id = '',
    this.status = 'draft',
    this.createdAt,
    this.updatedAt,
    this.craAuthorizationProvided = false,
    this.incorporationDocsProvided = false,
    this.payrollEnrollmentReturned = false,
    this.previousYearRecordsProvided = false,
    this.franchiseDocsProvided = false,
    this.companyName = '',
    this.businessNumber = '',
    this.registeredAddress = '',
    this.incorporationDate,
    this.isInactive = false,
    this.principalActivity = '',
    this.principalActivityPercentage = 0,
    this.directorFullName = '',
    this.signingOfficerFullNameAndPosition = '',
    this.signingOfficerPhone = '',
    this.totalSharesIssued = 0,
    this.totalAmountOfShares = 0.0,
    this.shareholders = const [],
  });

  factory T2OnboardingData.newForm() => T2OnboardingData(
        id: 'T2ONB_${DateTime.now().millisecondsSinceEpoch}',
        status: 'draft',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

  T2OnboardingData copyWith({
    String? id,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? craAuthorizationProvided,
    bool? incorporationDocsProvided,
    bool? payrollEnrollmentReturned,
    bool? previousYearRecordsProvided,
    bool? franchiseDocsProvided,
    String? companyName,
    String? businessNumber,
    String? registeredAddress,
    DateTime? incorporationDate,
    bool? isInactive,
    String? principalActivity,
    int? principalActivityPercentage,
    String? directorFullName,
    String? signingOfficerFullNameAndPosition,
    String? signingOfficerPhone,
    int? totalSharesIssued,
    double? totalAmountOfShares,
    List<T2ShareholderInfo>? shareholders,
  }) =>
      T2OnboardingData(
        id: id ?? this.id,
        status: status ?? this.status,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? DateTime.now(),
        craAuthorizationProvided: craAuthorizationProvided ?? this.craAuthorizationProvided,
        incorporationDocsProvided: incorporationDocsProvided ?? this.incorporationDocsProvided,
        payrollEnrollmentReturned: payrollEnrollmentReturned ?? this.payrollEnrollmentReturned,
        previousYearRecordsProvided: previousYearRecordsProvided ?? this.previousYearRecordsProvided,
        franchiseDocsProvided: franchiseDocsProvided ?? this.franchiseDocsProvided,
        companyName: companyName ?? this.companyName,
        businessNumber: businessNumber ?? this.businessNumber,
        registeredAddress: registeredAddress ?? this.registeredAddress,
        incorporationDate: incorporationDate ?? this.incorporationDate,
        isInactive: isInactive ?? this.isInactive,
        principalActivity: principalActivity ?? this.principalActivity,
        principalActivityPercentage: principalActivityPercentage ?? this.principalActivityPercentage,
        directorFullName: directorFullName ?? this.directorFullName,
        signingOfficerFullNameAndPosition:
            signingOfficerFullNameAndPosition ?? this.signingOfficerFullNameAndPosition,
        signingOfficerPhone: signingOfficerPhone ?? this.signingOfficerPhone,
        totalSharesIssued: totalSharesIssued ?? this.totalSharesIssued,
        totalAmountOfShares: totalAmountOfShares ?? this.totalAmountOfShares,
        shareholders: shareholders ?? this.shareholders,
      );

  factory T2OnboardingData.fromJson(Map<String, dynamic> json) => T2OnboardingData(
        id: json['id'] ?? '',
        status: json['status'] ?? 'draft',
        createdAt: json['createdAt'] != null ? DateTime.parse(json['createdAt']) : null,
        updatedAt: json['updatedAt'] != null ? DateTime.parse(json['updatedAt']) : null,
        craAuthorizationProvided: json['craAuthorizationProvided'] ?? false,
        incorporationDocsProvided: json['incorporationDocsProvided'] ?? false,
        payrollEnrollmentReturned: json['payrollEnrollmentReturned'] ?? false,
        previousYearRecordsProvided: json['previousYearRecordsProvided'] ?? false,
        franchiseDocsProvided: json['franchiseDocsProvided'] ?? false,
        companyName: json['companyName'] ?? '',
        businessNumber: json['businessNumber'] ?? '',
        registeredAddress: json['registeredAddress'] ?? '',
        incorporationDate: json['incorporationDate'] != null
            ? DateTime.parse(json['incorporationDate'])
            : null,
        isInactive: json['isInactive'] ?? false,
        principalActivity: json['principalActivity'] ?? '',
        principalActivityPercentage: json['principalActivityPercentage'] ?? 0,
        directorFullName: json['directorFullName'] ?? '',
        signingOfficerFullNameAndPosition:
            json['signingOfficerFullNameAndPosition'] ?? '',
        signingOfficerPhone: json['signingOfficerPhone'] ?? '',
        totalSharesIssued: json['totalSharesIssued'] ?? 0,
        totalAmountOfShares: (json['totalAmountOfShares'] ?? 0.0).toDouble(),
        shareholders: (json['shareholders'] as List<dynamic>? ?? [])
            .map((e) => T2ShareholderInfo.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'status': status,
        'createdAt': createdAt?.toIso8601String(),
        'updatedAt': updatedAt?.toIso8601String(),
        'craAuthorizationProvided': craAuthorizationProvided,
        'incorporationDocsProvided': incorporationDocsProvided,
        'payrollEnrollmentReturned': payrollEnrollmentReturned,
        'previousYearRecordsProvided': previousYearRecordsProvided,
        'franchiseDocsProvided': franchiseDocsProvided,
        'companyName': companyName,
        'businessNumber': businessNumber,
        'registeredAddress': registeredAddress,
        'incorporationDate': incorporationDate?.toIso8601String(),
        'isInactive': isInactive,
        'principalActivity': principalActivity,
        'principalActivityPercentage': principalActivityPercentage,
        'directorFullName': directorFullName,
        'signingOfficerFullNameAndPosition': signingOfficerFullNameAndPosition,
        'signingOfficerPhone': signingOfficerPhone,
        'totalSharesIssued': totalSharesIssued,
        'totalAmountOfShares': totalAmountOfShares,
        'shareholders': shareholders.map((e) => e.toJson()).toList(),
      };
}
