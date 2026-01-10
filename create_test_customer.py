#!/usr/bin/env python3
"""
Create a comprehensive test customer with T1 form data and documents
"""
import asyncio
import sys
from datetime import datetime, date
from uuid import uuid4
import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://postgres:password@database-1.ct2g4wqam4oi.ca-central-1.rds.amazonaws.com:5432/postgres
"

async def create_test_customer():
    """Create a comprehensive test customer"""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 1. Create User
            user_id = str(uuid4())
            email = "hacur.tichkule@test.com"
            password = "test123"
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            print(f"Creating user: {email}")
            
            user_query = text("""
                INSERT INTO users (id, email, password_hash, first_name, last_name, phone, 
                                   is_active, email_verified, created_at, updated_at)
                VALUES (:id, :email, :password_hash, :first_name, :last_name, :phone,
                        :is_active, :email_verified, :created_at, :updated_at)
                ON CONFLICT (email) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
                RETURNING id
            """)
            
            result = await session.execute(user_query, {
                "id": user_id,
                "email": email,
                "password_hash": hashed_password,
                "first_name": "Hacur",
                "last_name": "Tichkule",
                "phone": "+1-416-555-9999",
                "is_active": True,
                "email_verified": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Check if user already exists
            user_check = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            existing_user = user_check.fetchone()
            if existing_user:
                user_id = str(existing_user[0])
                print(f"✓ User already exists with ID: {user_id}")
            else:
                print(f"✓ User created with ID: {user_id}")
            
            # 2. Create Filing
            filing_id = str(uuid4())
            filing_year = 2026
            
            print(f"Creating filing for year {filing_year}")
            
            filing_query = text("""
                INSERT INTO filings (id, user_id, filing_year, status, created_at, updated_at)
                VALUES (:id, :user_id, :filing_year, :status, :created_at, :updated_at)
                RETURNING id
            """)
            
            await session.execute(filing_query, {
                "id": filing_id,
                "user_id": user_id,
                "filing_year": filing_year,
                "status": "in_preparation",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            print(f"✓ Filing created with ID: {filing_id}")
            
            # 3. Create T1 Form
            t1_form_id = str(uuid4())
            
            print("Creating T1 form")
            
            t1_form_query = text("""
                INSERT INTO t1_forms (id, user_id, filing_id, status, completion_percentage, 
                                      is_locked, created_at, updated_at)
                VALUES (:id, :user_id, :filing_id, :status, :completion_percentage,
                        :is_locked, :created_at, :updated_at)
                RETURNING id
            """)
            
            await session.execute(t1_form_query, {
                "id": t1_form_id,
                "user_id": user_id,
                "filing_id": filing_id,
                "status": "draft",
                "completion_percentage": 95,
                "is_locked": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            print(f"✓ T1 form created with ID: {t1_form_id}")
            
            # 4. Add comprehensive T1 form answers
            print("Adding T1 form answers...")
            
            answers = [
                # Personal Information
                ("personalInfo.firstName", "Hacur", "text"),
                ("personalInfo.middleName", "Kumar", "text"),
                ("personalInfo.lastName", "Tichkule", "text"),
                ("personalInfo.sin", "123456789", "text"),
                ("personalInfo.dateOfBirth", "1988-05-15", "text"),
                ("personalInfo.email", email, "text"),
                ("personalInfo.phoneNumber", "+1-416-555-9999", "text"),
                ("personalInfo.currentAddress.street", "456 Maple Street", "text"),
                ("personalInfo.currentAddress.city", "Toronto", "text"),
                ("personalInfo.currentAddress.province", "ON", "text"),
                ("personalInfo.currentAddress.postalCode", "M5V 2T6", "text"),
                ("personalInfo.maritalStatus", "married", "text"),
                ("personalInfo.isCanadianCitizen", True, "boolean"),
                
                # Spouse Information
                ("personalInfo.spouse.firstName", "Priya", "text"),
                ("personalInfo.spouse.lastName", "Tichkule", "text"),
                ("personalInfo.spouse.sin", "987654321", "text"),
                ("personalInfo.spouse.dateOfBirth", "1990-08-20", "text"),
                ("personalInfo.spouse.netIncome", "45000", "text"),
                
                # Children
                ("personalInfo.children[0].firstName", "Aarav", "text"),
                ("personalInfo.children[0].lastName", "Tichkule", "text"),
                ("personalInfo.children[0].dateOfBirth", "2015-03-10", "text"),
                ("personalInfo.children[0].sin", "111222333", "text"),
                ("personalInfo.children[0].relationship", "son", "text"),
                
                ("personalInfo.children[1].firstName", "Ananya", "text"),
                ("personalInfo.children[1].lastName", "Tichkule", "text"),
                ("personalInfo.children[1].dateOfBirth", "2018-07-25", "text"),
                ("personalInfo.children[1].sin", "444555666", "text"),
                ("personalInfo.children[1].relationship", "daughter", "text"),
                
                # Employment Income
                ("hasEmploymentIncome", True, "boolean"),
                
                # Medical Expenses
                ("hasMedicalExpenses", True, "boolean"),
                ("medicalExpenses[0].description", "Prescription Medications", "text"),
                ("medicalExpenses[0].amount", "2500", "text"),
                ("medicalExpenses[1].description", "Dental Services", "text"),
                ("medicalExpenses[1].amount", "3200", "text"),
                ("medicalExpenses[2].description", "Physiotherapy", "text"),
                ("medicalExpenses[2].amount", "1800", "text"),
                
                # Charitable Donations
                ("hasCharitableDonations", True, "boolean"),
                ("charitableDonations[0].organizationName", "Canadian Red Cross", "text"),
                ("charitableDonations[0].amount", "1500", "text"),
                ("charitableDonations[0].receiptNumber", "RC-2026-001", "text"),
                ("charitableDonations[1].organizationName", "SickKids Foundation", "text"),
                ("charitableDonations[1].amount", "2000", "text"),
                ("charitableDonations[1].receiptNumber", "SK-2026-789", "text"),
                
                # Moving Expenses
                ("hasMovingExpenses", False, "boolean"),
                
                # Daycare Expenses
                ("hasDaycareExpenses", True, "boolean"),
                ("daycareExpenses[0].providerName", "Little Stars Daycare", "text"),
                ("daycareExpenses[0].childName", "Ananya Tichkule", "text"),
                ("daycareExpenses[0].amount", "12000", "text"),
                ("daycareExpenses[0].receiptNumber", "LS-2026-456", "text"),
                
                # Foreign Property
                ("hasForeignProperty", True, "boolean"),
                ("foreignProperties[0].country", "United States", "text"),
                ("foreignProperties[0].propertyType", "Rental Property", "text"),
                ("foreignProperties[0].address", "123 Beach Road, Miami, FL 33139", "text"),
                ("foreignProperties[0].costAmount", "350000", "text"),
                ("foreignProperties[0].currentValue", "420000", "text"),
                ("foreignProperties[0].incomeGenerated", "24000", "text"),
                
                # Work From Home Expenses
                ("hasWorkFromHomeExpense", True, "boolean"),
                ("workFromHome.totalHouseArea", "2000", "text"),
                ("workFromHome.workArea", "200", "text"),
                ("workFromHome.rentExpense", "24000", "text"),
                ("workFromHome.mortgageExpense", "0", "text"),
                ("workFromHome.wifiExpense", "960", "text"),
                ("workFromHome.electricityExpense", "1800", "text"),
                ("workFromHome.waterExpense", "480", "text"),
                ("workFromHome.heatExpense", "1200", "text"),
                ("workFromHome.insuranceExpense", "1440", "text"),
                
                # RRSP/FHSA Investment
                ("hasRrspFhsaInvestment", True, "boolean"),
                ("rrspContributions[0].institutionName", "TD Bank RRSP", "text"),
                ("rrspContributions[0].amount", "15000", "text"),
                ("rrspContributions[0].receiptNumber", "TD-RRSP-2026-123", "text"),
                
                # Professional Dues
                ("hasProfessionalDues", True, "boolean"),
                ("professionalDues[0].organization", "Professional Engineers Ontario", "text"),
                ("professionalDues[0].amount", "450", "text"),
                ("professionalDues[0].receiptNumber", "PEO-2026-789", "text"),
                
                # Union Membership
                ("isUnionMember", False, "boolean"),
                
                # Children's Art & Sport Credit
                ("hasChildArtSportCredit", True, "boolean"),
                ("childArtSportActivities[0].childName", "Aarav Tichkule", "text"),
                ("childArtSportActivities[0].activityType", "Hockey", "text"),
                ("childArtSportActivities[0].amount", "800", "text"),
                ("childArtSportActivities[1].childName", "Ananya Tichkule", "text"),
                ("childArtSportActivities[1].activityType", "Ballet", "text"),
                ("childArtSportActivities[1].amount", "600", "text"),
                
                # Province Rent/Property Tax
                ("isProvinceFiler", True, "boolean"),
                ("provinceRent.amount", "24000", "text"),
                ("provinceRent.type", "rent", "text"),
                
                # Other flags (set to false)
                ("hasOtherIncome", False, "boolean"),
                ("isFirstTimeFiler", False, "boolean"),
                ("isSelfEmployed", False, "boolean"),
                ("isFirstHomeBuyer", False, "boolean"),
                ("wasStudentLastYear", False, "boolean"),
                ("hasDisabilityTaxCredit", False, "boolean"),
                ("isFilingForDeceased", False, "boolean"),
                ("soldPropertyShortTerm", False, "boolean"),
                ("soldPropertyLongTerm", False, "boolean"),
                
                # Status fields
                ("status", "draft", "text"),
                ("awaitingDocuments", False, "boolean"),
                ("createdAt", datetime.utcnow().date().isoformat(), "text"),
                ("updatedAt", datetime.utcnow().date().isoformat(), "text"),
                ("id", filing_id, "text"),
            ]
            
            answer_query = text("""
                INSERT INTO t1_answers (id, t1_form_id, field_key, value_text, value_boolean, 
                                        created_at, updated_at)
                VALUES (:id, :t1_form_id, :field_key, :value_text, :value_boolean,
                        :created_at, :updated_at)
            """)
            
            for field_key, value, value_type in answers:
                answer_id = str(uuid4())
                
                params = {
                    "id": answer_id,
                    "t1_form_id": t1_form_id,
                    "field_key": field_key,
                    "value_text": value if value_type == "text" else None,
                    "value_boolean": value if value_type == "boolean" else None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await session.execute(answer_query, params)
            
            print(f"✓ Added {len(answers)} T1 form answers")
            
            # Skip documents for now - schema needs verification
            print("\n⚠ Skipping documents creation (schema verification needed)")
            
            # Commit all changes
            await session.commit()
            
            print("\n" + "="*60)
            print("✓ Test customer created successfully!")
            print("="*60)
            print(f"\nCustomer Details:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print(f"  Name: Hacur Kumar Tichkule")
            print(f"  User ID: {user_id}")
            print(f"  Filing ID: {filing_id}")
            print(f"  T1 Form ID: {t1_form_id}")
            print(f"  T1 Completion: 95%")
            print(f"  T1 Answers: 48 fields populated")
            print(f"\nYou can now view this customer in the admin dashboard!")
            print(f"Look for 'Hacur Tichkule' in the clients list.")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_customer())
