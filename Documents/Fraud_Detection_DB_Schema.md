
# Fraud Detection System Database Schema

## PostgreSQL Tables

### customers
- customer_id (PK)
- customer_name
- email
- phone_number
- date_of_birth
- gender
- account_number
- account_type
- account_open_date
- account_age_days
- nationality
- country
- city
- address
- occupation
- annual_income
- kyc_status
- customer_risk_rating
- previous_fraud_flag
- fraud_incident_count
- created_at
- updated_at

### devices
- device_id (PK)
- device_fingerprint
- device_type
- operating_system
- browser
- first_seen
- last_seen
- associated_customers_count
- device_risk_score
- is_blacklisted
- created_at

### merchants
- merchant_id (PK)
- merchant_name
- merchant_category
- merchant_country
- merchant_risk_rating
- fraud_transaction_count
- total_transaction_count
- merchant_status
- created_at

### beneficiaries
- receiver_account (PK)
- receiver_name
- bank_name
- country
- risk_rating
- fraud_link_count
- sanction_match_flag
- created_at

### transactions
- transaction_id (PK)
- customer_id (FK)
- receiver_account (FK)
- merchant_id (FK)
- transaction_timestamp
- transaction_type
- transaction_amount
- currency
- payment_method
- transaction_status
- device_id (FK)
- ip_address
- origin_country
- destination_country
- is_international
- transaction_frequency_24h
- avg_transaction_amount_7d
- failed_transaction_count_24h
- unusual_amount_flag
- unusual_location_flag
- multiple_transactions_short_time
- high_risk_device_flag
- velocity_flag
- fraud_flag
- fraud_risk
- created_at

### customer_behavior
- behavior_id (PK)
- customer_id (FK)
- device_id (FK)
- device_fingerprint
- ip_address
- current_country
- current_city
- previous_country
- previous_city
- location_change_flag
- login_timestamp
- logout_timestamp
- session_duration_minutes
- transactions_last_1h
- transactions_last_24h
- avg_session_duration
- typing_speed_score
- mouse_movement_score
- device_risk_score
- behavior_risk_score
- account_takeover_suspected
- created_at

### sanction_list
- entity_id (PK)
- entity_name
- entity_type
- country
- sanction_source
- sanction_category
- reason_for_sanction
- risk_level
- pep_flag
- fraudster_flag
- blacklist_flag
- regulatory_reference
- effective_date
- expiry_date
- status
- created_at
- updated_at

### fraud_cases
- case_id (PK)
- fraud_type
- case_title
- modus_operandi
- fraud_pattern
- investigation_summary
- entities_involved
- risk_indicators
- resolution
- regulatory_reference
- created_at

### audit_logs
- audit_id (PK)
- transaction_id (FK)
- customer_id (FK)
- fraud_probability
- behavior_score
- graph_score
- sanction_score
- overall_risk_score
- risk_category
- decision
- screening_result
- behavior_agent_output
- graph_agent_output
- risk_agent_output
- explainability_output
- shap_top_features
- recommended_action
- linked_fraud_cases
- report_path
- investigation_status
- created_at

## Neo4j Nodes
- Customer
- Device
- Transaction
- Merchant
- Beneficiary
- SanctionEntity
- FraudCase

## Neo4j Relationships
- (Customer)-[:USES]->(Device)
- (Customer)-[:MADE]->(Transaction)
- (Transaction)-[:AT]->(Merchant)
- (Transaction)-[:TO]->(Beneficiary)
- (Customer)-[:MATCHES]->(SanctionEntity)
- (Beneficiary)-[:LINKED_TO]->(FraudCase)

## Recommended Indexes
- transactions(customer_id)
- transactions(transaction_timestamp)
- transactions(device_id)
- transactions(receiver_account)
- transactions(merchant_id)
- customer_behavior(customer_id)
- customer_behavior(device_id)
- sanction_list(entity_name)
