# T1 Form Structure Mapping

## Overview

The backend now fully supports the complete T1 form structure from `T1Structure (2).json`. All form data is:

1. **Stored in JSONB** (`form_data` column) - Complete nested structure preserved
2. **Mapped to flat columns** - For efficient querying and reporting

## Form Structure Support

### ✅ Personal Information Step

**Fields Mapped:**
- `personalInfo.firstName` → `first_name`
- `personalInfo.middleName` → `middle_name`
- `personalInfo.lastName` → `last_name`
- `personalInfo.sin` → `sin`
- `personalInfo.dateOfBirth` → `date_of_birth`
- `personalInfo.address` → `address`
- `personalInfo.phoneNumber` → `phone`
- `personalInfo.email` → `email`
- `personalInfo.isCanadianCitizen` → `is_canadian_citizen`
- `personalInfo.maritalStatus` → `marital_status`

**Spouse Information:**
- `personalInfo.spouseInfo.*` → `spouse_*` columns

**Children:**
- `personalInfo.children[]` → `has_children`, `children_count`
- Full array stored in JSONB

### ✅ Questionnaire Step

**All Boolean Flags Supported:**
- `hasForeignProperty` → `has_foreign_property`
- `hasMedicalExpenses` → `has_medical_expenses`
- `hasWorkFromHomeExpense` → `has_work_from_home`
- `hasDaycareExpenses` → `has_daycare_expenses`
- `isFirstTimeFiler` → `is_first_time_filer`
- `isProvinceFiler` → `is_province_filer`
- `soldPropertyShortTerm` → `sold_property_short_term`
- `wasStudentLastYear` → `was_student`
- `isUnionMember` → `is_union_member`
- `hasOtherIncome` → `has_other_income`
- `hasProfessionalDues` → `has_professional_dues`
- `hasRrspFhsaInvestment` → `has_rrsp_fhsa`
- `hasChildArtSportCredit` → `has_child_art_sport`
- `hasDisabilityTaxCredit` → `has_disability_tax_credit`
- `isFilingForDeceased` → `is_filing_for_deceased`
- `selfEmployment` → `has_self_employment`

### ✅ Foreign Property (Question 1)

**Array Aggregation:**
- `foreignProperty[]` → Aggregated to:
  - `foreign_property_count`
  - `foreign_property_max_cost`
  - `foreign_property_year_end_cost`
  - `foreign_property_total_income`
  - `foreign_property_total_gain_loss`
- Full array stored in JSONB

### ✅ Medical Expenses (Question 2)

**Array Aggregation:**
- `medicalExpenses[]` → Aggregated to:
  - `medical_expense_count`
  - `medical_expense_total_paid`
  - `medical_expense_insurance_covered`
  - `medical_expense_out_of_pocket`
- Full array stored in JSONB

### ✅ Work From Home (Question 9)

**Fields Mapped:**
- `workFromHomeExpense.totalHouseArea` → `wfh_total_house_area`
- `workFromHomeExpense.totalWorkArea` → `wfh_work_area`
- `workFromHomeExpense.rentExpense` → `wfh_rent_expense`
- `workFromHomeExpense.mortgageExpense` → `wfh_mortgage_expense`
- Utilities aggregated → `wfh_utilities_expense`
- `workFromHomeExpense.totalInsuranceExpense` → `wfh_insurance_expense`

### ✅ Daycare Expenses (Question 12)

**Array Aggregation:**
- `daycareExpenses[]` → Aggregated to:
  - `daycare_expense_total`
  - `daycare_weeks_total`
  - `daycare_children_count`
- Full array stored in JSONB

### ✅ First Time Filer (Question 13)

**Fields Mapped:**
- `firstTimeFiler.dateOfLandingIndividual` → `first_time_landing_date`
- `firstTimeFiler.incomeOutsideCanada` → `income_outside_canada`
- `firstTimeFiler.backHomeIncome2023` → `back_home_income_2023`
- `firstTimeFiler.backHomeIncome2024` → `back_home_income_2024`

