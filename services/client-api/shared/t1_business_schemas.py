"""
Pydantic schemas for T1 Business Form Data
Matches the Flutter app structure exactly
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID


# Personal Information Schemas
class T1SpouseInfoSchema(BaseModel):
    firstName: str = ""
    middleName: Optional[str] = None
    lastName: str = ""
    sin: str = ""
    dateOfBirth: Optional[datetime] = None

    class Config:
        from_attributes = True


class T1ChildInfoSchema(BaseModel):
    firstName: str = ""
    middleName: Optional[str] = None
    lastName: str = ""
    sin: str = ""
    dateOfBirth: Optional[datetime] = None

    class Config:
        from_attributes = True


class T1PersonalInfoSchema(BaseModel):
    firstName: str = ""
    middleName: Optional[str] = None
    lastName: str = ""
    sin: str = ""
    dateOfBirth: Optional[datetime] = None
    address: str = ""
    phoneNumber: str = ""
    email: EmailStr
    isCanadianCitizen: Optional[bool] = None
    maritalStatus: str = ""
    spouseInfo: Optional[T1SpouseInfoSchema] = None
    children: List[T1ChildInfoSchema] = []

    class Config:
        from_attributes = True


# Foreign Property Schema
class T1ForeignPropertySchema(BaseModel):
    investmentDetails: str = ""
    grossIncome: float = 0.0
    gainLossOnSale: float = 0.0
    maxCostDuringYear: float = 0.0
    costAmountYearEnd: float = 0.0
    country: str = ""

    class Config:
        from_attributes = True


# Moving Expense Schema
class T1MovingExpenseSchema(BaseModel):
    individual: str = ""
    oldAddress: str = ""
    newAddress: str = ""
    distanceFromOldToNew: str = ""
    distanceFromNewToOffice: str = ""
    airTicketCost: float = 0.0
    moversAndPackers: float = 0.0
    mealsAndOtherCost: float = 0.0
    anyOtherCost: float = 0.0
    dateOfTravel: Optional[datetime] = None
    dateOfJoining: Optional[datetime] = None
    companyName: str = ""
    newEmployerAddress: str = ""
    grossIncomeAfterMoving: float = 0.0

    class Config:
        from_attributes = True


# Self Employment Schemas
class T1UberBusinessSchema(BaseModel):
    uberSkipStatement: str = ""
    businessHstNumber: str = ""
    hstAccessCode: str = ""
    hstFillingPeriod: str = ""
    totalKmForUberSkip: float = 0.0
    totalOfficialKmDriven: float = 0.0
    totalKmDrivenEntireYear: float = 0.0
    businessNumberVehicleRegistration: float = 0.0
    meals: float = 0.0
    telephone: float = 0.0
    parkingFees: float = 0.0
    cleaningExpenses: float = 0.0
    safetyInspection: float = 0.0
    winterTireChange: float = 0.0
    oilChangeAndMaintenance: float = 0.0
    depreciation: float = 0.0
    insuranceOnVehicle: float = 0.0
    gas: float = 0.0
    financingCostInterest: float = 0.0
    leaseCost: float = 0.0
    otherExpense1: float = 0.0
    otherExpense2: float = 0.0

    class Config:
        from_attributes = True


class T1GeneralBusinessSchema(BaseModel):
    clientName: str = ""
    businessName: str = ""
    salesCommissionsFees: float = 0.0
    minusHstCollected: float = 0.0
    grossIncome: float = 0.0
    openingInventory: float = 0.0
    purchasesDuringYear: float = 0.0
    subcontracts: float = 0.0
    directWageCosts: float = 0.0
    otherCosts: float = 0.0
    purchaseReturns: float = 0.0
    advertising: float = 0.0
    mealsEntertainment: float = 0.0
    badDebts: float = 0.0
    insurance: float = 0.0
    interest: float = 0.0
    feesLicensesDues: float = 0.0
    officeExpenses: float = 0.0
    supplies: float = 0.0
    legalAccountingFees: float = 0.0
    managementAdministration: float = 0.0
    officeRent: float = 0.0
    maintenanceRepairs: float = 0.0
    salariesWagesBenefits: float = 0.0
    propertyTax: float = 0.0
    travel: float = 0.0
    telephoneUtilities: float = 0.0
    fuelCosts: float = 0.0
    deliveryFreightExpress: float = 0.0
    otherExpense1: float = 0.0
    otherExpense2: float = 0.0
    otherExpense3: float = 0.0
    areaOfHomeForBusiness: str = ""
    totalAreaOfHome: str = ""
    heat: float = 0.0
    electricity: float = 0.0
    houseInsurance: float = 0.0
    homeMaintenance: float = 0.0
    mortgageInterest: float = 0.0
    propertyTaxes: float = 0.0
    houseRent: float = 0.0
    homeOtherExpense1: float = 0.0
    homeOtherExpense2: float = 0.0
    kmDrivenForBusiness: float = 0.0
    totalKmDrivenInYear: float = 0.0
    vehicleFuel: float = 0.0
    vehicleInsurance: float = 0.0
    licenseRegistration: float = 0.0
    vehicleMaintenance: float = 0.0
    businessParking: float = 0.0
    vehicleOtherExpense: float = 0.0
    leasingFinancePayments: float = 0.0

    class Config:
        from_attributes = True


class T1RentalIncomeSchema(BaseModel):
    propertyAddress: str = ""
    coOwnerPartner1: str = ""
    coOwnerPartner2: str = ""
    coOwnerPartner3: str = ""
    numberOfUnits: int = 0
    grossRentalIncome: float = 0.0
    anyGovtIncomeRelatingToRental: float = 0.0
    personalUsePortion: str = ""
    houseInsurance: float = 0.0
    mortgageInterest: float = 0.0
    propertyTaxes: float = 0.0
    utilities: float = 0.0
    managementAdminFees: float = 0.0
    repairAndMaintenance: float = 0.0
    cleaningExpense: float = 0.0
    motorVehicleExpenses: float = 0.0
    legalProfessionalFees: float = 0.0
    advertisingPromotion: float = 0.0
    otherExpense: float = 0.0
    purchasePrice: float = 0.0
    purchaseDate: Optional[datetime] = None
    additionDeletionAmount: float = 0.0

    class Config:
        from_attributes = True


class T1SelfEmploymentSchema(BaseModel):
    businessTypes: List[str] = []
    uberBusiness: Optional[T1UberBusinessSchema] = None
    generalBusiness: Optional[T1GeneralBusinessSchema] = None
    rentalIncome: Optional[T1RentalIncomeSchema] = None

    class Config:
        from_attributes = True


# Main T1 Form Schema - matches T1FormData from Flutter
class T1FormDataSchema(BaseModel):
    id: str = ""
    status: str = "draft"  # draft, submitted
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    personalInfo: T1PersonalInfoSchema
    hasForeignProperty: Optional[bool] = None
    foreignProperties: List[T1ForeignPropertySchema] = []
    hasMedicalExpenses: Optional[bool] = None
    medicalExpenses: List[T1MedicalExpenseSchema] = []
    hasCharitableDonations: Optional[bool] = None
    hasMovingExpenses: Optional[bool] = None
    movingExpense: Optional[T1MovingExpenseSchema] = None
    movingExpenseForIndividual: Optional[bool] = None
    movingExpenseForSpouse: Optional[bool] = None
    movingExpenseIndividual: Optional[T1MovingExpenseSchema] = None
    movingExpenseSpouse: Optional[T1MovingExpenseSchema] = None
    isSelfEmployed: Optional[bool] = None
    selfEmployment: Optional[T1SelfEmploymentSchema] = None
    isFirstHomeBuyer: Optional[bool] = None
    soldPropertyLongTerm: Optional[bool] = None
    soldPropertyShortTerm: Optional[bool] = None
    soldPropertyShortTermDetails: Optional[T1SoldPropertyShortTermSchema] = None
    hasWorkFromHomeExpense: Optional[bool] = None
    workFromHomeExpense: Optional[T1WorkFromHomeExpenseSchema] = None
    wasStudentLastYear: Optional[bool] = None
    isUnionMember: Optional[bool] = None
    unionMemberDues: List[T1UnionMemberDueSchema] = []
    hasDaycareExpenses: Optional[bool] = None
    daycareExpenses: List[T1DaycareExpenseSchema] = []
    isFirstTimeFiler: Optional[bool] = None
    firstTimeFiler: Optional[T1FirstTimeFilerSchema] = None
    hasOtherIncome: Optional[bool] = None
    otherIncomeDescription: str = ""
    hasProfessionalDues: Optional[bool] = None
    professionalDues: List[T1ProfessionalDueSchema] = []
    hasRrspFhsaInvestment: Optional[bool] = None
    hasChildArtSportCredit: Optional[bool] = None
    childArtSportCredits: List[T1ChildArtSportCreditSchema] = []
    isProvinceFiler: Optional[bool] = None
    provinceFiler: List[T1ProvinceFilerSchema] = []
    hasDisabilityTaxCredit: Optional[bool] = None
    disabilityTaxCredits: List[T1DisabilityTaxCreditSchema] = []
    isFilingForDeceased: Optional[bool] = None
    deceasedReturnInfo: Optional[T1DeceasedReturnSchema] = None
    uploadedDocuments: Dict[str, str] = {}
    awaitingDocuments: bool = False

    class Config:
        from_attributes = True


# Request/Response Schemas
class T1FormCreateRequest(BaseModel):
    """Request schema for creating/updating T1 form"""
    formData: T1FormDataSchema


class T1FormResponse(BaseModel):
    """Response schema for T1 form"""
    success: bool
    message: str
    formData: Optional[T1FormDataSchema] = None


class T1FormListResponse(BaseModel):
    """Response schema for listing T1 forms"""
    success: bool
    forms: List[T1FormDataSchema] = []
    total: int = 0


class T1FormDeleteResponse(BaseModel):
    """Response schema for deleting T1 form"""
    success: bool
    message: str


# Medical Expense Schema
class T1MedicalExpenseSchema(BaseModel):
    paymentDate: Optional[datetime] = None
    patientName: str = ""
    paymentMadeTo: str = ""
    descriptionOfExpense: str = ""
    insuranceCovered: float = 0.0
    amountPaidFromPocket: float = 0.0

    class Config:
        from_attributes = True


# Work from Home Expense Schema
class T1WorkFromHomeExpenseSchema(BaseModel):
    totalHouseAreaSqft: float = 0.0
    totalWorkAreaSqft: float = 0.0
    rentExpense: float = 0.0
    mortgageExpense: float = 0.0
    wifiExpense: float = 0.0
    electricityExpense: float = 0.0
    waterExpense: float = 0.0
    heatExpense: float = 0.0
    totalInsuranceExpense: float = 0.0
    # Alternative simplified fields
    rentMortgageExpense: float = 0.0
    utilitiesExpense: float = 0.0

    class Config:
        from_attributes = True


# Daycare Expense Schema
class T1DaycareExpenseSchema(BaseModel):
    childcareProvider: str = ""
    amount: float = 0.0
    identificationNumberSin: str = ""
    weeks: int = 0

    class Config:
        from_attributes = True


# First Time Filer Schema
class T1FirstTimeFilerSchema(BaseModel):
    dateOfLandingIndividual: Optional[datetime] = None
    incomeOutsideCanadaCad: float = 0.0
    backHomeIncome2024Cad: float = 0.0
    backHomeIncome2023Cad: float = 0.0

    class Config:
        from_attributes = True


# Province Filer Schema
class T1ProvinceFilerSchema(BaseModel):
    rentOrPropertyTax: str = ""
    propertyAddress: str = ""
    postalCode: str = ""
    numberOfMonthsResides: int = 0
    amountPaid: float = 0.0

    class Config:
        from_attributes = True


# Sold Property Short Term Schema
class T1SoldPropertyShortTermSchema(BaseModel):
    propertyAddress: str = ""
    purchaseDate: Optional[datetime] = None
    sellDate: Optional[datetime] = None
    purchaseAndSellExpenses: float = 0.0

    class Config:
        from_attributes = True


# Union Member Due Schema
class T1UnionMemberDueSchema(BaseModel):
    institutionName: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


# Professional Due Schema
class T1ProfessionalDueSchema(BaseModel):
    name: str = ""
    organization: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


# Child Art/Sport Credit Schema
class T1ChildArtSportCreditSchema(BaseModel):
    instituteName: str = ""
    description: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


# Disability Tax Credit Schema
class T1DisabilityTaxCreditSchema(BaseModel):
    firstName: str = ""
    lastName: str = ""
    relation: str = ""
    approvedYear: int = 0

    class Config:
        from_attributes = True


# Deceased Return Schema
class T1DeceasedReturnSchema(BaseModel):
    deceasedFullName: str = ""
    dateOfDeath: Optional[datetime] = None
    deceasedSin: str = ""
    deceasedMailingAddress: str = ""
    legalRepresentativeName: str = ""
    legalRepresentativeContactNumber: str = ""
    legalRepresentativeAddress: str = ""

    class Config:
        from_attributes = True














