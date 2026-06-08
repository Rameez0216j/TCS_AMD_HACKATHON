"""
postgres_ingest.py
High-performance bulk ingestion script for the Fraud Detection Platform dataset.
Guarantees referential integrity by loading data in a strict topological order.
"""

import os
import psycopg2

# ==========================================
# 1. DATABASE CONNECTION CONFIGURATION
# ==========================================
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bankdb"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # Update with your actual database password

# ==========================================
# 2. SCHEMA DEFINITION (PostgreSQL DDL)
# ==========================================
DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS customers (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS devices (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS merchants (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS beneficiaries (
        receiver_account VARCHAR(50) PRIMARY KEY,
        receiver_name VARCHAR(255),
        bank_name VARCHAR(255),
        country VARCHAR(100),
        risk_rating VARCHAR(20),
        fraud_link_count INTEGER DEFAULT 0,
        sanction_match_flag BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS sanction_list (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS fraud_cases (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS customer_behavior (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_logs (
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
    """,
]

# Performance-optimized indexes
INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_tx_customer ON transactions(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(transaction_timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_tx_device ON transactions(device_id);",
    "CREATE INDEX IF NOT EXISTS idx_tx_receiver ON transactions(receiver_account);",
    "CREATE INDEX IF NOT EXISTS idx_tx_merchant ON transactions(merchant_id);",
    "CREATE INDEX IF NOT EXISTS idx_behavior_customer ON customer_behavior(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_behavior_device ON customer_behavior(device_id);",
    "CREATE INDEX IF NOT EXISTS idx_sanction_entity ON sanction_list(entity_name);",
]

# ==========================================
# 3. TOPOLOGICAL BULK INGESTION MAPPING
# ==========================================
# Critical Order: Entities with no foreign key dependencies MUST be loaded first!
INGESTION_PIPELINE = [
    {"table": "customers", "file": "customers.csv"},
    {"table": "devices", "file": "devices.csv"},
    {"table": "merchants", "file": "merchants.csv"},
    {"table": "beneficiaries", "file": "beneficiaries.csv"},
    {"table": "sanction_list", "file": "sanction_list.csv"},
    {"table": "fraud_cases", "file": "fraud_cases.csv"},
    {"table": "transactions", "file": "transactions.csv"},
    {"table": "customer_behavior", "file": "customer_behavior.csv"},
    {"table": "audit_logs", "file": "audit_logs.csv"},
]


def main():
    print("Connecting to PostgreSQL Database...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        print(" Connected successfully.")

        # Step 1: Establish Database Architecture
        print("\nDeploying Relational Tables (DDL)...")
        for statement in DDL_STATEMENTS:
            cursor.execute(statement)
        conn.commit()
        print(" Tables verified/created successfully.")

        # Step 2: Stream Data cleanly into PostgreSQL using COPY
        print("\nBeginning Pipeline Bulk Ingestion...")
        for pipeline in INGESTION_PIPELINE:
            table_name = pipeline["table"]
            csv_file = pipeline["file"]

            if not os.path.exists(csv_file):
                print(
                    f" ERROR: Missing data source file: {csv_file}. Skipping execution."
                )
                continue

            print(
                f" -> Streaming {csv_file} natively into target table '{table_name}'..."
            )

            # Using copy_expert bypasses standard row insertion bottlenecks for extreme speeds
            with open(csv_file, "r", encoding="utf-8") as f:
                # Read header row to inform Postgres exactly which columns are incoming
                header = f.readline().strip()
                f.seek(0)  # Reset stream pointer back to beginning

                copy_query = f"""
                    COPY {table_name} ({header}) 
                    FROM STDIN 
                    WITH (FORMAT CSV, HEADER TRUE, QUOTE '"', ESCAPE '"');
                """
                cursor.copy_expert(copy_query, f)
            conn.commit()

        # Step 3: Optimize with Analytics Structural Indexes
        print("\nGenerating Query Performance Indexes...")
        for index_stmt in INDEX_STATEMENTS:
            cursor.execute(index_stmt)
        conn.commit()

        print("\n" + "=" * 60)
        print("INGESTION COMPLETE: PLATFORM DATABASE IS LIVE AND READY FOR PRODUCTION")
        print("=" * 60)

    except Exception as e:
        print(f"\nCRITICAL PIPELINE FAILURE: {str(e)}")
        if "conn" in locals() and conn:
            conn.rollback()
    finally:
        if "cursor" in locals() and cursor:
            cursor.close()
        if "conn" in locals() and conn:
            conn.close()


if __name__ == "__main__":
    main()
