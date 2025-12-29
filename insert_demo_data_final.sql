-- ============================================================================
-- FINAL DEMO DATA INSERTION SCRIPT - TAXEASE DATABASE
-- All UUIDs properly cast, matches actual schema
-- Run: PGPASSWORD=Kushal07 psql -h localhost -U postgres -d taxease_db -f insert_demo_data_final.sql
-- ============================================================================

BEGIN;

-- Clean up existing demo data
DELETE FROM audit_logs WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM cost_estimates WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM notes WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM t1_answers WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM t1_personal_forms WHERE id LIKE 'pf0000%';
DELETE FROM t1_forms WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM t1_questions WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM t1_personal_info WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM payments WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM documents WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM files WHERE CAST(id AS TEXT) LIKE '00000001-0000-0000-000%-00000000000%';
DELETE FROM clients WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid);
DELETE FROM admin_users WHERE id IN ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid);
DELETE FROM users WHERE id IN ('11111111-1111-1111-1111-111111111111'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, '55555555-5555-5555-5555-555555555555'::uuid);

-- Users
INSERT INTO users (id, email, password_hash, first_name, last_name, phone, is_active, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111'::uuid, 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'John', 'Doe', '+1-555-0101', true, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222'::uuid, 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Jane', 'Smith', '+1-555-0102', true, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333'::uuid, 'michael.johnson@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Michael', 'Johnson', '+1-555-0103', true, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444'::uuid, 'sarah.williams@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Sarah', 'Williams', '+1-555-0104', true, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555'::uuid, 'david.brown@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'David', 'Brown', '+1-555-0105', true, NOW(), NOW());

-- Admin Users
INSERT INTO admin_users (id, email, password_hash, name, role, permissions, is_active, created_at, updated_at)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 'admin1@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Senior Admin', 'admin', ARRAY['view_clients', 'edit_clients'], true, NOW(), NOW()),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 'admin2@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Tax Specialist', 'admin', ARRAY['view_clients'], true, NOW(), NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 'admin3@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Document Manager', 'admin', ARRAY['view_documents'], true, NOW(), NOW()),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, 'admin4@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Payment Officer', 'admin', ARRAY['view_payments'], true, NOW(), NOW()),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid, 'admin5@taxease.ca', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVInHuBiK', 'Support Admin', 'admin', ARRAY['view_clients'], true, NOW(), NOW());

-- Clients
INSERT INTO clients (id, name, email, phone, filing_year, status, payment_status, assigned_admin_id, total_amount, paid_amount, created_at, updated_at)
VALUES
    ('11111111-1111-1111-1111-111111111111'::uuid, 'John Doe', 'john.doe@example.com', '+1-555-0101', 2025, 'documents_pending', 'pending', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, 500.00, 0.00, NOW(), NOW()),
    ('22222222-2222-2222-2222-222222222222'::uuid, 'Jane Smith', 'jane.smith@example.com', '+1-555-0102', 2025, 'in_progress', 'partial', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, 750.00, 250.00, NOW(), NOW()),
    ('33333333-3333-3333-3333-333333333333'::uuid, 'Michael Johnson', 'michael.johnson@example.com', '+1-555-0103', 2025, 'review', 'paid', 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, 600.00, 600.00, NOW(), NOW()),
    ('44444444-4444-4444-4444-444444444444'::uuid, 'Sarah Williams', 'sarah.williams@example.com', '+1-555-0104', 2025, 'completed', 'paid', 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, 550.00, 550.00, NOW(), NOW()),
    ('55555555-5555-5555-5555-555555555555'::uuid, 'David Brown', 'david.brown@example.com', '+1-555-0105', 2025, 'filed', 'paid', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid, 800.00, 800.00, NOW(), NOW());

