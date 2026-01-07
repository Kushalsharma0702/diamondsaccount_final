-- ==============================================
-- T1 PERSONAL TAX FORM DATABASE SCHEMA V2
-- ==============================================
-- Clean slate migration for T1 form processing
-- Production-ready with immutability, audit trails, and performance optimization

-- ==============================================
-- CORE T1 FORMS TABLE
-- ==============================================
CREATE TABLE t1_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- State machine
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'under_review', 'approved', 'rejected')),
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Progress tracking
    completion_percentage INTEGER NOT NULL DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    last_saved_step_id VARCHAR(50),
    
    -- Submission tracking
    submitted_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES admins(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(filing_id),
    CHECK (
        (status = 'draft' AND is_locked = FALSE) OR
        (status IN ('submitted', 'under_review', 'approved', 'rejected') AND is_locked = TRUE)
    )
);

-- Indexes for performance
CREATE INDEX idx_t1_forms_filing_id ON t1_forms(filing_id);
CREATE INDEX idx_t1_forms_user_id ON t1_forms(user_id);
CREATE INDEX idx_t1_forms_status ON t1_forms(status);
CREATE INDEX idx_t1_forms_created_at ON t1_forms(created_at DESC);

-- ==============================================
-- T1 ANSWERS TABLE (Normalized Polymorphic Storage)
-- ==============================================
CREATE TABLE t1_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    
    -- Field identification
    field_key VARCHAR(200) NOT NULL, -- e.g., "personalInfo.firstName", "selfEmployment.uberBusiness.income"
    
    -- Polymorphic value columns (only one should be populated per row)
    value_boolean BOOLEAN,
    value_text TEXT,
    value_numeric NUMERIC(20, 2),
    value_date DATE,
    value_array JSONB, -- For repeatable fields like children[], movingExpenses[]
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(t1_form_id, field_key),
    CHECK (
        (value_boolean IS NOT NULL AND value_text IS NULL AND value_numeric IS NULL AND value_date IS NULL AND value_array IS NULL) OR
        (value_boolean IS NULL AND value_text IS NOT NULL AND value_numeric IS NULL AND value_date IS NULL AND value_array IS NULL) OR
        (value_boolean IS NULL AND value_text IS NULL AND value_numeric IS NOT NULL AND value_date IS NULL AND value_array IS NULL) OR
        (value_boolean IS NULL AND value_text IS NULL AND value_numeric IS NULL AND value_date IS NOT NULL AND value_array IS NULL) OR
        (value_boolean IS NULL AND value_text IS NULL AND value_numeric IS NULL AND value_date IS NULL AND value_array IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_t1_answers_t1_form_id ON t1_answers(t1_form_id);
CREATE INDEX idx_t1_answers_field_key ON t1_answers(field_key);
CREATE INDEX idx_t1_answers_created_at ON t1_answers(created_at DESC);

-- GIN index for JSONB array searches
CREATE INDEX idx_t1_answers_value_array ON t1_answers USING GIN (value_array);

-- ==============================================
-- T1 SECTION PROGRESS TABLE (Admin Review Tracking)
-- ==============================================
CREATE TABLE t1_sections_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    
    -- Section identification
    step_id VARCHAR(50) NOT NULL, -- e.g., "personal_info", "questionnaire"
    section_id VARCHAR(100) NOT NULL, -- e.g., "individual_information", "spouse_information"
    
    -- Review status
    is_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_by UUID REFERENCES admins(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(t1_form_id, step_id, section_id)
);

-- Indexes for performance
CREATE INDEX idx_t1_sections_progress_t1_form_id ON t1_sections_progress(t1_form_id);
CREATE INDEX idx_t1_sections_progress_reviewed_by ON t1_sections_progress(reviewed_by);

-- ==============================================
-- EMAIL THREADS TABLE
-- ==============================================
CREATE TABLE email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(100) NOT NULL UNIQUE, -- Human-readable: "T1-{filing_id}-{timestamp}"
    t1_form_id UUID NOT NULL REFERENCES t1_forms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Thread metadata
    subject VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'archived')),
    
    -- Context
    context_field_key VARCHAR(200), -- Optional: which T1 field this thread relates to
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_email_threads_t1_form_id ON email_threads(t1_form_id);
CREATE INDEX idx_email_threads_user_id ON email_threads(user_id);
CREATE INDEX idx_email_threads_thread_id ON email_threads(thread_id);
CREATE INDEX idx_email_threads_last_message_at ON email_threads(last_message_at DESC);

