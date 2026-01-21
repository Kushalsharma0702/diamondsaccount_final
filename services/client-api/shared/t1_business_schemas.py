"""
Pydantic schemas for T1 Business Form Data
Matches the Flutter app structure exactly
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# -------------------------
# BASIC / SUPPORT SCHEMAS
# -------------------------

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
    children: List[T1ChildInfoSchema] = Field(default_factory=list)

    class Config:
        from_attributes = True


class T1ForeignPropertySchema(BaseModel):
    investmentDetails: str = ""
    grossIncome: float = 0.0
    gainLossOnSale: float = 0.0
    maxCostDuringYear: float = 0.0
    costAmountYearEnd: float = 0.0
    country: str = ""

    class Config:
        from_attributes = True


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


# -------------------------
# MEDICAL & EXPENSE SCHEMAS
# -------------------------

class T1MedicalExpenseSchema(BaseModel):
    paymentDate: Optional[datetime] = None
    patientName: str = ""
    paymentMadeTo: str = ""
    descriptionOfExpense: str = ""
    insuranceCovered: float = 0.0
    amountPaidFromPocket: float = 0.0

    class Config:
        from_attributes = True


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
    rentMortgageExpense: float = 0.0
    utilitiesExpense: float = 0.0

    class Config:
        from_attributes = True


class T1DaycareExpenseSchema(BaseModel):
    childcareProvider: str = ""
    amount: float = 0.0
    identificationNumberSin: str = ""
    weeks: int = 0

    class Config:
        from_attributes = True


class T1UnionMemberDueSchema(BaseModel):
    institutionName: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


class T1ProfessionalDueSchema(BaseModel):
    name: str = ""
    organization: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


class T1ChildArtSportCreditSchema(BaseModel):
    instituteName: str = ""
    description: str = ""
    amount: float = 0.0

    class Config:
        from_attributes = True


class T1DisabilityTaxCreditSchema(BaseModel):
    firstName: str = ""
    lastName: str = ""
    relation: str = ""
    approvedYear: int = 0

    class Config:
        from_attributes = True


class T1FirstTimeFilerSchema(BaseModel):
    dateOfLandingIndividual: Optional[datetime] = None
    incomeOutsideCanadaCad: float = 0.0
    backHomeIncome2024Cad: float = 0.0
    backHomeIncome2023Cad: float = 0.0

    class Config:
        from_attributes = True


class T1ProvinceFilerSchema(BaseModel):
    rentOrPropertyTax: str = ""
    propertyAddress: str = ""
    postalCode: str = ""
    numberOfMonthsResides: int = 0
    amountPaid: float = 0.0

    class Config:
        from_attributes = True


class T1SoldPropertyShortTermSchema(BaseModel):
    propertyAddress: str = ""
    purchaseDate: Optional[datetime] = None
    sellDate: Optional[datetime] = None
    purchaseAndSellExpenses: float = 0.0

    class Config:
        from_attributes = True


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


# -------------------------
# BUSINESS SCHEMAS
# -------------------------

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

    class Config:
        from_attributes = True


class T1RentalIncomeSchema(BaseModel):
    propertyAddress: str = ""
    grossRentalIncome: float = 0.0

    class Config:
        from_attributes = True


class T1SelfEmploymentSchema(BaseModel):
    businessTypes: List[str] = Field(default_factory=list)
    uberBusiness: Optional[T1UberBusinessSchema] = None
    generalBusiness: Optional[T1GeneralBusinessSchema] = None
    rentalIncome: Optional[T1RentalIncomeSchema] = None

    class Config:
        from_attributes = True


# -------------------------
# MAIN FORM SCHEMA (LAST)
# -------------------------

class T1FormDataSchema(BaseModel):
    id: str = ""
    status: str = "draft"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    personalInfo: T1PersonalInfoSchema

    hasForeignProperty: Optional[bool] = None
    foreignProperties: List[T1ForeignPropertySchema] = Field(default_factory=list)

    hasMedicalExpenses: Optional[bool] = None
    medicalExpenses: List[T1MedicalExpenseSchema] = Field(default_factory=list)

    hasMovingExpenses: Optional[bool] = None
    movingExpense: Optional[T1MovingExpenseSchema] = None

    isSelfEmployed: Optional[bool] = None
    selfEmployment: Optional[T1SelfEmploymentSchema] = None

    hasWorkFromHomeExpense: Optional[bool] = None
    workFromHomeExpense: Optional[T1WorkFromHomeExpenseSchema] = None

    unionMemberDues: List[T1UnionMemberDueSchema] = Field(default_factory=list)
    daycareExpenses: List[T1DaycareExpenseSchema] = Field(default_factory=list)

    uploadedDocuments: Dict[str, str] = Field(default_factory=dict)
    awaitingDocuments: bool = False

    class Config:
        from_attributes = True

# -------------------------
# REQUEST / RESPONSE SCHEMAS
# -------------------------

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
    forms: List[T1FormDataSchema] = Field(default_factory=list)
    total: int = 0


class T1FormDeleteResponse(BaseModel):
    """Response schema for deleting T1 form"""
    success: bool
    message: str
