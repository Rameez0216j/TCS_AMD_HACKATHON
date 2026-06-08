import datetime
import json
import os
import random
import uuid

# ==========================================
# CONFIGURATION & HACKATHON TARGET SIZES
# ==========================================
TARGET_CUSTOMERS = 2000
TARGET_DEVICES = 1500
TARGET_MERCHANTS = 100
TARGET_BENEFICIARIES = 3000
TARGET_SANCTION_ENTITIES = 300
TARGET_FRAUD_CASES = 200
TARGET_TRANSACTIONS = 25000
TARGET_BEHAVIOR_RECORDS = 15000

# Distribution lists
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

COUNTRIES = [
    "United States",
    "United Kingdom",
    "Canada",
    "Germany",
    "France",
    "India",
    "Singapore",
    "Australia",
    "Brazil",
    "UAE",
]
CURRENCIES = {
    "United States": "USD",
    "United Kingdom": "GBP",
    "Canada": "CAD",
    "Germany": "EUR",
    "France": "EUR",
    "India": "INR",
    "Singapore": "SGD",
    "Australia": "AUD",
    "Brazil": "BRL",
    "UAE": "AED",
}
FIRST_NAMES = [
    "James",
    "Mary",
    "John",
    "Patricia",
    "Robert",
    "Jennifer",
    "Michael",
    "Linda",
    "William",
    "Elizabeth",
    "David",
    "Barbara",
    "Richard",
    "Susan",
    "Joseph",
    "Jessica",
    "Thomas",
    "Sarah",
    "Charles",
    "Karen",
]
LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
]
OCCUPATIONS = [
    "Engineer",
    "Manager",
    "Analyst",
    "Doctor",
    "Teacher",
    "Consultant",
    "Entrepreneur",
    "Sales Representative",
    "Technician",
    "Student",
]


def generate_random_ip():
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def escape_csv(val):
    if val is None:
        return ""
    s = str(val)
    if "," in s or '"' in s or "\n" in s or "\r" in s:
        s = s.replace('"', '""')
        return f'"{s}"'
    return s


def write_to_csv(filename, headers, rows):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for row in rows:
            f.write(",".join(escape_csv(x) for x in row) + "\n")
    print(f" Successfully generated {filename} ({len(rows)} records)")


print("=" * 60)
print("GENERATING SYNTHETIC FRAUD DATASET FOR HACKATHON")
print("=" * 60)

# ==========================================
# 1. GENERATE SANCTION LIST & FRAUD CASES
# ==========================================
sanction_entities = []
sanction_names = []
for i in range(TARGET_SANCTION_ENTITIES):
    entity_id = f"SANC-{10000+i}"
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    sanction_names.append(name)
    e_type = random.choice(["Individual", "Entity", "Vessel", "Organization"])
    country = random.choice(COUNTRIES)
    source = random.choice(["OFAC", "EU_SANC", "UN_SC", "UK_HMT"])
    cat = random.choice(
        ["Terrorism Financing", "Narcotics Trafficking", "Cyber Crime", "Proliferation"]
    )
    risk = random.choice(["HIGH", "CRITICAL"])

    sanction_entities.append(
        [
            entity_id,
            name,
            e_type,
            country,
            source,
            cat,
            f"Involvement in illicit finance networks linked to {cat}.",
            risk,
            str(random.random() < 0.3).upper(),
            "TRUE",
            "TRUE",
            f"REG-REF-{random.randint(100,999)}",
            "2023-01-15",
            "2028-12-31",
            "ACTIVE",
            "2023-01-15 00:00:00",
            "2026-01-01 00:00:00",
        ]
    )

