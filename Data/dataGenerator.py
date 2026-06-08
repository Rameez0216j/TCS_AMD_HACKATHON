"""
generate_fraud_data_hybrid.py
High-Fidelity, Relationally Valid Fraud Dataset Generator.
Tailored for PostgreSQL DDL, Neo4j Graph Queries, and LangGraph Agent Platforms.
"""

import datetime
import json
import os
import random
import uuid
import numpy as np
import pandas as pd

try:
    from faker import Faker
except ImportError:
    raise SystemExit(
        "Dependencies missing! Please execute: pip install pandas numpy faker"
    )

fake = Faker()

# Enforce explicit seed targets for reproducibility
random.seed(42)
np.random.seed(42)

# ==========================================
# CONFIGURATION (RECOMMENDED HACKATHON SIZE)
# ==========================================
TARGET_CUSTOMERS = 2000
TARGET_DEVICES = 1500
TARGET_MERCHANTS = 100
TARGET_BENEFICIARIES = 3000
TARGET_SANCTION_ENTITIES = 300
TARGET_FRAUD_CASES = 200
TARGET_TRANSACTIONS = 25000
TARGET_BEHAVIOR_RECORDS = 15000

MERCHANT_CATS = (
    ["Retail"] * 20
    + ["Electronics"] * 15
    + ["Travel"] * 10
    + ["Food & Dining"] * 15
    + ["E-Commerce"] * 15
    + ["Gaming"] * 10
    + ["Financial Services"] * 10
    + ["Digital Services"] * 5
)
COUNTRIES = ["India", "Singapore", "UAE", "United Kingdom", "United States"]

print("=" * 60)
print("LAUNCHING INTEGRATED SYNTHETIC FRAUD DATA GENERATION ENGINE")
print("=" * 60)

now = datetime.datetime(2026, 6, 8, 12, 0, 0)

# ==========================================
# 1. SANCTION ENTITIES & FRAUD CASES
# ==========================================
sanctions = []
sanction_names = []
for i in range(TARGET_SANCTION_ENTITIES):
    name = fake.name()
    sanction_names.append(name)
    sanctions.append(
        {
            "entity_id": f"SAN{i:05d}",
            "entity_name": name,
            "entity_type": random.choice(["PERSON", "COMPANY"]),
            "country": random.choice(COUNTRIES),
            "sanction_source": "OFAC",
            "sanction_category": random.choice(
                ["Terrorism Financing", "Narcotics Trafficking", "Cyber Crime"]
            ),
            "reason_for_sanction": "Atypical capital aggregation networks matched to high risk jurisdictions.",
            "risk_level": "HIGH",
            "pep_flag": random.random() < 0.1,
            "fraudster_flag": True,
            "blacklist_flag": True,
            "regulatory_reference": f"REG-REF-{100+i}",
            "effective_date": (now - datetime.timedelta(days=730)).date(),
            "expiry_date": (now + datetime.timedelta(days=730)).date(),
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        }
    )
sanctions_df = pd.DataFrame(sanctions)

fraud_cases = []
fraud_patterns = [
    (
        "Mule Account Network",
        "Layering dirty funds across structured micro-deposits.",
        "High volume of incoming peer-to-peer transfers swept instantly.",
    ),
    (
        "Account Takeover (ATO)",
        "Credential stuffing followed by instant balance liquidation.",
        "Sudden device fingerprint shift accompanied by swift profile modifications.",
    ),
    (
        "Card-Not-Present (CNP)",
        "Stolen credential monetization via quick consumer checkouts.",
        "High velocity transaction targeting consumer electronics merchants.",
    ),
]
for i in range(TARGET_FRAUD_CASES):
    ftype, modus, pattern = random.choice(fraud_patterns)
    fraud_cases.append(
        {
            "case_id": f"CASE{i:05d}",
            "fraud_type": ftype,
            "case_title": f"{ftype} Investigation Ring #{i}",
            "modus_operandi": modus,
            "fraud_pattern": pattern,
            "investigation_summary": f"Completed forensic deep-dive analysis on clustered anomalies for node group {i}.",
            "entities_involved": "Distributed consumer accounts interacting with compromised endpoint assets.",
            "risk_indicators": "Velocity limit threshold breach, device pool correlation, proxy hopping.",
            "resolution": "Accounts isolated, associated assets blacklisted globally.",
            "regulatory_reference": f"FINCEN-SAR-2026-{1000+i}",
            "created_at": now,
        }
    )
