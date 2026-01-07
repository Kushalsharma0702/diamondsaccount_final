"""
T1 Business Form API Routes
Handles saving and loading T1 form data matching Flutter app structure
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List, Optional
import logging

from shared.database import get_db
from shared.models import User
from shared.t1_business_models import (
    T1FormMain, T1PersonalInfo, T1SpouseInfo, T1ChildInfo,
    T1ForeignProperty, T1MovingExpense, T1MovingExpenseIndividual, T1MovingExpenseSpouse,
    T1SelfEmployment, T1UberBusiness, T1GeneralBusiness, T1RentalIncome,
    T1MedicalExpense, T1WorkFromHomeExpense, T1DaycareExpense, T1FirstTimeFiler,
    T1ProvinceFiler, T1SoldPropertyShortTerm, T1UnionMemberDue, T1ProfessionalDue,
    T1ChildArtSportCredit, T1DisabilityTaxCredit, T1DeceasedReturn
)
from shared.t1_business_schemas import (
    T1FormDataSchema, T1FormCreateRequest, T1FormResponse,
    T1FormListResponse, T1FormDeleteResponse
)
from shared.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/t1-forms-business", tags=["T1 Business Forms"])


def convert_form_data_to_db(form_data: T1FormDataSchema, user_id: str, db_form: Optional[T1FormMain] = None) -> T1FormMain:
    """Convert Pydantic schema to database model"""
    if db_form is None:
        db_form = T1FormMain(
            id=form_data.id or f"T1_{int(datetime.utcnow().timestamp() * 1000)}",
            user_id=user_id,
            status=form_data.status or "draft"
        )
    
    # Update main form fields
    db_form.status = form_data.status
    db_form.has_foreign_property = form_data.hasForeignProperty
    db_form.has_medical_expenses = form_data.hasMedicalExpenses
    db_form.has_charitable_donations = form_data.hasCharitableDonations
    db_form.has_moving_expenses = form_data.hasMovingExpenses
    db_form.is_self_employed = form_data.isSelfEmployed
    db_form.is_first_home_buyer = form_data.isFirstHomeBuyer
    db_form.sold_property_long_term = form_data.soldPropertyLongTerm
    db_form.sold_property_short_term = form_data.soldPropertyShortTerm
    db_form.has_work_from_home_expense = form_data.hasWorkFromHomeExpense
    db_form.was_student_last_year = form_data.wasStudentLastYear
    db_form.is_union_member = form_data.isUnionMember
    db_form.has_daycare_expenses = form_data.hasDaycareExpenses
    db_form.is_first_time_filer = form_data.isFirstTimeFiler
    db_form.has_other_income = form_data.hasOtherIncome
    db_form.other_income_description = form_data.otherIncomeDescription
    db_form.has_professional_dues = form_data.hasProfessionalDues
    db_form.has_rrsp_fhsa_investment = form_data.hasRrspFhsaInvestment
    db_form.has_child_art_sport_credit = form_data.hasChildArtSportCredit
    db_form.is_province_filer = form_data.isProvinceFiler
    db_form.has_disability_tax_credit = form_data.hasDisabilityTaxCredit
    db_form.is_filing_for_deceased = form_data.isFilingForDeceased
    db_form.uploaded_documents = form_data.uploadedDocuments
    db_form.awaiting_documents = form_data.awaitingDocuments
    db_form.updated_at = datetime.utcnow()
    
    return db_form


def convert_db_to_form_data(db_form: T1FormMain) -> T1FormDataSchema:
    """Convert database model to Pydantic schema"""
    from shared.t1_business_schemas import (
        T1PersonalInfoSchema, T1SpouseInfoSchema, T1ChildInfoSchema,
        T1ForeignPropertySchema, T1MovingExpenseSchema, T1SelfEmploymentSchema,
        T1UberBusinessSchema, T1GeneralBusinessSchema, T1RentalIncomeSchema,
        T1MedicalExpenseSchema, T1WorkFromHomeExpenseSchema, T1DaycareExpenseSchema,
        T1FirstTimeFilerSchema, T1ProvinceFilerSchema, T1SoldPropertyShortTermSchema,
        T1UnionMemberDueSchema, T1ProfessionalDueSchema, T1ChildArtSportCreditSchema,
        T1DisabilityTaxCreditSchema, T1DeceasedReturnSchema
    )
    
    # Convert personal info
    personal_info = None
    if db_form.personal_info:
        spouse_info = None
        if db_form.personal_info.spouse_info:
            spouse_info = T1SpouseInfoSchema(
                firstName=db_form.personal_info.spouse_info.first_name,
                middleName=db_form.personal_info.spouse_info.middle_name,
                lastName=db_form.personal_info.spouse_info.last_name,
                sin=db_form.personal_info.spouse_info.sin,
                dateOfBirth=db_form.personal_info.spouse_info.date_of_birth
            )
        
        children = [
            T1ChildInfoSchema(
                firstName=child.first_name,
                middleName=child.middle_name,
                lastName=child.last_name,
                sin=child.sin,
                dateOfBirth=child.date_of_birth
            )
            for child in db_form.personal_info.children
        ]
        
        personal_info = T1PersonalInfoSchema(
            firstName=db_form.personal_info.first_name,
            middleName=db_form.personal_info.middle_name,
            lastName=db_form.personal_info.last_name,
            sin=db_form.personal_info.sin,
            dateOfBirth=db_form.personal_info.date_of_birth,
            address=db_form.personal_info.address,
            phoneNumber=db_form.personal_info.phone_number,
            email=db_form.personal_info.email,
            isCanadianCitizen=db_form.personal_info.is_canadian_citizen,
            maritalStatus=db_form.personal_info.marital_status,
            spouseInfo=spouse_info,
            children=children
        )
    
    # Convert foreign properties
    foreign_properties = [
        T1ForeignPropertySchema(
            investmentDetails=fp.investment_details or "",
            grossIncome=fp.gross_income or 0.0,
            gainLossOnSale=fp.gain_loss_on_sale or 0.0,
            maxCostDuringYear=fp.max_cost_during_year or 0.0,
            costAmountYearEnd=fp.cost_amount_year_end or 0.0,
            country=fp.country or ""
        )
        for fp in (db_form.foreign_properties or [])
    ]
    
    # Convert medical expenses
    medical_expenses = [
        T1MedicalExpenseSchema(
            paymentDate=me.payment_date,
            patientName=me.patient_name or "",
            paymentMadeTo=me.payment_made_to or "",
            descriptionOfExpense=me.description_of_expense or "",
            insuranceCovered=me.insurance_covered or 0.0,
            amountPaidFromPocket=me.amount_paid_from_pocket or 0.0
        )
        for me in (db_form.medical_expenses or [])
    ]
    
    # Convert work from home expense
    work_from_home_expense = None
    if db_form.work_from_home_expense:
        work_from_home_expense = T1WorkFromHomeExpenseSchema(
            totalHouseAreaSqft=db_form.work_from_home_expense.total_house_area_sqft or 0.0,
            totalWorkAreaSqft=db_form.work_from_home_expense.total_work_area_sqft or 0.0,
            rentExpense=db_form.work_from_home_expense.rent_expense or 0.0,
            mortgageExpense=db_form.work_from_home_expense.mortgage_expense or 0.0,
            wifiExpense=db_form.work_from_home_expense.wifi_expense or 0.0,
            electricityExpense=db_form.work_from_home_expense.electricity_expense or 0.0,
            waterExpense=db_form.work_from_home_expense.water_expense or 0.0,
            heatExpense=db_form.work_from_home_expense.heat_expense or 0.0,
            totalInsuranceExpense=db_form.work_from_home_expense.total_insurance_expense or 0.0,
            rentMortgageExpense=db_form.work_from_home_expense.rent_mortgage_expense or 0.0,
            utilitiesExpense=db_form.work_from_home_expense.utilities_expense or 0.0
        )
    
    # Convert daycare expenses
    daycare_expenses = [
        T1DaycareExpenseSchema(
            childcareProvider=de.childcare_provider or "",
            amount=de.amount or 0.0,
            identificationNumberSin=de.identification_number_sin or "",
            weeks=de.weeks or 0
        )
        for de in (db_form.daycare_expenses or [])
    ]
    
    # Convert first time filer
    first_time_filer = None
    if db_form.first_time_filer:
        first_time_filer = T1FirstTimeFilerSchema(
            dateOfLandingIndividual=db_form.first_time_filer.date_of_landing_individual,
            incomeOutsideCanadaCad=db_form.first_time_filer.income_outside_canada_cad or 0.0,
            backHomeIncome2024Cad=db_form.first_time_filer.back_home_income_2024_cad or 0.0,
            backHomeIncome2023Cad=db_form.first_time_filer.back_home_income_2023_cad or 0.0
        )
    
    # Convert province filer
    province_filer = [
        T1ProvinceFilerSchema(
            rentOrPropertyTax=pf.rent_or_property_tax or "",
            propertyAddress=pf.property_address or "",
            postalCode=pf.postal_code or "",
            numberOfMonthsResides=pf.number_of_months_resides or 0,
            amountPaid=pf.amount_paid or 0.0
        )
        for pf in (db_form.province_filer or [])
    ]
    
    # Convert sold property short term
    sold_property_short_term_details = None
    if db_form.sold_property_short_term:
        sold_property_short_term_details = T1SoldPropertyShortTermSchema(
            propertyAddress=db_form.sold_property_short_term.property_address or "",
            purchaseDate=db_form.sold_property_short_term.purchase_date,
            sellDate=db_form.sold_property_short_term.sell_date,
            purchaseAndSellExpenses=db_form.sold_property_short_term.purchase_and_sell_expenses or 0.0
        )
    
    # Convert union member dues
    union_member_dues = [
        T1UnionMemberDueSchema(
            institutionName=umd.institution_name or "",
            amount=umd.amount or 0.0
        )
        for umd in (db_form.union_member_dues or [])
    ]
    
    # Convert professional dues
    professional_dues = [
        T1ProfessionalDueSchema(
            name=pd.name or "",
            organization=pd.organization or "",
            amount=pd.amount or 0.0
        )
        for pd in (db_form.professional_dues or [])
    ]
    
    # Convert child art/sport credits
    child_art_sport_credits = [
        T1ChildArtSportCreditSchema(
            instituteName=casc.institute_name or "",
            description=casc.description or "",
            amount=casc.amount or 0.0
        )
        for casc in (db_form.child_art_sport_credits or [])
    ]
    
    # Convert disability tax credits
    disability_tax_credits = [
        T1DisabilityTaxCreditSchema(
            firstName=dtc.first_name or "",
            lastName=dtc.last_name or "",
            relation=dtc.relation or "",
            approvedYear=dtc.approved_year or 0
        )
        for dtc in (db_form.disability_tax_credits or [])
    ]
    
    # Convert deceased return
    deceased_return_info = None
    if db_form.deceased_return:
        deceased_return_info = T1DeceasedReturnSchema(
            deceasedFullName=db_form.deceased_return.deceased_full_name or "",
            dateOfDeath=db_form.deceased_return.date_of_death,
            deceasedSin=db_form.deceased_return.deceased_sin or "",
            deceasedMailingAddress=db_form.deceased_return.deceased_mailing_address or "",
            legalRepresentativeName=db_form.deceased_return.legal_representative_name or "",
            legalRepresentativeContactNumber=db_form.deceased_return.legal_representative_contact_number or "",
            legalRepresentativeAddress=db_form.deceased_return.legal_representative_address or ""
        )
    
    # Convert moving expenses (simplified - full implementation needed)
    moving_expense = None
    moving_expense_individual = None
    moving_expense_spouse = None
    
    # Convert self employment (simplified - full implementation needed)
    self_employment = None
    
    # Build the full form data
    return T1FormDataSchema(
        id=db_form.id,
        status=db_form.status,
        createdAt=db_form.created_at,
        updatedAt=db_form.updated_at,
        personalInfo=personal_info or T1PersonalInfoSchema(email=""),
        hasForeignProperty=db_form.has_foreign_property,
        foreignProperties=foreign_properties,
        hasMedicalExpenses=db_form.has_medical_expenses,
        medicalExpenses=medical_expenses,
        hasCharitableDonations=db_form.has_charitable_donations,
        hasMovingExpenses=db_form.has_moving_expenses,
        movingExpense=moving_expense,
        movingExpenseForIndividual=db_form.has_moving_expenses,  # Simplified
        movingExpenseForSpouse=None,  # Simplified
        movingExpenseIndividual=moving_expense_individual,
        movingExpenseSpouse=moving_expense_spouse,
        isSelfEmployed=db_form.is_self_employed,
        selfEmployment=self_employment,
        isFirstHomeBuyer=db_form.is_first_home_buyer,
        soldPropertyLongTerm=db_form.sold_property_long_term,
        soldPropertyShortTerm=db_form.sold_property_short_term,
        soldPropertyShortTermDetails=sold_property_short_term_details,
        hasWorkFromHomeExpense=db_form.has_work_from_home_expense,
        workFromHomeExpense=work_from_home_expense,
        wasStudentLastYear=db_form.was_student_last_year,
        isUnionMember=db_form.is_union_member,
        unionMemberDues=union_member_dues,
        hasDaycareExpenses=db_form.has_daycare_expenses,
        daycareExpenses=daycare_expenses,
        isFirstTimeFiler=db_form.is_first_time_filer,
        firstTimeFiler=first_time_filer,
        hasOtherIncome=db_form.has_other_income,
        otherIncomeDescription=db_form.other_income_description or "",
        hasProfessionalDues=db_form.has_professional_dues,
        professionalDues=professional_dues,
        hasRrspFhsaInvestment=db_form.has_rrsp_fhsa_investment,
        hasChildArtSportCredit=db_form.has_child_art_sport_credit,
        childArtSportCredits=child_art_sport_credits,
        isProvinceFiler=db_form.is_province_filer,
        provinceFiler=province_filer,
        hasDisabilityTaxCredit=db_form.has_disability_tax_credit,
        disabilityTaxCredits=disability_tax_credits,
        isFilingForDeceased=db_form.is_filing_for_deceased,
        deceasedReturnInfo=deceased_return_info,
        uploadedDocuments=db_form.uploaded_documents or {},
        awaitingDocuments=db_form.awaiting_documents or False
    )


@router.post("/", response_model=T1FormResponse, status_code=status.HTTP_201_CREATED)
async def save_t1_form(
    request: T1FormCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save or update a T1 form
    Matches the Flutter app's saveForm functionality
    """
    try:
        form_data = request.formData
        
        # Check if form exists
        stmt = select(T1FormMain).where(
            T1FormMain.id == form_data.id,
            T1FormMain.user_id == current_user.id
        )
        result = await db.execute(stmt)
        existing_form = result.scalar_one_or_none()
        
        if existing_form:
            # Update existing form
            db_form = convert_form_data_to_db(form_data, str(current_user.id), existing_form)
        else:
            # Create new form
            form_id = form_data.id or f"T1_{int(datetime.utcnow().timestamp() * 1000)}"
            db_form = T1FormMain(
                id=form_id,
                user_id=current_user.id,
                status=form_data.status or "draft"
            )
            db_form = convert_form_data_to_db(form_data, str(current_user.id), db_form)
            db.add(db_form)
        
        # Handle personal info
        if form_data.personalInfo:
            if existing_form and existing_form.personal_info:
                # Update existing personal info
                pi = existing_form.personal_info
                pi.first_name = form_data.personalInfo.firstName
                pi.middle_name = form_data.personalInfo.middleName
                pi.last_name = form_data.personalInfo.lastName
                pi.sin = form_data.personalInfo.sin
                pi.date_of_birth = form_data.personalInfo.dateOfBirth
                pi.address = form_data.personalInfo.address
                pi.phone_number = form_data.personalInfo.phoneNumber
                pi.email = form_data.personalInfo.email
                pi.is_canadian_citizen = form_data.personalInfo.isCanadianCitizen
                pi.marital_status = form_data.personalInfo.maritalStatus
            else:
                # Create new personal info
                pi = T1PersonalInfo(
                    form_id=db_form.id,
                    first_name=form_data.personalInfo.firstName,
                    middle_name=form_data.personalInfo.middleName,
                    last_name=form_data.personalInfo.lastName,
                    sin=form_data.personalInfo.sin,
                    date_of_birth=form_data.personalInfo.dateOfBirth,
                    address=form_data.personalInfo.address,
                    phone_number=form_data.personalInfo.phoneNumber,
                    email=form_data.personalInfo.email,
                    is_canadian_citizen=form_data.personalInfo.isCanadianCitizen,
                    marital_status=form_data.personalInfo.maritalStatus
                )
                db.add(pi)
                db_form.personal_info = pi
            
            # Handle spouse info
            if form_data.personalInfo.spouseInfo:
                if existing_form and existing_form.personal_info and existing_form.personal_info.spouse_info:
                    si = existing_form.personal_info.spouse_info
                    si.first_name = form_data.personalInfo.spouseInfo.firstName
                    si.middle_name = form_data.personalInfo.spouseInfo.middleName
                    si.last_name = form_data.personalInfo.spouseInfo.lastName
                    si.sin = form_data.personalInfo.spouseInfo.sin
                    si.date_of_birth = form_data.personalInfo.spouseInfo.dateOfBirth
                else:
                    si = T1SpouseInfo(
                        personal_info_id=pi.id,
                        first_name=form_data.personalInfo.spouseInfo.firstName,
                        middle_name=form_data.personalInfo.spouseInfo.middleName,
                        last_name=form_data.personalInfo.spouseInfo.lastName,
                        sin=form_data.personalInfo.spouseInfo.sin,
                        date_of_birth=form_data.personalInfo.spouseInfo.dateOfBirth
                    )
                    db.add(si)
            
            # Handle children
            if existing_form and existing_form.personal_info:
                # Delete existing children
                await db.execute(
                    delete(T1ChildInfo).where(T1ChildInfo.personal_info_id == existing_form.personal_info.id)
                )
            
            for child in form_data.personalInfo.children:
                child_info = T1ChildInfo(
                    personal_info_id=pi.id,
                    first_name=child.firstName,
                    middle_name=child.middleName,
                    last_name=child.lastName,
                    sin=child.sin,
                    date_of_birth=child.dateOfBirth
                )
                db.add(child_info)
        
        # Handle foreign properties
        if existing_form:
            await db.execute(
                delete(T1ForeignProperty).where(T1ForeignProperty.form_id == existing_form.id)
            )
        
        for fp in form_data.foreignProperties:
            foreign_prop = T1ForeignProperty(
                form_id=db_form.id,
                investment_details=fp.investmentDetails,
                gross_income=fp.grossIncome,
                gain_loss_on_sale=fp.gainLossOnSale,
                max_cost_during_year=fp.maxCostDuringYear,
                cost_amount_year_end=fp.costAmountYearEnd,
                country=fp.country
            )
            db.add(foreign_prop)
        
        # Handle medical expenses
        if existing_form:
            await db.execute(
                delete(T1MedicalExpense).where(T1MedicalExpense.form_id == existing_form.id)
            )
        
        for me in form_data.medicalExpenses:
            medical_exp = T1MedicalExpense(
                form_id=db_form.id,
                payment_date=me.paymentDate,
                patient_name=me.patientName,
                payment_made_to=me.paymentMadeTo,
                description_of_expense=me.descriptionOfExpense,
                insurance_covered=me.insuranceCovered,
                amount_paid_from_pocket=me.amountPaidFromPocket
            )
            db.add(medical_exp)
        
        # Handle work from home expense
        if form_data.workFromHomeExpense:
            if existing_form and existing_form.work_from_home_expense:
                wfh = existing_form.work_from_home_expense
                wfh.total_house_area_sqft = form_data.workFromHomeExpense.totalHouseAreaSqft
                wfh.total_work_area_sqft = form_data.workFromHomeExpense.totalWorkAreaSqft
                wfh.rent_expense = form_data.workFromHomeExpense.rentExpense
                wfh.mortgage_expense = form_data.workFromHomeExpense.mortgageExpense
                wfh.wifi_expense = form_data.workFromHomeExpense.wifiExpense
                wfh.electricity_expense = form_data.workFromHomeExpense.electricityExpense
                wfh.water_expense = form_data.workFromHomeExpense.waterExpense
                wfh.heat_expense = form_data.workFromHomeExpense.heatExpense
                wfh.total_insurance_expense = form_data.workFromHomeExpense.totalInsuranceExpense
                wfh.rent_mortgage_expense = form_data.workFromHomeExpense.rentMortgageExpense
                wfh.utilities_expense = form_data.workFromHomeExpense.utilitiesExpense
            else:
                wfh = T1WorkFromHomeExpense(
                    form_id=db_form.id,
                    total_house_area_sqft=form_data.workFromHomeExpense.totalHouseAreaSqft,
                    total_work_area_sqft=form_data.workFromHomeExpense.totalWorkAreaSqft,
                    rent_expense=form_data.workFromHomeExpense.rentExpense,
                    mortgage_expense=form_data.workFromHomeExpense.mortgageExpense,
                    wifi_expense=form_data.workFromHomeExpense.wifiExpense,
                    electricity_expense=form_data.workFromHomeExpense.electricityExpense,
                    water_expense=form_data.workFromHomeExpense.waterExpense,
                    heat_expense=form_data.workFromHomeExpense.heatExpense,
                    total_insurance_expense=form_data.workFromHomeExpense.totalInsuranceExpense,
                    rent_mortgage_expense=form_data.workFromHomeExpense.rentMortgageExpense,
                    utilities_expense=form_data.workFromHomeExpense.utilitiesExpense
                )
                db.add(wfh)
        
        # Handle daycare expenses
        if existing_form:
            await db.execute(
                delete(T1DaycareExpense).where(T1DaycareExpense.form_id == existing_form.id)
            )
        
        for de in form_data.daycareExpenses:
            daycare_exp = T1DaycareExpense(
                form_id=db_form.id,
                childcare_provider=de.childcareProvider,
                amount=de.amount,
                identification_number_sin=de.identificationNumberSin,
                weeks=de.weeks
            )
            db.add(daycare_exp)
        
        # Handle first time filer
        if form_data.firstTimeFiler:
            if existing_form and existing_form.first_time_filer:
                ftf = existing_form.first_time_filer
                ftf.date_of_landing_individual = form_data.firstTimeFiler.dateOfLandingIndividual
                ftf.income_outside_canada_cad = form_data.firstTimeFiler.incomeOutsideCanadaCad
                ftf.back_home_income_2024_cad = form_data.firstTimeFiler.backHomeIncome2024Cad
                ftf.back_home_income_2023_cad = form_data.firstTimeFiler.backHomeIncome2023Cad
            else:
                ftf = T1FirstTimeFiler(
                    form_id=db_form.id,
                    date_of_landing_individual=form_data.firstTimeFiler.dateOfLandingIndividual,
                    income_outside_canada_cad=form_data.firstTimeFiler.incomeOutsideCanadaCad,
                    back_home_income_2024_cad=form_data.firstTimeFiler.backHomeIncome2024Cad,
                    back_home_income_2023_cad=form_data.firstTimeFiler.backHomeIncome2023Cad
                )
                db.add(ftf)
        
        # Handle province filer
        if existing_form:
            await db.execute(
                delete(T1ProvinceFiler).where(T1ProvinceFiler.form_id == existing_form.id)
            )
        
        for pf in form_data.provinceFiler:
            province_f = T1ProvinceFiler(
                form_id=db_form.id,
                rent_or_property_tax=pf.rentOrPropertyTax,
                property_address=pf.propertyAddress,
                postal_code=pf.postalCode,
                number_of_months_resides=pf.numberOfMonthsResides,
                amount_paid=pf.amountPaid
            )
            db.add(province_f)
        
        # Handle sold property short term
        if form_data.soldPropertyShortTermDetails:
            if existing_form and existing_form.sold_property_short_term:
                spst = existing_form.sold_property_short_term
                spst.property_address = form_data.soldPropertyShortTermDetails.propertyAddress
                spst.purchase_date = form_data.soldPropertyShortTermDetails.purchaseDate
                spst.sell_date = form_data.soldPropertyShortTermDetails.sellDate
                spst.purchase_and_sell_expenses = form_data.soldPropertyShortTermDetails.purchaseAndSellExpenses
            else:
                spst = T1SoldPropertyShortTerm(
                    form_id=db_form.id,
                    property_address=form_data.soldPropertyShortTermDetails.propertyAddress,
                    purchase_date=form_data.soldPropertyShortTermDetails.purchaseDate,
                    sell_date=form_data.soldPropertyShortTermDetails.sellDate,
                    purchase_and_sell_expenses=form_data.soldPropertyShortTermDetails.purchaseAndSellExpenses
                )
                db.add(spst)
        
        # Handle union member dues
        if existing_form:
            await db.execute(
                delete(T1UnionMemberDue).where(T1UnionMemberDue.form_id == existing_form.id)
            )
        
        for umd in form_data.unionMemberDues:
            union_due = T1UnionMemberDue(
                form_id=db_form.id,
                institution_name=umd.institutionName,
                amount=umd.amount
            )
            db.add(union_due)
        
        # Handle professional dues
        if existing_form:
            await db.execute(
                delete(T1ProfessionalDue).where(T1ProfessionalDue.form_id == existing_form.id)
            )
        
        for pd in form_data.professionalDues:
            prof_due = T1ProfessionalDue(
                form_id=db_form.id,
                name=pd.name,
                organization=pd.organization,
                amount=pd.amount
            )
            db.add(prof_due)
        
        # Handle child art/sport credits
        if existing_form:
            await db.execute(
                delete(T1ChildArtSportCredit).where(T1ChildArtSportCredit.form_id == existing_form.id)
            )
        
        for casc in form_data.childArtSportCredits:
            art_sport = T1ChildArtSportCredit(
                form_id=db_form.id,
                institute_name=casc.instituteName,
                description=casc.description,
                amount=casc.amount
            )
            db.add(art_sport)
        
        # Handle disability tax credits
        if existing_form:
            await db.execute(
                delete(T1DisabilityTaxCredit).where(T1DisabilityTaxCredit.form_id == existing_form.id)
            )
        
        for dtc in form_data.disabilityTaxCredits:
            disability = T1DisabilityTaxCredit(
                form_id=db_form.id,
                first_name=dtc.firstName,
                last_name=dtc.lastName,
                relation=dtc.relation,
                approved_year=dtc.approvedYear
            )
            db.add(disability)
        
        # Handle deceased return
        if form_data.deceasedReturnInfo:
            if existing_form and existing_form.deceased_return:
                dr = existing_form.deceased_return
                dr.deceased_full_name = form_data.deceasedReturnInfo.deceasedFullName
                dr.date_of_death = form_data.deceasedReturnInfo.dateOfDeath
                dr.deceased_sin = form_data.deceasedReturnInfo.deceasedSin
                dr.deceased_mailing_address = form_data.deceasedReturnInfo.deceasedMailingAddress
                dr.legal_representative_name = form_data.deceasedReturnInfo.legalRepresentativeName
                dr.legal_representative_contact_number = form_data.deceasedReturnInfo.legalRepresentativeContactNumber
                dr.legal_representative_address = form_data.deceasedReturnInfo.legalRepresentativeAddress
            else:
                dr = T1DeceasedReturn(
                    form_id=db_form.id,
                    deceased_full_name=form_data.deceasedReturnInfo.deceasedFullName,
                    date_of_death=form_data.deceasedReturnInfo.dateOfDeath,
                    deceased_sin=form_data.deceasedReturnInfo.deceasedSin,
                    deceased_mailing_address=form_data.deceasedReturnInfo.deceasedMailingAddress,
                    legal_representative_name=form_data.deceasedReturnInfo.legalRepresentativeName,
                    legal_representative_contact_number=form_data.deceasedReturnInfo.legalRepresentativeContactNumber,
                    legal_representative_address=form_data.deceasedReturnInfo.legalRepresentativeAddress
                )
                db.add(dr)
        
        # Update main form boolean flags
        db_form.has_foreign_property = form_data.hasForeignProperty
        db_form.has_medical_expenses = form_data.hasMedicalExpenses
        db_form.has_charitable_donations = form_data.hasCharitableDonations
        db_form.has_moving_expenses = form_data.hasMovingExpenses
        db_form.is_self_employed = form_data.isSelfEmployed
        db_form.is_first_home_buyer = form_data.isFirstHomeBuyer
        db_form.sold_property_long_term = form_data.soldPropertyLongTerm
        db_form.sold_property_short_term = form_data.soldPropertyShortTerm
        db_form.has_work_from_home_expense = form_data.hasWorkFromHomeExpense
        db_form.was_student_last_year = form_data.wasStudentLastYear
        db_form.is_union_member = form_data.isUnionMember
        db_form.has_daycare_expenses = form_data.hasDaycareExpenses
        db_form.is_first_time_filer = form_data.isFirstTimeFiler
        db_form.has_other_income = form_data.hasOtherIncome
        db_form.other_income_description = form_data.otherIncomeDescription
        db_form.has_professional_dues = form_data.hasProfessionalDues
        db_form.has_rrsp_fhsa_investment = form_data.hasRrspFhsaInvestment
        db_form.has_child_art_sport_credit = form_data.hasChildArtSportCredit
        db_form.is_province_filer = form_data.isProvinceFiler
        db_form.has_disability_tax_credit = form_data.hasDisabilityTaxCredit
        db_form.is_filing_for_deceased = form_data.isFilingForDeceased
        db_form.uploaded_documents = form_data.uploadedDocuments
        db_form.awaiting_documents = form_data.awaitingDocuments
        
        # TODO: Handle moving expenses and self employment (already partially implemented)
        # Moving expenses and self employment handling would go here if needed
        
        await db.commit()
        await db.refresh(db_form)
        
        # Load the complete form with relationships
        stmt = select(T1FormMain).options(
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.spouse_info),
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.children),
            selectinload(T1FormMain.foreign_properties),
            selectinload(T1FormMain.medical_expenses),
            selectinload(T1FormMain.work_from_home_expense),
            selectinload(T1FormMain.daycare_expenses),
            selectinload(T1FormMain.first_time_filer),
            selectinload(T1FormMain.province_filer),
            selectinload(T1FormMain.sold_property_short_term),
            selectinload(T1FormMain.union_member_dues),
            selectinload(T1FormMain.professional_dues),
            selectinload(T1FormMain.child_art_sport_credits),
            selectinload(T1FormMain.disability_tax_credits),
            selectinload(T1FormMain.deceased_return)
        ).where(T1FormMain.id == db_form.id)
        
        result = await db.execute(stmt)
        saved_form = result.scalar_one()
        
        # Convert back to schema
        saved_form_data = convert_db_to_form_data(saved_form)
        
        return T1FormResponse(
            success=True,
            message="T1 form saved successfully",
            formData=saved_form_data
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving T1 form: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving T1 form: {str(e)}"
        )


