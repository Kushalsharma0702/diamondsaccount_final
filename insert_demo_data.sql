-- ============================================================================
-- DEMO DATA INSERTION SCRIPT FOR TAXEASE DATABASE
-- This script inserts 5 complete demo entries for all tables
-- Run with: PGPASSWORD=Kushal07 psql -h localhost -U postgres -d taxease_db -f insert_demo_data.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. USERS TABLE (Client app users)
-- ============================================================================
INSERT INTO users (id, email, password_hash, first_name, last_name, phone, is_active, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'John', 'Doe', '+1-555-0101', true, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Jane', 'Smith', '+1-555-0102', true, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'michael.johnson@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Michael', 'Johnson', '+1-555-0103', true, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444', 'sarah.williams@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Sarah', 'Williams', '+1-555-0104', true, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555', 'david.brown@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'David', 'Brown', '+1-555-0105', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 2. ADMIN USERS TABLE
-- ============================================================================
INSERT INTO admin_users (id, email, password_hash, name, role, permissions, is_active, created_at, updated_at)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'admin1@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Senior Admin', 'admin', ARRAY['view_clients', 'edit_clients', 'view_documents', 'edit_documents'], true, NOW(), NOW()),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'admin2@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Tax Specialist', 'admin', ARRAY['view_clients', 'edit_clients'], true, NOW(), NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'admin3@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Document Manager', 'admin', ARRAY['view_documents', 'edit_documents'], true, NOW(), NOW()),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'admin4@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Payment Officer', 'admin', ARRAY['view_payments', 'edit_payments'], true, NOW(), NOW()),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'admin5@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Support Admin', 'admin', ARRAY['view_clients'], true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 3. CLIENTS TABLE
-- ============================================================================
INSERT INTO clients (id, name, email, phone, filing_year, status, payment_status, assigned_admin_id, total_amount, paid_amount, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'John Doe', 'john.doe@example.com', '+1-555-0101', 2025, 'documents_pending', 'pending', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 500.00, 0.00, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'Jane Smith', 'jane.smith@example.com', '+1-555-0102', 2025, 'in_progress', 'partial', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 750.00, 250.00, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'Michael Johnson', 'michael.johnson@example.com', '+1-555-0103', 2025, 'review', 'paid', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 600.00, 600.00, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444', 'Sarah Williams', 'sarah.williams@example.com', '+1-555-0104', 2025, 'completed', 'paid', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 550.00, 550.00, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555', 'David Brown', 'david.brown@example.com', '+1-555-0105', 2025, 'filed', 'paid', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 800.00, 800.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 4. FILES TABLE (For document uploads)
-- ============================================================================
INSERT INTO files (id, user_id, file_name, file_type, file_size, file_path, upload_date, status, created_at, updated_at)
VALUES
    (1001, '11111111-1111-1111-1111-111111111111', 'T4_2024_JohnDoe.pdf', 'application/pdf', 245760, '/uploads/2025/t4_johndoe.pdf', NOW(), 'uploaded', NOW(), NOW()),
    (1002, '22222222-2222-2222-2222-222222222222', 'T5_2024_JaneSmith.pdf', 'application/pdf', 189440, '/uploads/2025/t5_janesmith.pdf', NOW(), 'uploaded', NOW(), NOW()),
    (1003, '33333333-3333-3333-3333-333333333333', 'Medical_Receipts_Michael.pdf', 'application/pdf', 512000, '/uploads/2025/medical_michael.pdf', NOW(), 'uploaded', NOW(), NOW()),
    (1004, '44444444-4444-4444-4444-444444444444', 'Donation_Receipts_Sarah.pdf', 'application/pdf', 102400, '/uploads/2025/donation_sarah.pdf', NOW(), 'uploaded', NOW(), NOW()),
    (1005, '55555555-5555-5555-5555-555555555555', 'Property_Statement_David.pdf', 'application/pdf', 327680, '/uploads/2025/property_david.pdf', NOW(), 'uploaded', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 5. T1 PERSONAL INFO TABLE
-- ============================================================================
INSERT INTO t1_personal_info (id, user_id, sin, first_name, last_name, date_of_birth, marital_status, address_line1, city, province, postal_code, email, phone, created_at, updated_at)
VALUES
    (2001, '11111111-1111-1111-1111-111111111111', '123-456-789', 'John', 'Doe', '1985-03-15', 'married', '123 Main Street', 'Toronto', 'ON', 'M5H 2N2', 'john.doe@example.com', '+1-555-0101', NOW(), NOW()),
    (2002, '22222222-2222-2222-2222-222222222222', '234-567-890', 'Jane', 'Smith', '1990-07-22', 'single', '456 Oak Avenue', 'Vancouver', 'BC', 'V6B 1A1', 'jane.smith@example.com', '+1-555-0102', NOW(), NOW()),
    (2003, '33333333-3333-3333-3333-333333333333', '345-678-901', 'Michael', 'Johnson', '1982-11-30', 'married', '789 Pine Road', 'Calgary', 'AB', 'T2P 3B8', 'michael.johnson@example.com', '+1-555-0103', NOW(), NOW()),
    (2004, '44444444-4444-4444-4444-444444444444', '456-789-012', 'Sarah', 'Williams', '1988-05-18', 'divorced', '321 Elm Street', 'Ottawa', 'ON', 'K1A 0A6', 'sarah.williams@example.com', '+1-555-0104', NOW(), NOW()),
    (2005, '55555555-5555-5555-5555-555555555555', '567-890-123', 'David', 'Brown', '1975-09-25', 'married', '654 Maple Drive', 'Montreal', 'QC', 'H3A 0B1', 'david.brown@example.com', '+1-555-0105', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 6. T1 FORMS (Main questionnaire responses)
-- ============================================================================
INSERT INTO t1_forms (id, user_id, filing_year, status, has_t4, has_t5, has_moving_expenses, has_medical_expenses, has_donations, has_rrsp, has_foreign_property, created_at, updated_at)
VALUES
    (3001, '11111111-1111-1111-1111-111111111111', 2024, 'in_progress', true, false, false, true, false, true, false, NOW(), NOW()),
    (3002, '22222222-2222-2222-2222-222222222222', 2024, 'in_progress', true, true, false, false, true, false, false, NOW(), NOW()),
    (3003, '33333333-3333-3333-3333-333333333333', 2024, 'completed', true, false, true, true, true, true, false, NOW(), NOW()),
    (3004, '44444444-4444-4444-4444-444444444444', 2024, 'completed', true, true, false, true, true, false, false, NOW(), NOW()),
    (3005, '55555555-5555-5555-5555-555555555555', 2024, 'filed', true, true, false, false, false, true, true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 7. T1 PERSONAL FORMS TABLE
-- ============================================================================
INSERT INTO t1_personal_forms (id, user_id, filing_year, first_name, last_name, sin, date_of_birth, marital_status, 
    has_t4_employment, has_t5_investment, has_self_employment, has_rental_income, has_uber_business, has_general_business,
    has_moving_expenses, has_medical_expenses, has_donations, has_foreign_property, has_rrsp, has_spouse,
    form_status, created_at, updated_at)
VALUES
    (4001, '11111111-1111-1111-1111-111111111111', 2024, 'John', 'Doe', '123-456-789', '1985-03-15', 'married',
     true, false, false, false, false, false, false, true, false, false, true, true, 'in_progress', NOW(), NOW()),
    (4002, '22222222-2222-2222-2222-222222222222', 2024, 'Jane', 'Smith', '234-567-890', '1990-07-22', 'single',
     true, true, false, false, false, false, false, false, true, false, false, false, 'in_progress', NOW(), NOW()),
    (4003, '33333333-3333-3333-3333-333333333333', 2024, 'Michael', 'Johnson', '345-678-901', '1982-11-30', 'married',
     true, false, true, false, false, false, true, true, true, false, true, true, 'completed', NOW(), NOW()),
    (4004, '44444444-4444-4444-4444-444444444444', 2024, 'Sarah', 'Williams', '456-789-012', '1988-05-18', 'divorced',
     true, true, false, true, false, false, false, true, true, false, false, false, 'completed', NOW(), NOW()),
    (4005, '55555555-5555-5555-5555-555555555555', 2024, 'David', 'Brown', '567-890-123', '1975-09-25', 'married',
     true, true, false, false, true, false, false, false, false, true, true, true, 'filed', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 8. T1 SPOUSE INFO TABLE
-- ============================================================================
INSERT INTO t1_spouse_info (id, t1_form_id, first_name, last_name, sin, date_of_birth, net_income, created_at, updated_at)
VALUES
    (5001, 4001, 'Mary', 'Doe', '987-654-321', '1987-06-20', 35000.00, NOW(), NOW()),
    (5003, 4003, 'Emily', 'Johnson', '876-543-210', '1984-09-15', 42000.00, NOW(), NOW()),
    (5005, 4005, 'Linda', 'Brown', '765-432-109', '1978-12-10', 38000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 9. T1 CHILD INFO TABLE
-- ============================================================================
INSERT INTO t1_child_info (id, t1_form_id, first_name, last_name, date_of_birth, relationship, is_eligible_for_child_care, created_at, updated_at)
VALUES
    (6001, 4001, 'Tommy', 'Doe', '2015-04-10', 'son', true, NOW(), NOW()),
    (6002, 4001, 'Emma', 'Doe', '2018-08-22', 'daughter', true, NOW(), NOW()),
    (6003, 4003, 'Lucas', 'Johnson', '2012-03-15', 'son', true, NOW(), NOW()),
    (6004, 4004, 'Sophia', 'Williams', '2016-11-30', 'daughter', true, NOW(), NOW()),
    (6005, 4005, 'Oliver', 'Brown', '2014-07-25', 'son', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 10. T1 SELF EMPLOYMENT TABLE
-- ============================================================================
INSERT INTO t1_self_employment (id, t1_form_id, business_name, business_activity, gross_income, expenses, net_income, created_at, updated_at)
VALUES
    (7001, 4003, 'Johnson Consulting', 'IT Consulting', 85000.00, 15000.00, 70000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 11. T1 RENTAL INCOME TABLE
-- ============================================================================
INSERT INTO t1_rental_income (id, t1_form_id, property_address, rental_income, expenses, net_rental_income, created_at, updated_at)
VALUES
    (8001, 4004, '789 Rental Ave, Ottawa, ON', 24000.00, 8000.00, 16000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 12. T1 UBER BUSINESS TABLE
-- ============================================================================
INSERT INTO t1_uber_business (id, t1_form_id, gross_earnings, platform_fees, vehicle_expenses, other_expenses, net_income, created_at, updated_at)
VALUES
    (9001, 4005, 45000.00, 9000.00, 12000.00, 3000.00, 21000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 13. T1 GENERAL BUSINESS TABLE
-- ============================================================================
INSERT INTO t1_general_business (id, t1_form_id, business_name, business_type, gross_revenue, cost_of_goods_sold, total_expenses, net_income, created_at, updated_at)
VALUES
    (10001, 4003, 'Johnson IT Solutions', 'Professional Services', 120000.00, 0.00, 30000.00, 90000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 14. T1 MOVING EXPENSES TABLE
-- ============================================================================
INSERT INTO t1_moving_expenses (id, t1_form_id, reason_for_move, old_address, new_address, distance_km, moving_date, 
    travel_costs, transportation_costs, meals, temporary_accommodation, total_expenses, created_at, updated_at)
VALUES
    (11001, 4003, 'New job', '456 Old St, Toronto, ON', '789 Pine Rd, Calgary, AB', 3400, '2024-06-15',
     1500.00, 3500.00, 300.00, 1200.00, 6500.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 15. T1 MOVING EXPENSES INDIVIDUAL TABLE
-- ============================================================================
INSERT INTO t1_moving_expenses_individual (id, moving_expense_id, travel_costs, transportation_costs, temporary_living_costs, other_costs, created_at, updated_at)
VALUES
    (12001, 11001, 1500.00, 3500.00, 1200.00, 300.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 16. T1 FOREIGN PROPERTIES TABLE
-- ============================================================================
INSERT INTO t1_foreign_properties (id, t1_form_id, country, property_type, property_address, acquisition_date, cost_amount, current_value, income_generated, created_at, updated_at)
VALUES
    (13001, 4005, 'United States', 'Rental Property', '123 Beach Ave, Miami, FL', '2020-03-15', 250000.00, 280000.00, 18000.00, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 17. T1 QUESTIONS TABLE (Questionnaire questions)
-- ============================================================================
INSERT INTO t1_questions (id, question_text, question_type, category, section, options, is_required, display_order, created_at, updated_at)
VALUES
    (20001, 'Do you have T4 employment income?', 'yes_no', 'employment', 'income', NULL, true, 1, NOW(), NOW()),
    (20002, 'Do you have T5 investment income?', 'yes_no', 'investment', 'income', NULL, true, 2, NOW(), NOW()),
    (20003, 'Do you have self-employment income?', 'yes_no', 'self_employment', 'income', NULL, true, 3, NOW(), NOW()),
    (20004, 'Did you have moving expenses for work or school?', 'yes_no', 'moving', 'deductions', NULL, false, 4, NOW(), NOW()),
    (20005, 'Do you have medical expenses to claim?', 'yes_no', 'medical', 'deductions', NULL, false, 5, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 18. T1 ANSWERS TABLE (Questionnaire responses)
-- ============================================================================
INSERT INTO t1_answers (id, t1_form_id, question_id, answer_text, answer_boolean, created_at, updated_at)
VALUES
    (30001, 4001, 20001, NULL, true, NOW(), NOW()),
    (30002, 4001, 20002, NULL, false, NOW(), NOW()),
    (30003, 4002, 20001, NULL, true, NOW(), NOW()),
    (30004, 4003, 20003, NULL, true, NOW(), NOW()),
    (30005, 4004, 20005, NULL, true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 19. T1 ANSWER FILES TABLE (File uploads for questionnaire answers)
-- ============================================================================
INSERT INTO t1_answer_files (id, answer_id, file_id, created_at)
VALUES
    (40001, 30001, 1001, NOW()),
    (40002, 30003, 1002, NOW()),
    (40003, 30004, 1003, NOW()),
    (40004, 30005, 1004, NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 20. DOCUMENTS TABLE
-- ============================================================================
INSERT INTO documents (id, client_id, document_type, file_name, file_path, file_size, status, uploaded_by, created_at, updated_at)
VALUES
    (50001, '11111111-1111-1111-1111-111111111111', 'T4', 'T4_2024_JohnDoe.pdf', '/uploads/2025/t4_johndoe.pdf', 245760, 'pending', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', NOW(), NOW()),
    (50002, '22222222-2222-2222-2222-222222222222', 'T5', 'T5_2024_JaneSmith.pdf', '/uploads/2025/t5_janesmith.pdf', 189440, 'approved', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', NOW(), NOW()),
    (50003, '33333333-3333-3333-3333-333333333333', 'Medical Receipt', 'Medical_Receipts_Michael.pdf', '/uploads/2025/medical_michael.pdf', 512000, 'approved', 'cccccccc-cccc-cccc-cccc-cccccccccccc', NOW(), NOW()),
    (50004, '44444444-4444-4444-4444-444444444444', 'Donation Receipt', 'Donation_Receipts_Sarah.pdf', '/uploads/2025/donation_sarah.pdf', 102400, 'approved', 'dddddddd-dddd-dddd-dddd-dddddddddddd', NOW(), NOW()),
    (50005, '55555555-5555-5555-5555-555555555555', 'Property Statement', 'Property_Statement_David.pdf', '/uploads/2025/property_david.pdf', 327680, 'approved', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 21. PAYMENTS TABLE
-- ============================================================================
INSERT INTO payments (id, client_id, amount, payment_method, payment_status, transaction_id, created_at, updated_at)
VALUES
    (60001, '22222222-2222-2222-2222-222222222222', 250.00, 'credit_card', 'completed', 'TXN-2025-001', NOW(), NOW()),
    (60002, '33333333-3333-3333-3333-333333333333', 600.00, 'bank_transfer', 'completed', 'TXN-2025-002', NOW(), NOW()),
    (60003, '44444444-4444-4444-4444-444444444444', 550.00, 'credit_card', 'completed', 'TXN-2025-003', NOW(), NOW()),
    (60004, '55555555-5555-5555-5555-555555555555', 800.00, 'paypal', 'completed', 'TXN-2025-004', NOW(), NOW()),
    (60005, '11111111-1111-1111-1111-111111111111', 150.00, 'credit_card', 'pending', 'TXN-2025-005', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 22. COST ESTIMATES TABLE
-- ============================================================================
INSERT INTO cost_estimates (id, client_id, base_cost, additional_forms_cost, complexity_multiplier, estimated_total, status, created_at, updated_at)
VALUES
    (70001, '11111111-1111-1111-1111-111111111111', 300.00, 100.00, 1.2, 480.00, 'pending', NOW(), NOW()),
    (70002, '22222222-2222-2222-2222-222222222222', 350.00, 150.00, 1.5, 750.00, 'approved', NOW(), NOW()),
    (70003, '33333333-3333-3333-3333-333333333333', 300.00, 200.00, 1.2, 600.00, 'approved', NOW(), NOW()),
    (70004, '44444444-4444-4444-4444-444444444444', 300.00, 150.00, 1.2, 540.00, 'approved', NOW(), NOW()),
    (70005, '55555555-5555-5555-5555-555555555555', 400.00, 250.00, 1.2, 780.00, 'approved', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 23. NOTES TABLE
-- ============================================================================
INSERT INTO notes (id, client_id, admin_id, note_text, is_internal, created_at, updated_at)
VALUES
    (80001, '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Client needs to submit T4 slip', true, NOW(), NOW()),
    (80002, '22222222-2222-2222-2222-222222222222', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Partial payment received, follow up on balance', true, NOW(), NOW()),
    (80003, '33333333-3333-3333-3333-333333333333', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'Medical expenses reviewed and approved', false, NOW(), NOW()),
    (80004, '44444444-4444-4444-4444-444444444444', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'All documents received, ready for filing', false, NOW(), NOW()),
    (80005, '55555555-5555-5555-5555-555555555555', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Tax return filed successfully, confirmation sent', false, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 24. AUDIT LOGS TABLE
-- ============================================================================
INSERT INTO audit_logs (id, performed_by_id, action, entity_type, entity_id, changes, ip_address, user_agent, created_at)
VALUES
    (90001, 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'CREATE', 'client', '11111111-1111-1111-1111-111111111111', '{"status": "documents_pending"}', '192.168.1.101', 'Mozilla/5.0', NOW()),
    (90002, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'UPDATE', 'client', '22222222-2222-2222-2222-222222222222', '{"status": "in_progress"}', '192.168.1.102', 'Mozilla/5.0', NOW()),
    (90003, 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'APPROVE', 'document', '50003', '{"status": "approved"}', '192.168.1.103', 'Mozilla/5.0', NOW()),
    (90004, 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'UPDATE', 'payment', '60003', '{"status": "completed"}', '192.168.1.104', 'Mozilla/5.0', NOW()),
    (90005, 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'FILE', 'client', '55555555-5555-5555-5555-555555555555', '{"status": "filed"}', '192.168.1.105', 'Mozilla/5.0', NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 25. REPORTS TABLE
-- ============================================================================
INSERT INTO reports (id, client_id, report_type, filing_year, report_data, generated_by, status, created_at, updated_at)
VALUES
    (100001, '33333333-3333-3333-3333-333333333333', 'T1_SUMMARY', 2024, '{"total_income": 85000, "total_deductions": 15000, "net_income": 70000}', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'completed', NOW(), NOW()),
    (100002, '44444444-4444-4444-4444-444444444444', 'TAX_RETURN', 2024, '{"total_income": 65000, "taxes_owed": 8500, "refund": 0}', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'completed', NOW(), NOW()),
    (100003, '55555555-5555-5555-5555-555555555555', 'NOTICE_OF_ASSESSMENT', 2024, '{"total_income": 98000, "taxes_paid": 22000, "refund": 1200}', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'completed', NOW(), NOW()),
    (100004, '22222222-2222-2222-2222-222222222222', 'T1_SUMMARY', 2024, '{"total_income": 55000, "total_deductions": 8000, "net_income": 47000}', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'in_progress', NOW(), NOW()),
    (100005, '11111111-1111-1111-1111-111111111111', 'TAX_ESTIMATE', 2024, '{"estimated_income": 72000, "estimated_taxes": 12000}', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'draft', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 26. T1 CALCULATION SNAPSHOTS TABLE
-- ============================================================================
INSERT INTO t1_calculation_snapshots (id, t1_form_id, snapshot_data, created_at)
VALUES
    (110001, 4003, '{"total_income": 85000, "rrsp_deduction": 10000, "medical_expenses": 2500, "net_income": 72500}'::jsonb, NOW()),
    (110002, 4004, '{"total_income": 65000, "medical_expenses": 1800, "donations": 500, "net_income": 62700}'::jsonb, NOW()),
    (110003, 4005, '{"total_income": 98000, "rrsp_deduction": 15000, "foreign_income": 18000, "net_income": 101000}'::jsonb, NOW()),
    (110004, 4002, '{"total_income": 55000, "donations": 250, "net_income": 54750}'::jsonb, NOW()),
    (110005, 4001, '{"total_income": 72000, "rrsp_deduction": 8000, "medical_expenses": 1200, "net_income": 62800}'::jsonb, NOW())
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- ============================================================================
-- Verify insertion
-- ============================================================================
SELECT 'Demo data insertion completed!' AS status;
SELECT 'Users: ' || COUNT(*) FROM users WHERE id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555');
SELECT 'Admin Users: ' || COUNT(*) FROM admin_users WHERE id IN ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee');
SELECT 'Clients: ' || COUNT(*) FROM clients WHERE id IN ('11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555');
SELECT 'T1 Personal Forms: ' || COUNT(*) FROM t1_personal_forms WHERE id BETWEEN 4001 AND 4005;
SELECT 'T1 Questions: ' || COUNT(*) FROM t1_questions WHERE id BETWEEN 20001 AND 20005;
SELECT 'T1 Answers: ' || COUNT(*) FROM t1_answers WHERE id BETWEEN 30001 AND 30005;
SELECT 'Documents: ' || COUNT(*) FROM documents WHERE id BETWEEN 50001 AND 50005;
SELECT 'Payments: ' || COUNT(*) FROM payments WHERE id BETWEEN 60001 AND 60005;
