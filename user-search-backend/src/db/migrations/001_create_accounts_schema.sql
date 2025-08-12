-- src/db/migrations/001_create_accounts_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM for account types
CREATE TYPE account_type_enum AS ENUM ('service_provider', 'service_consumer');

-- Base accounts table with shared fields
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    address JSONB NOT NULL,
    tags TEXT[] DEFAULT '{}',
    account_type account_type_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Service providers specific data
CREATE TABLE service_providers (
    account_id UUID PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    hourly_rate DECIMAL(10, 2),
    availability JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Service consumers specific data
CREATE TABLE service_consumers (
    account_id UUID PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    preferred_budget DECIMAL(10, 2),
    service_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_accounts_email ON accounts(email);
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_tags ON accounts USING GIN(tags);
CREATE INDEX idx_service_providers_rate ON service_providers(hourly_rate);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_providers_updated_at BEFORE UPDATE ON service_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_consumers_updated_at BEFORE UPDATE ON service_consumers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
