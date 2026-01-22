#!/usr/bin/env python3
"""
Create comprehensive T1 test data for Manjulika Tai
This script creates a complete user with fully filled T1 form including all subforms
Run this from an environment with AWS RDS access (EC2 instance)
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
import uuid
from decimal import Decimal

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Load environment
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

# Import models
from database.schemas_v2 import (
    Base, User, Filing, T1Form, T1Answer, T1SectionProgress,
    FilingStatus
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = os.getenv("DATABASE_SYNC_URL")
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔗 Connecting to: {os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def create_manjulika_tai_data():
    """Create complete T1 data for Manjulika Tai"""
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("📝 CREATING COMPREHENSIVE T1 DATA FOR MANJULIKA TAI")
        print("="*70 + "\n")
        
        # Step 1: Create User
        print("👤 Creating user: Manjulika Tai...")
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="manjulika.tai@example.com",
            first_name="Manjulika",
            last_name="Tai",
            phone="+1-416-555-9876",
            password_hash=pwd_context.hash("ManjulikaTai@2024!"),
            email_verified=True,
            is_active=True
        )
        db.add(user)
        db.flush()
        print(f"   ✅ User created with ID: {user_id}")
        
        # Step 2: Create Filing
        print("\n📄 Creating filing for tax year 2024...")
        filing_id = uuid.uuid4()
        filing = Filing(
            id=filing_id,
            user_id=user_id,
            filing_year=2024,
            filing_type="personal",
            status=FilingStatus.IN_PREPARATION,
            assessment_fee=Decimal("299.99"),
            payment_status="pending",
            is_active=True
        )
        db.add(filing)
        db.flush()
        print(f"   ✅ Filing created with ID: {filing_id}")
        
        # Step 3: Create T1 Form
        print("\n📋 Creating T1 form...")
        t1_form_id = uuid.uuid4()
        t1_form = T1Form(
            id=t1_form_id,
            filing_id=filing_id,
            user_id=user_id,
            status="draft",
            is_locked=False,
            completion_percentage=85,
            last_saved_step_id="questionnaire"
        )
        db.add(t1_form)
        db.flush()
        print(f"   ✅ T1 Form created with ID: {t1_form_id}")
        
        # Step 4: Create comprehensive T1 Answers
        print("\n💾 Creating comprehensive T1 answers...")
        answers = []
        
        # PERSONAL INFORMATION
        print("   📝 Personal Information...")
        personal_info_answers = [
            ("personalInfo.firstName", None, "Manjulika", None, None, None),
            ("personalInfo.middleName", None, "Devi", None, None, None),
            ("personalInfo.lastName", None, "Tai", None, None, None),
            ("personalInfo.sin", None, None, 987654321, None, None),
            ("personalInfo.dateOfBirth", None, None, None, date(1985, 8, 15), None),
            ("personalInfo.address", None, "123 Haunted Mansion Drive, Apt 666, Toronto, ON M5H 2N2", None, None, None),
            ("personalInfo.phoneNumber", None, "+1-416-555-9876", None, None, None),
            ("personalInfo.email", None, "manjulika.tai@example.com", None, None, None),
            ("personalInfo.isCanadianCitizen", True, None, None, None, None),
            ("personalInfo.maritalStatus", None, "married", None, None, None),
        ]
        
        # SPOUSE INFORMATION
        print("   💑 Spouse Information...")
        spouse_answers = [
            ("personalInfo.spouseInfo.firstName", None, "Vikram", None, None, None),
            ("personalInfo.spouseInfo.middleName", None, "Singh", None, None, None),
            ("personalInfo.spouseInfo.lastName", None, "Rathore", None, None, None),
            ("personalInfo.spouseInfo.sin", None, None, 876543210, None, None),
            ("personalInfo.spouseInfo.dateOfBirth", None, None, None, date(1983, 3, 20), None),
        ]
        
        # CHILDREN
        print("   👶 Children Information...")
        children_answers = [
            ("personalInfo.children", None, None, None, None, [
                {
                    "firstName": "Chotu",
                    "middleName": "Ram",
                    "lastName": "Rathore",
                    "sin": "765432109",
                    "dateOfBirth": "2015-06-10"
                },
                {
                    "firstName": "Pinky",
                    "middleName": "Kumari",
                    "lastName": "Rathore",
                    "sin": "654321098",
                    "dateOfBirth": "2018-09-25"
                }
            ]),
        ]
        
        # QUESTIONNAIRE ANSWERS
        print("   ❓ Questionnaire...")
        
        # Q1: Foreign Property
        foreign_property_answers = [
            ("hasForeignProperty", True, None, None, None, None),
            ("foreignProperty", None, None, None, None, [
                {
                    "investmentDetails": "Real Estate in Mumbai, India",
                    "grossIncome": 25000.00,
                    "gainLoss": 15000.00,
                    "maxCostDuringYear": 500000.00,
                    "costAtYearEnd": 485000.00,
                    "country": "India"
                },
                {
                    "investmentDetails": "Stocks in US Market - Apple Inc.",
                    "grossIncome": 3500.00,
                    "gainLoss": 8200.00,
                    "maxCostDuringYear": 125000.00,
                    "costAtYearEnd": 133200.00,
                    "country": "United States"
                }
            ]),
        ]
        
        # Q2: Medical Expenses
        medical_answers = [
            ("hasMedicalExpenses", True, None, None, None, None),
            ("medicalExpenses", None, None, None, None, [
                {
                    "paymentDate": "2024-02-15",
                    "patientName": "Manjulika Tai",
                    "paymentMadeTo": "Toronto General Hospital",
                    "description": "Dental Surgery - Root Canal",
                    "insuranceCovered": 500.00,
                    "amountPaidFromPocket": 1200.00
                },
                {
                    "paymentDate": "2024-05-20",
                    "patientName": "Chotu Ram Rathore",
                    "paymentMadeTo": "SickKids Hospital",
                    "description": "Pediatric Eye Surgery",
                    "insuranceCovered": 2000.00,
                    "amountPaidFromPocket": 800.00
                },
                {
                    "paymentDate": "2024-09-10",
                    "patientName": "Vikram Singh Rathore",
                    "paymentMadeTo": "Physiotherapy Clinic Downtown",
                    "description": "Physical Therapy Sessions (12 weeks)",
                    "insuranceCovered": 0.00,
                    "amountPaidFromPocket": 1500.00
                }
            ]),
        ]
        
        # Q9: Work From Home Expense
        wfh_answers = [
            ("hasWorkFromHomeExpense", True, None, None, None, None),
            ("workFromHomeExpense.totalHouseArea", None, None, 1800.00, None, None),
            ("workFromHomeExpense.totalWorkArea", None, None, 200.00, None, None),
            ("workFromHomeExpense.rentExpense", None, None, 24000.00, None, None),
            ("workFromHomeExpense.mortgageExpense", None, None, 0.00, None, None),
            ("workFromHomeExpense.wifiExpense", None, None, 960.00, None, None),
            ("workFromHomeExpense.electricityExpense", None, None, 1800.00, None, None),
            ("workFromHomeExpense.waterExpense", None, None, 600.00, None, None),
            ("workFromHomeExpense.heatExpense", None, None, 2400.00, None, None),
            ("workFromHomeExpense.totalInsuranceExpense", None, None, 1200.00, None, None),
        ]
        
        # Q12: Daycare Expenses
        daycare_answers = [
            ("hasDaycareExpenses", True, None, None, None, None),
            ("daycareExpenses", None, None, None, None, [
                {
                    "childcareProvider": "Little Angels Daycare",
                    "amount": 8500.00,
                    "identificationNumber": "123456789",
                    "weeks": 48
                },
                {
                    "childcareProvider": "After School Program - St. Mary's",
                    "amount": 3200.00,
                    "identificationNumber": "987654321",
                    "weeks": 40
                }
            ]),
        ]
        
        # Q13: First Time Filer
        first_time_filer_answers = [
            ("isFirstTimeFiler", False, None, None, None, None),
        ]
        
        # Q18: Province Filer (Ontario)
        province_answers = [
            ("isProvinceFiler", True, None, None, None, None),
            ("provinceFilerDetails", None, None, None, None, [
                {
                    "rentOrPropertyTax": "Rent",
                    "propertyAddress": "123 Haunted Mansion Drive, Apt 666, Toronto, ON",
                    "postalCode": "M5H 2N2",
                    "noOfMonthsResides": 12
                }
            ]),
        ]
        
        # Q8: Sold Property Short Term
        property_sale_answers = [
            ("soldPropertyShortTerm", False, None, None, None, None),
        ]
        
        # Additional Questions (all false/no)
        additional_questions = [
            ("hasRentalIncome", False, None, None, None, None),
            ("hasSelfEmploymentIncome", False, None, None, None, None),
            ("hasCapitalGains", False, None, None, None, None),
            ("hasInvestmentIncome", True, None, None, None, None),
            ("investmentIncome.interestIncome", None, None, 1250.00, None, None),
            ("investmentIncome.dividendIncome", None, None, 3400.00, None, None),
            ("hasRRSPContribution", True, None, None, None, None),
            ("rrspContribution.amount", None, None, 15000.00, None, None),
            ("hasTFSAContribution", True, None, None, None, None),
            ("tfsaContribution.amount", None, None, 6500.00, None, None),
            ("hasCharitableDonations", True, None, None, None, None),
            ("charitableDonations.totalAmount", None, None, 2500.00, None, None),
            ("hasMovingExpenses", False, None, None, None, None),
            ("hasStudentLoanInterest", False, None, None, None, None),
            ("hasTuitionFees", False, None, None, None, None),
            ("hasDisabilityAmount", False, None, None, None, None),
            ("hasPublicTransitPasses", False, None, None, None, None),
        ]
        
        # EMPLOYMENT INCOME
        employment_answers = [
            ("hasEmploymentIncome", True, None, None, None, None),
            ("employmentIncome", None, None, None, None, [
                {
                    "employerName": "Haunted Spirits Inc.",
                    "employerAddress": "666 Ghost Street, Toronto, ON",
                    "employmentIncome": 85000.00,
                    "incomeTax": 18500.00,
                    "cpp": 3499.80,
                    "ei": 952.74,
                    "rppContribution": 5000.00,
                    "unionDues": 450.00,
                    "charitableDonations": 500.00
                }
            ]),
        ]
        
        # Combine all answers
        all_answer_data = (
            personal_info_answers + spouse_answers + children_answers +
            foreign_property_answers + medical_answers + wfh_answers +
            daycare_answers + first_time_filer_answers + province_answers +
            property_sale_answers + additional_questions + employment_answers
        )
        
        # Create answer objects
        for field_key, bool_val, text_val, num_val, date_val, array_val in all_answer_data:
            answer = T1Answer(
                id=uuid.uuid4(),
                t1_form_id=t1_form_id,
                field_key=field_key,
                value_boolean=bool_val,
                value_text=text_val,
                value_numeric=num_val,
                value_date=date_val,
                value_array=array_val
            )
            answers.append(answer)
        
        db.add_all(answers)
        print(f"   ✅ Created {len(answers)} field answers")
        
        # Step 5: Create Section Progress
        print("\n📊 Creating section progress...")
        sections = [
            T1SectionProgress(
                id=uuid.uuid4(),
                t1_form_id=t1_form_id,
                step_id="personal_info",
                section_id="individual_information",
                is_complete=True,
                completion_percentage=100
            ),
            T1SectionProgress(
                id=uuid.uuid4(),
                t1_form_id=t1_form_id,
                step_id="personal_info",
                section_id="spouse_information",
                is_complete=True,
                completion_percentage=100
            ),
            T1SectionProgress(
                id=uuid.uuid4(),
                t1_form_id=t1_form_id,
                step_id="personal_info",
                section_id="children_details",
                is_complete=True,
                completion_percentage=100
            ),
            T1SectionProgress(
                id=uuid.uuid4(),
                t1_form_id=t1_form_id,
                step_id="questionnaire",
                section_id="main_questions",
                is_complete=True,
                completion_percentage=90
            ),
        ]
        db.add_all(sections)
        print(f"   ✅ Created {len(sections)} section progress records")
        
        # Commit everything
        db.commit()
        
        print("\n" + "="*70)
        print("✅ SUCCESSFULLY CREATED COMPREHENSIVE DATA!")
        print("="*70)
        print(f"\n📋 Summary:")
        print(f"   User ID:      {user_id}")
        print(f"   Email:        manjulika.tai@example.com")
        print(f"   Password:     ManjulikaTai@2024!")
        print(f"   Filing ID:    {filing_id}")
        print(f"   T1 Form ID:   {t1_form_id}")
        print(f"   Total Fields: {len(answers)}")
        print(f"\n📝 Data includes:")
        print(f"   ✅ Complete personal information")
        print(f"   ✅ Spouse information")
        print(f"   ✅ 2 Children")
        print(f"   ✅ Foreign property (2 properties)")
        print(f"   ✅ Medical expenses (3 entries)")
        print(f"   ✅ Work from home expenses")
        print(f"   ✅ Daycare expenses (2 providers)")
        print(f"   ✅ Province filer details (Ontario)")
        print(f"   ✅ Employment income")
        print(f"   ✅ Investment income")
        print(f"   ✅ RRSP contributions")
        print(f"   ✅ Charitable donations")
        print(f"\n🎉 Manjulika Tai can now login and view her complete T1 form!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating data: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


def main():
    """Main execution"""
    try:
        result = create_manjulika_tai_data()
        return 0 if result else 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