fraud_cases = []
fraud_patterns = [
    (
        "Card-Not-Present Fraud",
        "Stolen credential monetization via quick consumer goods checkout.",
        "High transaction velocity targeting electronics merchants within short windows.",
    ),
    (
        "Account Takeover",
        "Credential stuffing followed by instant balance liquidation.",
        "Sudden device fingerprint shift accompanied by swift changes to critical profile settings.",
    ),
    (
        "Mule Account Network",
        "Layering dirty funds across distributed micro-deposits.",
        "High volume of structured incoming cross-border peer-to-peer transfers swept instantly.",
    ),
    (
        "Synthetic Identity Theft",
        "Fabricated personas accessing lines of credit with no intent to repay.",
        "Unusually high open accounts tied to unverified or newly populated credit files.",
    ),
]

for i in range(TARGET_FRAUD_CASES):
    case_id = f"FC-{10000+i}"
    ftype, modus, pattern = random.choice(fraud_patterns)
    fraud_cases.append(
        [
            case_id,
            ftype,
            f"{ftype} Ring Alpha-{i}",
            modus,
            pattern,
            f"Completed digital forensics investigation for network cluster {i}.",
            f"Multiple domestic consumers, target nodes grouped around resource clusters.",
            "Velocity flags, High graph neighborhood commonality, Proxy IP match.",
            "Recovered portion of funds, compromised accounts blacklisted.",
            f"FINCEN-SAR-2026-{1000+i}",
            "2025-06-01 12:00:00",
        ]
    )

# ==========================================
# 2. GENERATE MERCHANTS & BENEFICIARIES
# ==========================================
merchants = []
merchant_ids = []
for i in range(TARGET_MERCHANTS):
    m_id = f"MERCH-{1000+i}"
    merchant_ids.append(m_id)
    cat = MERCHANT_CATS[i]
    country = random.choice(COUNTRIES)
    # Target 10 specific merchants as high risk elements
    is_high_risk = i < 10
    risk = "HIGH" if is_high_risk else random.choice(["LOW", "LOW", "MEDIUM"])
    status = "UNDER_REVIEW" if is_high_risk else "ACTIVE"

    merchants.append(
        [
            m_id,
            f"{cat} Global Inc {i+1}",
            cat,
            country,
            risk,
            "0",
            "0",
            status,
            "2024-01-01 00:00:00",
        ]
    )

beneficiaries = []
beneficiary_ids = []
for i in range(TARGET_BENEFICIARIES):
    b_id = f"ACC-{random.randint(1000000000, 9999999999)}"
    beneficiary_ids.append(b_id)
    # Inject 50 targeted mule accounts
    is_mule = i < 50
    risk = "HIGH" if is_mule else random.choice(["LOW", "LOW", "MEDIUM"])

    beneficiaries.append(
        [
            b_id,
            f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            f"{random.choice(['Apex', 'Vertex', 'Horizon', 'Core'])} Bank",
            random.choice(COUNTRIES),
            risk,
            "0",
            str(random.random() < 0.02).upper(),
            "2024-01-01 00:00:00",
        ]
    )

# ==========================================
# 3. GENERATE DEVICES
# ==========================================
devices = []
device_ids = []
for i in range(TARGET_DEVICES):
    d_id = f"DEV-{uuid.uuid4().hex[:12].upper()}"
    device_ids.append(d_id)
    # Inject 100 heavily compromised / high risk devices
    is_compromised = i < 100
    risk_score = (
        round(random.uniform(75.0, 99.9), 2)
        if is_compromised
        else round(random.uniform(0.0, 45.0), 2)
    )
    is_blacklisted = "TRUE" if is_compromised or risk_score > 85 else "FALSE"

    devices.append(
        [
            d_id,
            f"fp-{uuid.uuid4().hex[:16]}",
            random.choice(["Mobile", "Desktop", "Tablet"]),
            random.choice(["iOS", "Android", "Windows", "MacOS"]),
            random.choice(["Safari", "Chrome", "Firefox", "Edge"]),
            "2024-06-01 00:00:00",
            "2026-05-30 00:00:00",
            "1",
            str(risk_score),
            is_blacklisted,
            "2024-06-01 00:00:00",
        ]
    )

