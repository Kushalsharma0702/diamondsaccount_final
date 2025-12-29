"""
Database models for T1 Business Form Data
Matches the Flutter app structure exactly
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class T1FormMain(Base):
    """Main T1 Form table - matches T1FormData from Flutter"""
    __tablename__ = "t1_forms_main"
    
    id = Column(String(50), primary_key=True)  # Format: T1_{timestamp}
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="draft")  # draft, submitted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Boolean flags from questionnaire
    has_foreign_property = Column(Boolean, nullable=True)
    has_medical_expenses = Column(Boolean, nullable=True)
    has_charitable_donations = Column(Boolean, nullable=True)
    has_moving_expenses = Column(Boolean, nullable=True)
    is_self_employed = Column(Boolean, nullable=True)
    is_first_home_buyer = Column(Boolean, nullable=True)
    sold_property_long_term = Column(Boolean, nullable=True)
    sold_property_short_term = Column(Boolean, nullable=True)
    has_work_from_home_expense = Column(Boolean, nullable=True)
    was_student_last_year = Column(Boolean, nullable=True)
    is_union_member = Column(Boolean, nullable=True)
    has_daycare_expenses = Column(Boolean, nullable=True)
    is_first_time_filer = Column(Boolean, nullable=True)
    has_other_income = Column(Boolean, nullable=True)
    other_income_description = Column(Text, nullable=True)
    has_professional_dues = Column(Boolean, nullable=True)
    has_rrsp_fhsa_investment = Column(Boolean, nullable=True)
    has_child_art_sport_credit = Column(Boolean, nullable=True)
    is_province_filer = Column(Boolean, nullable=True)
    
    # Document tracking
    uploaded_documents = Column(JSON, default=dict)  # Map<String, String>
    awaiting_documents = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="t1_forms_main")
    personal_info = relationship("T1PersonalInfo", back_populates="form", uselist=False, cascade="all, delete-orphan")
    foreign_properties = relationship("T1ForeignProperty", back_populates="form", cascade="all, delete-orphan")
    moving_expense = relationship("T1MovingExpense", back_populates="form", uselist=False, cascade="all, delete-orphan")
    moving_expense_individual = relationship("T1MovingExpenseIndividual", back_populates="form", uselist=False, cascade="all, delete-orphan")
    moving_expense_spouse = relationship("T1MovingExpenseSpouse", back_populates="form", uselist=False, cascade="all, delete-orphan")
    self_employment = relationship("T1SelfEmployment", back_populates="form", uselist=False, cascade="all, delete-orphan")


class T1PersonalInfo(Base):
    """Personal Information - matches T1PersonalInfo from Flutter"""
    __tablename__ = "t1_personal_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False, unique=True)
    
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    sin = Column(String(20), nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    is_canadian_citizen = Column(Boolean, nullable=True)
    marital_status = Column(String(20), nullable=False)  # single, married, common-law, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="personal_info")
    spouse_info = relationship("T1SpouseInfo", back_populates="personal_info", uselist=False, cascade="all, delete-orphan")
    children = relationship("T1ChildInfo", back_populates="personal_info", cascade="all, delete-orphan")


class T1SpouseInfo(Base):
    """Spouse Information"""
    __tablename__ = "t1_spouse_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personal_info_id = Column(UUID(as_uuid=True), ForeignKey("t1_personal_info.id"), nullable=False, unique=True)
    
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    sin = Column(String(20), nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    personal_info = relationship("T1PersonalInfo", back_populates="spouse_info")


class T1ChildInfo(Base):
    """Child Information"""
    __tablename__ = "t1_child_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    personal_info_id = Column(UUID(as_uuid=True), ForeignKey("t1_personal_info.id"), nullable=False)
    
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    sin = Column(String(20), nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    personal_info = relationship("T1PersonalInfo", back_populates="children")


class T1ForeignProperty(Base):
    """Foreign Property Information"""
    __tablename__ = "t1_foreign_properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False)
    
    investment_details = Column(Text, nullable=True)
    gross_income = Column(Float, default=0.0)
    gain_loss_on_sale = Column(Float, default=0.0)
    max_cost_during_year = Column(Float, default=0.0)
    cost_amount_year_end = Column(Float, default=0.0)
    country = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="foreign_properties")


class T1MovingExpense(Base):
    """Moving Expense (Legacy)"""
    __tablename__ = "t1_moving_expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False, unique=True)
    
    individual = Column(String(100), nullable=True)
    old_address = Column(Text, nullable=True)
    new_address = Column(Text, nullable=True)
    distance_from_old_to_new = Column(String(50), nullable=True)
    distance_from_new_to_office = Column(String(50), nullable=True)
    air_ticket_cost = Column(Float, default=0.0)
    movers_and_packers = Column(Float, default=0.0)
    meals_and_other_cost = Column(Float, default=0.0)
    any_other_cost = Column(Float, default=0.0)
    date_of_travel = Column(DateTime(timezone=True), nullable=True)
    date_of_joining = Column(DateTime(timezone=True), nullable=True)
    company_name = Column(String(200), nullable=True)
    new_employer_address = Column(Text, nullable=True)
    gross_income_after_moving = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="moving_expense")


class T1MovingExpenseIndividual(Base):
    """Moving Expense for Individual"""
    __tablename__ = "t1_moving_expenses_individual"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False, unique=True)
    
    individual = Column(String(100), nullable=True)
    old_address = Column(Text, nullable=True)
    new_address = Column(Text, nullable=True)
    distance_from_old_to_new = Column(String(50), nullable=True)
    distance_from_new_to_office = Column(String(50), nullable=True)
    air_ticket_cost = Column(Float, default=0.0)
    movers_and_packers = Column(Float, default=0.0)
    meals_and_other_cost = Column(Float, default=0.0)
    any_other_cost = Column(Float, default=0.0)
    date_of_travel = Column(DateTime(timezone=True), nullable=True)
    date_of_joining = Column(DateTime(timezone=True), nullable=True)
    company_name = Column(String(200), nullable=True)
    new_employer_address = Column(Text, nullable=True)
    gross_income_after_moving = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="moving_expense_individual")


class T1MovingExpenseSpouse(Base):
    """Moving Expense for Spouse"""
    __tablename__ = "t1_moving_expenses_spouse"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False, unique=True)
    
    individual = Column(String(100), nullable=True)
    old_address = Column(Text, nullable=True)
    new_address = Column(Text, nullable=True)
    distance_from_old_to_new = Column(String(50), nullable=True)
    distance_from_new_to_office = Column(String(50), nullable=True)
    air_ticket_cost = Column(Float, default=0.0)
    movers_and_packers = Column(Float, default=0.0)
    meals_and_other_cost = Column(Float, default=0.0)
    any_other_cost = Column(Float, default=0.0)
    date_of_travel = Column(DateTime(timezone=True), nullable=True)
    date_of_joining = Column(DateTime(timezone=True), nullable=True)
    company_name = Column(String(200), nullable=True)
    new_employer_address = Column(Text, nullable=True)
    gross_income_after_moving = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="moving_expense_spouse")


class T1SelfEmployment(Base):
    """Self Employment wrapper - matches T1SelfEmployment from Flutter"""
    __tablename__ = "t1_self_employment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(String(50), ForeignKey("t1_forms_main.id"), nullable=False, unique=True)
    
    business_types = Column(JSON, default=list)  # List of strings: 'uber', 'general', 'rental'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    form = relationship("T1FormMain", back_populates="self_employment")
    uber_business = relationship("T1UberBusiness", back_populates="self_employment", uselist=False, cascade="all, delete-orphan")
    general_business = relationship("T1GeneralBusiness", back_populates="self_employment", uselist=False, cascade="all, delete-orphan")
    rental_income = relationship("T1RentalIncome", back_populates="self_employment", uselist=False, cascade="all, delete-orphan")


class T1UberBusiness(Base):
    """Uber/Skip/DoorDash Business Details - matches T1UberBusinessExtended from Flutter"""
    __tablename__ = "t1_uber_business"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    self_employment_id = Column(UUID(as_uuid=True), ForeignKey("t1_self_employment.id"), nullable=False, unique=True)
    
    # Business Info
    uber_skip_statement = Column(String(200), nullable=True)
    business_hst_number = Column(String(50), nullable=True)
    hst_access_code = Column(String(50), nullable=True)
    hst_filling_period = Column(String(50), nullable=True)
    
    # Income
    total_km_for_uber_skip = Column(Float, default=0.0)
    total_official_km_driven = Column(Float, default=0.0)
    total_km_driven_entire_year = Column(Float, default=0.0)
    
    # Expenses
    business_number_vehicle_registration = Column(Float, default=0.0)
    meals = Column(Float, default=0.0)
    telephone = Column(Float, default=0.0)
    parking_fees = Column(Float, default=0.0)
    cleaning_expenses = Column(Float, default=0.0)
    safety_inspection = Column(Float, default=0.0)
    winter_tire_change = Column(Float, default=0.0)
    oil_change_and_maintenance = Column(Float, default=0.0)
    depreciation = Column(Float, default=0.0)
    insurance_on_vehicle = Column(Float, default=0.0)
    gas = Column(Float, default=0.0)
    financing_cost_interest = Column(Float, default=0.0)
    lease_cost = Column(Float, default=0.0)
    other_expense1 = Column(Float, default=0.0)
    other_expense2 = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    self_employment = relationship("T1SelfEmployment", back_populates="uber_business")


class T1GeneralBusiness(Base):
    """General Business Details - matches T1GeneralBusinessExtended from Flutter"""
    __tablename__ = "t1_general_business"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    self_employment_id = Column(UUID(as_uuid=True), ForeignKey("t1_self_employment.id"), nullable=False, unique=True)
    
    client_name = Column(String(200), nullable=True)
    business_name = Column(String(200), nullable=True)
    
    # Income
    sales_commissions_fees = Column(Float, default=0.0)
    minus_hst_collected = Column(Float, default=0.0)
    gross_income = Column(Float, default=0.0)
    
    # Cost of Goods Sold
    opening_inventory = Column(Float, default=0.0)
    purchases_during_year = Column(Float, default=0.0)
    subcontracts = Column(Float, default=0.0)
    direct_wage_costs = Column(Float, default=0.0)
    other_costs = Column(Float, default=0.0)
    purchase_returns = Column(Float, default=0.0)
    
    # Expenses
    advertising = Column(Float, default=0.0)
    meals_entertainment = Column(Float, default=0.0)
    bad_debts = Column(Float, default=0.0)
    insurance = Column(Float, default=0.0)
    interest = Column(Float, default=0.0)
    fees_licenses_dues = Column(Float, default=0.0)
    office_expenses = Column(Float, default=0.0)
    supplies = Column(Float, default=0.0)
    legal_accounting_fees = Column(Float, default=0.0)
    management_administration = Column(Float, default=0.0)
    office_rent = Column(Float, default=0.0)
    maintenance_repairs = Column(Float, default=0.0)
    salaries_wages_benefits = Column(Float, default=0.0)
    property_tax = Column(Float, default=0.0)
    travel = Column(Float, default=0.0)
    telephone_utilities = Column(Float, default=0.0)
    fuel_costs = Column(Float, default=0.0)
    delivery_freight_express = Column(Float, default=0.0)
    other_expense1 = Column(Float, default=0.0)
    other_expense2 = Column(Float, default=0.0)
    other_expense3 = Column(Float, default=0.0)
    
    # Office-In-House Expenses
    area_of_home_for_business = Column(String(50), nullable=True)
    total_area_of_home = Column(String(50), nullable=True)
    heat = Column(Float, default=0.0)
    electricity = Column(Float, default=0.0)
    house_insurance = Column(Float, default=0.0)
    home_maintenance = Column(Float, default=0.0)
    mortgage_interest = Column(Float, default=0.0)
    property_taxes = Column(Float, default=0.0)
    house_rent = Column(Float, default=0.0)
    home_other_expense1 = Column(Float, default=0.0)
    home_other_expense2 = Column(Float, default=0.0)
    
    # Motor Vehicle Expenses
    km_driven_for_business = Column(Float, default=0.0)
    total_km_driven_in_year = Column(Float, default=0.0)
    vehicle_fuel = Column(Float, default=0.0)
    vehicle_insurance = Column(Float, default=0.0)
    license_registration = Column(Float, default=0.0)
    vehicle_maintenance = Column(Float, default=0.0)
    business_parking = Column(Float, default=0.0)
    vehicle_other_expense = Column(Float, default=0.0)
    leasing_finance_payments = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    self_employment = relationship("T1SelfEmployment", back_populates="general_business")


class T1RentalIncome(Base):
    """Rental Income Details - matches T1RentalIncomeExtended from Flutter"""
    __tablename__ = "t1_rental_income"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    self_employment_id = Column(UUID(as_uuid=True), ForeignKey("t1_self_employment.id"), nullable=False, unique=True)
    
    property_address = Column(Text, nullable=True)
    co_owner_partner1 = Column(String(200), nullable=True)
    co_owner_partner2 = Column(String(200), nullable=True)
    co_owner_partner3 = Column(String(200), nullable=True)
    number_of_units = Column(Integer, default=0)
    gross_rental_income = Column(Float, default=0.0)
    any_govt_income_relating_to_rental = Column(Float, default=0.0)
    
    # Expenses
    personal_use_portion = Column(String(50), nullable=True)
    house_insurance = Column(Float, default=0.0)
    mortgage_interest = Column(Float, default=0.0)
    property_taxes = Column(Float, default=0.0)
    utilities = Column(Float, default=0.0)
    management_admin_fees = Column(Float, default=0.0)
    repair_and_maintenance = Column(Float, default=0.0)
    cleaning_expense = Column(Float, default=0.0)
    motor_vehicle_expenses = Column(Float, default=0.0)
    legal_professional_fees = Column(Float, default=0.0)
    advertising_promotion = Column(Float, default=0.0)
    other_expense = Column(Float, default=0.0)
    
    # CCA/Depreciation
    purchase_price = Column(Float, default=0.0)
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    addition_deletion_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    self_employment = relationship("T1SelfEmployment", back_populates="rental_income")