### ✅ Short Term Property Sale (Question 8)

**Fields Mapped:**
- `soldPropertyShortTerm.propertyAddress` → `flip_property_address`
- `soldPropertyShortTerm.purchaseDate` → `flip_purchase_date`
- `soldPropertyShortTerm.sellDate` → `flip_sell_date`
- `soldPropertyShortTerm.purchaseSellExpenses` → `flip_purchase_sell_expenses`

### ✅ Union Dues (Question 11)

**Array Aggregation:**
- `unionDues[]` → Aggregated to:
  - `union_dues_total`
  - `union_dues_count`
- Full array stored in JSONB

### ✅ Other Income (Question 14)

**Fields Mapped:**
- `otherIncome.otherIncomeDescription` → `other_income_description`
- `otherIncome.amount` → `other_income_amount`

### ✅ Professional Dues (Question 15)

**Array Aggregation:**
- `professionalDues[]` → Aggregated to:
  - `professional_dues_total`
  - `professional_dues_count`
- Full array stored in JSONB

### ✅ Child Art/Sport (Question 17)

**Array Aggregation:**
- `childArtSportCredit[]` → Aggregated to:
  - `child_art_sport_total`
  - `child_art_sport_count`
- Full array stored in JSONB

### ✅ Disability Tax Credit (Question 19)

**Array Aggregation:**
- `disabilityClaimMembers[]` → Aggregated to:
  - `disability_members_count`
  - `disability_approved_year_min`
- Full array stored in JSONB

### ✅ Province Filer (Question 18)

**Array Aggregation:**
- `provinceFiler[]` → Aggregated to:
  - `province_rent_property_tax_total`
  - `province_months_resided`
- Full array stored in JSONB

### ✅ Self Employment

**Business Types:**
- `selfEmployment.businessTypes[]` → `self_employment_type` (comma-separated)

**Uber/Skip/Doordash Business:**
- `selfEmployment.uberBusiness.*` → `uber_*` columns
- All expenses aggregated appropriately

**General Business:**
- `selfEmployment.generalBusiness.*` → `general_business_*` columns
- Income, expenses, home office, vehicle expenses aggregated

**Rental Income:**
- `selfEmployment.rentalIncome.*` → `rental_*` columns
- Gross income, expenses, mortgage interest, property tax

### ✅ Deceased Return (Question 20)

**Flag:**
- `isFilingForDeceased` → `is_filing_for_deceased`
- Full `deceasedReturnInfo` object stored in JSONB

## API Endpoints

### POST `/api/v1/client/tax-return`

**Request:**
```json
{
  "formData": {
    "personalInfo": { ... },
    "hasForeignProperty": true,
    "foreignProperty": [ ... ],
    "selfEmployment": { ... },
    ...
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "draft",
  "filing_year": 2023,
  "created_at": "2023-12-24T...",
  "updated_at": "2023-12-24T..."
}
```

### GET `/api/v1/client/tax-return?email=...&filing_year=2023`

Returns complete `form_data` JSONB if available, otherwise reconstructs from flat columns.

## Database Schema

**Table:** `t1_returns_flat`

- **Primary Key:** `id` (UUID)
- **Unique Constraint:** `(client_id, filing_year)`
- **JSONB Column:** `form_data` - Stores complete nested structure
- **Flat Columns:** ~60+ columns for efficient querying

## Data Flow

1. **Frontend** sends complete T1 form structure as JSON
2. **Backend** maps to flat columns + stores full JSON in `form_data`
3. **Database** stores both for:
   - Fast queries (flat columns)
   - Complete data retrieval (JSONB)
4. **Admin Panel** can query by flags, view full form data

## Notes

- All arrays are aggregated to summary fields for querying
- Full array data preserved in JSONB `form_data`
- Date fields parsed from various formats
- Numeric fields handle null/empty values gracefully
- Upsert logic: updates existing record if `(client_id, filing_year)` exists










