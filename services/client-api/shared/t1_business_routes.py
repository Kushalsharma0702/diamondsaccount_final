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
    T1SelfEmployment, T1UberBusiness, T1GeneralBusiness, T1RentalIncome
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
    db_form.uploaded_documents = form_data.uploadedDocuments
    db_form.awaiting_documents = form_data.awaitingDocuments
    db_form.updated_at = datetime.utcnow()
    
    return db_form


def convert_db_to_form_data(db_form: T1FormMain) -> T1FormDataSchema:
    """Convert database model to Pydantic schema"""
    from shared.t1_business_schemas import (
        T1PersonalInfoSchema, T1SpouseInfoSchema, T1ChildInfoSchema,
        T1ForeignPropertySchema, T1MovingExpenseSchema, T1SelfEmploymentSchema,
        T1UberBusinessSchema, T1GeneralBusinessSchema, T1RentalIncomeSchema
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
        hasWorkFromHomeExpense=db_form.has_work_from_home_expense,
        wasStudentLastYear=db_form.was_student_last_year,
        isUnionMember=db_form.is_union_member,
        hasDaycareExpenses=db_form.has_daycare_expenses,
        isFirstTimeFiler=db_form.is_first_time_filer,
        hasOtherIncome=db_form.has_other_income,
        otherIncomeDescription=db_form.other_income_description or "",
        hasProfessionalDues=db_form.has_professional_dues,
        hasRrspFhsaInvestment=db_form.has_rrsp_fhsa_investment,
        hasChildArtSportCredit=db_form.has_child_art_sport_credit,
        isProvinceFiler=db_form.is_province_filer,
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
        
        # TODO: Handle moving expenses, self employment, etc.
        # This is a simplified version - full implementation would handle all nested objects
        
        await db.commit()
        await db.refresh(db_form)
        
        # Load the complete form with relationships
        stmt = select(T1FormMain).options(
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.spouse_info),
            selectinload(T1FormMain.personal_info).selectinload(T1PersonalInfo.children),
            selectinload(T1FormMain.foreign_properties)
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
            selectinload(T1FormMain.foreign_properties)
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
            selectinload(T1FormMain.foreign_properties)
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












