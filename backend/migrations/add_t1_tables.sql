-- =====================================================================
-- T1 PERSONAL TAX FORM TABLES MIGRATION
-- =====================================================================
-- This migration adds support for T1 Personal Tax Form data collection,
-- validation, submission, and admin review workflows.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. T1 FORMS TABLE
-- ---------------------------------------------------------------------
-- Stores one row per T1 filing with state machine and locking mechanism
CREATE TABLE IF NOT EXISTS t1_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    form_version VARCHAR(10) NOT NULL DEFAULT '2024',  -- CRA year-over-year changes
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted')),
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    locked_at TIMESTAMPTZ NULL,
    unlocked_by UUID NULL REFERENCES admins(id),
    unlocked_at TIMESTAMPTZ NULL,
    unlock_reason TEXT NULL,
    completion_percentage INTEGER NOT NULL DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    submitted_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(filing_id)
);

CREATE INDEX idx_t1_forms_filing_id ON t1_forms(filing_id);
CREATE INDEX idx_t1_forms_status ON t1_forms(status);
CREATE INDEX idx_t1_forms_locked ON t1_forms(is_locked);

-- Trigger: Prevent modification of submitted T1 forms (immutability guarantee)
CREATE OR REPLACE FUNCTION prevent_t1_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'submitted' AND OLD.is_locked = TRUE THEN
        IF NEW.status != OLD.status OR 
           (NEW.is_locked != OLD.is_locked AND NEW.is_locked != FALSE) THEN
            RAISE EXCEPTION 'Cannot modify submitted and locked T1 form (id=%). Use unlock endpoint first.', OLD.id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_t1_modification
BEFORE UPDATE ON t1_forms
FOR EACH ROW EXECUTE FUNCTION prevent_t1_modification();

-- ---------------------------------------------------------------------
-- 2. T1 ANSWERS TABLE
-- ---------------------------------------------------------------------
-- Normalized key-value storage with polymorphic values
CREATE TABLE IF NOT EXISTS t1_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    field_key VARCHAR(255) NOT NULL,  -- Matches T1Structure.json exactly (e.g., "personalInfo.firstName")
    value_boolean BOOLEAN NULL,
    value_text TEXT NULL,
    value_numeric NUMERIC(15,2) NULL,
    value_date DATE NULL,
    value_array JSONB NULL,  -- For repeatable subforms (e.g., children array)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(t1_form_id, field_key)
);

CREATE INDEX idx_t1_answers_form_id ON t1_answers(t1_form_id);
CREATE INDEX idx_t1_answers_field_key ON t1_answers(field_key);
CREATE INDEX idx_t1_answers_array_gin ON t1_answers USING gin(value_array);

-- Trigger: Prevent modification of answers after T1 submission
CREATE OR REPLACE FUNCTION prevent_t1_answer_modification()
RETURNS TRIGGER AS $$
DECLARE
    form_status VARCHAR(20);
    form_locked BOOLEAN;
BEGIN
    SELECT status, is_locked INTO form_status, form_locked
    FROM t1_forms WHERE id = NEW.t1_form_id;
    
    IF form_status = 'submitted' AND form_locked = TRUE THEN
        RAISE EXCEPTION 'Cannot modify answers for submitted and locked T1 form (id=%)', NEW.t1_form_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_t1_answer_modification
BEFORE UPDATE ON t1_answers
FOR EACH ROW EXECUTE FUNCTION prevent_t1_answer_modification();

CREATE TRIGGER trigger_prevent_t1_answer_insert_after_lock
BEFORE INSERT ON t1_answers
FOR EACH ROW EXECUTE FUNCTION prevent_t1_answer_modification();

-- ---------------------------------------------------------------------
-- 3. T1 SECTIONS PROGRESS TABLE
-- ---------------------------------------------------------------------
-- Tracks completion and review status per step/section for admin dashboard
CREATE TABLE IF NOT EXISTS t1_sections_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    step_id VARCHAR(100) NOT NULL,  -- e.g., "personal_info", "questionnaire", "movingExpenses"
    section_id VARCHAR(100) NULL,   -- e.g., "individual_information", "spouse_information"
    is_complete BOOLEAN NOT NULL DEFAULT FALSE,
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_by UUID NULL REFERENCES admins(id),
    reviewed_at TIMESTAMPTZ NULL,
    review_notes TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(t1_form_id, step_id, section_id)
);

CREATE INDEX idx_t1_sections_progress_form_id ON t1_sections_progress(t1_form_id);
CREATE INDEX idx_t1_sections_progress_reviewed ON t1_sections_progress(is_reviewed);