fraud_cases_df = pd.DataFrame(fraud_cases)

# ==========================================
# 2. MERCHANTS & BENEFICIARIES
# ==========================================
merchants = []
for i in range(TARGET_MERCHANTS):
    merchants.append(
        {
            "merchant_id": f"MER{i:04d}",
            "merchant_name": fake.company(),
            "merchant_category": MERCHANT_CATS[i],
            "merchant_country": random.choice(COUNTRIES),
            "merchant_risk_rating": (
                "HIGH" if i < 10 else random.choice(["LOW", "LOW", "MEDIUM"])
            ),  # Inject 10 high-risk nodes
            "fraud_transaction_count": 0,  # Dynamically accumulated later
            "total_transaction_count": 0,  # Dynamically accumulated later
            "merchant_status": "ACTIVE",
            "created_at": now,
        }
    )
merchants_df = pd.DataFrame(merchants)

beneficiaries = []
for i in range(TARGET_BENEFICIARIES):
    beneficiaries.append(
        {
            "receiver_account": f"ACC{random.randint(1000000000, 9999999999)}",
            "receiver_name": fake.name(),
            "bank_name": f"{fake.company()} Bank",
            "country": random.choice(COUNTRIES),
            "risk_rating": (
                "HIGH" if i < 50 else random.choice(["LOW", "LOW", "MEDIUM"])
            ),  # Inject 50 mule targets
            "fraud_link_count": 0,  # Dynamically accumulated later
            "sanction_match_flag": random.random() < 0.02,
            "created_at": now,
        }
    )
beneficiaries_df = pd.DataFrame(beneficiaries)

# ==========================================
# 3. DEVICES & CUSTOMERS (WITH STRUCTURED FRAUD RING MAPPINGS)
# ==========================================
devices = []
for i in range(TARGET_DEVICES):
    devices.append(
        {
            "device_id": f"DEV{i:05d}",
            "device_fingerprint": uuid.uuid4().hex,
            "device_type": random.choice(["Mobile", "Laptop", "Tablet"]),
            "operating_system": random.choice(["Android", "iOS", "Windows", "MacOS"]),
            "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
            "first_seen": now - datetime.timedelta(days=random.randint(30, 365)),
            "last_seen": now,
            "associated_customers_count": 1,
            "device_risk_score": (
                round(random.uniform(75.0, 99.9), 2)
                if i < 100
                else round(random.uniform(0.0, 40.0), 2)
            ),
            "is_blacklisted": True if i < 100 else False,
            "created_at": now,
        }
    )
devices_df = pd.DataFrame(devices)

customers = []
customer_metadata = {}
shared_device_pool = (
    devices_df["device_id"].iloc[:20].tolist()
)  # Targeted hardware assets for rings
shared_ips = [fake.ipv4() for _ in range(50)]

for i in range(TARGET_CUSTOMERS):
    cid = f"CUST{10000+i}"

    # Force compliance hits
    if i < 100:
        c_name = sanction_names[i]
        risk_rating = "HIGH"
        prev_fraud = True
    else:
        c_name = fake.name()
        risk_rating = random.choice(["LOW", "LOW", "MEDIUM", "HIGH"])
        prev_fraud = random.random() < 0.05

    # Structure 20 clean Fraud Ring network groups
    is_ring_member = 100 <= i < 300
    if is_ring_member:
        ring_idx = (i - 100) % 20
        assigned_device = shared_device_pool[ring_idx]
        assigned_ip = shared_ips[ring_idx]
        risk_rating = "HIGH"
    else:
        assigned_device = random.choice(devices_df["device_id"].tolist())
        assigned_ip = fake.ipv4()

    customer_metadata[cid] = {
        "device_id": assigned_device,
        "ip": assigned_ip,
        "is_ring": is_ring_member,
    }
    open_date = fake.date_between(start_date="-5y", end_date="-30d")

    customers.append(
        {
            "customer_id": cid,
            "customer_name": c_name,
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=75),
            "gender": random.choice(["Male", "Female", "Other"]),
            "account_number": f"ACT{10000000 + i}",
            "account_type": random.choice(["Checking", "Savings"]),
            "account_open_date": open_date,
            "account_age_days": (now.date() - open_date).days,
            "nationality": "Indian",
            "country": "India",
            "city": fake.city(),
            "address": fake.address().replace("\n", " "),
            "occupation": fake.job(),
            "annual_income": round(random.uniform(300000, 4500000), 2),
            "kyc_status": "PASSED" if i >= 30 else "PENDING",
            "customer_risk_rating": risk_rating,
            "previous_fraud_flag": prev_fraud,
            "fraud_incident_count": random.randint(1, 4) if prev_fraud else 0,
            "created_at": now,
            "updated_at": now,
        }
    )