# ==========================================
# 4. GENERATE CUSTOMERS (WITH PATTERNS)
# ==========================================
customers = []
customer_ids = []
customer_device_map = {}

# Set up explicit shared resource groups to build graph networks
shared_devices = device_ids[:300]  # 20% of hardware assets shared
shared_ips = [generate_random_ip() for _ in range(100)]

# Initialize structural fraud clusters
fraud_rings = {ring_idx: [] for ring_idx in range(20)}

for i in range(TARGET_CUSTOMERS):
    c_id = f"CUST-{10000+i}"
    customer_ids.append(c_id)

    # Force 100 exact matches into the sanction data
    if i < 100:
        name = sanction_names[i]
        risk_rating = "HIGH"
        prev_fraud = "TRUE"
    else:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        risk_rating = random.choice(["LOW", "LOW", "MEDIUM", "HIGH"])
        prev_fraud = "TRUE" if random.random() < 0.05 else "FALSE"

    # Map customers to localized ring infrastructure
    is_ring_member = 100 <= i < 350
    if is_ring_member:
        ring_idx = (i - 100) % 20
        fraud_rings[ring_idx].append(c_id)
        c_device = shared_devices[ring_idx % len(shared_devices)]
        c_ip = shared_ips[ring_idx % len(shared_ips)]
        risk_rating = "HIGH"
    else:
        c_device = random.choice(device_ids)
        c_ip = generate_random_ip()

    customer_device_map[c_id] = {
        "device_id": c_device,
        "ip": c_ip,
        "is_ring": is_ring_member,
    }
    country = random.choice(COUNTRIES)

    customers.append(
        [
            c_id,
            name,
            name.lower().replace(" ", "") + "@example.com",
            f"+1-{random.randint(200,999)}-555-{random.randint(1000,9999)}",
            f"{random.randint(1965, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            random.choice(["Male", "Female", "Other"]),
            f"ACT-{random.randint(100000, 999999)}",
            random.choice(["Checking", "Savings"]),
            "2022-01-01",
            "1620",
            country,
            country,
            f"City-{random.randint(1,50)}",
            f"{random.randint(100,999)} Main St",
            random.choice(OCCUPATIONS),
            str(round(random.uniform(30000, 150000), 2)),
            "PASSED" if i >= 50 else "FAILED",
            risk_rating,
            prev_fraud,
            str(random.randint(1, 4)) if prev_fraud == "TRUE" else "0",
            "2022-01-01 00:00:00",
            "2026-01-01 00:00:00",
        ]
    )

# ==========================================
# 5. GENERATE TRANSACTIONS & AUDIT LOGS
# ==========================================
transactions = []
audit_logs = []

base_time = datetime.datetime(2026, 1, 1, 0, 0, 0)

# Track usage statistics to backfill counters in master entities
merchant_tx_counts = {m[0]: 0 for m in merchants}
merchant_fraud_counts = {m[0]: 0 for m in merchants}
beneficiary_tx_counts = {b[0]: 0 for b in beneficiaries}
beneficiary_fraud_counts = {b[0]: 0 for b in beneficiaries}

print(
    f" Simulating 25,000 transactions along with corresponding GenAI Multi-Agent Audit logs..."
)