-- ==============================================
-- EMAIL MESSAGES TABLE
-- ==============================================
CREATE TABLE email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(100) NOT NULL REFERENCES email_threads(thread_id) ON DELETE CASCADE,
    
    -- Sender information
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'admin')),
    sender_id UUID NOT NULL, -- References users.id or admins.id
    sender_name VARCHAR(255) NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    
    -- Message content
    message_type VARCHAR(20) NOT NULL DEFAULT 'message' CHECK (message_type IN ('message', 'document_request', 'status_update')),
    message_body TEXT NOT NULL,
    
    -- Metadata
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_email_messages_thread_id ON email_messages(thread_id);
CREATE INDEX idx_email_messages_sender_id ON email_messages(sender_id);
CREATE INDEX idx_email_messages_created_at ON email_messages(created_at DESC);
CREATE INDEX idx_email_messages_is_read ON email_messages(is_read);

-- ==============================================
-- EXTEND DOCUMENTS TABLE FOR T1 SUPPORT
-- ==============================================
-- Add T1-specific columns to existing documents table
ALTER TABLE documents
ADD COLUMN t1_form_id UUID REFERENCES t1_forms(id) ON DELETE CASCADE,
ADD COLUMN question_key VARCHAR(200), -- Links document to specific T1 question
ADD COLUMN is_approved BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN approved_by UUID REFERENCES admins(id),
ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN rejection_reason TEXT;

-- Indexes for T1 documents
CREATE INDEX idx_documents_t1_form_id ON documents(t1_form_id);
CREATE INDEX idx_documents_question_key ON documents(question_key);
CREATE INDEX idx_documents_is_approved ON documents(is_approved);

-- ==============================================
-- IMMUTABILITY TRIGGERS
-- ==============================================

-- Prevent modification of submitted T1 forms
CREATE OR REPLACE FUNCTION prevent_t1_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_locked = TRUE AND NEW.is_locked = TRUE THEN
        -- Allow only admin review fields to be modified
        IF OLD.status != NEW.status OR 
           OLD.reviewed_by IS DISTINCT FROM NEW.reviewed_by OR
           OLD.reviewed_at IS DISTINCT FROM NEW.reviewed_at OR
           OLD.review_notes IS DISTINCT FROM NEW.review_notes THEN
            RETURN NEW;
        END IF;
        RAISE EXCEPTION 'Cannot modify locked T1 form (id=%)', OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_t1_modification
BEFORE UPDATE ON t1_forms
FOR EACH ROW
EXECUTE FUNCTION prevent_t1_modification();

-- Prevent modification of answers after submission
CREATE OR REPLACE FUNCTION prevent_t1_answer_modification()
RETURNS TRIGGER AS $$
DECLARE
    form_locked BOOLEAN;
BEGIN
    SELECT is_locked INTO form_locked FROM t1_forms WHERE id = OLD.t1_form_id;
    IF form_locked = TRUE THEN
        RAISE EXCEPTION 'Cannot modify answers for locked T1 form (t1_form_id=%)', OLD.t1_form_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_t1_answer_modification
BEFORE UPDATE ON t1_answers
FOR EACH ROW
EXECUTE FUNCTION prevent_t1_answer_modification();

CREATE TRIGGER trigger_prevent_t1_answer_deletion
BEFORE DELETE ON t1_answers
FOR EACH ROW
EXECUTE FUNCTION prevent_t1_answer_modification();

-- Prevent modification of approved documents
CREATE OR REPLACE FUNCTION prevent_approved_document_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_approved = TRUE AND NEW.is_approved = TRUE THEN
        RAISE EXCEPTION 'Cannot modify approved document (id=%)', OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_approved_document_modification
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION prevent_approved_document_modification();

-- ==============================================
-- AUTO-UPDATE TIMESTAMP TRIGGERS
-- ==============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_t1_forms_updated_at
BEFORE UPDATE ON t1_forms
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_t1_answers_updated_at
BEFORE UPDATE ON t1_answers
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_t1_sections_progress_updated_at
BEFORE UPDATE ON t1_sections_progress
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- VALIDATION & CLEANUP
-- ==============================================

-- Verify all tables created successfully
DO $$
DECLARE
    tables_created INTEGER;
BEGIN
    SELECT COUNT(*) INTO tables_created
    FROM information_schema.tables
    WHERE table_name IN ('t1_forms', 't1_answers', 't1_sections_progress', 'email_threads', 'email_messages')
    AND table_schema = 'public';
    
    IF tables_created = 5 THEN
        RAISE NOTICE '✓ All 5 T1 tables created successfully';
    ELSE
        RAISE EXCEPTION '✗ Expected 5 tables, found %', tables_created;
    END IF;
END;
$$;

-- Migration complete
SELECT 'T1 DATABASE SCHEMA V2 MIGRATION COMPLETE' AS status;
