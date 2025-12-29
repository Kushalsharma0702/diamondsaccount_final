-- ============================================================================
-- CORRECTED DEMO DATA INSERTION SCRIPT FOR TAXEASE DATABASE
-- Matches actual database schema
-- Run with: PGPASSWORD=Kushal07 psql -h localhost -U postgres -d taxease_db -f insert_demo_data_corrected.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- CLEAN UP ALL DEMO DATA FIRST (with CASCADE to handle foreign keys)
-- ============================================================================
\echo 'Cleaning up existing demo data...'

-- Delete in reverse dependency order (using CAST for UUID columns)
DELETE FROM audit_logs WHERE CAST(id AS TEXT) LIKE 'al000%';
DELETE FROM cost_estimates WHERE CAST(id AS TEXT) LIKE 'ce000%';
DELETE FROM notes WHERE CAST(id AS TEXT) LIKE 'n0000%';
DELETE FROM t1_answers WHERE CAST(id AS TEXT) LIKE 'a0000%';
DELETE FROM t1_personal_forms WHERE id LIKE 'pf000%';
DELETE FROM t1_forms WHERE CAST(id AS TEXT) LIKE 'tf000%';
DELETE FROM t1_questions WHERE CAST(id AS TEXT) LIKE 'q0000%';
DELETE FROM t1_personal_info WHERE CAST(id AS TEXT) LIKE 'pi000%';
DELETE FROM payments WHERE CAST(id AS TEXT) LIKE 'p0000%';
DELETE FROM documents WHERE CAST(id AS TEXT) LIKE 'd0000%';
DELETE FROM files WHERE CAST(id AS TEXT) LIKE 'f0000%';
DELETE FROM clients WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid);
DELETE FROM admin_users WHERE id IN ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid);
DELETE FROM users WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid);

\echo 'Cleanup complete. Inserting new demo data...'

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
INSERT INTO users (id, email, password_hash, first_name, last_name, phone, is_active, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'John', 'Doe', '+1-555-0101', true, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Jane', 'Smith', '+1-555-0102', true, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'michael.johnson@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Michael', 'Johnson', '+1-555-0103', true, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444', 'sarah.williams@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Sarah', 'Williams', '+1-555-0104', true, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555', 'david.brown@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'David', 'Brown', '+1-555-0105', true, NOW(), NOW());

-- ============================================================================
-- 2. ADMIN USERS TABLE
-- ============================================================================
INSERT INTO admin_users (id, email, password_hash, name, role, permissions, is_active, created_at, updated_at)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'admin1@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Senior Admin', 'admin', ARRAY['view_clients', 'edit_clients', 'view_documents', 'edit_documents'], true, NOW(), NOW()),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'admin2@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Tax Specialist', 'admin', ARRAY['view_clients', 'edit_clients'], true, NOW(), NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'admin3@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Document Manager', 'admin', ARRAY['view_documents', 'edit_documents'], true, NOW(), NOW()),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'admin4@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Payment Officer', 'admin', ARRAY['view_payments', 'edit_payments'], true, NOW(), NOW()),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'admin5@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Support Admin', 'admin', ARRAY['view_clients'], true, NOW(), NOW());

-- ============================================================================
-- 3. CLIENTS TABLE
-- ============================================================================
INSERT INTO clients (id, name, email, phone, filing_year, status, payment_status, assigned_admin_id, total_amount, paid_amount, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'John Doe', 'john.doe@example.com', '+1-555-0101', 2025, 'documents_pending', 'pending', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 500.00, 0.00, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222', 'Jane Smith', 'jane.smith@example.com', '+1-555-0102', 2025, 'in_progress', 'partial', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 750.00, 250.00, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333', 'Michael Johnson', 'michael.johnson@example.com', '+1-555-0103', 2025, 'review', 'paid', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 600.00, 600.00, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444', 'Sarah Williams', 'sarah.williams@example.com', '+1-555-0104', 2025, 'completed', 'paid', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 550.00, 550.00, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555', 'David Brown', 'david.brown@example.com', '+1-555-0105', 2025, 'filed', 'paid', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 800.00, 800.00, NOW(), NOW());