for i in range(TARGET_TRANSACTIONS):
    tx_id = f"TX-{100000+i}"

    # Step out events sequentially over time
    tx_time = base_time + datetime.timedelta(minutes=i * random.uniform(1.2, 2.5))
    tx_timestamp_str = tx_time.strftime("%Y-%m-%d %H:%M:%S")

    c_id = random.choice(customer_ids)
    c_meta = customer_device_map[c_id]

    # Establish transaction routing targets
    m_id = random.choice(merchant_ids)
    b_id = random.choice(beneficiary_ids)

    # Determine fraud labels based on explicit pattern triggers
    is_fraud = False
    fraud_reason = "None"

    # Force fraud mapping criteria
    if c_meta["is_ring"]:
        is_fraud = True
        fraud_reason = "Fraud Ring Network Activity"
    elif (
        m_id in merchant_ids[:10] and random.random() < 0.6
    ):  # High risk merchant target
        is_fraud = True
        fraud_reason = "Compromised Merchant Point"
    elif b_id in beneficiary_ids[:50] and random.random() < 0.7:  # Mule extraction
        is_fraud = True
        fraud_reason = "Mule Account Liquidation"
    elif (
        c_meta["device_id"] in device_ids[:100] and random.random() < 0.5
    ):  # High risk hardware asset
        is_fraud = True
        fraud_reason = "Infected/Blacklisted Asset Usage"
    elif random.random() < 0.02:  # Ambient residual baseline fraud
        is_fraud = True
        fraud_reason = "Anomalous Behavioral Shift"

    # Enforce exact overall fraud macro split (8% fraud target)
    # If we are nearing targets or running loose, normalize programmatically
    if i > int(TARGET_TRANSACTIONS * 0.90):
        current_fraud_p = sum(1 for x in transactions if x[23] == "TRUE") / (
            len(transactions) + 1
        )
        if current_fraud_p < 0.08:
            is_fraud = True
        elif current_fraud_p > 0.085:
            is_fraud = False

    # Adjust physical transaction bounds based on flag status
    if is_fraud:
        tx_amount = round(random.uniform(1200, 4999), 2)
        v_flag = "TRUE" if random.random() < 0.6 else "FALSE"
        loc_flag = "TRUE" if random.random() < 0.5 else "FALSE"
        amt_flag = "TRUE" if tx_amount > 2500 else "FALSE"
        multi_flag = "TRUE" if random.random() < 0.7 else "FALSE"
        dev_flag = "TRUE" if c_meta["device_id"] in device_ids[:100] else "FALSE"
        fraud_flag_str = "TRUE"
        risk_str = "HIGH"
    else:
        tx_amount = round(random.uniform(10, 450), 2)
        v_flag = "FALSE"
        loc_flag = "FALSE"
        amt_flag = "FALSE"
        multi_flag = "FALSE"
        dev_flag = "FALSE"
        fraud_flag_str = "FALSE"
        risk_str = random.choice(["LOW", "LOW", "LOW", "MEDIUM"])

    # Log operational metric tracking counters
    merchant_tx_counts[m_id] += 1
    beneficiary_tx_counts[b_id] += 1
    if is_fraud:
        merchant_fraud_counts[m_id] += 1
        beneficiary_fraud_counts[b_id] += 1

    # Base record insertion
    transactions.append(
        [
            tx_id,
            c_id,
            b_id,
            m_id,
            tx_timestamp_str,
            random.choice(["P2P", "POS", "WEB"]),
            str(tx_amount),
            "USD",
            random.choice(["CREDIT_CARD", "ACH", "WIRE"]),
            "COMPLETED" if not is_fraud or random.random() > 0.4 else "DECLINED",
            c_meta["device_id"],
            c_meta["ip"],
            "United States",
            random.choice(COUNTRIES),
            str(random.random() < 0.15).upper(),
            str(random.randint(1, 4)),
            "150.00",
            "0",
            amt_flag,
            loc_flag,
            multi_flag,
            dev_flag,
            v_flag,
            fraud_flag_str,
            risk_str,
            tx_timestamp_str,
        ]
    )

    # ----------------------------------------------------
    # GENERATE DETAILED GENAI MULTI-AGENT AUDIT METRICS
    # ----------------------------------------------------
    audit_id = f"AUD-{200000+i}"

    # Calculate deterministic base probabilities matching target categories
    if is_fraud:
        f_prob = round(random.uniform(0.78, 0.99), 2)
        b_score = round(random.uniform(70.0, 95.0), 2)
        g_score = round(random.uniform(75.0, 99.0), 2)
        s_score = (
            round(random.uniform(80.0, 100.0), 2)
            if c_id in customer_ids[:100]
            else round(random.uniform(0, 30), 2)
        )

        # Enforce exact split targets for choices
        decision = random.choice(["BLOCKED", "BLOCKED", "REVIEW_REQUIRED"])
        risk_cat = "HIGH"
        invest_status = "OPEN"
        rec_action = "IMMEDIATE_LOCK_AND_SAR_FILING"
    else:
        f_prob = round(random.uniform(0.01, 0.22), 2)
        b_score = round(random.uniform(5.0, 40.0), 2)
        g_score = round(random.uniform(0.0, 35.0), 2)
        s_score = round(random.uniform(0.0, 10.0), 2)

        decision = "APPROVED"
        risk_cat = random.choice(["LOW", "LOW", "LOW", "MEDIUM"])
        if risk_cat == "MEDIUM":
            decision = "REVIEW_REQUIRED" if random.random() < 0.5 else "APPROVED"
        invest_status = "CLOSED_LEGITIMATE" if decision == "APPROVED" else "OPEN"
        rec_action = (
            "MONITOR_FLOW" if decision == "APPROVED" else "MANUAL_COMPLIANCE_REVIEW"
        )

    # Enforce static strict distributions across the dataset
    if i > int(TARGET_TRANSACTIONS * 0.92):
        current_decision_p = sum(1 for x in audit_logs if x[9] == "APPROVED") / (
            len(audit_logs) + 1
        )
        if current_decision_p < 0.88:
            decision = "APPROVED"
            risk_cat = "LOW"
        else:
            decision = random.choice(["BLOCKED", "REVIEW_REQUIRED"])
            risk_cat = "HIGH" if decision == "BLOCKED" else "MEDIUM"

    # Inject simulated RAG and SHAP evaluation values
    shap_features = {
        "velocity_flag_24h": (
            round(random.uniform(0.3, 0.6), 3)
            if v_flag == "TRUE"
            else round(random.uniform(0.0, 0.05), 3)
        ),
        "device_risk_weight": (
            round(random.uniform(0.4, 0.8), 3)
            if dev_flag == "TRUE"
            else round(random.uniform(0.0, 0.1), 3)
        ),
        "graph_degree_centrality": (
            round(random.uniform(0.5, 0.9), 3)
            if c_meta["is_ring"]
            else round(random.uniform(0.0, 0.12), 3)
        ),
        "amount_deviation": (
            round(random.uniform(0.2, 0.5), 3)
            if amt_flag == "TRUE"
            else round(random.uniform(0.0, 0.08), 3)
        ),
    }
    # Sort features to keep the top driver relevant
    sorted_features = sorted(shap_features.items(), key=lambda x: x[1], reverse=True)
    shap_top_str = json.dumps(dict(sorted_features))

    # Compile text structures for the Multi-Agent Framework
    scr_res = f"Sanction Screening completed. Match confidence: {'100%' if c_id in customer_ids[:100] else '0%'}. Checked databases: OFAC, EU_SANC."

    beh_agent = f"Behavioral Analytics Agent: Typing latency score is {round(100-b_score, 1)}. Mouse trajectory variance indicates {'BOT_AUTOMATION' if is_fraud and random.random() > 0.5 else 'HUMAN_INPUT'}. Session length atypical for user habits."

    graph_agent = f"Graph Topology Agent: Node evaluation flagged via Cypher path verification. Target customer {c_id} {'shares critical device ' + c_meta['device_id'] + ' with multiple distinct identities' if c_meta['is_ring'] else 'exhibits normal standard isolated ego-network context'}."

    risk_agent = f"Risk Engine Orchestrator: Computed aggregated risk matrix yields score of {round((f_prob*100), 2)}%. Model recommendation points directly to: {decision}."

    exp_out = f"Explainability Summary: The transaction was routed to {decision} primarily driven by {sorted_features[0][0]} value of {sorted_features[0][1]}. Secondary triggers include localization consistency metrics."

    linked_case = (
        f"FC-{10000 + random.randint(0, TARGET_FRAUD_CASES-1)}" if is_fraud else ""
    )

    audit_logs.append(
        [
            audit_id,
            tx_id,
            c_id,
            str(f_prob),
            str(b_score),
            str(g_score),
            str(s_score),
            str(round(f_prob * 10, 2)),
            risk_cat,
            decision,
            scr_res,
            beh_agent,
            graph_agent,
            risk_agent,
            exp_out,
            shap_top_str,
            rec_action,
            linked_case,
            f"/reports/pdf/{tx_id}_summary.pdf",
            invest_status,
            tx_timestamp_str,
        ]
    )

