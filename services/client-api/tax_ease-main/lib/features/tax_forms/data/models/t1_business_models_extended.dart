// Extended business models matching exact Excel file structures

// Uber/Skip/DoorDash Business Details (from uberskip_doordash.xlsx)
class T1UberBusinessExtended {
  final String uberSkipStatement;
  final String businessHstNumber;
  final String hstAccessCode;
  final String hstFillingPeriod;
  
  // Income
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
  final double otherExpense1;
  final double otherExpense2;
  
  const T1UberBusinessExtended({
    this.uberSkipStatement = '',
    this.businessHstNumber = '',
    this.hstAccessCode = '',
    this.hstFillingPeriod = '',
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
    this.otherExpense1 = 0.0,
    this.otherExpense2 = 0.0,
  });

  Map<String, dynamic> toJson() => {
    'uberSkipStatement': uberSkipStatement,
    'businessHstNumber': businessHstNumber,
    'hstAccessCode': hstAccessCode,
    'hstFillingPeriod': hstFillingPeriod,
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
    'otherExpense1': otherExpense1,
    'otherExpense2': otherExpense2,
  };

  factory T1UberBusinessExtended.fromJson(Map<String, dynamic> json) => T1UberBusinessExtended(
    uberSkipStatement: json['uberSkipStatement'] ?? '',
    businessHstNumber: json['businessHstNumber'] ?? '',
    hstAccessCode: json['hstAccessCode'] ?? '',
    hstFillingPeriod: json['hstFillingPeriod'] ?? '',
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
    otherExpense1: (json['otherExpense1'] ?? 0.0).toDouble(),
    otherExpense2: (json['otherExpense2'] ?? 0.0).toDouble(),
  );
}

// General Business Details (from business.xlsx)
class T1GeneralBusinessExtended {
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
  
  const T1GeneralBusinessExtended({
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

  Map<String, dynamic> toJson() => {
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

  factory T1GeneralBusinessExtended.fromJson(Map<String, dynamic> json) => T1GeneralBusinessExtended(
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

// Rental Income Details (from rental_income.xlsx)
class T1RentalIncomeExtended {
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
  
  const T1RentalIncomeExtended({
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

  Map<String, dynamic> toJson() => {
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

  factory T1RentalIncomeExtended.fromJson(Map<String, dynamic> json) => T1RentalIncomeExtended(
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