-- ---------------------------------------------------------------------
-- 4. EXTEND DOCUMENTS TABLE
-- ---------------------------------------------------------------------
-- Add T1-specific columns to existing documents table
DO $$ 
BEGIN
    -- Add columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='t1_form_id') THEN
        ALTER TABLE documents ADD COLUMN t1_form_id UUID NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='question_key') THEN
        ALTER TABLE documents ADD COLUMN question_key VARCHAR(255) NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='document_requirement_label') THEN
        ALTER TABLE documents ADD COLUMN document_requirement_label VARCHAR(255) NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='is_approved') THEN
        ALTER TABLE documents ADD COLUMN is_approved BOOLEAN NULL DEFAULT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='approved_by') THEN
        ALTER TABLE documents ADD COLUMN approved_by UUID NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='approved_at') THEN
        ALTER TABLE documents ADD COLUMN approved_at TIMESTAMPTZ NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='documents' AND column_name='rejection_reason') THEN
        ALTER TABLE documents ADD COLUMN rejection_reason TEXT NULL;
    END IF;
END $$;

-- Add foreign key constraints after t1_forms table exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'documents_t1_form_id_fkey') THEN
        ALTER TABLE documents ADD CONSTRAINT documents_t1_form_id_fkey 
            FOREIGN KEY (t1_form_id) REFERENCES t1_forms(id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'documents_approved_by_fkey') THEN
        ALTER TABLE documents ADD CONSTRAINT documents_approved_by_fkey 
            FOREIGN KEY (approved_by) REFERENCES admins(id);
    END IF;
END $$;

-- Create indexes if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_documents_t1_form_id') THEN
        CREATE INDEX idx_documents_t1_form_id ON documents(t1_form_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_documents_question_key') THEN
        CREATE INDEX idx_documents_question_key ON documents(question_key);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_documents_is_approved') THEN
        CREATE INDEX idx_documents_is_approved ON documents(is_approved);
    END IF;
END $$;

-- Trigger: Prevent modification of approved documents (immutability guarantee)
CREATE OR REPLACE FUNCTION prevent_approved_document_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_approved = TRUE THEN
        RAISE EXCEPTION 'Cannot modify approved document (id=%)', OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_prevent_approved_document_modification ON documents;
CREATE TRIGGER trigger_prevent_approved_document_modification
BEFORE UPDATE ON documents
FOR EACH ROW 
WHEN (OLD.is_approved = TRUE)
EXECUTE FUNCTION prevent_approved_document_modification();

-- ---------------------------------------------------------------------
-- 5. EMAIL THREADS TABLE
-- ---------------------------------------------------------------------
-- Thread-based email communication between users and admins
CREATE TABLE IF NOT EXISTS email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(100) NOT NULL UNIQUE,  -- UUID or similar
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_id UUID NULL REFERENCES admins(id),
    subject VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_email_threads_thread_id ON email_threads(thread_id);
CREATE INDEX idx_email_threads_t1_form_id ON email_threads(t1_form_id);
CREATE INDEX idx_email_threads_user_id ON email_threads(user_id);
CREATE INDEX idx_email_threads_admin_id ON email_threads(admin_id);
CREATE INDEX idx_email_threads_status ON email_threads(status);

-- ---------------------------------------------------------------------
-- 6. EMAIL MESSAGES TABLE
-- ---------------------------------------------------------------------
-- Individual messages within a thread
CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(100) NOT NULL REFERENCES email_threads(thread_id) ON DELETE CASCADE,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'admin', 'system')),
    sender_id UUID NULL,  -- user_id or admin_id depending on sender_type
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('request', 'response', 'notification', 'system')),
    message_body TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_email_messages_thread_id ON email_messages(thread_id);
CREATE INDEX idx_email_messages_sender_type ON email_messages(sender_type);
CREATE INDEX idx_email_messages_is_read ON email_messages(is_read);

-- ---------------------------------------------------------------------
-- 7. AUDIT LOG EXTENSIONS
-- ---------------------------------------------------------------------
-- Add T1-specific action types to audit_logs (if not already present)
-- Note: Assumes audit_logs table already exists from production hardening

-- Example audit log entries for T1 actions:
-- INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, created_at) VALUES
-- (1, 'T1_SUBMITTED', 't1_forms', 1, '{"filing_id": 123, "form_version": "2024"}', '192.168.1.1', NOW());

-- ---------------------------------------------------------------------
-- 8. AUTO-UPDATE TIMESTAMPS
-- ---------------------------------------------------------------------
-- Trigger to auto-update updated_at columns

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_t1_forms_updated_at
BEFORE UPDATE ON t1_forms
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_t1_answers_updated_at
BEFORE UPDATE ON t1_answers
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_t1_sections_progress_updated_at
BEFORE UPDATE ON t1_sections_progress
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_email_threads_updated_at
BEFORE UPDATE ON email_threads
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- MIGRATION COMPLETE
-- =====================================================================
-- Tables created:
--   1. t1_forms (state machine with locking)
--   2. t1_answers (normalized key-value storage)
--   3. t1_sections_progress (completion tracking)
--   4. email_threads (email threading)
--   5. email_messages (individual messages)
-- Extended tables:
--   - documents (T1 linking and approval workflow)
-- Triggers:
--   - Immutability enforcement for submitted T1 forms and approved documents
--   - Auto-update timestamps
-- =====================================================================