-- ============================================================================
-- 4. FILES TABLE (Corrected columns)
-- ============================================================================
INSERT INTO files (id, user_id, filename, original_filename, file_type, file_size, upload_status, created_at)
VALUES
    ('f0000001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', 't4_johndoe_2024.pdf', 'T4_2024_JohnDoe.pdf', 'application/pdf', 245760, 'completed', NOW()),
    ('f0000002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', 't5_janesmith_2024.pdf', 'T5_2024_JaneSmith.pdf', 'application/pdf', 189440, 'completed', NOW()),
    ('f0000003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', 'medical_michael.pdf', 'Medical_Receipts_Michael.pdf', 'application/pdf', 512000, 'completed', NOW()),
    ('f0000004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', 'donation_sarah.pdf', 'Donation_Receipts_Sarah.pdf', 'application/pdf', 102400, 'completed', NOW()),
    ('f0000005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', 'property_david.pdf', 'Property_Statement_David.pdf', 'application/pdf', 327680, 'completed', NOW());

-- ============================================================================
-- 5. DOCUMENTS TABLE (Corrected columns)
-- ============================================================================
INSERT INTO documents (id, client_id, name, type, status, version, uploaded_at, notes, created_at, updated_at)
VALUES
    ('d0000001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', 'T4 Employment Income', 'T4', 'pending', 1, NOW(), 'Needs review', NOW(), NOW()),
    ('d0000002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', 'T5 Investment Income', 'T5', 'approved', 1, NOW(), 'Approved', NOW(), NOW()),
    ('d0000003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', 'Medical Receipts', 'medical', 'approved', 1, NOW(), 'All receipts verified', NOW(), NOW()),
    ('d0000004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', 'Donation Receipts', 'donation', 'approved', 1, NOW(), 'Charitable donations verified', NOW(), NOW()),
    ('d0000005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', 'Foreign Property Statement', 'foreign_property', 'approved', 1, NOW(), 'US property documented', NOW(), NOW());

-- ============================================================================
-- 6. PAYMENTS TABLE (Corrected columns)
-- ============================================================================
INSERT INTO payments (id, client_id, amount, method, note, created_by_id, created_at)
VALUES
    ('00000001-0000-0000-0001-000000000001'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 250.00, 'credit_card', 'Partial payment for 2024 return', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, NOW()),
    ('00000002-0000-0000-0002-000000000002'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, 600.00, 'bank_transfer', 'Full payment received', 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, NOW()),
    ('00000003-0000-0000-0003-000000000003'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, 550.00, 'credit_card', 'Payment for tax filing', 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, NOW()),
    ('00000004-0000-0000-0004-000000000004'::uuid, '55555555-5555-5555-5555-555555555555'::uuid, 800.00, 'paypal', 'Complete payment', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid, NOW()),
    ('00000005-0000-0000-0005-000000000005'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 150.00, 'credit_card', 'Deposit payment', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, NOW());

-- ============================================================================
-- 7. T1 QUESTIONS TABLE (Corrected columns)
-- ============================================================================
INSERT INTO t1_questions (id, code, question_text, answer_type, is_repeatable, has_children, created_at)
VALUES
    ('q0000001-0001-0001-0001-000000000001', 'Q001_T4_EMPLOYMENT', 'Do you have T4 employment income?', 'yes_no', false, false, NOW()),
    ('q0000002-0002-0002-0002-000000000002', 'Q002_T5_INVESTMENT', 'Do you have T5 investment income?', 'yes_no', false, false, NOW()),
    ('q0000003-0003-0003-0003-000000000003', 'Q003_SELF_EMPLOYMENT', 'Do you have self-employment income?', 'yes_no', false, true, NOW()),
    ('q0000004-0004-0004-0004-000000000004', 'Q004_MOVING_EXPENSES', 'Did you have moving expenses for work or school?', 'yes_no', false, true, NOW()),
    ('q0000005-0005-0005-0005-000000000005', 'Q005_MEDICAL_EXPENSES', 'Do you have medical expenses to claim?', 'yes_no', false, true, NOW());

-- ============================================================================
-- 8. T1 ANSWERS TABLE (Corrected for UUID)
-- ============================================================================
INSERT INTO t1_answers (id, t1_form_id, question_id, answer, created_at, updated_at)
VALUES
    ('a0000001-0001-0001-0001-000000000001', 'tf000001-0001-0001-0001-000000000001', 'q0000001-0001-0001-0001-000000000001', 'true', NOW(), NOW()),
    ('a0000002-0002-0002-0002-000000000002', 'tf000001-0001-0001-0001-000000000001', 'q0000002-0002-0002-0002-000000000002', 'false', NOW(), NOW()),
    ('a0000003-0003-0003-0003-000000000003', 'tf000002-0002-0002-0002-000000000002', 'q0000001-0001-0001-0001-000000000001', 'true', NOW(), NOW()),
    ('a0000004-0004-0004-0004-000000000004', 'tf000003-0003-0003-0003-000000000003', 'q0000003-0003-0003-0003-000000000003', 'true', NOW(), NOW()),
    ('a0000005-0005-0005-0005-000000000005', 'tf000004-0004-0004-0004-000000000004', 'q0000005-0005-0005-0005-000000000005', 'true', NOW(), NOW());

