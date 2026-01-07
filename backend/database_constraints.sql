-- ============================================================================
-- DATABASE CONSTRAINTS FOR TAX-EASE API V2
-- Purpose: Last line of defense against data corruption
-- ============================================================================

-- ============================================================================
-- FILING CONSTRAINTS
-- ============================================================================

-- Constraint: Total fee must be non-negative
ALTER TABLE filings
ADD CONSTRAINT check_total_fee_non_negative
CHECK (total_fee IS NULL OR total_fee >= 0);

-- Constraint: Filing year must be reasonable (1900-2100)
ALTER TABLE filings
ADD CONSTRAINT check_filing_year_valid
CHECK (filing_year BETWEEN 1900 AND 2100);

-- Constraint: Status must be valid enum value
ALTER TABLE filings
ADD CONSTRAINT check_filing_status_valid
CHECK (status IN (
    'documents_pending',
    'submitted',
    'payment_request_sent',
    'payment_completed',
    'in_preparation',
    'awaiting_approval',
    'filed',
    'completed',
    'cancelled'
));

-- ============================================================================
-- DOCUMENT CONSTRAINTS
-- ============================================================================

-- Constraint: File size must be positive
ALTER TABLE documents
ADD CONSTRAINT check_file_size_positive
CHECK (file_size > 0);

-- Constraint: Status must be valid enum value
ALTER TABLE documents
ADD CONSTRAINT check_document_status_valid
CHECK (status IN (
    'pending',
    'complete',
    'missing',
    'approved',
    'reupload_requested'
));

-- ============================================================================
-- PAYMENT CONSTRAINTS (IMMUTABILITY)
-- ============================================================================

-- Constraint: Payment amount must be positive
ALTER TABLE payments
ADD CONSTRAINT check_payment_amount_positive
CHECK (amount > 0);

-- Constraint: Payment method must be valid
ALTER TABLE payments
ADD CONSTRAINT check_payment_method_valid
CHECK (method IN (
    'credit_card',
    'debit_card',
    'bank_transfer',
    'check',
    'cash',
    'other'
));

-- Trigger: Prevent updates to payments (append-only)
CREATE OR REPLACE FUNCTION prevent_payment_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Payments are immutable and cannot be modified. Payment ID: %', OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_payment_update ON payments;
CREATE TRIGGER prevent_payment_update
BEFORE UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION prevent_payment_modification();

-- Trigger: Prevent deletion of payments (audit trail)
CREATE OR REPLACE FUNCTION prevent_payment_deletion()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Payments cannot be deleted. Payment ID: %. Use voiding mechanism instead.', OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_payment_delete ON payments;
CREATE TRIGGER prevent_payment_delete
BEFORE DELETE ON payments
FOR EACH ROW
EXECUTE FUNCTION prevent_payment_deletion();

-- ============================================================================
-- USER CONSTRAINTS
-- ============================================================================

-- Constraint: Email must contain @ symbol
ALTER TABLE users
ADD CONSTRAINT check_email_format
CHECK (email LIKE '%@%');

-- Constraint: Password hash must be non-empty
ALTER TABLE users
ADD CONSTRAINT check_password_hash_non_empty
CHECK (LENGTH(password_hash) > 0);

-- ============================================================================
-- ADMIN CONSTRAINTS
-- ============================================================================

-- Constraint: Admin role must be valid
ALTER TABLE admins
ADD CONSTRAINT check_admin_role_valid
CHECK (role IN ('admin', 'superadmin'));

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    performed_by_id UUID NOT NULL REFERENCES admins(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    changes JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_audit_logs_performed_by ON audit_logs(performed_by_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Trigger: Prevent modification of audit logs (immutable)
CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable. Log ID: %', OLD.id;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_audit_log_update ON audit_logs;
CREATE TRIGGER prevent_audit_log_update
BEFORE UPDATE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_log_modification();

DROP TRIGGER IF EXISTS prevent_audit_log_delete ON audit_logs;
CREATE TRIGGER prevent_audit_log_delete
BEFORE DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_log_modification();

-- ============================================================================
-- CONSTRAINT EXPLANATIONS
-- ============================================================================

/*
CORRUPTION PREVENTION MATRIX:

1. check_total_fee_non_negative
   Prevents: Negative fees that would corrupt billing calculations

2. check_filing_year_valid
   Prevents: Garbage data (year 0, year 99999) that breaks queries

3. check_filing_status_valid
   Prevents: Invalid status values that break state machine logic

4. check_file_size_positive
   Prevents: Zero or negative file sizes (corrupted uploads)

5. check_document_status_valid
   Prevents: Invalid document statuses that break workflows

6. check_payment_amount_positive
   Prevents: Zero or negative payments (fraud, data corruption)

7. check_payment_method_valid
   Prevents: Invalid payment methods that break reporting

8. prevent_payment_modification (trigger)
   Prevents: Altering payment history (financial audit trail)

9. prevent_payment_deletion (trigger)
   Prevents: Hiding payment history (fraud, compliance violation)

10. check_email_format
    Prevents: Invalid email addresses that break authentication

11. check_password_hash_non_empty
    Prevents: Empty passwords that bypass authentication

12. check_admin_role_valid
    Prevents: Invalid roles that break authorization

13. prevent_audit_log_modification (trigger)
    Prevents: Tampering with forensic evidence
*/

-- ============================================================================
-- APPLY ALL CONSTRAINTS
-- ============================================================================

-- Execute this file:
-- psql -d CA_Project -f database_constraints.sql