customers_df = pd.DataFrame(customers)

# ==========================================
# 4. TRANSACTIONS & MULTI-AGENT AUDIT LOGS
# ==========================================
transactions = []
audits = []

merchant_tx_stats = {m["merchant_id"]: {"total": 0, "fraud": 0} for m in merchants}
beneficiary_tx_stats = {
    b["receiver_account"]: {"total": 0, "fraud": 0} for b in beneficiaries
}

# Distribution target counts to perfectly match hackathon spec rules
total_fraud_target = int(TARGET_TRANSACTIONS * 0.08)  # 8%
total_blocked_target = int(TARGET_TRANSACTIONS * 0.05)  # 5%
total_review_target = int(TARGET_TRANSACTIONS * 0.07)  # 7%

fraud_count = 0
blocked_count = 0
review_count = 0

print(
    f" Simulating {TARGET_TRANSACTIONS} transactions with interconnected graph entities..."
)

for i in range(TARGET_TRANSACTIONS):
    txid = f"TXN{i:08d}"
    tx_time = now - datetime.timedelta(
        days=random.randint(0, 89),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    # Relational entity lookup
    cust = customers_df.sample(1).iloc[0]
    cid = cust["customer_id"]
    meta = customer_metadata[cid]

    mer = merchants_df.sample(1).iloc[0]
    mid = mer["merchant_id"]

    ben = beneficiaries_df.sample(1).iloc[0]
    b_acc = ben["receiver_account"]

    # Fraud logic injection engine
    is_fraud = False
    if meta["is_ring"]:
        is_fraud = True
    elif mid in [m["merchant_id"] for m in merchants[:10]] and random.random() < 0.5:
        is_fraud = True
    elif (
        b_acc in [b["receiver_account"] for b in beneficiaries[:50]]
        and random.random() < 0.6
    ):
        is_fraud = True
    elif (
        meta["device_id"] in [d["device_id"] for d in devices[:100]]
        and random.random() < 0.4
    ):
        is_fraud = True

    # Balance adjustments near limits to force exact global percentage distributions
    if is_fraud and fraud_count >= total_fraud_target:
        is_fraud = False
    if not is_fraud and (total_fraud_target - fraud_count) >= (TARGET_TRANSACTIONS - i):
        is_fraud = True

    # Real-world skewed amount logic (Lognormal)
    if is_fraud:
        amount = round(
            float(np.random.lognormal(9.5, 0.5)), 2
        )  # Higher concentration of ticket values
        fraud_count += 1
        risk_cat = "HIGH"
        f_prob = round(random.uniform(0.76, 0.99), 2)
    else:
        amount = round(float(np.random.lognormal(7.2, 0.8)), 2)
        risk_cat = "LOW" if random.random() < 0.85 else "MEDIUM"
        f_prob = round(random.uniform(0.01, 0.45), 2)

    # Re-balance decision categories to hit targets exactly
    if risk_cat == "HIGH":
        if blocked_count < total_blocked_target:
            decision = "BLOCKED"
            blocked_count += 1
        else:
            decision = "REVIEW_REQUIRED"
            review_count += 1
    elif risk_cat == "MEDIUM":
        if review_count < total_review_target:
            decision = "REVIEW_REQUIRED"
            review_count += 1
        else:
            decision = "APPROVED"
    else:
        decision = "APPROVED"

    # Compile metric state tracking
    merchant_tx_stats[mid]["total"] += 1
    beneficiary_tx_stats[b_acc]["total"] += 1
    if is_fraud:
        merchant_tx_stats[mid]["fraud"] += 1
        beneficiary_tx_stats[b_acc]["fraud"] += 1

    # Base Transaction Table Structure (Strictly matching DDL format)
    transactions.append(
        {
            "transaction_id": txid,
            "customer_id": cid,
            "receiver_account": b_acc,
            "merchant_id": mid,
            "transaction_timestamp": tx_time,
            "transaction_type": random.choice(["TRANSFER", "UPI", "CARD", "WIRE"]),
            "transaction_amount": amount,
            "currency": "INR",
            "payment_method": "ONLINE",
            "transaction_status": "SUCCESS" if decision != "BLOCKED" else "DECLINED",
            "device_id": meta["device_id"],
            "ip_address": meta["ip"],
            "origin_country": "India",
            "destination_country": ben["country"],
            "is_international": ben["country"] != "India",
            "transaction_frequency_24h": (
                random.randint(1, 5) if not is_fraud else random.randint(12, 45)
            ),
            "avg_transaction_amount_7d": round(amount * random.uniform(0.8, 1.2), 2),
            "failed_transaction_count_24h": (
                random.randint(0, 1) if not is_fraud else random.randint(3, 9)
            ),
            "unusual_amount_flag": amount > 150000,
            "unusual_location_flag": random.random() < 0.03 if not is_fraud else True,
            "multiple_transactions_short_time": is_fraud,
            "high_risk_device_flag": meta["device_id"]
            in [d["device_id"] for d in devices[:100]],
            "velocity_flag": is_fraud,
            "fraud_flag": is_fraud,
            "fraud_risk": risk_cat,
            "created_at": tx_time,
        }
    )

    # GenAI Multi-Agent Content Injections (For LangGraph/RAG engines)
    shap_data = {
        "device_risk_weight": (
            round(random.uniform(0.6, 0.9), 2)
            if is_fraud
            else round(random.uniform(0.0, 0.1), 2)
        ),
        "velocity_24h_delta": (
            round(random.uniform(0.5, 0.8), 2)
            if is_fraud
            else round(random.uniform(0.0, 0.05), 2)
        ),
        "graph_connection_degree": (
            round(random.uniform(0.7, 0.95), 2)
            if meta["is_ring"]
            else round(random.uniform(0.0, 0.1), 2)
        ),
    }
    sorted_shap = dict(
        sorted(shap_data.items(), key=lambda item: item[1], reverse=True)
    )

    scr_out = f"Compliance Screening Complete. Confidence Match: {'100%' if cid in [c['customer_id'] for c in customers[:100]] else '0%'}. Targeted systems scanned: OFAC, Sanctions Master Registry."
    beh_agent = f"Behavioral Agent: Input dynamics show transaction speed variance. Interaction cadence signature matches automated bot behaviors: {is_fraud}."
    graph_agent = f"Graph Agent: Evaluated structural path patterns via Neo4j index lookup. Customer account maps cleanly into a density cluster of active identities utilizing shared asset {meta['device_id']}."
    risk_agent = f"Risk Orchestration Agent: Aggregated core behavioral features. Calculated fraud threat probability output: {round(f_prob*100, 2)}%. Recommendation protocol overrides to action: {decision}."
    exp_out = f"Explainability Summary: Transaction evaluation driven by SHAP values. Primary vector variance centered around feature key: {list(sorted_shap.keys())[0]}."

    audits.append(
        {
            "audit_id": f"AUD{i:08d}",
            "transaction_id": txid,
            "customer_id": cid,
            "fraud_probability": f_prob * 100,
            "behavior_score": (
                round(random.uniform(70, 100), 2)
                if is_fraud
                else round(random.uniform(1, 40), 2)
            ),
            "graph_score": (
                round(random.uniform(75, 100), 2)
                if meta["is_ring"]
                else round(random.uniform(1, 35), 2)
            ),
            "sanction_score": (
                100.0 if cid in [c["customer_id"] for c in customers[:100]] else 0.0
            ),
            "overall_risk_score": f_prob * 100,
            "risk_category": risk_cat,
            "decision": decision,
            "screening_result": scr_out,
            "behavior_agent_output": beh_agent,
            "graph_agent_output": graph_agent,
            "risk_agent_output": risk_agent,
            "explainability_output": exp_out,
            "shap_top_features": json.dumps(sorted_shap),
            "recommended_action": (
                "IMMEDIATE_SAR_FILING"
                if decision == "BLOCKED"
                else (
                    "MANUAL_COMPLIANCE_HOLD"
                    if decision == "REVIEW_REQUIRED"
                    else "PASS"
                )
            ),
            "linked_fraud_cases": (
                f"CASE{random.randint(0, TARGET_FRAUD_CASES-1)}" if is_fraud else ""
            ),
            "report_path": f"/reports/pdf/{txid}_forensic_summary.pdf",
            "investigation_status": "OPEN" if decision != "APPROVED" else "CLOSED",
            "created_at": tx_time,
        }
    )

transactions_df = pd.DataFrame(transactions)
audits_df = pd.DataFrame(audits)

# ==========================================
# 5. CUSTOMER BEHAVIOR JOURNEY STREAM
# ==========================================
behaviors = []
for i in range(TARGET_BEHAVIOR_RECORDS):
    cust = customers_df.sample(1).iloc[0]
    cid = cust["customer_id"]
    meta = customer_metadata[cid]
    ts = now - datetime.timedelta(
        days=random.randint(0, 45), minutes=random.randint(0, 1440)
    )
    is_ato = i < 200  # Inject 200 explicit Account Takeover profiles

    behaviors.append(
        {
            "behavior_id": f"BEH{i:06d}",
            "customer_id": cid,
            "device_id": meta["device_id"],
            "device_fingerprint": uuid.uuid4().hex[:16],
            "ip_address": fake.ipv4() if is_ato else meta["ip"],
            "current_country": "India" if not is_ato else "China",
            "current_city": fake.city(),
            "previous_country": "India",
            "previous_city": fake.city(),
            "location_change_flag": is_ato,
            "login_timestamp": ts,
            "logout_timestamp": ts + datetime.timedelta(minutes=random.randint(5, 45)),
            "session_duration_minutes": random.randint(5, 45),
            "transactions_last_1h": (
                random.randint(0, 2) if not is_ato else random.randint(5, 15)
            ),
            "transactions_last_24h": random.randint(1, 6),
            "avg_session_duration": 15.4,
            "typing_speed_score": (
                round(random.uniform(10, 35), 2)
                if is_ato
                else round(random.uniform(60, 95), 2)
            ),
            "mouse_movement_score": (
                round(random.uniform(5, 30), 2)
                if is_ato
                else round(random.uniform(55, 99), 2)
            ),
            "device_risk_score": 90.0 if is_ato else 15.0,
            "behavior_risk_score": 95.0 if is_ato else 10.0,
            "account_takeover_suspected": is_ato,
            "created_at": ts,
        }
    )
behavior_records_df = pd.DataFrame(behaviors)

# ==========================================
# 6. RECONCILE AND UPDATE AGGREGATION LOOKUPS
# ==========================================
for idx, row in merchants_df.iterrows():
    mid = row["merchant_id"]
    merchants_df.at[idx, "total_transaction_count"] = merchant_tx_stats[mid]["total"]
    merchants_df.at[idx, "fraud_transaction_count"] = merchant_tx_stats[mid]["fraud"]

for idx, row in beneficiaries_df.iterrows():
    b_acc = row["receiver_account"]
    beneficiaries_df.at[idx, "fraud_link_count"] = beneficiary_tx_stats[b_acc]["fraud"]

# ==========================================
# 7. SAVE PIPELINE ARTIFACTS
# ==========================================
print("\n" + "=" * 60)
print("EXPORTING SYNCHRONIZED ENTITY CSV MATRIX TO DISK")
print("=" * 60)

customers_df.to_csv("customers.csv", index=False)
devices_df.to_csv("devices.csv", index=False)
merchants_df.to_csv("merchants.csv", index=False)
beneficiaries_df.to_csv("beneficiaries.csv", index=False)
transactions_df.to_csv("transactions.csv", index=False)
behavior_records_df.to_csv("customer_behavior.csv", index=False)
sanctions_df.to_csv("sanction_list.csv", index=False)
fraud_cases_df.to_csv("fraud_cases.csv", index=False)
audits_df.to_csv("audit_logs.csv", index=False)

print(
    " SUCCESS: All relational records are perfectly mapped and scaled for processing."
)