# ==========================================
# 6. GENERATE CUSTOMER BEHAVIOR RECORDS
# ==========================================
behavior_records = []
print(f" Simulating 15,000 deep customer behavioral clickstream logs...")

for i in range(TARGET_BEHAVIOR_RECORDS):
    b_id = f"BEH-{300000+i}"
    c_id = random.choice(customer_ids)
    c_meta = customer_device_map[c_id]

    is_ato = i < 200  # Inject exactly 200 explicit Account Takeover signatures

    if is_ato:
        ip = generate_random_ip()  # Sudden location change
        country_curr = "China"
        country_prev = "United States"
        loc_flag = "TRUE"
        b_risk = round(random.uniform(80.0, 99.5), 2)
        d_risk = round(random.uniform(70.0, 95.0), 2)
        ato_suspected = "TRUE"
        t_speed = round(random.uniform(10.0, 30.0), 2)  # Robotic or erratic inputs
    else:
        ip = c_meta["ip"]
        country_curr = "United States"
        country_prev = "United States"
        loc_flag = "FALSE"
        b_risk = round(random.uniform(0.0, 35.0), 2)
        d_risk = round(random.uniform(0.0, 40.0), 2)
        ato_suspected = "FALSE"
        t_speed = round(random.uniform(60.0, 85.0), 2)

    log_time = base_time + datetime.timedelta(minutes=i * random.uniform(2.0, 4.0))

    behavior_records.append(
        [
            b_id,
            c_id,
            c_meta["device_id"],
            f"fp-{uuid.uuid4().hex[:16]}",
            ip,
            country_curr,
            "Metropolis",
            country_prev,
            "Suburban",
            loc_flag,
            log_time.strftime("%Y-%m-%d %H:%M:%S"),
            (log_time + datetime.timedelta(minutes=12)).strftime("%Y-%m-%d %H:%M:%S"),
            "12",
            "1",
            "3",
            "14.5",
            str(t_speed),
            "75.2",
            str(d_risk),
            str(b_risk),
            ato_suspected,
            log_time.strftime("%Y-%m-%d %H:%M:%S"),
        ]
    )

