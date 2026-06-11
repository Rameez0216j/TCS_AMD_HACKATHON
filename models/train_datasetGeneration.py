import os
import json
import uuid
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set deterministic seeds for pipeline reproducibility
random.seed(1337)
np.random.seed(1337)

def generate_robust_production_dataset(n_records=100000):
    print(f"🚀 Initializing high-fidelity data engine for {n_records} streaming entries...")
    
    # ----------------------------------------------------
    # 1. CORE RELATIONAL ENTITY POOLS
    # ----------------------------------------------------
    # Expanded pools to prevent artificial feature collision while maintaining tight fraud clusters
    customers = [f"CUST_{10000 + i}" for i in range(2500)]
    mule_customers = customers[:150] # Target organized fraud ring accounts
    
    devices = [f"DEV_{i:05d}" for i in range(1200)]
    tainted_devices = devices[:50] # Device pool shared by automated account takeovers
    
    merchants = [f"MER_{i:03d}" for i in range(200)]
    high_risk_merchants = merchants[:10]
    
    beneficiaries = [f"BEN_{20000 + i}" for i in range(1500)]
    flagged_beneficiaries = beneficiaries[:75]
    
    countries = ["IN", "US", "AE", "GB", "SG", "MY", "CH", "HK", "DE"]
    payment_methods = ["UPI", "CREDIT_CARD", "NET_BANKING", "WALLET"]
    transaction_types = ["TRANSFER", "PAYMENT", "WITHDRAWAL"]

    data = []
    
    # Establish a clean temporal distribution rolling backward from the current date
    base_timeline = datetime.utcnow() - timedelta(days=45)
    
    # Track sliding windows using dictionaries to accurately simulate stateful real-time metrics
    customer_last_tx = {}
    device_account_map = {}

    for i in range(n_records):
        # Linearly step forward in time (roughly 38-40 seconds per transaction stream event)
        current_time = base_timeline + timedelta(seconds=i * 39)
        
        # Default state selections
        customer = random.choice(customers)
        device = random.choice(devices)
        merchant = random.choice(merchants)
        beneficiary = random.choice(beneficiaries)
        tx_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
        
        # ----------------------------------------------------
        # 2. FRAUD PATTERN & INJECTION HEURISTICS
        # ----------------------------------------------------
        is_fraud = False
        attack_vector = "NONE"
        
        # Vector A: Organized Mule Account Network
        if customer in mule_customers:
            is_fraud = True
            attack_vector = "MULE_RING"
            
        # Vector B: Device Cloning / Account Takeover (ATO Spraying)
        elif device in tainted_devices and random.random() < 0.65:
            is_fraud = True
            attack_vector = "ATO_VELOCITY"
            # Force entity clustering to replicate multi-account device sharing
            customer = random.choice(mule_customers) 
            
        # Vector C: High-Risk Shell Merchants / Cross-Border Scams
        elif merchant in high_risk_merchants and random.random() < 0.55:
            is_fraud = True
            attack_vector = "MERCHANT_SCAM"
            
        # Vector D: High-Risk Laundering Beneficiary Drops
        elif beneficiary in flagged_beneficiaries and random.random() < 0.70:
            is_fraud = True
            attack_vector = "BENEFICIARY_DROP"

        # ----------------------------------------------------
        # 3. DYNAMIC FINANCIAL LOGNORMAL ENGINE
        # ----------------------------------------------------
        if is_fraud:
            # Force high-value spikes on financial profiles
            amount = round(float(np.random.lognormal(9.6, 0.45)), 2)
            risk_cat = "HIGH"
            fraud_prob = round(random.uniform(76.0, 99.95), 2)
            
            # Streaming decisions mimic dynamic orchestration routing
            decision = random.choice(["BLOCKED", "REVIEW_REQUIRED"])
            transaction_status = "FAILED" if decision == "BLOCKED" else random.choice(["PENDING", "FAILED", "REVERSED"])
        else:
            # Safe, normal distributed retail profile amounts
            amount = round(float(np.random.lognormal(6.4, 0.65)), 2)
            risk_cat = "LOW" if random.random() < 0.88 else "MEDIUM"
            fraud_prob = round(random.uniform(0.05, 42.5), 2)
            
            decision = "APPROVED" if risk_cat == "LOW" else "REVIEW_REQUIRED"
            transaction_status = "SUCCESS" if decision == "APPROVED" else random.choice(["PENDING", "SUCCESS"])

        # ----------------------------------------------------
        # 4. NETWORK TELEMETRY & CROSS-BORDER ANALYSIS
        # ----------------------------------------------------
        hour_of_day = current_time.hour
        
        # Inject off-hour anomalies (fraudsters often operate at night relative to source origin)
        if is_fraud:
            origin_country = random.choice(countries)
            dest_country = random.choice(countries) if random.random() < 0.45 else "IN"
            # Simulated multi-hop proxy IPs
            ip_address = f"{random.randint(45,210)}.{random.randint(20,240)}.{random.randint(10,254)}.{random.randint(1,254)}"
        else:
            origin_country = "IN"
            dest_country = "IN" if random.random() < 0.95 else random.choice(countries)
            # Local enterprise/residential subnet profiles
            ip_address = f"192.168.{random.randint(1,100)}.{random.randint(1,254)}"

        is_international = int(origin_country != dest_country)

        # ----------------------------------------------------
        # 5. STATEFUL VELOCITY FEATURE SIMULATION
        # ----------------------------------------------------
        # Simulate window statistics calculated by stateful streaming engines (e.g., Flink/Spark Streaming)
        if is_fraud:
            transaction_frequency_24h = random.randint(20, 75)
            failed_transaction_count_24h = random.randint(4, 18) if random.random() < 0.5 else 0
            session_duration_minutes = random.randint(1, 8)  # Rapid script velocity
            typing_speed_flag = int(random.random() < 0.75) # High robotic script alignment
            shared_device_mule_count = random.randint(6, 22)
        else:
            transaction_frequency_24h = random.randint(1, 6)
            failed_transaction_count_24h = random.randint(0, 1) if random.random() < 0.05 else 0
            session_duration_minutes = random.randint(8, 40) # Natural human navigation
            typing_speed_flag = 0
            shared_device_mule_count = 1

        # Calculate continuous evaluation properties
        account_age_days = random.randint(15, 1800) if not is_fraud else random.randint(2, 90) # Mule profiles lean newer
        avg_transaction_amount_7d = round(float(np.random.lognormal(6.6, 0.55)), 2)
        
        device_risk_score = round(random.uniform(72.0, 100.0), 2) if device in tainted_devices else round(random.uniform(0.0, 30.0), 2)
        
        unusual_amount_flag = int(is_fraud or (amount > avg_transaction_amount_7d * 3.5))
        unusual_location_flag = int(origin_country != "IN")

        # Complex overall ground truth target compilation for continuous index prediction
        base_score = fraud_prob if is_fraud else max(fraud_prob, device_risk_score * 0.5)
        if attack_vector in ["ATO_VELOCITY", "MULE_RING"]:
            base_score = min(100.0, base_score + random.uniform(5.0, 12.0))
        
        overall_risk_score = round(min(100.0, max(0.0, base_score)), 2)

        # Append structured payload dictionary
        data.append({
            "transaction_id": tx_id,
            "customer_id": customer,
            "beneficiary_id": beneficiary,
            "merchant_id": merchant,
            "device_id": device,
            "transaction_timestamp": current_time.isoformat() + "Z",
            "transaction_type": random.choice(transaction_types),
            "transaction_amount": amount,
            "payment_method": random.choice(payment_methods),
            "ip_address": ip_address,
            "origin_country": origin_country,
            "destination_country": dest_country,
            "transaction_status": transaction_status,
            "is_international": is_international,
            "hour_of_day": hour_of_day,
            
            # Flattened Classifier Attributes
            "account_age_days": account_age_days,
            "transaction_frequency_24h": transaction_frequency_24h,
            "failed_transaction_count_24h": failed_transaction_count_24h,
            "avg_transaction_amount_7d": avg_transaction_amount_7d,
            "session_duration_minutes": session_duration_minutes,
            "device_risk_score": device_risk_score,
            "unusual_amount_flag": unusual_amount_flag,
            "unusual_location_flag": unusual_location_flag,
            "typing_speed_flag": typing_speed_flag,
            
            # Graph Matrix Contexts
            "shared_device_mule_count": shared_device_mule_count,
            "known_fraud_ring_edge": int(is_fraud),
            "biometric_anomaly_detected": int(is_fraud),
            "automation_script_suspected": int(is_fraud and random.random() < 0.85),
            
            # Machine Learning Model Target Fields
            "attack_vector_type": attack_vector,
            "is_fraud": int(is_fraud),
            "risk_score": overall_risk_score,
            "risk_category": risk_cat
        })

    # Save to workspace disk
    df = pd.DataFrame(data)
    output_filename = "scaled_fraud_training_data_100k.csv"
    df.to_csv(output_filename, index=False)
    
    print("\n📊 --- Generated Production Dataset Summary ---")
    print(f"📁 Total Rows Generated: {len(df)} lines written to '{output_filename}'")
    print(f"🛑 Fraud Base Distribution: {df['is_fraud'].value_counts(normalize=True)[1]*100:.2f}%")
    print("\n🔥 Breakdown per Structural Attack Profiler:")
    print(df['attack_vector_type'].value_counts())

if __name__ == "__main__":
    generate_robust_production_dataset(100000)