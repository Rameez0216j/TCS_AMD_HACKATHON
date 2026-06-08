# Fraud Detection Platform Database Design

## PostgreSQL System of Record

### Tables

- customers
- transactions
- customer_behavior
- sanction_list
- audit_logs
- devices
- merchants
- beneficiaries
- fraud_cases

---

# PostgreSQL DDL

## Customers

```sql
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(20),
    account_number VARCHAR(50),
    account_type VARCHAR(50),
    account_open_date DATE,
    account_age_days INTEGER,
    nationality VARCHAR(100),
    country VARCHAR(100),
    city VARCHAR(100),
    address TEXT,
    occupation VARCHAR(100),
    annual_income NUMERIC(15,2),
    kyc_status VARCHAR(50),
    customer_risk_rating VARCHAR(20),
    previous_fraud_flag BOOLEAN,
    fraud_incident_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Devices

```sql
CREATE TABLE devices (
    device_id VARCHAR(100) PRIMARY KEY,
    device_fingerprint VARCHAR(255),
    device_type VARCHAR(50),
    operating_system VARCHAR(100),
    browser VARCHAR(100),
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    associated_customers_count INTEGER,
    device_risk_score NUMERIC(5,2),
    is_blacklisted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## Merchants

```sql
CREATE TABLE merchants (
    merchant_id VARCHAR(50) PRIMARY KEY,
    merchant_name VARCHAR(255),
    merchant_category VARCHAR(100),
    merchant_country VARCHAR(100),
    merchant_risk_rating VARCHAR(20),
    fraud_transaction_count INTEGER DEFAULT 0,
    total_transaction_count INTEGER DEFAULT 0,
    merchant_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Beneficiaries

```sql
CREATE TABLE beneficiaries (
    receiver_account VARCHAR(50) PRIMARY KEY,
    receiver_name VARCHAR(255),
    bank_name VARCHAR(255),
    country VARCHAR(100),
    risk_rating VARCHAR(20),
    fraud_link_count INTEGER DEFAULT 0,
    sanction_match_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Transactions

```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    receiver_account VARCHAR(50) REFERENCES beneficiaries(receiver_account),
    merchant_id VARCHAR(50) REFERENCES merchants(merchant_id),
    transaction_timestamp TIMESTAMP,
    transaction_type VARCHAR(50),
    transaction_amount NUMERIC(15,2),
    currency VARCHAR(20),
    payment_method VARCHAR(50),
    transaction_status VARCHAR(50),
    device_id VARCHAR(100) REFERENCES devices(device_id),
    ip_address VARCHAR(100),
    origin_country VARCHAR(100),
    destination_country VARCHAR(100),
    is_international BOOLEAN,
    transaction_frequency_24h INTEGER,
    avg_transaction_amount_7d NUMERIC(15,2),
    failed_transaction_count_24h INTEGER,
    unusual_amount_flag BOOLEAN,
    unusual_location_flag BOOLEAN,
    multiple_transactions_short_time BOOLEAN,
    high_risk_device_flag BOOLEAN,
    velocity_flag BOOLEAN,
    fraud_flag BOOLEAN,
    fraud_risk VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Customer Behavior

```sql
CREATE TABLE customer_behavior (
    behavior_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    device_id VARCHAR(100) REFERENCES devices(device_id),
    device_fingerprint VARCHAR(255),
    ip_address VARCHAR(100),
    current_country VARCHAR(100),
    current_city VARCHAR(100),
    previous_country VARCHAR(100),
    previous_city VARCHAR(100),
    location_change_flag BOOLEAN,
    login_timestamp TIMESTAMP,
    logout_timestamp TIMESTAMP,
    session_duration_minutes INTEGER,
    transactions_last_1h INTEGER,
    transactions_last_24h INTEGER,
    avg_session_duration NUMERIC(10,2),
    typing_speed_score NUMERIC(10,2),
    mouse_movement_score NUMERIC(10,2),
    device_risk_score NUMERIC(5,2),
    behavior_risk_score NUMERIC(5,2),
    account_takeover_suspected BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Sanction List

```sql
CREATE TABLE sanction_list (
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
);
```

## Fraud Cases

```sql
CREATE TABLE fraud_cases (
    case_id VARCHAR(50) PRIMARY KEY,
    fraud_type VARCHAR(100),
    case_title VARCHAR(255),
    modus_operandi TEXT,
    fraud_pattern TEXT,
    investigation_summary TEXT,
    entities_involved TEXT,
    risk_indicators TEXT,
    resolution TEXT,
    regulatory_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Audit Logs

```sql
CREATE TABLE audit_logs (
    audit_id VARCHAR(50) PRIMARY KEY,
    transaction_id VARCHAR(50) REFERENCES transactions(transaction_id),
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    fraud_probability NUMERIC(5,2),
    behavior_score NUMERIC(5,2),
    graph_score NUMERIC(5,2),
    sanction_score NUMERIC(5,2),
    overall_risk_score NUMERIC(5,2),
    risk_category VARCHAR(20),
    decision VARCHAR(50),
    screening_result TEXT,
    behavior_agent_output TEXT,
    graph_agent_output TEXT,
    risk_agent_output TEXT,
    explainability_output TEXT,
    shap_top_features TEXT,
    recommended_action TEXT,
    linked_fraud_cases TEXT,
    report_path TEXT,
    investigation_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

# PostgreSQL Indexes

```sql
CREATE INDEX idx_tx_customer ON transactions(customer_id);
CREATE INDEX idx_tx_timestamp ON transactions(transaction_timestamp);
CREATE INDEX idx_tx_device ON transactions(device_id);
CREATE INDEX idx_tx_receiver ON transactions(receiver_account);
CREATE INDEX idx_tx_merchant ON transactions(merchant_id);
CREATE INDEX idx_behavior_customer ON customer_behavior(customer_id);
CREATE INDEX idx_behavior_device ON customer_behavior(device_id);
CREATE INDEX idx_sanction_entity ON sanction_list(entity_name);
```

# Neo4j Design

## Nodes

- Customer
- Device
- Transaction
- Merchant
- Beneficiary
- SanctionEntity
- FraudCase

## Constraints

```cypher
CREATE CONSTRAINT customer_id IF NOT EXISTS
FOR (c:Customer)
REQUIRE c.customer_id IS UNIQUE;

CREATE CONSTRAINT device_id IF NOT EXISTS
FOR (d:Device)
REQUIRE d.device_id IS UNIQUE;

CREATE CONSTRAINT merchant_id IF NOT EXISTS
FOR (m:Merchant)
REQUIRE m.merchant_id IS UNIQUE;

CREATE CONSTRAINT beneficiary_id IF NOT EXISTS
FOR (b:Beneficiary)
REQUIRE b.receiver_account IS UNIQUE;

CREATE CONSTRAINT transaction_id IF NOT EXISTS
FOR (t:Transaction)
REQUIRE t.transaction_id IS UNIQUE;

CREATE CONSTRAINT sanction_id IF NOT EXISTS
FOR (s:SanctionEntity)
REQUIRE s.entity_id IS UNIQUE;

CREATE CONSTRAINT fraud_case_id IF NOT EXISTS
FOR (f:FraudCase)
REQUIRE f.case_id IS UNIQUE;
```

## Relationships

```cypher
MATCH (c:Customer {customer_id:$customer_id})
MATCH (d:Device {device_id:$device_id})
MERGE (c)-[:USES]->(d);

MATCH (c:Customer {customer_id:$customer_id})
MATCH (t:Transaction {transaction_id:$transaction_id})
MERGE (c)-[:MADE]->(t);

MATCH (t:Transaction {transaction_id:$transaction_id})
MATCH (m:Merchant {merchant_id:$merchant_id})
MERGE (t)-[:AT]->(m);

MATCH (t:Transaction {transaction_id:$transaction_id})
MATCH (b:Beneficiary {receiver_account:$receiver_account})
MERGE (t)-[:TO]->(b);

MATCH (c:Customer {customer_id:$customer_id})
MATCH (s:SanctionEntity {entity_id:$entity_id})
MERGE (c)-[:MATCHES]->(s);
```

# Fraud Investigation Queries

## Shared Device Fraud

```cypher
MATCH (c:Customer)-[:USES]->(d:Device)
WITH d, COUNT(c) AS customers
WHERE customers > 5
RETURN d.device_id, customers;
```

## Mule Account Detection

```cypher
MATCH (t:Transaction)-[:TO]->(b:Beneficiary)
WITH b, COUNT(t) AS tx_count
WHERE tx_count > 20
RETURN b.receiver_account, tx_count;
```

## Fraud Ring Detection

```cypher
MATCH (c:Customer)-[:USES]->(d:Device)<-[:USES]-(other)
WHERE c <> other
RETURN c.customer_id, other.customer_id, d.device_id;
```