-- ============================================================================
-- 9. T1 FORMS TABLE (Need to create t1_form_id references first)
-- ============================================================================
INSERT INTO t1_forms (id, user_id, filing_year, status, created_at, updated_at)
VALUES
    ('tf000001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', 2024, 'in_progress', NOW(), NOW()),
    ('tf000002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', 2024, 'in_progress', NOW(), NOW()),
    ('tf000003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', 2024, 'completed', NOW(), NOW()),
    ('tf000004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', 2024, 'completed', NOW(), NOW()),
    ('tf000005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', 2024, 'filed', NOW(), NOW());

-- ============================================================================
-- 10. T1 PERSONAL INFO TABLE
-- ============================================================================
INSERT INTO t1_personal_info (id, user_id, sin, first_name, last_name, date_of_birth, marital_status, address_line1, city, province, postal_code, email, phone, created_at, updated_at)
VALUES
    ('pi00001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', '123-456-789', 'John', 'Doe', '1985-03-15', 'married', '123 Main Street', 'Toronto', 'ON', 'M5H 2N2', 'john.doe@example.com', '+1-555-0101', NOW(), NOW()),
    ('pi00002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', '234-567-890', 'Jane', 'Smith', '1990-07-22', 'single', '456 Oak Avenue', 'Vancouver', 'BC', 'V6B 1A1', 'jane.smith@example.com', '+1-555-0102', NOW(), NOW()),
    ('pi00003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', '345-678-901', 'Michael', 'Johnson', '1982-11-30', 'married', '789 Pine Road', 'Calgary', 'AB', 'T2P 3B8', 'michael.johnson@example.com', '+1-555-0103', NOW(), NOW()),
    ('pi00004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', '456-789-012', 'Sarah', 'Williams', '1988-05-18', 'divorced', '321 Elm Street', 'Ottawa', 'ON', 'K1A 0A6', 'sarah.williams@example.com', '+1-555-0104', NOW(), NOW()),
    ('pi00005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', '567-890-123', 'David', 'Brown', '1975-09-25', 'married', '654 Maple Drive', 'Montreal', 'QC', 'H3A 0B1', 'david.brown@example.com', '+1-555-0105', NOW(), NOW());

-- ============================================================================
-- 11. T1 PERSONAL FORMS (Matching actual schema)
-- ============================================================================
INSERT INTO t1_personal_forms (id, user_id, tax_year, status, first_name, last_name, email, 
    has_foreign_property, has_medical_expenses, has_charitable_donations, has_moving_expenses, is_self_employed, is_first_home_buyer)
VALUES
    ('pf00001', '11111111-1111-1111-1111-111111111111', 2024, 'in_progress', 'John', 'Doe', 'john.doe@example.com', 
     false, true, false, false, false, false),
    ('pf00002', '22222222-2222-2222-2222-222222222222', 2024, 'in_progress', 'Jane', 'Smith', 'jane.smith@example.com', 
     false, false, true, false, false, false),
    ('pf00003', '33333333-3333-3333-3333-333333333333', 2024, 'completed', 'Michael', 'Johnson', 'michael.johnson@example.com', 
     false, true, true, true, true, false),
    ('pf00004', '44444444-4444-4444-4444-444444444444', 2024, 'completed', 'Sarah', 'Williams', 'sarah.williams@example.com', 
     false, true, true, false, false, false),
    ('pf00005', '55555555-5555-5555-5555-555555555555', 2024, 'filed', 'David', 'Brown', 'david.brown@example.com', 
     true, false, false, false, false, false);

