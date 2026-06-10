import time
import json
import random
import uuid
from datetime import datetime
import numpy as np
import requests

API_URL = "http://127.0.0.1:5000/api/v1/transactions"

# In-memory data states
CUSTOMERS = [f"CUST{10000 + i}" for i in range(1000)]
DEVICES = [f"DEV{i:05d}" for i in range(500)]
MERCHANTS = [f"MER{i:04d}" for i in range(100)]
BENEFICIARIES = [f"ACC{random.randint(1000000000, 9999999999)}" for _ in range(500)]
COUNTRIES = ["India", "Singapore", "UAE", "United Kingdom", "United States"]

FRAUD_RING_CUSTOMERS = CUSTOMERS[:50]
HIGH_RISK_DEVICES = DEVICES[:20]

print("=" * 60)
print("LAUNCHING LIVE HTTP TRANSACTION GENERATOR")
print(f"Streaming directly to API: {API_URL} every 1.0s...")
print("=" * 60)

try:
    while True:
        customer_id = random.choice(CUSTOMERS)
        device_id = random.choice(DEVICES)
        merchant_id = random.choice(MERCHANTS)
        receiver_account = random.choice(BENEFICIARIES)
        
        inject_anomaly = (customer_id in FRAUD_RING_CUSTOMERS) or (device_id in HIGH_RISK_DEVICES) or (random.random() < 0.05)

        if inject_anomaly:
            transaction_amount = round(float(np.random.lognormal(9.8, 0.4)), 2)
            transaction_type = random.choice(["WIRE", "UPI", "TRANSFER"])
            destination_country = random.choice(["Singapore", "UAE", "United States"])
            current_country = "China" if random.random() < 0.4 else "India"
        else:
            transaction_amount = round(float(np.random.lognormal(7.0, 0.7)), 2)
            transaction_type = random.choice(["CARD", "UPI", "TRANSFER", "CHANNELS"])
            destination_country = "India"
            current_country = "India"

        behavioral_telemetry = {
            "device_fingerprint": uuid.uuid4().hex[:16],
            "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
            "operating_system": random.choice(["Android", "iOS", "Windows", "MacOS"]),
            "typing_speed_score": round(random.uniform(10.0, 35.0), 2) if inject_anomaly else round(random.uniform(65.0, 95.0), 2),
            "mouse_movement_score": round(random.uniform(5.0, 30.0), 2) if inject_anomaly else round(random.uniform(60.0, 99.0), 2),
            "session_duration_minutes": random.randint(1, 4) if inject_anomaly else random.randint(8, 30)
        }

        payload = {
            "transaction_id": f"TXN{random.randint(10000000, 99999999)}",
            "customer_id": customer_id,
            "receiver_account": receiver_account,
            "merchant_id": merchant_id,
            "transaction_timestamp": datetime.now().isoformat(),
            "transaction_type": transaction_type,
            "transaction_amount": transaction_amount,
            "currency": "INR",
            "payment_method": "ONLINE",
            "device_id": device_id,
            "ip_address": "192.168.1." + str(random.randint(2, 254)) if not inject_anomaly else "103.22.14." + str(random.randint(2, 254)),
            "origin_country": current_country,
            "destination_country": destination_country,
            "is_international": current_country != destination_country,
            "behavioral_telemetry": behavioral_telemetry
        }

        # Hit the API Server
        try:
            response = requests.post(API_URL, json=payload, timeout=2)
            if response.status_code == 200:
                print(f"[+] Sent Event: {payload['transaction_id']}")
            else:
                print(f"[-] API Server Error: Status Code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[-] Connection Error: Could not reach API server. Details: {e}")

        # Strict 1-second interval pause
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n[-] Stream engine halted successfully.")