-- Files
INSERT INTO files (id, user_id, filename, original_filename, file_type, file_size, upload_status, created_at)
VALUES
    ('00000001-0000-0000-0001-000000000001'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 't4_johndoe_2024.pdf', 'T4_2024_JohnDoe.pdf', 'application/pdf', 245760, 'completed', NOW()),
    ('00000002-0000-0000-0002-000000000002'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 't5_janesmith_2024.pdf', 'T5_2024_JaneSmith.pdf', 'application/pdf', 189440, 'completed', NOW()),
    ('00000003-0000-0000-0003-000000000003'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, 'medical_michael.pdf', 'Medical_Receipts_Michael.pdf', 'application/pdf', 512000, 'completed', NOW()),
    ('00000004-0000-0000-0004-000000000004'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, 'donation_sarah.pdf', 'Donation_Receipts_Sarah.pdf', 'application/pdf', 102400, 'completed', NOW()),
    ('00000005-0000-0000-0005-000000000005'::uuid, '55555555-5555-5555-5555-555555555555'::uuid, 'property_david.pdf', 'Property_Statement_David.pdf', 'application/pdf', 327680, 'completed', NOW());

-- Documents
INSERT INTO documents (id, client_id, name, type, status, version, uploaded_at, notes, created_at, updated_at)
VALUES
    ('00000001-0000-0000-0011-000000000001'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 'T4 Employment Income', 'T4', 'pending', 1, NOW(), 'Needs review', NOW(), NOW()),
    ('00000002-0000-0000-0012-000000000002'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 'T5 Investment Income', 'T5', 'approved', 1, NOW(), 'Approved', NOW(), NOW()),
    ('00000003-0000-0000-0013-000000000003'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, 'Medical Receipts', 'medical', 'approved', 1, NOW(), 'All receipts verified', NOW(), NOW()),
    ('00000004-0000-0000-0014-000000000004'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, 'Donation Receipts', 'donation', 'approved', 1, NOW(), 'Charitable donations verified', NOW(), NOW()),
    ('00000005-0000-0000-0015-000000000005'::uuid, '55555555-5555-5555-5555-555555555555'::uuid, 'Foreign Property Statement', 'foreign_property', 'approved', 1, NOW(), 'US property documented', NOW(), NOW());

-- Payments
INSERT INTO payments (id, client_id, amount, method, note, created_by_id, created_at)
VALUES
    ('00000001-0000-0000-0021-000000000001'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 250.00, 'credit_card', 'Partial payment for 2024 return', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::uuid, NOW()),
    ('00000002-0000-0000-0022-000000000002'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, 600.00, 'bank_transfer', 'Full payment received', 'cccccccc-cccc-cccc-cccc-cccccccccccc'::uuid, NOW()),
    ('00000003-0000-0000-0023-000000000003'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, 550.00, 'credit_card', 'Payment for tax filing', 'dddddddd-dddd-dddd-dddd-dddddddddddd'::uuid, NOW()),
    ('00000004-0000-0000-0024-000000000004'::uuid, '55555555-5555-5555-5555-555555555555'::uuid, 800.00, 'paypal', 'Complete payment', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::uuid, NOW()),
    ('00000005-0000-0000-0025-000000000005'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 150.00, 'credit_card', 'Deposit payment', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::uuid, NOW());

-- T1 Questions
INSERT INTO t1_questions (id, code, question_text, answer_type, is_repeatable, has_children, created_at)
VALUES
    ('00000001-0000-0000-0031-000000000001'::uuid, 'Q001_T4_EMPLOYMENT', 'Do you have T4 employment income?', 'yes_no', false, false, NOW()),
    ('00000002-0000-0000-0032-000000000002'::uuid, 'Q002_T5_INVESTMENT', 'Do you have T5 investment income?', 'yes_no', false, false, NOW()),
    ('00000003-0000-0000-0033-000000000003'::uuid, 'Q003_SELF_EMPLOYMENT', 'Do you have self-employment income?', 'yes_no', false, true, NOW()),
    ('00000004-0000-0000-0034-000000000004'::uuid, 'Q004_MOVING_EXPENSES', 'Did you have moving expenses for work or school?', 'yes_no', false, true, NOW()),
    ('00000005-0000-0000-0035-000000000005'::uuid, 'Q005_MEDICAL_EXPENSES', 'Do you have medical expenses to claim?', 'yes_no', false, true, NOW());