-- ============================================================================
-- 12. NOTES TABLE
-- ============================================================================
INSERT INTO notes (id, client_id, admin_id, note_text, is_internal, created_at, updated_at)
VALUES
    ('n0000001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Client needs to submit T4 slip', true, NOW(), NOW()),
    ('n0000002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Partial payment received, follow up on balance', true, NOW(), NOW()),
    ('n0000003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'Medical expenses reviewed and approved', false, NOW(), NOW()),
    ('n0000004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'All documents received, ready for filing', false, NOW(), NOW()),
    ('n0000005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Tax return filed successfully', false, NOW(), NOW());

-- ============================================================================
-- 13. AUDIT LOGS TABLE
-- ============================================================================
INSERT INTO audit_logs (id, performed_by_id, action, entity_type, entity_id, changes, ip_address, user_agent, created_at)
VALUES
    ('al00001-0001-0001-0001-000000000001', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'CREATE', 'client', '11111111-1111-1111-1111-111111111111', '{"status": "documents_pending"}', '192.168.1.101', 'Mozilla/5.0', NOW()),
    ('al00002-0002-0002-0002-000000000002', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'UPDATE', 'client', '22222222-2222-2222-2222-222222222222', '{"status": "in_progress"}', '192.168.1.102', 'Mozilla/5.0', NOW()),
    ('al00003-0003-0003-0003-000000000003', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'APPROVE', 'document', 'd0000003-0003-0003-0003-000000000003', '{"status": "approved"}', '192.168.1.103', 'Mozilla/5.0', NOW()),
    ('al00004-0004-0004-0004-000000000004', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'UPDATE', 'payment', 'p0000003-0003-0003-0003-000000000003', '{"status": "completed"}', '192.168.1.104', 'Mozilla/5.0', NOW()),
    ('al00005-0005-0005-0005-000000000005', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'FILE', 'client', '55555555-5555-5555-5555-555555555555', '{"status": "filed"}', '192.168.1.105', 'Mozilla/5.0', NOW());

-- ============================================================================
-- 14. COST ESTIMATES TABLE
-- ============================================================================
INSERT INTO cost_estimates (id, client_id, base_cost, additional_forms_cost, complexity_multiplier, estimated_total, status, created_at, updated_at)
VALUES
    ('ce00001-0001-0001-0001-000000000001', '11111111-1111-1111-1111-111111111111', 300.00, 100.00, 1.2, 480.00, 'pending', NOW(), NOW()),
    ('ce00002-0002-0002-0002-000000000002', '22222222-2222-2222-2222-222222222222', 350.00, 150.00, 1.5, 750.00, 'approved', NOW(), NOW()),
    ('ce00003-0003-0003-0003-000000000003', '33333333-3333-3333-3333-333333333333', 300.00, 200.00, 1.2, 600.00, 'approved', NOW(), NOW()),
    ('ce00004-0004-0004-0004-000000000004', '44444444-4444-4444-4444-444444444444', 300.00, 150.00, 1.2, 540.00, 'approved', NOW(), NOW()),
    ('ce00005-0005-0005-0005-000000000005', '55555555-5555-5555-5555-555555555555', 400.00, 250.00, 1.2, 780.00, 'approved', NOW(), NOW());

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
\echo '============================================================'
\echo 'Demo Data Insertion Summary'
\echo '============================================================'

SELECT 'Users' AS table_name, COUNT(*) AS records FROM users 
WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid)
UNION ALL
SELECT 'Admin Users', COUNT(*) FROM admin_users 
WHERE id IN ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid)
UNION ALL
SELECT 'Clients', COUNT(*) FROM clients 
WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid)
UNION ALL
SELECT 'Files', COUNT(*) FROM files WHERE filename LIKE '%2024%' OR filename LIKE '%johndoe%' OR filename LIKE '%janesmith%'
UNION ALL
SELECT 'Documents', COUNT(*) FROM documents WHERE name LIKE 'T4%' OR name LIKE 'T5%' OR name LIKE 'Medical%' OR name LIKE 'Donation%' OR name LIKE 'Foreign%'
UNION ALL
SELECT 'Payments', COUNT(*) FROM payments WHERE amount IN (250.00, 600.00, 550.00, 800.00, 150.00)
UNION ALL
SELECT 'T1 Questions', COUNT(*) FROM t1_questions WHERE code LIKE 'Q00%'
UNION ALL
SELECT 'T1 Answers', COUNT(*) FROM t1_answers WHERE CAST(id AS TEXT) LIKE 'a0000%'
UNION ALL
SELECT 'T1 Personal Forms', COUNT(*) FROM t1_personal_forms WHERE id LIKE 'pf000%'
UNION ALL
SELECT 'Notes', COUNT(*) FROM notes WHERE CAST(id AS TEXT) LIKE 'n0000%'
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM audit_logs WHERE CAST(id AS TEXT) LIKE 'al000%'
UNION ALL
SELECT 'Cost Estimates', COUNT(*) FROM cost_estimates WHERE CAST(id AS TEXT) LIKE 'ce000%';

\echo '============================================================'
\echo 'Demo data insertion completed successfully!'
\echo 'Password for all users: password123'
\echo '============================================================'
