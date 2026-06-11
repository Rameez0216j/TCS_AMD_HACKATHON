CREATE TABLE
    IF NOT EXISTS customers (
        customer_id VARCHAR(50) PRIMARY KEY,
        customer_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone_number VARCHAR(50) UNIQUE NOT NULL,
        account_number VARCHAR(50) UNIQUE NOT NULL,
        date_of_birth DATE,
        gender VARCHAR(20),
        account_type VARCHAR(50),
        account_open_date DATE,
        account_age_days INTEGER,
        nationality VARCHAR(100),
        country VARCHAR(100),
        city VARCHAR(100),
        address TEXT,
        occupation VARCHAR(100),
        annual_income NUMERIC(15, 2),
        kyc_status VARCHAR(20),
        customer_risk_rating VARCHAR(20),
        previous_fraud_flag BOOLEAN DEFAULT FALSE,
        fraud_incident_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS devices (
        device_id VARCHAR(100) PRIMARY KEY,
        device_fingerprint VARCHAR(255) UNIQUE,
        device_type VARCHAR(50),
        operating_system VARCHAR(100),
        browser VARCHAR(100),
        first_seen TIMESTAMP,
        last_seen TIMESTAMP,
        device_risk_score NUMERIC(5, 2),
        is_blacklisted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS beneficiaries (
        beneficiary_id VARCHAR(50) PRIMARY KEY,
        receiver_account VARCHAR(50) UNIQUE NOT NULL,
        receiver_name VARCHAR(255),
        bank_name VARCHAR(255),
        country VARCHAR(100),
        risk_rating VARCHAR(20),
        fraud_link_count INTEGER DEFAULT 0,
        sanction_match_flag BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS merchants (
        merchant_id VARCHAR(50) PRIMARY KEY,
        merchant_name VARCHAR(255) UNIQUE NOT NULL,
        merchant_category VARCHAR(100),
        merchant_country VARCHAR(100),
        merchant_risk_rating VARCHAR(20),
        fraud_transaction_count INTEGER DEFAULT 0,
        total_transaction_count INTEGER DEFAULT 0,
        merchant_status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS customer_devices (
        customer_device_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50) NOT NULL,
        device_id VARCHAR(100) NOT NULL,
        first_seen TIMESTAMP,
        last_seen TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE,
        FOREIGN KEY (device_id) REFERENCES devices (device_id) ON DELETE CASCADE,
        CONSTRAINT unique_customer_device UNIQUE (customer_id, device_id)
    );

CREATE TABLE
    IF NOT EXISTS customer_beneficiaries (
        customer_beneficiary_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50) NOT NULL,
        beneficiary_id VARCHAR(50) NOT NULL,
        first_transaction_date TIMESTAMP,
        last_transaction_date TIMESTAMP,
        relationship_risk_score NUMERIC(5, 2),

        entity_id VARCHAR(50) PRIMARY KEY,
        entity_name VARCHAR(255),
        entity_type VARCHAR(50),
        country VARCHAR(100),
        sanction_source VARCHAR(100),
        sanction_category VARCHAR(100),
        reason_for_sanction TEXT,
        risk_level VARCHAR(20),
        pep_flag BOOLEAN,
        fraudster_flag BOOLEAN,
        blacklist_flag BOOLEAN,
        regulatory_reference TEXT,
        effective_date DATE,
        expiry_date DATE,
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        transaction_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50) NOT NULL,
        beneficiary_id VARCHAR(50),
        merchant_id VARCHAR(50),
        device_id VARCHAR(100),
        transaction_timestamp TIMESTAMP NOT NULL,
        transaction_type VARCHAR(50),
        transaction_amount NUMERIC(15, 2),
        currency CHAR(3),
        payment_method VARCHAR(50),
        transaction_status VARCHAR(20),
        ip_address VARCHAR(100),
        origin_country VARCHAR(100),
        destination_country VARCHAR(100),
        is_international BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    );