-- T1 Forms (insert before answers since answers reference these)
INSERT INTO t1_forms (id, user_id, tax_year, status, created_at, updated_at)
VALUES
    ('00000001-0000-0000-0041-000000000001'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 2024, 'in_progress', NOW(), NOW()),
    ('00000002-0000-0000-0042-000000000002'::uuid, '22222222-2222-2222-2222-222222222222'::uuid, 2024, 'in_progress', NOW(), NOW()),
    ('00000003-0000-0000-0043-000000000003'::uuid, '33333333-3333-3333-3333-333333333333'::uuid, 2024, 'completed', NOW(), NOW()),
    ('00000004-0000-0000-0044-000000000004'::uuid, '44444444-4444-4444-4444-444444444444'::uuid, 2024, 'completed', NOW(), NOW()),
    ('00000005-0000-0000-0045-000000000005'::uuid, '55555555-5555-5555-5555-555555555555'::uuid, 2024, 'filed', NOW(), NOW());

-- T1 Answers
INSERT INTO t1_answers (id, form_id, question_code, value, created_at)
VALUES
    ('00000001-0000-0000-0051-000000000001'::uuid, '00000001-0000-0000-0041-000000000001'::uuid, 'Q001_T4_EMPLOYMENT', '{"value": true}'::jsonb, NOW()),
    ('00000002-0000-0000-0052-000000000002'::uuid, '00000001-0000-0000-0041-000000000001'::uuid, 'Q002_T5_INVESTMENT', '{"value": false}'::jsonb, NOW()),
    ('00000003-0000-0000-0053-000000000003'::uuid, '00000002-0000-0000-0042-000000000002'::uuid, 'Q001_T4_EMPLOYMENT', '{"value": true}'::jsonb, NOW()),
    ('00000004-0000-0000-0054-000000000004'::uuid, '00000003-0000-0000-0043-000000000003'::uuid, 'Q003_SELF_EMPLOYMENT', '{"value": true}'::jsonb, NOW()),
    ('00000005-0000-0000-0055-000000000005'::uuid, '00000004-0000-0000-0044-000000000004'::uuid, 'Q005_MEDICAL_EXPENSES', '{"value": true}'::jsonb, NOW());

-- Skipping t1_personal_info, t1_personal_forms, notes, audit_logs, and cost_estimates
-- These tables have schema mismatches - focus on core tables for demo purposes

COMMIT;

-- Verification
SELECT 'Users' AS table_name, COUNT(*) AS records FROM users WHERE email LIKE '%example.com'
UNION ALL SELECT 'Admin Users', COUNT(*) FROM admin_users WHERE email LIKE '%admin%@taxease.ca'
UNION ALL SELECT 'Clients', COUNT(*) FROM clients WHERE email LIKE '%example.com'
UNION ALL SELECT 'Files', COUNT(*) FROM files WHERE filename LIKE '%2024%'
UNION ALL SELECT 'Documents', COUNT(*) FROM documents WHERE name != ''
UNION ALL SELECT 'Payments', COUNT(*) FROM payments WHERE amount > 0
UNION ALL SELECT 'T1 Questions', COUNT(*) FROM t1_questions WHERE code LIKE 'Q00%'
UNION ALL SELECT 'T1 Forms', COUNT(*) FROM t1_forms WHERE tax_year = 2024
UNION ALL SELECT 'T1 Answers', COUNT(*) FROM t1_answers WHERE value IS NOT NULL;

\echo '============================================================'
\echo 'Demo data insertion completed successfully!'
\echo '5 entries inserted in each table'
\echo 'Password for all users: password123'
\echo '============================================================'
