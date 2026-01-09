-- Migration: Add company_id to users table
-- Date: January 9, 2026
-- Multi-Tenant Company System

-- Check if company_id column already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='company_id'
    ) THEN
        -- Add company_id column to users table
        ALTER TABLE users ADD COLUMN company_id INTEGER DEFAULT 1;
        
        -- Add foreign key constraint
        ALTER TABLE users ADD CONSTRAINT fk_users_company 
            FOREIGN KEY (company_id) REFERENCES companies(id);
        
        RAISE NOTICE 'Column company_id added to users table';
    ELSE
        RAISE NOTICE 'Column company_id already exists';
    END IF;
END $$;

-- Verify the change
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'company_id';
