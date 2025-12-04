"""
Enhanced T1 Personal Tax Form Schemas with comprehensive validation
Based on the provided JSON schema and sample data
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, List, Union
from datetime import date, datetime
from enum import Enum

# Enums for validation
class FormStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"

class MaritalStatus(str, Enum):
    single = "single"
    married = "married"
    divorced = "divorced"
    widowed = "widowed"
    common_law = "common_law"

class BusinessType(str, Enum):
    uber = "uber"
    general = "general"
    rental = "rental"

# Base schema for common fields
class BaseT1Schema(BaseModel):
    class Config:
        from_attributes = True
        str_strip_whitespace = True

# Child schemas for nested objects
class T1SpouseInfo(BaseT1Schema):
    firstName: str = Field(..., min_length=1)
    middleName: Optional[str] = None
    lastName: str = Field(..., min_length=1)
    sin: str = Field(..., pattern=r'^\d{9}$')
    dateOfBirth: Optional[date] = None

class T1ChildInfo(BaseT1Schema):
    firstName: str = Field(..., min_length=1)
    middleName: Optional[str] = None
    lastName: str = Field(..., min_length=1)
    sin: str = Field(..., pattern=r'^\d{9}$')
    dateOfBirth: Optional[date] = None

class T1ForeignProperty(BaseT1Schema):
    investmentDetails: str
    grossIncome: float = Field(..., ge=0)
    gainLossOnSale: float
    maxCostDuringYear: float = Field(..., ge=0)
    costAmountYearEnd: float = Field(..., ge=0)
    country: str

class T1MovingExpense(BaseT1Schema):
    individual: str
    oldAddress: str
    newAddress: str
    distanceFromOldToNew: str
    distanceFromNewToOffice: str
    airTicketCost: float = Field(..., ge=0)
    moversAndPackers: float = Field(..., ge=0)
    mealsAndOtherCost: float = Field(..., ge=0)
    anyOtherCost: float = Field(..., ge=0)
    dateOfTravel: Optional[date] = None
    dateOfJoining: Optional[date] = None
    companyName: str
    newEmployerAddress: str
    grossIncomeAfterMoving: float = Field(..., ge=0)

class T1UberBusiness(BaseT1Schema):
    uberSkipStatement: str
    businessHstNumber: str
    hstAccessCode: str
    hstFillingPeriod: str
    income: float = Field(..., ge=0)
    totalKmForUberSkip: float = Field(..., ge=0)
    totalOfficialKmDriven: float = Field(..., ge=0)
    totalKmDrivenEntireYear: float = Field(..., ge=0)
    businessNumberVehicleRegistration: float = Field(..., ge=0)
    meals: float = Field(..., ge=0)
    telephone: float = Field(..., ge=0)
    parkingFees: float = Field(..., ge=0)
    cleaningExpenses: float = Field(..., ge=0)
    safetyInspection: float = Field(..., ge=0)
    winterTireChange: float = Field(..., ge=0)
    oilChangeAndMaintenance: float = Field(..., ge=0)
    depreciation: float = Field(..., ge=0)
    insuranceOnVehicle: float = Field(..., ge=0)
    gas: float = Field(..., ge=0)
    financingCostInterest: float = Field(..., ge=0)
    leaseCost: float = Field(..., ge=0)
    otherExpense: float = Field(..., ge=0)

class T1GeneralBusiness(BaseT1Schema):
    clientName: str
    businessName: str
    salesCommissionsFees: Optional[float] = Field(default=0, ge=0)
    minusHstCollected: Optional[float] = Field(default=0, ge=0)
    grossIncome: Optional[float] = 0
    openingInventory: Optional[float] = Field(default=0, ge=0)
    purchasesDuringYear: Optional[float] = Field(default=0, ge=0)
    subcontracts: Optional[float] = Field(default=0, ge=0)
    directWageCosts: Optional[float] = Field(default=0, ge=0)
    otherCosts: Optional[float] = Field(default=0, ge=0)
    purchaseReturns: Optional[float] = Field(default=0, ge=0)
    advertising: Optional[float] = Field(default=0, ge=0)
    mealsEntertainment: Optional[float] = Field(default=0, ge=0)
    badDebts: Optional[float] = Field(default=0, ge=0)
    insurance: Optional[float] = Field(default=0, ge=0)
    interest: Optional[float] = Field(default=0, ge=0)
    feesLicensesDues: Optional[float] = Field(default=0, ge=0)
    officeExpenses: Optional[float] = Field(default=0, ge=0)
    supplies: Optional[float] = Field(default=0, ge=0)
    legalAccountingFees: Optional[float] = Field(default=0, ge=0)
    managementAdministration: Optional[float] = Field(default=0, ge=0)
    officeRent: Optional[float] = Field(default=0, ge=0)
    maintenanceRepairs: Optional[float] = Field(default=0, ge=0)
    salariesWagesBenefits: Optional[float] = Field(default=0, ge=0)
    propertyTax: Optional[float] = Field(default=0, ge=0)
    travel: Optional[float] = Field(default=0, ge=0)
    telephoneUtilities: Optional[float] = Field(default=0, ge=0)
    fuelCosts: Optional[float] = Field(default=0, ge=0)
    deliveryFreightExpress: Optional[float] = Field(default=0, ge=0)
    otherExpense1: Optional[float] = Field(default=0, ge=0)
    otherExpense2: Optional[float] = Field(default=0, ge=0)
    otherExpense3: Optional[float] = Field(default=0, ge=0)
    
    # Home office expenses
    areaOfHomeForBusiness: Optional[str] = None
    totalAreaOfHome: Optional[str] = None
    heat: Optional[float] = Field(default=0, ge=0)
    electricity: Optional[float] = Field(default=0, ge=0)
    houseInsurance: Optional[float] = Field(default=0, ge=0)
    homeMaintenance: Optional[float] = Field(default=0, ge=0)
    mortgageInterest: Optional[float] = Field(default=0, ge=0)
    propertyTaxes: Optional[float] = Field(default=0, ge=0)
    houseRent: Optional[float] = Field(default=0, ge=0)
    homeOtherExpense1: Optional[float] = Field(default=0, ge=0)
    homeOtherExpense2: Optional[float] = Field(default=0, ge=0)
    
    # Vehicle expenses
    kmDrivenForBusiness: Optional[float] = Field(default=0, ge=0)
    totalKmDrivenInYear: Optional[float] = Field(default=0, ge=0)
    vehicleFuel: Optional[float] = Field(default=0, ge=0)
    vehicleInsurance: Optional[float] = Field(default=0, ge=0)
    licenseRegistration: Optional[float] = Field(default=0, ge=0)
    vehicleMaintenance: Optional[float] = Field(default=0, ge=0)
    businessParking: Optional[float] = Field(default=0, ge=0)
    vehicleOtherExpense: Optional[float] = Field(default=0, ge=0)
    leasingFinancePayments: Optional[float] = Field(default=0, ge=0)

class T1RentalIncome(BaseT1Schema):
    propertyAddress: str
    coOwnerPartner1: Optional[str] = None
    coOwnerPartner2: Optional[str] = None
    coOwnerPartner3: Optional[str] = None
    numberOfUnits: int = Field(..., ge=0)
    grossRentalIncome: float = Field(..., ge=0)
    anyGovtIncomeRelatingToRental: float = Field(..., ge=0)
    personalUsePortion: str
    houseInsurance: float = Field(..., ge=0)
    mortgageInterest: float = Field(..., ge=0)
    propertyTaxes: float = Field(..., ge=0)
    utilities: float = Field(..., ge=0)
    managementAdminFees: float = Field(..., ge=0)
    repairAndMaintenance: float = Field(..., ge=0)
    cleaningExpense: float = Field(..., ge=0)
    motorVehicleExpenses: float = Field(..., ge=0)
    legalProfessionalFees: float = Field(..., ge=0)
    advertisingPromotion: float = Field(..., ge=0)
    otherExpense: float = Field(..., ge=0)
    purchasePrice: float = Field(..., ge=0)
    purchaseDate: Optional[date] = None
    additionDeletionAmount: float

class T1SelfEmployment(BaseT1Schema):
    businessTypes: List[BusinessType]
    uberBusiness: Optional[T1UberBusiness] = None
    generalBusiness: Optional[T1GeneralBusiness] = None
    rentalIncome: Optional[T1RentalIncome] = None
    
    @model_validator(mode='after')
    def validate_business_types(self):
        """Validate that business sections match business types"""
        errors = []
        business_types = self.businessTypes or []
        
        if BusinessType.uber in business_types and not self.uberBusiness:
            errors.append('uberBusiness is required when businessTypes includes "uber"')
        if BusinessType.general in business_types and not self.generalBusiness:
            errors.append('generalBusiness is required when businessTypes includes "general"')
        if BusinessType.rental in business_types and not self.rentalIncome:
            errors.append('rentalIncome is required when businessTypes includes "rental"')
        
        if errors:
            raise ValueError('; '.join(errors))
        
        return self

class T1PersonalInfo(BaseT1Schema):
    firstName: str = Field(..., min_length=1)
    middleName: Optional[str] = None
    lastName: str = Field(..., min_length=1)
    sin: str = Field(..., pattern=r'^\d{9}$')
    dateOfBirth: Optional[date] = None
    address: str = Field(..., min_length=1)
    phoneNumber: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    email: EmailStr
    isCanadianCitizen: Optional[bool] = True
    maritalStatus: str = Field(..., min_length=1)
    spouseInfo: Optional[T1SpouseInfo] = None
    children: Optional[List[T1ChildInfo]] = []

# Main T1 Form schemas
class T1PersonalFormBase(BaseT1Schema):
    # Form ID and timestamps (optional for create, required for response)
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    # Personal Information (Required)
    personalInfo: T1PersonalInfo
    
    # Status and metadata
    status: FormStatus = FormStatus.draft
    
    # Foreign Property
    hasForeignProperty: Optional[bool] = False
    foreignProperties: Optional[List[T1ForeignProperty]] = []
    
    # Medical and Charitable
    hasMedicalExpenses: Optional[bool] = False
    hasCharitableDonations: Optional[bool] = False
    
    # Moving Expenses
    hasMovingExpenses: Optional[bool] = False
    movingExpense: Optional[T1MovingExpense] = None
    movingExpenseForIndividual: Optional[bool] = False
    movingExpenseForSpouse: Optional[bool] = False
    movingExpenseIndividual: Optional[T1MovingExpense] = None
    movingExpenseSpouse: Optional[T1MovingExpense] = None
    
    # Self Employment
    isSelfEmployed: Optional[bool] = False
    selfEmployment: Optional[T1SelfEmployment] = None
    
    # Other Income and Deductions
    isFirstHomeBuyer: Optional[bool] = False
    soldPropertyLongTerm: Optional[bool] = False
    soldPropertyShortTerm: Optional[bool] = False
    hasWorkFromHomeExpense: Optional[bool] = False
    wasStudentLastYear: Optional[bool] = False
    isUnionMember: Optional[bool] = False
    hasDaycareExpenses: Optional[bool] = False
    isFirstTimeFiler: Optional[bool] = False
    hasOtherIncome: Optional[bool] = False
    otherIncomeDescription: Optional[str] = None
    hasProfessionalDues: Optional[bool] = False
    hasRrspFhsaInvestment: Optional[bool] = False
    hasChildArtSportCredit: Optional[bool] = False
    isProvinceFiler: Optional[bool] = False
    
    @model_validator(mode='after')
    def validate_conditional_fields(self):
        """Validate all conditional field requirements based on boolean flags"""
        errors = []
        
        # Validate foreignProperties - only check when flag is true
        if self.hasForeignProperty is True:
            if not self.foreignProperties or len(self.foreignProperties) == 0:
                errors.append('foreignProperties array is required when hasForeignProperty is true')
        
        # Validate moving expenses - only check when flags are true
        if self.hasMovingExpenses is True:
            if self.movingExpenseForIndividual is True and not self.movingExpenseIndividual:
                errors.append('movingExpenseIndividual is required when hasMovingExpenses=true and movingExpenseForIndividual=true')
            if self.movingExpenseForSpouse is True and not self.movingExpenseSpouse:
                errors.append('movingExpenseSpouse is required when hasMovingExpenses=true and movingExpenseForSpouse=true')
        
        # Validate self employment - only check when flag is true
        if self.isSelfEmployed is True:
            if not self.selfEmployment:
                errors.append('selfEmployment object is required when isSelfEmployed is true')
            elif self.selfEmployment:
                # Validate business types match provided business sections
                business_types = self.selfEmployment.businessTypes or []
                if BusinessType.uber in business_types and not self.selfEmployment.uberBusiness:
                    errors.append('uberBusiness is required when businessTypes includes "uber"')
                if BusinessType.general in business_types and not self.selfEmployment.generalBusiness:
                    errors.append('generalBusiness is required when businessTypes includes "general"')
                if BusinessType.rental in business_types and not self.selfEmployment.rentalIncome:
                    errors.append('rentalIncome is required when businessTypes includes "rental"')
        
        # Validate other income description - only check when flag is true
        if self.hasOtherIncome is True:
            if not self.otherIncomeDescription or (isinstance(self.otherIncomeDescription, str) and self.otherIncomeDescription.strip() == ''):
                errors.append('otherIncomeDescription is required when hasOtherIncome is true')
        
        if errors:
            raise ValueError('Validation errors: ' + '; '.join(errors))
        
        return self

class T1PersonalFormCreate(T1PersonalFormBase):
    pass

class T1PersonalFormUpdate(BaseT1Schema):
    # All fields optional for updates
    personalInfo: Optional[T1PersonalInfo] = None
    status: Optional[FormStatus] = None
    hasForeignProperty: Optional[bool] = None
    foreignProperties: Optional[List[T1ForeignProperty]] = None
    hasMedicalExpenses: Optional[bool] = None
    hasCharitableDonations: Optional[bool] = None
    hasMovingExpenses: Optional[bool] = None
    movingExpense: Optional[T1MovingExpense] = None
    movingExpenseForIndividual: Optional[bool] = None
    movingExpenseForSpouse: Optional[bool] = None
    movingExpenseIndividual: Optional[T1MovingExpense] = None
    movingExpenseSpouse: Optional[T1MovingExpense] = None
    isSelfEmployed: Optional[bool] = None
    selfEmployment: Optional[T1SelfEmployment] = None
    isFirstHomeBuyer: Optional[bool] = None
    soldPropertyLongTerm: Optional[bool] = None
    soldPropertyShortTerm: Optional[bool] = None
    hasWorkFromHomeExpense: Optional[bool] = None
    wasStudentLastYear: Optional[bool] = None
    isUnionMember: Optional[bool] = None
    hasDaycareExpenses: Optional[bool] = None
    isFirstTimeFiler: Optional[bool] = None
    hasOtherIncome: Optional[bool] = None
    otherIncomeDescription: Optional[str] = None
    hasProfessionalDues: Optional[bool] = None
    hasRrspFhsaInvestment: Optional[bool] = None
    hasChildArtSportCredit: Optional[bool] = None
    isProvinceFiler: Optional[bool] = None

class T1PersonalFormResponse(T1PersonalFormBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Encryption metadata
    is_encrypted: bool = False
    encryption_algorithm: Optional[str] = None

# List response
class T1PersonalFormListResponse(BaseT1Schema):
    forms: List[T1PersonalFormResponse]
    total: int
    offset: int
    limit: int