@router.get("/", response_model=T1FormListResponse)
async def get_all_t1_forms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all T1 forms for the current user
    Matches the Flutter app's loadAllForms functionality
    """
    try:
        stmt = select(T1FormMain).options(
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.spouse_info),
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.children),
            selectinload(T1FormMain.foreign_properties),
            selectinload(T1FormMain.medical_expenses),
            selectinload(T1FormMain.work_from_home_expense),
            selectinload(T1FormMain.daycare_expenses),
            selectinload(T1FormMain.first_time_filer),
            selectinload(T1FormMain.province_filer),
            selectinload(T1FormMain.sold_property_short_term),
            selectinload(T1FormMain.union_member_dues),
            selectinload(T1FormMain.professional_dues),
            selectinload(T1FormMain.child_art_sport_credits),
            selectinload(T1FormMain.disability_tax_credits),
            selectinload(T1FormMain.deceased_return)
        ).where(T1FormMain.user_id == current_user.id)
        
        result = await db.execute(stmt)
        forms = result.scalars().all()
        
        form_data_list = [convert_db_to_form_data(form) for form in forms]
        
        return T1FormListResponse(
            success=True,
            forms=form_data_list,
            total=len(form_data_list)
        )
        
    except Exception as e:
        logger.error(f"Error loading T1 forms: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading T1 forms: {str(e)}"
        )


@router.get("/{form_id}", response_model=T1FormResponse)
async def get_t1_form_by_id(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific T1 form by ID
    Matches the Flutter app's getFormById functionality
    """
    try:
        stmt = select(T1FormMain).options(
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.spouse_info),
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.children),
            selectinload(T1FormMain.foreign_properties),
            selectinload(T1FormMain.medical_expenses),
            selectinload(T1FormMain.work_from_home_expense),
            selectinload(T1FormMain.daycare_expenses),
            selectinload(T1FormMain.first_time_filer),
            selectinload(T1FormMain.province_filer),
            selectinload(T1FormMain.sold_property_short_term),
            selectinload(T1FormMain.union_member_dues),
            selectinload(T1FormMain.professional_dues),
            selectinload(T1FormMain.child_art_sport_credits),
            selectinload(T1FormMain.disability_tax_credits),
            selectinload(T1FormMain.deceased_return)
        ).where(
            T1FormMain.id == form_id,
            T1FormMain.user_id == current_user.id
        )
        
        result = await db.execute(stmt)
        form = result.scalar_one_or_none()
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="T1 form not found"
            )
        
        form_data = convert_db_to_form_data(form)
        
        return T1FormResponse(
            success=True,
            message="T1 form retrieved successfully",
            formData=form_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading T1 form: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading T1 form: {str(e)}"
        )


@router.delete("/{form_id}", response_model=T1FormDeleteResponse)
async def delete_t1_form(
    form_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a T1 form by ID
    Matches the Flutter app's deleteForm functionality
    """
    try:
        stmt = select(T1FormMain).where(
            T1FormMain.id == form_id,
            T1FormMain.user_id == current_user.id
        )
        result = await db.execute(stmt)
        form = result.scalar_one_or_none()
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="T1 form not found"
            )
        
        await db.delete(form)
        await db.commit()
        
        return T1FormDeleteResponse(
            success=True,
            message="T1 form deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting T1 form: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting T1 form: {str(e)}"
        )














