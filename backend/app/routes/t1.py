"""T1 tax form endpoints - handles complete T1 form structure."""
from datetime import datetime, date
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import T1ReturnFlat, Client
from backend.app.database import get_db

router = APIRouter(prefix="/client", tags=["t1"])


class T1FormRequest(BaseModel):
    formData: Dict[str, Any]


class T1FormResponse(BaseModel):
    id: str
    status: str
    filing_year: int
    created_at: str
    updated_at: str


def safe_get(data: Dict, *keys, default=None):
    """Safely get nested dictionary values."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, {})
        else:
            return default
    return data if data else default


def parse_date(date_str: Any) -> Optional[date]:
    """Parse date string to date object."""
    if not date_str:
        return None
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, datetime):
        return date_str.date()
    try:
        from dateutil import parser as date_parser
        parsed = date_parser.parse(str(date_str))
        return parsed.date() if isinstance(parsed, datetime) else parsed
    except:
        try:
            # Try standard format YYYY-MM-DD
            return datetime.strptime(str(date_str), "%Y-%m-%d").date()
        except:
            return None


def sum_list(items: List[Dict], key: str, default=0.0) -> float:
    """Sum values from list of dictionaries."""
    if not items or not isinstance(items, list):
        return default
    return sum(float(item.get(key, 0) or 0) for item in items if isinstance(item, dict))


def count_list(items: List) -> int:
    """Count items in list."""
    return len(items) if isinstance(items, list) else 0


def map_t1_form_data(form_data: Dict[str, Any], client_id: str, filing_year: int) -> Dict[str, Any]:
    """Map T1 form JSON structure to T1ReturnFlat table columns."""
    personal_info = form_data.get("personalInfo", {})
    
    # Personal Information
    mapped = {
        "client_id": client_id,
        "filing_year": filing_year,
        "status": form_data.get("status", "draft"),
        "first_name": personal_info.get("firstName"),
        "middle_name": personal_info.get("middleName"),
        "last_name": personal_info.get("lastName"),
        "sin": str(personal_info.get("sin", ""))[:9] if personal_info.get("sin") else None,
        "date_of_birth": parse_date(personal_info.get("dateOfBirth")),
        "address": personal_info.get("address"),
        "phone": personal_info.get("phoneNumber"),
        "email": personal_info.get("email"),
        "is_canadian_citizen": personal_info.get("isCanadianCitizen"),
        "marital_status": personal_info.get("maritalStatus"),
    }
    
    # Spouse Information
    spouse_info = personal_info.get("spouseInfo", {})
    if spouse_info:
        mapped.update({
            "spouse_first_name": spouse_info.get("firstName"),
            "spouse_last_name": spouse_info.get("lastName"),
            "spouse_sin": str(spouse_info.get("sin", ""))[:9] if spouse_info.get("sin") else None,
            "spouse_date_of_birth": parse_date(spouse_info.get("dateOfBirth")),
        })
    
    # Children
    children = personal_info.get("children", [])
    mapped.update({
        "has_children": len(children) > 0 if children else None,
        "children_count": count_list(children),
    })
    
    # Questionnaire Flags
    mapped.update({
        "has_foreign_property": form_data.get("hasForeignProperty", False),
        "has_medical_expenses": form_data.get("hasMedicalExpenses", False),
        "has_work_from_home": form_data.get("hasWorkFromHomeExpense", False),
        "has_daycare_expenses": form_data.get("hasDaycareExpenses", False),
        "is_first_time_filer": form_data.get("isFirstTimeFiler", False),
        "is_province_filer": form_data.get("isProvinceFiler", False),
        "sold_property_short_term": form_data.get("soldPropertyShortTerm", False),
        "was_student": form_data.get("wasStudentLastYear", False),
        "is_union_member": form_data.get("isUnionMember", False),
        "has_other_income": form_data.get("hasOtherIncome", False),
        "has_professional_dues": form_data.get("hasProfessionalDues", False),
        "has_rrsp_fhsa": form_data.get("hasRrspFhsaInvestment", False),
        "has_child_art_sport": form_data.get("hasChildArtSportCredit", False),
        "has_disability_tax_credit": form_data.get("hasDisabilityTaxCredit", False),
        "is_filing_for_deceased": form_data.get("isFilingForDeceased", False),
        "has_self_employment": bool(form_data.get("selfEmployment", {})),
    })
    
    # Foreign Property (aggregate from array)
    foreign_properties = form_data.get("foreignProperty", [])
    if foreign_properties:
        mapped.update({
            "foreign_property_count": count_list(foreign_properties),
            "foreign_property_max_cost": max((float(p.get("maximumCostDuringTheYear", 0) or 0) for p in foreign_properties if isinstance(p, dict)), default=0.0),
            "foreign_property_year_end_cost": sum_list(foreign_properties, "costAmountAtTheYearEnd"),
            "foreign_property_total_income": sum_list(foreign_properties, "grossIncome"),
            "foreign_property_total_gain_loss": sum_list(foreign_properties, "gainLossOnSale"),
        })
    
    # Medical Expenses (aggregate from array)
    medical_expenses = form_data.get("medicalExpenses", [])
    if medical_expenses:
        mapped.update({
            "medical_expense_count": count_list(medical_expenses),
            "medical_expense_total_paid": sum_list(medical_expenses, "amountPaidFromPocket") + sum_list(medical_expenses, "insuranceCovered"),
            "medical_expense_insurance_covered": sum_list(medical_expenses, "insuranceCovered"),
            "medical_expense_out_of_pocket": sum_list(medical_expenses, "amountPaidFromPocket"),
        })
    
    # Work From Home
    wfh = form_data.get("workFromHomeExpense", {})
    if wfh:
        mapped.update({
            "wfh_total_house_area": float(wfh.get("totalHouseArea", 0) or 0),
            "wfh_work_area": float(wfh.get("totalWorkArea", 0) or 0),
            "wfh_rent_expense": float(wfh.get("rentExpense", 0) or 0),
            "wfh_mortgage_expense": float(wfh.get("mortgageExpense", 0) or 0),
            "wfh_utilities_expense": (
                float(wfh.get("wifiExpense", 0) or 0) +
                float(wfh.get("electricityExpense", 0) or 0) +
                float(wfh.get("waterExpense", 0) or 0) +
                float(wfh.get("heatExpense", 0) or 0)
            ),
            "wfh_insurance_expense": float(wfh.get("totalInsuranceExpense", 0) or 0),
        })
    
    # Daycare Expenses
    daycare_expenses = form_data.get("daycareExpenses", [])
    if daycare_expenses:
        mapped.update({
            "daycare_expense_total": sum_list(daycare_expenses, "amount"),
            "daycare_weeks_total": sum((int(d.get("weeks", 0) or 0) for d in daycare_expenses if isinstance(d, dict))),
            "daycare_children_count": count_list(daycare_expenses),
        })
    
    # First Time Filer
    first_time = form_data.get("firstTimeFiler", {})
    if first_time:
        mapped.update({
            "first_time_landing_date": parse_date(first_time.get("dateOfLandingIndividual")),
            "income_outside_canada": float(first_time.get("incomeOutsideCanada", 0) or 0),
            "back_home_income_2023": float(first_time.get("backHomeIncome2023", 0) or 0),
            "back_home_income_2024": float(first_time.get("backHomeIncome2024", 0) or 0),
        })
    
    # Short Term Property Sale (Flip)
    flip = form_data.get("soldPropertyShortTerm", {})
    if flip:
        mapped.update({
            "flip_property_address": flip.get("propertyAddress"),
            "flip_purchase_date": parse_date(flip.get("purchaseDate")),
            "flip_sell_date": parse_date(flip.get("sellDate")),
            "flip_purchase_sell_expenses": float(flip.get("purchaseSellExpenses", 0) or 0),
        })
    
    # Student
    student = form_data.get("wasStudentLastYear")
    if student:
        # T2202 form data would be in documents, here we just flag it
        mapped["was_student"] = True
    
    # Union Dues
    union_dues = form_data.get("unionDues", [])
    if union_dues:
        mapped.update({
            "union_dues_total": sum_list(union_dues, "amount"),
            "union_dues_count": count_list(union_dues),
        })
    
    # Other Income
    other_income = form_data.get("otherIncome")
    if other_income:
        mapped.update({
            "other_income_description": other_income.get("otherIncomeDescription", ""),
            "other_income_amount": float(other_income.get("amount", 0) or 0),
        })
    
    # Professional Dues
    professional_dues = form_data.get("professionalDues", [])
    if professional_dues:
        mapped.update({
            "professional_dues_total": sum_list(professional_dues, "amount"),
            "professional_dues_count": count_list(professional_dues),
        })
    
    # RRSP/FHSA
    rrsp_fhsa = form_data.get("rrspFhsaInvestment")
    if rrsp_fhsa:
        mapped["has_rrsp_fhsa"] = True
        # Amount would be in T-slips documents
    
    # Child Art/Sport
    child_art_sport = form_data.get("childArtSportCredit", [])
    if child_art_sport:
        mapped.update({
            "child_art_sport_total": sum_list(child_art_sport, "amount"),
            "child_art_sport_count": count_list(child_art_sport),
        })
    
    # Disability Tax Credit
    disability = form_data.get("disabilityClaimMembers", [])
    if disability:
        mapped.update({
            "disability_members_count": count_list(disability),
            "disability_approved_year_min": min((int(d.get("approvedYear", 0) or 0) for d in disability if isinstance(d, dict)), default=None),
        })
    
    # Province Filer
    province = form_data.get("provinceFiler", [])
    if province:
        mapped.update({
            "province_rent_property_tax_total": sum_list(province, "amountPaid"),
            "province_months_resided": sum((int(p.get("noOfMonthsResides", 0) or 0) for p in province if isinstance(p, dict))),
        })
    
    # Self Employment
    self_emp = form_data.get("selfEmployment", {})
    if self_emp:
        business_types = self_emp.get("businessTypes", [])
        business_type_str = ",".join(business_types) if isinstance(business_types, list) else str(business_types)
        mapped["self_employment_type"] = business_type_str[:20]  # Limit to 20 chars
        
        # Uber/Skip/Doordash Business
        uber_business = self_emp.get("uberBusiness", {})
        if uber_business:
            mapped.update({
                "uber_income": float(uber_business.get("income", 0) or 0),
                "uber_total_km": float(uber_business.get("totalKmDrivenEntireYear", 0) or 0),
                "uber_gas_expense": float(uber_business.get("gas", 0) or 0),
                "uber_insurance_expense": float(uber_business.get("insuranceOnVehicle", 0) or 0),
                "uber_maintenance_expense": (
                    float(uber_business.get("oilChangeAndMaintenance", 0) or 0) +
                    float(uber_business.get("safetyInspection", 0) or 0) +
                    float(uber_business.get("winterTireChange", 0) or 0)
                ),
                "uber_other_expense": (
                    float(uber_business.get("meals", 0) or 0) +
                    float(uber_business.get("telephone", 0) or 0) +
                    float(uber_business.get("parkingFees", 0) or 0) +
                    float(uber_business.get("cleaningExpenses", 0) or 0) +
                    float(uber_business.get("depreciation", 0) or 0) +
                    float(uber_business.get("financingCostInterest", 0) or 0) +
                    float(uber_business.get("leaseCost", 0) or 0) +
                    float(uber_business.get("otherExpense", 0) or 0)
                ),
            })
        
        # General Business
        general_business = self_emp.get("generalBusiness", {})
        if general_business:
            gross_income = float(general_business.get("grossIncome", 0) or 0)
            total_expenses = (
                float(general_business.get("openingInventory", 0) or 0) +
                float(general_business.get("purchasesDuringYear", 0) or 0) +
                float(general_business.get("subcontracts", 0) or 0) +
                float(general_business.get("directWageCosts", 0) or 0) +
                float(general_business.get("otherCosts", 0) or 0) +
                float(general_business.get("advertising", 0) or 0) +
                float(general_business.get("mealsEntertainment", 0) or 0) +
                float(general_business.get("badDebts", 0) or 0) +
                float(general_business.get("insurance", 0) or 0) +
                float(general_business.get("interest", 0) or 0) +
                float(general_business.get("feesLicensesDues", 0) or 0) +
                float(general_business.get("officeExpenses", 0) or 0) +
                float(general_business.get("supplies", 0) or 0) +
                float(general_business.get("legalAccountingFees", 0) or 0) +
                float(general_business.get("managementAdministration", 0) or 0) +
                float(general_business.get("officeRent", 0) or 0) +
                float(general_business.get("maintenanceRepairs", 0) or 0) +
                float(general_business.get("salariesWagesBenefits", 0) or 0) +
                float(general_business.get("propertyTax", 0) or 0) +
                float(general_business.get("travel", 0) or 0) +
                float(general_business.get("telephoneUtilities", 0) or 0) +
                float(general_business.get("fuelCosts", 0) or 0) +
                float(general_business.get("deliveryFreightExpress", 0) or 0) +
                float(general_business.get("otherExpense1", 0) or 0) +
                float(general_business.get("otherExpense2", 0) or 0) +
                float(general_business.get("otherExpense3", 0) or 0)
            )
            
            home_office_expense = (
                float(general_business.get("heat", 0) or 0) +
                float(general_business.get("electricity", 0) or 0) +
                float(general_business.get("houseInsurance", 0) or 0) +
                float(general_business.get("homeMaintenance", 0) or 0) +
                float(general_business.get("mortgageInterest", 0) or 0) +
                float(general_business.get("propertyTaxes", 0) or 0) +
                float(general_business.get("houseRent", 0) or 0) +
                float(general_business.get("homeOtherExpense1", 0) or 0) +
                float(general_business.get("homeOtherExpense2", 0) or 0)
            )
            
            vehicle_expense = (
                float(general_business.get("vehicleFuel", 0) or 0) +
                float(general_business.get("vehicleInsurance", 0) or 0) +
                float(general_business.get("licenseRegistration", 0) or 0) +
                float(general_business.get("vehicleMaintenance", 0) or 0) +
                float(general_business.get("businessParking", 0) or 0) +
                float(general_business.get("vehicleOtherExpense", 0) or 0) +
                float(general_business.get("leasingFinancePayments", 0) or 0)
            )
            
            mapped.update({
                "general_business_income": gross_income,
                "general_business_expenses": total_expenses,
                "general_home_office_expense": home_office_expense,
                "general_vehicle_expense": vehicle_expense,
            })
        
        # Rental Income
        rental_income = self_emp.get("rentalIncome", {})
        if rental_income:
            mapped.update({
                "rental_property_address": rental_income.get("propertyAddress"),
                "rental_gross_income": float(rental_income.get("grossRentalIncome", 0) or 0),
                "rental_mortgage_interest": float(rental_income.get("mortgageInterest", 0) or 0),
                "rental_property_tax": float(rental_income.get("propertyTaxes", 0) or 0),
                "rental_total_expenses": (
                    float(rental_income.get("houseInsurance", 0) or 0) +
                    float(rental_income.get("mortgageInterest", 0) or 0) +
                    float(rental_income.get("propertyTaxes", 0) or 0) +
                    float(rental_income.get("utilities", 0) or 0) +
                    float(rental_income.get("managementAdminFees", 0) or 0) +
                    float(rental_income.get("repairAndMaintenance", 0) or 0) +
                    float(rental_income.get("cleaningExpense", 0) or 0) +
                    float(rental_income.get("motorVehicleExpenses", 0) or 0) +
                    float(rental_income.get("legalProfessionalFees", 0) or 0) +
                    float(rental_income.get("advertisingPromotion", 0) or 0) +
                    float(rental_income.get("otherExpense", 0) or 0)
                ),
            })
    
    # Deceased Return
    deceased = form_data.get("deceasedReturnInfo", {})
    if deceased:
        mapped["is_filing_for_deceased"] = True
    
    # Store complete form data in JSONB
    mapped["form_data"] = form_data
    
    return mapped


@router.post("/tax-return", response_model=T1FormResponse)
def submit_t1_form(request: T1FormRequest, db: Session = Depends(get_db)):
    """Submit or update T1 tax form - handles complete T1 structure from frontend."""
    form_data = request.formData
    personal_info = form_data.get("personalInfo", {})
    client_email = personal_info.get("email")
    
    if not client_email:
        raise HTTPException(status_code=400, detail="Email required in personalInfo.email")

    # Find client by email
    client = db.query(Client).filter(Client.email == client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    filing_year = form_data.get("filingYear") or form_data.get("filing_year") or datetime.utcnow().year
    form_status = form_data.get("status", "draft")

    # Map form data to flat table structure
    mapped_data = map_t1_form_data(form_data, str(client.id), filing_year)
    
    # Check if T1 return exists (upsert on client_id + filing_year)
    t1_return = (
        db.query(T1ReturnFlat)
        .filter(
            T1ReturnFlat.client_id == client.id,
            T1ReturnFlat.filing_year == filing_year
        )
        .first()
    )

    if t1_return:
        # Update existing record
        for key, value in mapped_data.items():
            if hasattr(t1_return, key):
                setattr(t1_return, key, value)
        t1_return.updated_at = datetime.utcnow()
        
        if form_status == "submitted":
            t1_return.submitted_at = datetime.utcnow()
            if client.status == "documents_pending":
                client.status = "under_review"
    else:
        # Create new record
        t1_return = T1ReturnFlat(**mapped_data)
        db.add(t1_return)

    db.commit()
    db.refresh(t1_return)

    return T1FormResponse(
        id=str(t1_return.id),
        status=t1_return.status,
        filing_year=t1_return.filing_year,
        created_at=t1_return.created_at.isoformat(),
        updated_at=t1_return.updated_at.isoformat(),
    )


@router.get("/tax-return", response_model=Dict[str, Any])
def get_t1_form(
    client_id: Optional[str] = None,
    email: Optional[str] = None,
    filing_year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get T1 form data for a client."""
    if not client_id and not email:
        raise HTTPException(status_code=400, detail="client_id or email required")
    
    if email:
        client = db.query(Client).filter(Client.email == email).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        client_id = str(client.id)
    
    query = db.query(T1ReturnFlat).filter(T1ReturnFlat.client_id == client_id)
    if filing_year:
        query = query.filter(T1ReturnFlat.filing_year == filing_year)
    else:
        # Get latest year
        query = query.order_by(T1ReturnFlat.filing_year.desc())
    
    t1_return = query.first()
    if not t1_return:
        raise HTTPException(status_code=404, detail="T1 return not found")
    
    # Return full form_data JSONB if available, otherwise reconstruct from flat columns
    if t1_return.form_data:
        return t1_return.form_data
    else:
        # Fallback: return basic structure (would need full reconstruction logic)
        return {
            "id": str(t1_return.id),
            "status": t1_return.status,
            "filingYear": t1_return.filing_year,
            "personalInfo": {
                "firstName": t1_return.first_name,
                "lastName": t1_return.last_name,
                "email": t1_return.email,
            }
        }