# ==========================================
# 7. BACKFILL MASTER TABLES WITH AGGREGATIONS
# ==========================================
for row in merchants:
    m_id = row[0]
    row[5] = str(merchant_fraud_counts[m_id])
    row[6] = str(merchant_tx_counts[m_id])

for row in beneficiaries:
    b_id = row[0]
    row[5] = str(beneficiary_fraud_counts[b_id])

# ==========================================
# 8. WRITE ALL FILES TO DISK
# ==========================================
print("\n" + "=" * 60)
print("WRITING PROCESSED CSV DATA TO DISK")
print("=" * 60)

write_to_csv(
    "customers.csv",
    [
        "customer_id",
        "customer_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "account_number",
        "account_type",
        "account_open_date",
        "account_age_days",
        "nationality",
        "country",
        "city",
        "address",
        "occupation",
        "annual_income",
        "kyc_status",
        "customer_risk_rating",
        "previous_fraud_flag",
        "fraud_incident_count",
        "created_at",
        "updated_at",
    ],
    customers,
)

write_to_csv(
    "devices.csv",
    [
        "device_id",
        "device_fingerprint",
        "device_type",
        "operating_system",
        "browser",
        "first_seen",
        "last_seen",
        "associated_customers_count",
        "device_risk_score",
        "is_blacklisted",
        "created_at",
    ],
    devices,
)

