-- ============================================================================
-- Create notification_device_tokens table for FCM push notifications
-- ============================================================================
-- Run this SQL directly on your AWS RDS PostgreSQL database
-- via AWS Console Query Editor, DBeaver, pgAdmin, or psql
-- ============================================================================

-- Create the device platform enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE deviceplatform AS ENUM ('android', 'ios', 'web', 'macos', 'windows', 'linux');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create the notification_device_tokens table
CREATE TABLE IF NOT EXISTS notification_device_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    token VARCHAR(500) NOT NULL,
    platform deviceplatform NOT NULL,
    device_id VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    app_version VARCHAR(50),
    locale VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_device_token_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint on token
    CONSTRAINT uq_device_token UNIQUE (token)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_device_token_user_active 
    ON notification_device_tokens(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_device_token_token 
    ON notification_device_tokens(token);

-- Verify the table was created
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'notification_device_tokens'
ORDER BY ordinal_position;

-- Display success message
DO $$
BEGIN
    RAISE NOTICE '✅ notification_device_tokens table created successfully!';
END $$;
