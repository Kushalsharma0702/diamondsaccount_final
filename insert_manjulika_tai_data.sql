-- ============================================================================
-- MANJULIKA TAI - COMPREHENSIVE T1 FORM TEST DATA
-- ============================================================================
-- Run this SQL directly on your AWS RDS PostgreSQL database
-- This creates a complete user with fully filled T1 form including all subforms
-- ============================================================================

-- Generate UUIDs for our records
DO $$
DECLARE
    v_user_id UUID := gen_random_uuid();
    v_filing_id UUID := gen_random_uuid();
    v_t1_form_id UUID := gen_random_uuid();
BEGIN
    -- ========================================================================
    -- 1. CREATE USER: Manjulika Tai
    -- ========================================================================
    INSERT INTO users (
        id, email, first_name, last_name, phone, password_hash,
        email_verified, is_active, created_at, updated_at
    ) VALUES (
        v_user_id,
        'manjulika.tai@example.com',
        'Manjulika',
        'Tai',
        '+1-416-555-9876',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5iGgXd7KmztCa', -- Password: ManjulikaTai@2024!
        true,
        true,
        NOW(),
        NOW()
    );
    
    RAISE NOTICE '✅ User created: %', v_user_id;
    
    -- ========================================================================
    -- 2. CREATE FILING FOR 2024
    -- ========================================================================
    INSERT INTO filings (
        id, user_id, filing_year, filing_type, status,
        assessment_fee, payment_status, is_active,
        created_at, updated_at
    ) VALUES (
        v_filing_id,
        v_user_id,
        2024,
        'personal',
        'in_preparation',
        299.99,
        'pending',
        true,
        NOW(),
        NOW()
    );
    
    RAISE NOTICE '✅ Filing created: %', v_filing_id;
    
    -- ========================================================================
    -- 3. CREATE T1 FORM
    -- ========================================================================
    INSERT INTO t1_forms (
        id, filing_id, user_id, status, is_locked,
        completion_percentage, last_saved_step_id,
        created_at, updated_at
    ) VALUES (
        v_t1_form_id,
        v_filing_id,
        v_user_id,
        'draft',
        false,
        85,
        'questionnaire',
        NOW(),
        NOW()
    );
    
    RAISE NOTICE '✅ T1 Form created: %', v_t1_form_id;
    
    -- ========================================================================
    -- 4. INSERT T1 ANSWERS - PERSONAL INFORMATION
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_text, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.firstName', 'Manjulika', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.middleName', 'Devi', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.lastName', 'Tai', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.address', '123 Haunted Mansion Drive, Apt 666, Toronto, ON M5H 2N2', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.phoneNumber', '+1-416-555-9876', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.email', 'manjulika.tai@example.com', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.maritalStatus', 'married', NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_numeric, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.sin', 987654321, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_date, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.dateOfBirth', '1985-08-15', NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.isCanadianCitizen', true, NOW(), NOW());
    
    RAISE NOTICE '✅ Personal info added';
    
    -- ========================================================================
    -- 5. SPOUSE INFORMATION
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_text, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.spouseInfo.firstName', 'Vikram', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.spouseInfo.middleName', 'Singh', NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.spouseInfo.lastName', 'Rathore', NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_numeric, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.spouseInfo.sin', 876543210, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_date, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.spouseInfo.dateOfBirth', '1983-03-20', NOW(), NOW());
    
    RAISE NOTICE '✅ Spouse info added';
    
    -- ========================================================================
    -- 6. CHILDREN INFORMATION (JSONB Array)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personalInfo.children', 
         '[
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
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Children info added';
    
    -- ========================================================================
    -- 7. FOREIGN PROPERTY (Q1)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'hasForeignProperty', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'foreignProperty', 
         '[
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
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Foreign property added';
    
    -- ========================================================================
    -- 8. MEDICAL EXPENSES (Q2)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'hasMedicalExpenses', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'medicalExpenses', 
         '[
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
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Medical expenses added';
    
    -- ========================================================================
    -- 9. WORK FROM HOME EXPENSES (Q9)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'hasWorkFromHomeExpense', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_numeric, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.totalHouseArea', 1800.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.totalWorkArea', 200.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.rentExpense', 24000.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.mortgageExpense', 0.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.wifiExpense', 960.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.electricityExpense', 1800.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.waterExpense', 600.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.heatExpense', 2400.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'workFromHomeExpense.totalInsuranceExpense', 1200.00, NOW(), NOW());
    
    RAISE NOTICE '✅ Work from home expenses added';
    
    -- ========================================================================
    -- 10. DAYCARE EXPENSES (Q12)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'hasDaycareExpenses', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'daycareExpenses', 
         '[
             {
                 "childcareProvider": "Little Angels Daycare",
                 "amount": 8500.00,
                 "identificationNumber": "123456789",
                 "weeks": 48
             },
             {
                 "childcareProvider": "After School Program - St. Mary''s",
                 "amount": 3200.00,
                 "identificationNumber": "987654321",
                 "weeks": 40
             }
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Daycare expenses added';
    
    -- ========================================================================
    -- 11. PROVINCE FILER (Q18 - Ontario)
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'isProvinceFiler', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'provinceFilerDetails', 
         '[
             {
                 "rentOrPropertyTax": "Rent",
                 "propertyAddress": "123 Haunted Mansion Drive, Apt 666, Toronto, ON",
                 "postalCode": "M5H 2N2",
                 "noOfMonthsResides": 12
             }
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Province filer details added';
    
    -- ========================================================================
    -- 12. EMPLOYMENT INCOME
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'hasEmploymentIncome', true, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_array, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'employmentIncome', 
         '[
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
         ]'::jsonb, NOW(), NOW());
    
    RAISE NOTICE '✅ Employment income added';
    
    -- ========================================================================
    -- 13. ADDITIONAL QUESTIONS
    -- ========================================================================
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_boolean, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'isFirstTimeFiler', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'soldPropertyShortTerm', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasRentalIncome', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasSelfEmploymentIncome', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasCapitalGains', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasInvestmentIncome', true, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasRRSPContribution', true, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasTFSAContribution', true, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasCharitableDonations', true, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasMovingExpenses', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasStudentLoanInterest', false, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'hasTuitionFees', false, NOW(), NOW());
    
    INSERT INTO t1_answers (id, t1_form_id, field_key, value_numeric, created_at, updated_at) VALUES
        (gen_random_uuid(), v_t1_form_id, 'investmentIncome.interestIncome', 1250.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'investmentIncome.dividendIncome', 3400.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'rrspContribution.amount', 15000.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'tfsaContribution.amount', 6500.00, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'charitableDonations.totalAmount', 2500.00, NOW(), NOW());
    
    RAISE NOTICE '✅ Additional questions added';
    
    -- ========================================================================
    -- 14. SECTION PROGRESS
    -- ========================================================================
    INSERT INTO t1_section_progress (
        id, t1_form_id, step_id, section_id, is_complete, completion_percentage,
        created_at, updated_at
    ) VALUES
        (gen_random_uuid(), v_t1_form_id, 'personal_info', 'individual_information', true, 100, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personal_info', 'spouse_information', true, 100, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'personal_info', 'children_details', true, 100, NOW(), NOW()),
        (gen_random_uuid(), v_t1_form_id, 'questionnaire', 'main_questions', true, 90, NOW(), NOW());
    
    RAISE NOTICE '✅ Section progress added';
    
    -- ========================================================================
    -- FINAL SUMMARY
    -- ========================================================================
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '✅ MANJULIKA TAI - COMPREHENSIVE DATA CREATED SUCCESSFULLY!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'User ID:      %', v_user_id;
    RAISE NOTICE 'Email:        manjulika.tai@example.com';
    RAISE NOTICE 'Password:     ManjulikaTai@2024!';
    RAISE NOTICE 'Filing ID:    %', v_filing_id;
    RAISE NOTICE 'T1 Form ID:   %', v_t1_form_id;
    RAISE NOTICE '';
    RAISE NOTICE '📝 Data includes:';
    RAISE NOTICE '   ✅ Complete personal information';
    RAISE NOTICE '   ✅ Spouse: Vikram Singh Rathore';
    RAISE NOTICE '   ✅ 2 Children: Chotu & Pinky';
    RAISE NOTICE '   ✅ Foreign properties (2 entries)';
    RAISE NOTICE '   ✅ Medical expenses (3 entries)';
    RAISE NOTICE '   ✅ Work from home expenses';
    RAISE NOTICE '   ✅ Daycare expenses (2 providers)';
    RAISE NOTICE '   ✅ Province filer details (Ontario)';
    RAISE NOTICE '   ✅ Employment income ($85,000)';
    RAISE NOTICE '   ✅ Investment income';
    RAISE NOTICE '   ✅ RRSP contributions ($15,000)';
    RAISE NOTICE '   ✅ TFSA contributions ($6,500)';
    RAISE NOTICE '   ✅ Charitable donations ($2,500)';
    RAISE NOTICE '============================================================';
    
END $$;

-- Verify the data
SELECT 
    'User' as entity,
    id,
    email,
    first_name || ' ' || last_name as name
FROM users 
WHERE email = 'manjulika.tai@example.com';

SELECT 
    'Filing' as entity,
    f.id,
    f.filing_year,
    f.status,
    u.email as user_email
FROM filings f
JOIN users u ON f.user_id = u.id
WHERE u.email = 'manjulika.tai@example.com';

SELECT 
    'T1 Form' as entity,
    t.id,
    t.status,
    t.completion_percentage,
    COUNT(a.id) as total_answers
FROM t1_forms t
JOIN users u ON t.user_id = u.id
LEFT JOIN t1_answers a ON t.id = a.t1_form_id
WHERE u.email = 'manjulika.tai@example.com'
GROUP BY t.id, t.status, t.completion_percentage;