write_to_csv(
    "merchants.csv",
    [
        "merchant_id",
        "merchant_name",
        "merchant_category",
        "merchant_country",
        "merchant_risk_rating",
        "fraud_transaction_count",
        "total_transaction_count",
        "merchant_status",
        "created_at",
    ],
    merchants,
)

write_to_csv(
    "beneficiaries.csv",
    [
        "receiver_account",
        "receiver_name",
        "bank_name",
        "country",
        "risk_rating",
        "fraud_link_count",
        "sanction_match_flag",
        "created_at",
    ],
    beneficiaries,
)

write_to_csv(
    "transactions.csv",
    [
        "transaction_id",
        "customer_id",
        "receiver_account",
        "merchant_id",
        "transaction_timestamp",
        "transaction_type",
        "transaction_amount",
        "currency",
        "payment_method",
        "transaction_status",
        "device_id",
        "ip_address",
        "origin_country",
        "destination_country",
        "is_international",
        "transaction_frequency_24h",
        "avg_transaction_amount_7d",
        "failed_transaction_count_24h",
        "unusual_amount_flag",
        "unusual_location_flag",
        "multiple_transactions_short_time",
        "high_risk_device_flag",
        "velocity_flag",
        "fraud_flag",
        "fraud_risk",
        "created_at",
    ],
    transactions,
)

write_to_csv(
    "customer_behavior.csv",
    [
        "behavior_id",
        "customer_id",
        "device_id",
        "device_fingerprint",
        "ip_address",
        "current_country",
        "current_city",
        "previous_country",
        "previous_city",
        "location_change_flag",
        "login_timestamp",
        "logout_timestamp",
        "session_duration_minutes",
        "transactions_last_1h",
        "transactions_last_24h",
        "avg_session_duration",
        "typing_speed_score",
        "mouse_movement_score",
        "device_risk_score",
        "behavior_risk_score",
        "account_takeover_suspected",
        "created_at",
    ],
    behavior_records,
)

write_to_csv(
    "sanction_list.csv",
    [
        "entity_id",
        "entity_name",
        "entity_type",
        "country",
        "sanction_source",
        "sanction_category",
        "reason_for_sanction",
        "risk_level",
        "pep_flag",
        "fraudster_flag",
        "blacklist_flag",
        "regulatory_reference",
        "effective_date",
        "expiry_date",
        "status",
        "created_at",
        "updated_at",
    ],
    sanction_entities,
)

write_to_csv(
    "fraud_cases.csv",
    [
        "case_id",
        "fraud_type",
        "case_title",
        "modus_operandi",
        "fraud_pattern",
        "investigation_summary",
        "entities_involved",
        "risk_indicators",
        "resolution",
        "regulatory_reference",
        "created_at",
    ],
    fraud_cases,
)

write_to_csv(
    "audit_logs.csv",
    [
        "audit_id",
        "transaction_id",
        "customer_id",
        "fraud_probability",
        "behavior_score",
        "graph_score",
        "sanction_score",
        "overall_risk_score",
        "risk_category",
        "decision",
        "screening_result",
        "behavior_agent_output",
        "graph_agent_output",
        "risk_agent_output",
        "explainability_output",
        "shap_top_features",
        "recommended_action",
        "linked_fraud_cases",
        "report_path",
        "investigation_status",
        "created_at",
    ],
    audit_logs,
)

print("\n" + "=" * 60)
print("DATA GENERATION COMPLETE: ALL DATA STRUCTURES SYNCHRONIZED PERFECTLY")
print("=" * 60)
