// Simplified T1 Form Data Models
// This is a working version without JSON serialization complexity

class T1PersonalInfo {
  final String firstName;
  final String? middleName;
  final String lastName;
  final String sin;
  final DateTime? dateOfBirth;
  final String address;
  final String phoneNumber;
  final String email;
  final bool? isCanadianCitizen;
  final String maritalStatus;
  final T1SpouseInfo? spouseInfo;
  final List<T1ChildInfo> children;

  const T1PersonalInfo({
    this.firstName = '',
    this.middleName,
    this.lastName = '',
    this.sin = '',
    this.dateOfBirth,
    this.address = '',
    this.phoneNumber = '',
    this.email = '',
    this.isCanadianCitizen,
    this.maritalStatus = '',
    this.spouseInfo,
    this.children = const [],
  });

  factory T1PersonalInfo.fromJson(Map<String, dynamic> json) {
    return T1PersonalInfo(
      firstName: json['firstName'] ?? '',
      middleName: json['middleName'],
      lastName: json['lastName'] ?? '',
      sin: json['sin'] ?? '',
      dateOfBirth: json['dateOfBirth'] != null ? DateTime.parse(json['dateOfBirth']) : null,
      address: json['address'] ?? '',
      phoneNumber: json['phoneNumber'] ?? '',
      email: json['email'] ?? '',
      isCanadianCitizen: json['isCanadianCitizen'],
      maritalStatus: json['maritalStatus'] ?? '',
      spouseInfo: json['spouseInfo'] != null ? T1SpouseInfo.fromJson(json['spouseInfo']) : null,
      children: (json['children'] as List? ?? []).map((e) => T1ChildInfo.fromJson(e)).toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'firstName': firstName,
      'middleName': middleName,
      'lastName': lastName,
      'sin': sin,
      'dateOfBirth': dateOfBirth?.toIso8601String(),
      'address': address,
      'phoneNumber': phoneNumber,
      'email': email,
      'isCanadianCitizen': isCanadianCitizen,
      'maritalStatus': maritalStatus,
      'spouseInfo': spouseInfo?.toJson(),
      'children': children.map((e) => e.toJson()).toList(),
    };
  }

  T1PersonalInfo copyWith({
    String? firstName,
    String? middleName,
    String? lastName,
    String? sin,
    DateTime? dateOfBirth,
    String? address,
    String? phoneNumber,
    String? email,
    bool? isCanadianCitizen,
    String? maritalStatus,
    T1SpouseInfo? spouseInfo,
    List<T1ChildInfo>? children,
  }) {
    return T1PersonalInfo(
      firstName: firstName ?? this.firstName,
      middleName: middleName ?? this.middleName,
      lastName: lastName ?? this.lastName,
      sin: sin ?? this.sin,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      address: address ?? this.address,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      email: email ?? this.email,
      isCanadianCitizen: isCanadianCitizen ?? this.isCanadianCitizen,
      maritalStatus: maritalStatus ?? this.maritalStatus,
      spouseInfo: spouseInfo ?? this.spouseInfo,
      children: children ?? this.children,
    );
  }
}

class T1SpouseInfo {
  final String firstName;
  final String? middleName;
  final String lastName;
  final String sin;
  final DateTime? dateOfBirth;

  const T1SpouseInfo({
    this.firstName = '',
    this.middleName,
    this.lastName = '',
    this.sin = '',
    this.dateOfBirth,
  });

  factory T1SpouseInfo.fromJson(Map<String, dynamic> json) {
    return T1SpouseInfo(
      firstName: json['firstName'] ?? '',
      middleName: json['middleName'],
      lastName: json['lastName'] ?? '',
      sin: json['sin'] ?? '',
      dateOfBirth: json['dateOfBirth'] != null ? DateTime.parse(json['dateOfBirth']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'firstName': firstName,
      'middleName': middleName,
      'lastName': lastName,
      'sin': sin,
      'dateOfBirth': dateOfBirth?.toIso8601String(),
    };
  }

  T1SpouseInfo copyWith({
    String? firstName,
    String? middleName,
    String? lastName,
    String? sin,
    DateTime? dateOfBirth,
  }) {
    return T1SpouseInfo(
      firstName: firstName ?? this.firstName,
      middleName: middleName ?? this.middleName,
      lastName: lastName ?? this.lastName,
      sin: sin ?? this.sin,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
    );
  }
}

class T1ChildInfo {
  final String firstName;
  final String? middleName;
  final String lastName;
  final String sin;
  final DateTime? dateOfBirth;

  const T1ChildInfo({
    this.firstName = '',
    this.middleName,
    this.lastName = '',
    this.sin = '',
    this.dateOfBirth,
  });

  factory T1ChildInfo.fromJson(Map<String, dynamic> json) {
    return T1ChildInfo(
      firstName: json['firstName'] ?? '',
      middleName: json['middleName'],
      lastName: json['lastName'] ?? '',
      sin: json['sin'] ?? '',
      dateOfBirth: json['dateOfBirth'] != null ? DateTime.parse(json['dateOfBirth']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'firstName': firstName,
      'middleName': middleName,
      'lastName': lastName,
      'sin': sin,
      'dateOfBirth': dateOfBirth?.toIso8601String(),
    };
  }

  T1ChildInfo copyWith({
    String? firstName,
    String? middleName,
    String? lastName,
    String? sin,
    DateTime? dateOfBirth,
  }) {
    return T1ChildInfo(
      firstName: firstName ?? this.firstName,
      middleName: middleName ?? this.middleName,
      lastName: lastName ?? this.lastName,
      sin: sin ?? this.sin,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
    );
  }
}

// Simplified classes for questionnaire sections
class T1ForeignProperty {
  final String investmentDetails;
  final double grossIncome;
  final double gainLossOnSale;
  final double maxCostDuringYear;
  final double costAmountYearEnd;
  final String country;

  const T1ForeignProperty({
    this.investmentDetails = '',
    this.grossIncome = 0.0,
    this.gainLossOnSale = 0.0,
    this.maxCostDuringYear = 0.0,
    this.costAmountYearEnd = 0.0,
    this.country = '',
  });

  factory T1ForeignProperty.fromJson(Map<String, dynamic> json) {
    return T1ForeignProperty(
      investmentDetails: json['investmentDetails'] ?? '',
      grossIncome: (json['grossIncome'] ?? 0.0).toDouble(),
      gainLossOnSale: (json['gainLossOnSale'] ?? 0.0).toDouble(),
      maxCostDuringYear: (json['maxCostDuringYear'] ?? 0.0).toDouble(),
      costAmountYearEnd: (json['costAmountYearEnd'] ?? 0.0).toDouble(),
      country: json['country'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'investmentDetails': investmentDetails,
      'grossIncome': grossIncome,
      'gainLossOnSale': gainLossOnSale,
      'maxCostDuringYear': maxCostDuringYear,
      'costAmountYearEnd': costAmountYearEnd,
      'country': country,
    };
  }
}

// Moving Expense Details (from moving_expense.xlsx)
class T1MovingExpense {
  final String individual;
  final String oldAddress;
  final String newAddress;
  final String distanceFromOldToNew;
  final String distanceFromNewToOffice;
  final double airTicketCost;
  final double moversAndPackers;
  final double mealsAndOtherCost;
  final double anyOtherCost;
  final DateTime? dateOfTravel;
  final DateTime? dateOfJoining;
  final String companyName;
  final String newEmployerAddress;
  final double grossIncomeAfterMoving;

