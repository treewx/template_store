-- Initialize Rent Check Database
-- This script is automatically run when PostgreSQL container starts

\c rentcheck;

-- Create tables for rent check application
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    rent_amount DECIMAL(10,2) NOT NULL,
    due_day INTEGER NOT NULL CHECK (due_day >= 1 AND due_day <= 31),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('weekly', 'fortnightly', 'monthly')),
    tenant_nickname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    matched BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notification_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    property_id INTEGER REFERENCES properties(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_properties_user_id ON properties(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_property_id ON transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_notification_log_user_id ON notification_log(user_id);

-- Insert demo data (optional)
INSERT INTO users (email, password_hash, email_verified) VALUES 
('demo@rentcheck.co.nz', '$2b$12$demo.hash.for.testing.purposes.only', true)
ON CONFLICT (email) DO NOTHING;

COMMIT;