  const T1MovingExpense({
    this.individual = '',
    this.oldAddress = '',
    this.newAddress = '',
    this.distanceFromOldToNew = '',
    this.distanceFromNewToOffice = '',
    this.airTicketCost = 0.0,
    this.moversAndPackers = 0.0,
    this.mealsAndOtherCost = 0.0,
    this.anyOtherCost = 0.0,
    this.dateOfTravel,
    this.dateOfJoining,
    this.companyName = '',
    this.newEmployerAddress = '',
    this.grossIncomeAfterMoving = 0.0,
  });

  factory T1MovingExpense.fromJson(Map<String, dynamic> json) {
    return T1MovingExpense(
      individual: json['individual'] ?? '',
      oldAddress: json['oldAddress'] ?? '',
      newAddress: json['newAddress'] ?? '',
      distanceFromOldToNew: json['distanceFromOldToNew'] ?? '',
      distanceFromNewToOffice: json['distanceFromNewToOffice'] ?? '',
      airTicketCost: (json['airTicketCost'] ?? 0.0).toDouble(),
      moversAndPackers: (json['moversAndPackers'] ?? 0.0).toDouble(),
      mealsAndOtherCost: (json['mealsAndOtherCost'] ?? 0.0).toDouble(),
      anyOtherCost: (json['anyOtherCost'] ?? 0.0).toDouble(),
      dateOfTravel: json['dateOfTravel'] != null ? DateTime.parse(json['dateOfTravel']) : null,
      dateOfJoining: json['dateOfJoining'] != null ? DateTime.parse(json['dateOfJoining']) : null,
      companyName: json['companyName'] ?? '',
      newEmployerAddress: json['newEmployerAddress'] ?? '',
      grossIncomeAfterMoving: (json['grossIncomeAfterMoving'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'individual': individual,
      'oldAddress': oldAddress,
      'newAddress': newAddress,
      'distanceFromOldToNew': distanceFromOldToNew,
      'distanceFromNewToOffice': distanceFromNewToOffice,
      'airTicketCost': airTicketCost,
      'moversAndPackers': moversAndPackers,
      'mealsAndOtherCost': mealsAndOtherCost,
      'anyOtherCost': anyOtherCost,
      'dateOfTravel': dateOfTravel?.toIso8601String(),
      'dateOfJoining': dateOfJoining?.toIso8601String(),
      'companyName': companyName,
      'newEmployerAddress': newEmployerAddress,
      'grossIncomeAfterMoving': grossIncomeAfterMoving,
    };
  }

  T1MovingExpense copyWith({
    String? individual,
    String? oldAddress,
    String? newAddress,
    String? distanceFromOldToNew,
    String? distanceFromNewToOffice,
    double? airTicketCost,
    double? moversAndPackers,
    double? mealsAndOtherCost,
    double? anyOtherCost,
    DateTime? dateOfTravel,
    DateTime? dateOfJoining,
    String? companyName,
    String? newEmployerAddress,
    double? grossIncomeAfterMoving,
  }) {
    return T1MovingExpense(
      individual: individual ?? this.individual,
      oldAddress: oldAddress ?? this.oldAddress,
      newAddress: newAddress ?? this.newAddress,
      distanceFromOldToNew: distanceFromOldToNew ?? this.distanceFromOldToNew,
      distanceFromNewToOffice: distanceFromNewToOffice ?? this.distanceFromNewToOffice,
      airTicketCost: airTicketCost ?? this.airTicketCost,
      moversAndPackers: moversAndPackers ?? this.moversAndPackers,
      mealsAndOtherCost: mealsAndOtherCost ?? this.mealsAndOtherCost,
      anyOtherCost: anyOtherCost ?? this.anyOtherCost,
      dateOfTravel: dateOfTravel ?? this.dateOfTravel,
      dateOfJoining: dateOfJoining ?? this.dateOfJoining,
      companyName: companyName ?? this.companyName,
      newEmployerAddress: newEmployerAddress ?? this.newEmployerAddress,
      grossIncomeAfterMoving: grossIncomeAfterMoving ?? this.grossIncomeAfterMoving,
    );
  }
}

// Uber/Skip/DoorDash Business Details (from uberskip_doordash.xlsx)
class T1UberBusiness {
  final String uberSkipStatement;
  final String businessHstNumber;
  final String hstAccessCode;
  final String hstFillingPeriod;
  final double income;
  final double totalKmForUberSkip;
  final double totalOfficialKmDriven;
  final double totalKmDrivenEntireYear;
  
  // Expenses
  final double businessNumberVehicleRegistration;
  final double meals;
  final double telephone;
  final double parkingFees;
  final double cleaningExpenses;
  final double safetyInspection;
  final double winterTireChange;
  final double oilChangeAndMaintenance;
  final double depreciation;
  final double insuranceOnVehicle;
  final double gas;
  final double financingCostInterest;
  final double leaseCost;
  final double otherExpense;
  
  const T1UberBusiness({
    this.uberSkipStatement = '',
    this.businessHstNumber = '',
    this.hstAccessCode = '',
    this.hstFillingPeriod = '',
    this.income = 0.0,
    this.totalKmForUberSkip = 0.0,
    this.totalOfficialKmDriven = 0.0,
    this.totalKmDrivenEntireYear = 0.0,
    this.businessNumberVehicleRegistration = 0.0,
    this.meals = 0.0,
    this.telephone = 0.0,
    this.parkingFees = 0.0,
    this.cleaningExpenses = 0.0,
    this.safetyInspection = 0.0,
    this.winterTireChange = 0.0,
    this.oilChangeAndMaintenance = 0.0,
    this.depreciation = 0.0,
    this.insuranceOnVehicle = 0.0,
    this.gas = 0.0,
    this.financingCostInterest = 0.0,
    this.leaseCost = 0.0,
    this.otherExpense = 0.0,
  });

  factory T1UberBusiness.fromJson(Map<String, dynamic> json) {
    return T1UberBusiness(
      uberSkipStatement: json['uberSkipStatement'] ?? '',
      businessHstNumber: json['businessHstNumber'] ?? '',
      hstAccessCode: json['hstAccessCode'] ?? '',
      hstFillingPeriod: json['hstFillingPeriod'] ?? '',
      income: (json['income'] ?? 0.0).toDouble(),
      totalKmForUberSkip: (json['totalKmForUberSkip'] ?? 0.0).toDouble(),
      totalOfficialKmDriven: (json['totalOfficialKmDriven'] ?? 0.0).toDouble(),
      totalKmDrivenEntireYear: (json['totalKmDrivenEntireYear'] ?? 0.0).toDouble(),
      businessNumberVehicleRegistration: (json['businessNumberVehicleRegistration'] ?? 0.0).toDouble(),
      meals: (json['meals'] ?? 0.0).toDouble(),
      telephone: (json['telephone'] ?? 0.0).toDouble(),
      parkingFees: (json['parkingFees'] ?? 0.0).toDouble(),
      cleaningExpenses: (json['cleaningExpenses'] ?? 0.0).toDouble(),
      safetyInspection: (json['safetyInspection'] ?? 0.0).toDouble(),
      winterTireChange: (json['winterTireChange'] ?? 0.0).toDouble(),
      oilChangeAndMaintenance: (json['oilChangeAndMaintenance'] ?? 0.0).toDouble(),
      depreciation: (json['depreciation'] ?? 0.0).toDouble(),
      insuranceOnVehicle: (json['insuranceOnVehicle'] ?? 0.0).toDouble(),
      gas: (json['gas'] ?? 0.0).toDouble(),
      financingCostInterest: (json['financingCostInterest'] ?? 0.0).toDouble(),
      leaseCost: (json['leaseCost'] ?? 0.0).toDouble(),
      otherExpense: (json['otherExpense'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'uberSkipStatement': uberSkipStatement,
      'businessHstNumber': businessHstNumber,
      'hstAccessCode': hstAccessCode,
      'hstFillingPeriod': hstFillingPeriod,
      'income': income,
      'totalKmForUberSkip': totalKmForUberSkip,
      'totalOfficialKmDriven': totalOfficialKmDriven,
      'totalKmDrivenEntireYear': totalKmDrivenEntireYear,
      'businessNumberVehicleRegistration': businessNumberVehicleRegistration,
      'meals': meals,
      'telephone': telephone,
      'parkingFees': parkingFees,
      'cleaningExpenses': cleaningExpenses,
      'safetyInspection': safetyInspection,
      'winterTireChange': winterTireChange,
      'oilChangeAndMaintenance': oilChangeAndMaintenance,
      'depreciation': depreciation,
      'insuranceOnVehicle': insuranceOnVehicle,
      'gas': gas,
      'financingCostInterest': financingCostInterest,
      'leaseCost': leaseCost,
      'otherExpense': otherExpense,
    };
  }

  T1UberBusiness copyWith({
    String? uberSkipStatement,
    String? businessHstNumber,
    String? hstAccessCode,
    String? hstFillingPeriod,
    double? income,
    double? totalKmForUberSkip,
    double? totalOfficialKmDriven,
    double? totalKmDrivenEntireYear,
    double? businessNumberVehicleRegistration,
    double? meals,
    double? telephone,
    double? parkingFees,
    double? cleaningExpenses,
    double? safetyInspection,
    double? winterTireChange,
    double? oilChangeAndMaintenance,
    double? depreciation,
    double? insuranceOnVehicle,
    double? gas,
    double? financingCostInterest,
    double? leaseCost,
    double? otherExpense,
  }) {
    return T1UberBusiness(
      uberSkipStatement: uberSkipStatement ?? this.uberSkipStatement,
      businessHstNumber: businessHstNumber ?? this.businessHstNumber,
      hstAccessCode: hstAccessCode ?? this.hstAccessCode,
      hstFillingPeriod: hstFillingPeriod ?? this.hstFillingPeriod,
      income: income ?? this.income,
      totalKmForUberSkip: totalKmForUberSkip ?? this.totalKmForUberSkip,
      totalOfficialKmDriven: totalOfficialKmDriven ?? this.totalOfficialKmDriven,
      totalKmDrivenEntireYear: totalKmDrivenEntireYear ?? this.totalKmDrivenEntireYear,
      businessNumberVehicleRegistration: businessNumberVehicleRegistration ?? this.businessNumberVehicleRegistration,
      meals: meals ?? this.meals,
      telephone: telephone ?? this.telephone,
      parkingFees: parkingFees ?? this.parkingFees,
      cleaningExpenses: cleaningExpenses ?? this.cleaningExpenses,
      safetyInspection: safetyInspection ?? this.safetyInspection,
      winterTireChange: winterTireChange ?? this.winterTireChange,
      oilChangeAndMaintenance: oilChangeAndMaintenance ?? this.oilChangeAndMaintenance,
      depreciation: depreciation ?? this.depreciation,
      insuranceOnVehicle: insuranceOnVehicle ?? this.insuranceOnVehicle,
      gas: gas ?? this.gas,
      financingCostInterest: financingCostInterest ?? this.financingCostInterest,
      leaseCost: leaseCost ?? this.leaseCost,
      otherExpense: otherExpense ?? this.otherExpense,
    );
  }
}

// General Business Details (from business.xlsx)
class T1GeneralBusiness {
  final String clientName;
  final String businessName;
  
  // Income
  final double salesCommissionsFees;
  final double minusHstCollected;
  final double grossIncome;
  
  // Cost of Goods Sold
  final double openingInventory;
  final double purchasesDuringYear;
  final double subcontracts;
  final double directWageCosts;
  final double otherCosts;
  final double purchaseReturns;
  
  // Expenses
  final double advertising;
  final double mealsEntertainment;
  final double badDebts;
  final double insurance;
  final double interest;
  final double feesLicensesDues;
  final double officeExpenses;
  final double supplies;
  final double legalAccountingFees;
  final double managementAdministration;
  final double officeRent;
  final double maintenanceRepairs;
  final double salariesWagesBenefits;
  final double propertyTax;
  final double travel;
  final double telephoneUtilities;
  final double fuelCosts;
  final double deliveryFreightExpress;
  final double otherExpense1;
  final double otherExpense2;
  final double otherExpense3;
  
  // Office-In-House Expenses
  final String areaOfHomeForBusiness;
  final String totalAreaOfHome;
  final double heat;
  final double electricity;
  final double houseInsurance;
  final double homeMaintenance;
  final double mortgageInterest;
  final double propertyTaxes;
  final double houseRent;
  final double homeOtherExpense1;
  final double homeOtherExpense2;
  
  // Motor Vehicle Expenses
  final double kmDrivenForBusiness;
  final double totalKmDrivenInYear;
  final double vehicleFuel;
  final double vehicleInsurance;
  final double licenseRegistration;
  final double vehicleMaintenance;
  final double businessParking;
  final double vehicleOtherExpense;
  final double leasingFinancePayments;

  const T1GeneralBusiness({
    this.clientName = '',
    this.businessName = '',
    this.salesCommissionsFees = 0.0,
    this.minusHstCollected = 0.0,
    this.grossIncome = 0.0,
    this.openingInventory = 0.0,
    this.purchasesDuringYear = 0.0,
    this.subcontracts = 0.0,
    this.directWageCosts = 0.0,
    this.otherCosts = 0.0,
    this.purchaseReturns = 0.0,
    this.advertising = 0.0,
    this.mealsEntertainment = 0.0,
    this.badDebts = 0.0,
    this.insurance = 0.0,
    this.interest = 0.0,
    this.feesLicensesDues = 0.0,
    this.officeExpenses = 0.0,
    this.supplies = 0.0,
    this.legalAccountingFees = 0.0,
    this.managementAdministration = 0.0,
    this.officeRent = 0.0,
    this.maintenanceRepairs = 0.0,
    this.salariesWagesBenefits = 0.0,
    this.propertyTax = 0.0,
    this.travel = 0.0,
    this.telephoneUtilities = 0.0,
    this.fuelCosts = 0.0,
    this.deliveryFreightExpress = 0.0,
    this.otherExpense1 = 0.0,
    this.otherExpense2 = 0.0,
    this.otherExpense3 = 0.0,
    this.areaOfHomeForBusiness = '',
    this.totalAreaOfHome = '',
    this.heat = 0.0,
    this.electricity = 0.0,
    this.houseInsurance = 0.0,
    this.homeMaintenance = 0.0,
    this.mortgageInterest = 0.0,
    this.propertyTaxes = 0.0,
    this.houseRent = 0.0,
    this.homeOtherExpense1 = 0.0,
    this.homeOtherExpense2 = 0.0,
    this.kmDrivenForBusiness = 0.0,
    this.totalKmDrivenInYear = 0.0,
    this.vehicleFuel = 0.0,
    this.vehicleInsurance = 0.0,
    this.licenseRegistration = 0.0,
    this.vehicleMaintenance = 0.0,
    this.businessParking = 0.0,
    this.vehicleOtherExpense = 0.0,
    this.leasingFinancePayments = 0.0,
  });

  factory T1GeneralBusiness.fromJson(Map<String, dynamic> json) {
    return T1GeneralBusiness(
      clientName: json['clientName'] ?? '',
      businessName: json['businessName'] ?? '',
      salesCommissionsFees: (json['salesCommissionsFees'] ?? 0.0).toDouble(),
      minusHstCollected: (json['minusHstCollected'] ?? 0.0).toDouble(),
      grossIncome: (json['grossIncome'] ?? 0.0).toDouble(),
      openingInventory: (json['openingInventory'] ?? 0.0).toDouble(),
      purchasesDuringYear: (json['purchasesDuringYear'] ?? 0.0).toDouble(),
      subcontracts: (json['subcontracts'] ?? 0.0).toDouble(),
      directWageCosts: (json['directWageCosts'] ?? 0.0).toDouble(),
      otherCosts: (json['otherCosts'] ?? 0.0).toDouble(),
      purchaseReturns: (json['purchaseReturns'] ?? 0.0).toDouble(),
      advertising: (json['advertising'] ?? 0.0).toDouble(),
      mealsEntertainment: (json['mealsEntertainment'] ?? 0.0).toDouble(),
      badDebts: (json['badDebts'] ?? 0.0).toDouble(),
      insurance: (json['insurance'] ?? 0.0).toDouble(),
      interest: (json['interest'] ?? 0.0).toDouble(),
      feesLicensesDues: (json['feesLicensesDues'] ?? 0.0).toDouble(),
      officeExpenses: (json['officeExpenses'] ?? 0.0).toDouble(),
      supplies: (json['supplies'] ?? 0.0).toDouble(),
      legalAccountingFees: (json['legalAccountingFees'] ?? 0.0).toDouble(),
      managementAdministration: (json['managementAdministration'] ?? 0.0).toDouble(),
      officeRent: (json['officeRent'] ?? 0.0).toDouble(),
      maintenanceRepairs: (json['maintenanceRepairs'] ?? 0.0).toDouble(),
      salariesWagesBenefits: (json['salariesWagesBenefits'] ?? 0.0).toDouble(),
      propertyTax: (json['propertyTax'] ?? 0.0).toDouble(),
      travel: (json['travel'] ?? 0.0).toDouble(),
      telephoneUtilities: (json['telephoneUtilities'] ?? 0.0).toDouble(),
      fuelCosts: (json['fuelCosts'] ?? 0.0).toDouble(),
      deliveryFreightExpress: (json['deliveryFreightExpress'] ?? 0.0).toDouble(),
      otherExpense1: (json['otherExpense1'] ?? 0.0).toDouble(),
      otherExpense2: (json['otherExpense2'] ?? 0.0).toDouble(),
      otherExpense3: (json['otherExpense3'] ?? 0.0).toDouble(),
      areaOfHomeForBusiness: json['areaOfHomeForBusiness'] ?? '',
      totalAreaOfHome: json['totalAreaOfHome'] ?? '',
      heat: (json['heat'] ?? 0.0).toDouble(),
      electricity: (json['electricity'] ?? 0.0).toDouble(),
      houseInsurance: (json['houseInsurance'] ?? 0.0).toDouble(),
      homeMaintenance: (json['homeMaintenance'] ?? 0.0).toDouble(),
      mortgageInterest: (json['mortgageInterest'] ?? 0.0).toDouble(),
      propertyTaxes: (json['propertyTaxes'] ?? 0.0).toDouble(),
      houseRent: (json['houseRent'] ?? 0.0).toDouble(),
      homeOtherExpense1: (json['homeOtherExpense1'] ?? 0.0).toDouble(),
      homeOtherExpense2: (json['homeOtherExpense2'] ?? 0.0).toDouble(),
      kmDrivenForBusiness: (json['kmDrivenForBusiness'] ?? 0.0).toDouble(),
      totalKmDrivenInYear: (json['totalKmDrivenInYear'] ?? 0.0).toDouble(),
      vehicleFuel: (json['vehicleFuel'] ?? 0.0).toDouble(),
      vehicleInsurance: (json['vehicleInsurance'] ?? 0.0).toDouble(),
      licenseRegistration: (json['licenseRegistration'] ?? 0.0).toDouble(),
      vehicleMaintenance: (json['vehicleMaintenance'] ?? 0.0).toDouble(),
      businessParking: (json['businessParking'] ?? 0.0).toDouble(),
      vehicleOtherExpense: (json['vehicleOtherExpense'] ?? 0.0).toDouble(),
      leasingFinancePayments: (json['leasingFinancePayments'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'clientName': clientName,
      'businessName': businessName,
      'salesCommissionsFees': salesCommissionsFees,
      'minusHstCollected': minusHstCollected,
      'grossIncome': grossIncome,
      'openingInventory': openingInventory,
      'purchasesDuringYear': purchasesDuringYear,
      'subcontracts': subcontracts,
      'directWageCosts': directWageCosts,
      'otherCosts': otherCosts,
      'purchaseReturns': purchaseReturns,
      'advertising': advertising,
      'mealsEntertainment': mealsEntertainment,
      'badDebts': badDebts,
      'insurance': insurance,
      'interest': interest,
      'feesLicensesDues': feesLicensesDues,
      'officeExpenses': officeExpenses,
      'supplies': supplies,
      'legalAccountingFees': legalAccountingFees,
      'managementAdministration': managementAdministration,
      'officeRent': officeRent,
      'maintenanceRepairs': maintenanceRepairs,
      'salariesWagesBenefits': salariesWagesBenefits,
      'propertyTax': propertyTax,
      'travel': travel,
      'telephoneUtilities': telephoneUtilities,
      'fuelCosts': fuelCosts,
      'deliveryFreightExpress': deliveryFreightExpress,
      'otherExpense1': otherExpense1,
      'otherExpense2': otherExpense2,
      'otherExpense3': otherExpense3,
      'areaOfHomeForBusiness': areaOfHomeForBusiness,
      'totalAreaOfHome': totalAreaOfHome,
      'heat': heat,
      'electricity': electricity,
      'houseInsurance': houseInsurance,
      'homeMaintenance': homeMaintenance,
      'mortgageInterest': mortgageInterest,
      'propertyTaxes': propertyTaxes,
      'houseRent': houseRent,
      'homeOtherExpense1': homeOtherExpense1,
      'homeOtherExpense2': homeOtherExpense2,
      'kmDrivenForBusiness': kmDrivenForBusiness,
      'totalKmDrivenInYear': totalKmDrivenInYear,
      'vehicleFuel': vehicleFuel,
      'vehicleInsurance': vehicleInsurance,
      'licenseRegistration': licenseRegistration,
      'vehicleMaintenance': vehicleMaintenance,
      'businessParking': businessParking,
      'vehicleOtherExpense': vehicleOtherExpense,
      'leasingFinancePayments': leasingFinancePayments,
    };
  }

  T1GeneralBusiness copyWith({
    String? clientName,
    String? businessName,
    double? salesCommissionsFees,
    double? minusHstCollected,
    double? grossIncome,
    double? openingInventory,
    double? purchasesDuringYear,
    double? subcontracts,
    double? directWageCosts,
    double? otherCosts,
    double? purchaseReturns,
    double? advertising,
    double? mealsEntertainment,
    double? badDebts,
    double? insurance,
    double? interest,
    double? feesLicensesDues,
    double? officeExpenses,
    double? supplies,
    double? legalAccountingFees,
    double? managementAdministration,
    double? officeRent,
    double? maintenanceRepairs,
    double? salariesWagesBenefits,
    double? propertyTax,
    double? travel,
    double? telephoneUtilities,
    double? fuelCosts,
    double? deliveryFreightExpress,
    double? otherExpense1,
    double? otherExpense2,
    double? otherExpense3,
    String? areaOfHomeForBusiness,
    String? totalAreaOfHome,
    double? heat,
    double? electricity,
    double? houseInsurance,
    double? homeMaintenance,
    double? mortgageInterest,
    double? propertyTaxes,
    double? houseRent,
    double? homeOtherExpense1,
    double? homeOtherExpense2,
    double? kmDrivenForBusiness,
    double? totalKmDrivenInYear,
    double? vehicleFuel,
    double? vehicleInsurance,
    double? licenseRegistration,
    double? vehicleMaintenance,
    double? businessParking,
    double? vehicleOtherExpense,
    double? leasingFinancePayments,
  }) {
    return T1GeneralBusiness(
      clientName: clientName ?? this.clientName,
      businessName: businessName ?? this.businessName,
      salesCommissionsFees: salesCommissionsFees ?? this.salesCommissionsFees,
      minusHstCollected: minusHstCollected ?? this.minusHstCollected,
      grossIncome: grossIncome ?? this.grossIncome,
      openingInventory: openingInventory ?? this.openingInventory,
      purchasesDuringYear: purchasesDuringYear ?? this.purchasesDuringYear,
      subcontracts: subcontracts ?? this.subcontracts,
      directWageCosts: directWageCosts ?? this.directWageCosts,
      otherCosts: otherCosts ?? this.otherCosts,
      purchaseReturns: purchaseReturns ?? this.purchaseReturns,
      advertising: advertising ?? this.advertising,
      mealsEntertainment: mealsEntertainment ?? this.mealsEntertainment,
      badDebts: badDebts ?? this.badDebts,
      insurance: insurance ?? this.insurance,
      interest: interest ?? this.interest,
      feesLicensesDues: feesLicensesDues ?? this.feesLicensesDues,
      officeExpenses: officeExpenses ?? this.officeExpenses,
      supplies: supplies ?? this.supplies,
      legalAccountingFees: legalAccountingFees ?? this.legalAccountingFees,
      managementAdministration: managementAdministration ?? this.managementAdministration,
      officeRent: officeRent ?? this.officeRent,
      maintenanceRepairs: maintenanceRepairs ?? this.maintenanceRepairs,
      salariesWagesBenefits: salariesWagesBenefits ?? this.salariesWagesBenefits,
      propertyTax: propertyTax ?? this.propertyTax,
      travel: travel ?? this.travel,
      telephoneUtilities: telephoneUtilities ?? this.telephoneUtilities,
      fuelCosts: fuelCosts ?? this.fuelCosts,
      deliveryFreightExpress: deliveryFreightExpress ?? this.deliveryFreightExpress,
      otherExpense1: otherExpense1 ?? this.otherExpense1,
      otherExpense2: otherExpense2 ?? this.otherExpense2,
      otherExpense3: otherExpense3 ?? this.otherExpense3,
      areaOfHomeForBusiness: areaOfHomeForBusiness ?? this.areaOfHomeForBusiness,
      totalAreaOfHome: totalAreaOfHome ?? this.totalAreaOfHome,
      heat: heat ?? this.heat,
      electricity: electricity ?? this.electricity,
      houseInsurance: houseInsurance ?? this.houseInsurance,
      homeMaintenance: homeMaintenance ?? this.homeMaintenance,
      mortgageInterest: mortgageInterest ?? this.mortgageInterest,
      propertyTaxes: propertyTaxes ?? this.propertyTaxes,
      houseRent: houseRent ?? this.houseRent,
      homeOtherExpense1: homeOtherExpense1 ?? this.homeOtherExpense1,
      homeOtherExpense2: homeOtherExpense2 ?? this.homeOtherExpense2,
      kmDrivenForBusiness: kmDrivenForBusiness ?? this.kmDrivenForBusiness,
      totalKmDrivenInYear: totalKmDrivenInYear ?? this.totalKmDrivenInYear,
      vehicleFuel: vehicleFuel ?? this.vehicleFuel,
      vehicleInsurance: vehicleInsurance ?? this.vehicleInsurance,
      licenseRegistration: licenseRegistration ?? this.licenseRegistration,
      vehicleMaintenance: vehicleMaintenance ?? this.vehicleMaintenance,
      businessParking: businessParking ?? this.businessParking,
      vehicleOtherExpense: vehicleOtherExpense ?? this.vehicleOtherExpense,
      leasingFinancePayments: leasingFinancePayments ?? this.leasingFinancePayments,
    );
  }
}

// Rental Income Details (from rental_income.xlsx)
class T1RentalIncome {
  final String propertyAddress;
  final String coOwnerPartner1;
  final String coOwnerPartner2;
  final String coOwnerPartner3;
  final int numberOfUnits;
  final double grossRentalIncome;
  final double anyGovtIncomeRelatingToRental;
  
  // Expenses
  final String personalUsePortion;
  final double houseInsurance;
  final double mortgageInterest;
  final double propertyTaxes;
  final double utilities;
  final double managementAdminFees;
  final double repairAndMaintenance;
  final double cleaningExpense;
  final double motorVehicleExpenses;
  final double legalProfessionalFees;
  final double advertisingPromotion;
  final double otherExpense;
  
  // CCA/Depreciation
  final double purchasePrice;
  final DateTime? purchaseDate;
  final double additionDeletionAmount;

  const T1RentalIncome({
    this.propertyAddress = '',
    this.coOwnerPartner1 = '',
    this.coOwnerPartner2 = '',
    this.coOwnerPartner3 = '',
    this.numberOfUnits = 0,
    this.grossRentalIncome = 0.0,
    this.anyGovtIncomeRelatingToRental = 0.0,
    this.personalUsePortion = '',
    this.houseInsurance = 0.0,
    this.mortgageInterest = 0.0,
    this.propertyTaxes = 0.0,
    this.utilities = 0.0,
    this.managementAdminFees = 0.0,
    this.repairAndMaintenance = 0.0,
    this.cleaningExpense = 0.0,
    this.motorVehicleExpenses = 0.0,
    this.legalProfessionalFees = 0.0,
    this.advertisingPromotion = 0.0,
    this.otherExpense = 0.0,
    this.purchasePrice = 0.0,
    this.purchaseDate,
    this.additionDeletionAmount = 0.0,
  });

  factory T1RentalIncome.fromJson(Map<String, dynamic> json) {
    return T1RentalIncome(
      propertyAddress: json['propertyAddress'] ?? '',
      coOwnerPartner1: json['coOwnerPartner1'] ?? '',
      coOwnerPartner2: json['coOwnerPartner2'] ?? '',
      coOwnerPartner3: json['coOwnerPartner3'] ?? '',
      numberOfUnits: json['numberOfUnits'] ?? 0,
      grossRentalIncome: (json['grossRentalIncome'] ?? 0.0).toDouble(),
      anyGovtIncomeRelatingToRental: (json['anyGovtIncomeRelatingToRental'] ?? 0.0).toDouble(),
      personalUsePortion: json['personalUsePortion'] ?? '',
      houseInsurance: (json['houseInsurance'] ?? 0.0).toDouble(),
      mortgageInterest: (json['mortgageInterest'] ?? 0.0).toDouble(),
      propertyTaxes: (json['propertyTaxes'] ?? 0.0).toDouble(),
      utilities: (json['utilities'] ?? 0.0).toDouble(),
      managementAdminFees: (json['managementAdminFees'] ?? 0.0).toDouble(),
      repairAndMaintenance: (json['repairAndMaintenance'] ?? 0.0).toDouble(),
      cleaningExpense: (json['cleaningExpense'] ?? 0.0).toDouble(),
      motorVehicleExpenses: (json['motorVehicleExpenses'] ?? 0.0).toDouble(),
      legalProfessionalFees: (json['legalProfessionalFees'] ?? 0.0).toDouble(),
      advertisingPromotion: (json['advertisingPromotion'] ?? 0.0).toDouble(),
      otherExpense: (json['otherExpense'] ?? 0.0).toDouble(),
      purchasePrice: (json['purchasePrice'] ?? 0.0).toDouble(),
      purchaseDate: json['purchaseDate'] != null ? DateTime.parse(json['purchaseDate']) : null,
      additionDeletionAmount: (json['additionDeletionAmount'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'propertyAddress': propertyAddress,
      'coOwnerPartner1': coOwnerPartner1,
      'coOwnerPartner2': coOwnerPartner2,
      'coOwnerPartner3': coOwnerPartner3,
      'numberOfUnits': numberOfUnits,
      'grossRentalIncome': grossRentalIncome,
      'anyGovtIncomeRelatingToRental': anyGovtIncomeRelatingToRental,
      'personalUsePortion': personalUsePortion,
      'houseInsurance': houseInsurance,
      'mortgageInterest': mortgageInterest,
      'propertyTaxes': propertyTaxes,
      'utilities': utilities,
      'managementAdminFees': managementAdminFees,
      'repairAndMaintenance': repairAndMaintenance,
      'cleaningExpense': cleaningExpense,
      'motorVehicleExpenses': motorVehicleExpenses,
      'legalProfessionalFees': legalProfessionalFees,
      'advertisingPromotion': advertisingPromotion,
      'otherExpense': otherExpense,
      'purchasePrice': purchasePrice,
      'purchaseDate': purchaseDate?.toIso8601String(),
      'additionDeletionAmount': additionDeletionAmount,
    };
  }

  T1RentalIncome copyWith({
    String? propertyAddress,
    String? coOwnerPartner1,
    String? coOwnerPartner2,
    String? coOwnerPartner3,
    int? numberOfUnits,
    double? grossRentalIncome,
    double? anyGovtIncomeRelatingToRental,
    String? personalUsePortion,
    double? houseInsurance,
    double? mortgageInterest,
    double? propertyTaxes,
    double? utilities,
    double? managementAdminFees,
    double? repairAndMaintenance,
    double? cleaningExpense,
    double? motorVehicleExpenses,
    double? legalProfessionalFees,
    double? advertisingPromotion,
    double? otherExpense,
    double? purchasePrice,
    DateTime? purchaseDate,
    double? additionDeletionAmount,
  }) {
    return T1RentalIncome(
      propertyAddress: propertyAddress ?? this.propertyAddress,
      coOwnerPartner1: coOwnerPartner1 ?? this.coOwnerPartner1,
      coOwnerPartner2: coOwnerPartner2 ?? this.coOwnerPartner2,
      coOwnerPartner3: coOwnerPartner3 ?? this.coOwnerPartner3,
      numberOfUnits: numberOfUnits ?? this.numberOfUnits,
      grossRentalIncome: grossRentalIncome ?? this.grossRentalIncome,
      anyGovtIncomeRelatingToRental: anyGovtIncomeRelatingToRental ?? this.anyGovtIncomeRelatingToRental,
      personalUsePortion: personalUsePortion ?? this.personalUsePortion,
      houseInsurance: houseInsurance ?? this.houseInsurance,
      mortgageInterest: mortgageInterest ?? this.mortgageInterest,
      propertyTaxes: propertyTaxes ?? this.propertyTaxes,
      utilities: utilities ?? this.utilities,
      managementAdminFees: managementAdminFees ?? this.managementAdminFees,
      repairAndMaintenance: repairAndMaintenance ?? this.repairAndMaintenance,
      cleaningExpense: cleaningExpense ?? this.cleaningExpense,
      motorVehicleExpenses: motorVehicleExpenses ?? this.motorVehicleExpenses,
      legalProfessionalFees: legalProfessionalFees ?? this.legalProfessionalFees,
      advertisingPromotion: advertisingPromotion ?? this.advertisingPromotion,
      otherExpense: otherExpense ?? this.otherExpense,
      purchasePrice: purchasePrice ?? this.purchasePrice,
      purchaseDate: purchaseDate ?? this.purchaseDate,
      additionDeletionAmount: additionDeletionAmount ?? this.additionDeletionAmount,
    );
  }
}

// Self Employment wrapper
class T1SelfEmployment {
  final List<String> businessTypes; // List of selected types: 'uber', 'general', 'rental'
  final T1UberBusiness? uberBusiness;
  final T1GeneralBusiness? generalBusiness;
  final T1RentalIncome? rentalIncome;

  const T1SelfEmployment({
    this.businessTypes = const [],
    this.uberBusiness,
    this.generalBusiness,
    this.rentalIncome,
  });

  factory T1SelfEmployment.fromJson(Map<String, dynamic> json) {
    return T1SelfEmployment(
      businessTypes: List<String>.from(json['businessTypes'] ?? []),
      uberBusiness: json['uberBusiness'] != null 
          ? T1UberBusiness.fromJson(json['uberBusiness']) 
          : null,
      generalBusiness: json['generalBusiness'] != null 
          ? T1GeneralBusiness.fromJson(json['generalBusiness']) 
          : null,
      rentalIncome: json['rentalIncome'] != null 
          ? T1RentalIncome.fromJson(json['rentalIncome']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'businessTypes': businessTypes,
      'uberBusiness': uberBusiness?.toJson(),
      'generalBusiness': generalBusiness?.toJson(),
      'rentalIncome': rentalIncome?.toJson(),
    };
  }

  T1SelfEmployment copyWith({
    List<String>? businessTypes,
    T1UberBusiness? uberBusiness,
    T1GeneralBusiness? generalBusiness,
    T1RentalIncome? rentalIncome,
  }) {
    return T1SelfEmployment(
      businessTypes: businessTypes ?? this.businessTypes,
      uberBusiness: uberBusiness ?? this.uberBusiness,
      generalBusiness: generalBusiness ?? this.generalBusiness,
      rentalIncome: rentalIncome ?? this.rentalIncome,
    );
  }
}

// Main form data class
class T1FormData {
  final String id;
  final String status; // 'draft', 'submitted'
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final T1PersonalInfo personalInfo;
  final bool? hasForeignProperty;
  final List<T1ForeignProperty> foreignProperties;
  final bool? hasMedicalExpenses;
  final bool? hasCharitableDonations;
  final bool? hasMovingExpenses;
  // Legacy single moving expense field (kept for backward compatibility)
  final T1MovingExpense? movingExpense;
  // New: selection and per-person moving expense subforms
  final bool? movingExpenseForIndividual;
  final bool? movingExpenseForSpouse;
  final T1MovingExpense? movingExpenseIndividual;
  final T1MovingExpense? movingExpenseSpouse;
  final bool? isSelfEmployed;
  final T1SelfEmployment? selfEmployment;
  final bool? isFirstHomeBuyer;
  final bool? soldPropertyLongTerm;
  final bool? soldPropertyShortTerm;
  final bool? hasWorkFromHomeExpense;
  final bool? wasStudentLastYear;
  final bool? isUnionMember;
  final bool? hasDaycareExpenses;
  final bool? isFirstTimeFiler;
  final bool? hasOtherIncome;
  final String otherIncomeDescription;
  final bool? hasProfessionalDues;
  final bool? hasRrspFhsaInvestment;
  final bool? hasChildArtSportCredit;
  final bool? isProvinceFiler;

  T1FormData({
    this.id = '',
    this.status = 'draft',
    DateTime? createdAt,
    DateTime? updatedAt,
    this.personalInfo = const T1PersonalInfo(),
    this.hasForeignProperty,
    this.foreignProperties = const [],
    this.hasMedicalExpenses,
    this.hasCharitableDonations,
    this.hasMovingExpenses,
    this.movingExpense,
    this.movingExpenseForIndividual,
    this.movingExpenseForSpouse,
    this.movingExpenseIndividual,
    this.movingExpenseSpouse,
    this.isSelfEmployed,
    this.selfEmployment,
    this.isFirstHomeBuyer,
    this.soldPropertyLongTerm,
    this.soldPropertyShortTerm,
    this.hasWorkFromHomeExpense,
    this.wasStudentLastYear,
    this.isUnionMember,
    this.hasDaycareExpenses,
    this.isFirstTimeFiler,
    this.hasOtherIncome,
    this.otherIncomeDescription = '',
    this.hasProfessionalDues,
    this.hasRrspFhsaInvestment,
    this.hasChildArtSportCredit,
    this.isProvinceFiler,
  }) : createdAt = createdAt ?? DateTime.now(),
       updatedAt = updatedAt ?? DateTime.now();

  // Create const empty constructor with placeholder dates
  const T1FormData.empty()
      : id = '',
        status = 'draft',
        createdAt = null,
        updatedAt = null,
        personalInfo = const T1PersonalInfo(),
        hasForeignProperty = null,
        foreignProperties = const [],
        hasMedicalExpenses = null,
        hasCharitableDonations = null,
        hasMovingExpenses = null,
        movingExpense = null,
        movingExpenseForIndividual = null,
        movingExpenseForSpouse = null,
        movingExpenseIndividual = null,
        movingExpenseSpouse = null,
        isSelfEmployed = null,
        selfEmployment = null,
        isFirstHomeBuyer = null,
        soldPropertyLongTerm = null,
        soldPropertyShortTerm = null,
        hasWorkFromHomeExpense = null,
        wasStudentLastYear = null,
        isUnionMember = null,
        hasDaycareExpenses = null,
        isFirstTimeFiler = null,
        hasOtherIncome = null,
        otherIncomeDescription = '',
        hasProfessionalDues = null,
        hasRrspFhsaInvestment = null,
        hasChildArtSportCredit = null,
        isProvinceFiler = null;

  factory T1FormData.fromJson(Map<String, dynamic> json) {
    return T1FormData(
      id: json['id'] ?? '',
      status: json['status'] ?? 'draft',
      createdAt: json['createdAt'] != null ? DateTime.parse(json['createdAt']) : DateTime.now(),
      updatedAt: json['updatedAt'] != null ? DateTime.parse(json['updatedAt']) : DateTime.now(),
      personalInfo: json['personalInfo'] != null 
          ? T1PersonalInfo.fromJson(json['personalInfo']) 
          : const T1PersonalInfo(),
      hasForeignProperty: json['hasForeignProperty'],
      foreignProperties: (json['foreignProperties'] as List? ?? [])
          .map((e) => T1ForeignProperty.fromJson(e))
          .toList(),
      hasMedicalExpenses: json['hasMedicalExpenses'],
      hasCharitableDonations: json['hasCharitableDonations'],
      hasMovingExpenses: json['hasMovingExpenses'],
      movingExpense: json['movingExpense'] != null 
          ? T1MovingExpense.fromJson(json['movingExpense'])
          : null,
      movingExpenseForIndividual: json['movingExpenseForIndividual'],
      movingExpenseForSpouse: json['movingExpenseForSpouse'],
      movingExpenseIndividual: json['movingExpenseIndividual'] != null 
          ? T1MovingExpense.fromJson(json['movingExpenseIndividual'])
          : null,
      movingExpenseSpouse: json['movingExpenseSpouse'] != null 
          ? T1MovingExpense.fromJson(json['movingExpenseSpouse'])
          : null,
      isSelfEmployed: json['isSelfEmployed'],
      selfEmployment: json['selfEmployment'] != null 
          ? T1SelfEmployment.fromJson(json['selfEmployment'])
          : null,
      isFirstHomeBuyer: json['isFirstHomeBuyer'],
      soldPropertyLongTerm: json['soldPropertyLongTerm'],
      soldPropertyShortTerm: json['soldPropertyShortTerm'],
      hasWorkFromHomeExpense: json['hasWorkFromHomeExpense'],
      wasStudentLastYear: json['wasStudentLastYear'],
      isUnionMember: json['isUnionMember'],
      hasDaycareExpenses: json['hasDaycareExpenses'],
      isFirstTimeFiler: json['isFirstTimeFiler'],
      hasOtherIncome: json['hasOtherIncome'],
      otherIncomeDescription: json['otherIncomeDescription'] ?? '',
      hasProfessionalDues: json['hasProfessionalDues'],
      hasRrspFhsaInvestment: json['hasRrspFhsaInvestment'],
      hasChildArtSportCredit: json['hasChildArtSportCredit'],
      isProvinceFiler: json['isProvinceFiler'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'status': status,
      'createdAt': createdAt?.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'personalInfo': personalInfo.toJson(),
      'hasForeignProperty': hasForeignProperty,
      'foreignProperties': foreignProperties.map((e) => e.toJson()).toList(),
      'hasMedicalExpenses': hasMedicalExpenses,
      'hasCharitableDonations': hasCharitableDonations,
      'hasMovingExpenses': hasMovingExpenses,
      'movingExpense': movingExpense?.toJson(),
      'movingExpenseForIndividual': movingExpenseForIndividual,
      'movingExpenseForSpouse': movingExpenseForSpouse,
      'movingExpenseIndividual': movingExpenseIndividual?.toJson(),
      'movingExpenseSpouse': movingExpenseSpouse?.toJson(),
      'isSelfEmployed': isSelfEmployed,
      'selfEmployment': selfEmployment?.toJson(),
      'isFirstHomeBuyer': isFirstHomeBuyer,
      'soldPropertyLongTerm': soldPropertyLongTerm,
      'soldPropertyShortTerm': soldPropertyShortTerm,
      'hasWorkFromHomeExpense': hasWorkFromHomeExpense,
      'wasStudentLastYear': wasStudentLastYear,
      'isUnionMember': isUnionMember,
      'hasDaycareExpenses': hasDaycareExpenses,
      'isFirstTimeFiler': isFirstTimeFiler,
      'hasOtherIncome': hasOtherIncome,
      'otherIncomeDescription': otherIncomeDescription,
      'hasProfessionalDues': hasProfessionalDues,
      'hasRrspFhsaInvestment': hasRrspFhsaInvestment,
      'hasChildArtSportCredit': hasChildArtSportCredit,
      'isProvinceFiler': isProvinceFiler,
    };
  }

  T1FormData copyWith({
    String? id,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    T1PersonalInfo? personalInfo,
    bool? hasForeignProperty,
    List<T1ForeignProperty>? foreignProperties,
    bool? hasMedicalExpenses,
    bool? hasCharitableDonations,
    bool? hasMovingExpenses,
    T1MovingExpense? movingExpense,
    bool? movingExpenseForIndividual,
    bool? movingExpenseForSpouse,
    T1MovingExpense? movingExpenseIndividual,
    T1MovingExpense? movingExpenseSpouse,
    bool? isSelfEmployed,
    T1SelfEmployment? selfEmployment,
    bool? isFirstHomeBuyer,
    bool? soldPropertyLongTerm,
    bool? soldPropertyShortTerm,
    bool? hasWorkFromHomeExpense,
    bool? wasStudentLastYear,
    bool? isUnionMember,
    bool? hasDaycareExpenses,
    bool? isFirstTimeFiler,
    bool? hasOtherIncome,
    String? otherIncomeDescription,
    bool? hasProfessionalDues,
    bool? hasRrspFhsaInvestment,
    bool? hasChildArtSportCredit,
    bool? isProvinceFiler,
  }) {
    return T1FormData(
      id: id ?? this.id,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? DateTime.now(), // Always update the timestamp
      personalInfo: personalInfo ?? this.personalInfo,
      hasForeignProperty: hasForeignProperty ?? this.hasForeignProperty,
      foreignProperties: foreignProperties ?? this.foreignProperties,
      hasMedicalExpenses: hasMedicalExpenses ?? this.hasMedicalExpenses,
      hasCharitableDonations: hasCharitableDonations ?? this.hasCharitableDonations,
      hasMovingExpenses: hasMovingExpenses ?? this.hasMovingExpenses,
      movingExpense: movingExpense ?? this.movingExpense,
      movingExpenseForIndividual: movingExpenseForIndividual ?? this.movingExpenseForIndividual,
      movingExpenseForSpouse: movingExpenseForSpouse ?? this.movingExpenseForSpouse,
      movingExpenseIndividual: movingExpenseIndividual ?? this.movingExpenseIndividual,
      movingExpenseSpouse: movingExpenseSpouse ?? this.movingExpenseSpouse,
      isSelfEmployed: isSelfEmployed ?? this.isSelfEmployed,
      selfEmployment: selfEmployment ?? this.selfEmployment,
      isFirstHomeBuyer: isFirstHomeBuyer ?? this.isFirstHomeBuyer,
      soldPropertyLongTerm: soldPropertyLongTerm ?? this.soldPropertyLongTerm,
      soldPropertyShortTerm: soldPropertyShortTerm ?? this.soldPropertyShortTerm,
      hasWorkFromHomeExpense: hasWorkFromHomeExpense ?? this.hasWorkFromHomeExpense,
      wasStudentLastYear: wasStudentLastYear ?? this.wasStudentLastYear,
      isUnionMember: isUnionMember ?? this.isUnionMember,
      hasDaycareExpenses: hasDaycareExpenses ?? this.hasDaycareExpenses,
      isFirstTimeFiler: isFirstTimeFiler ?? this.isFirstTimeFiler,
      hasOtherIncome: hasOtherIncome ?? this.hasOtherIncome,
      otherIncomeDescription: otherIncomeDescription ?? this.otherIncomeDescription,
      hasProfessionalDues: hasProfessionalDues ?? this.hasProfessionalDues,
      hasRrspFhsaInvestment: hasRrspFhsaInvestment ?? this.hasRrspFhsaInvestment,
      hasChildArtSportCredit: hasChildArtSportCredit ?? this.hasChildArtSportCredit,
      isProvinceFiler: isProvinceFiler ?? this.isProvinceFiler,
    );
  }
}
