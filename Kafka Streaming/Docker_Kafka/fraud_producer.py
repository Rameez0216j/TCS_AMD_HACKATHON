import time
import json
import random
import uuid
from datetime import datetime
import numpy as np
from confluent_kafka import Producer

# Kafka Setup Configuration
config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'fraud-data-engine'
}
producer = Producer(config)
TOPIC_NAME = 'fraud-transactions'

def delivery_report(err, msg):
    if err is not None:
        print(f"[-] Message delivery failed: {err}")
    else:
        print(f"[+] Broadcasted Event -> Partition [{msg.partition()}] at offset {msg.offset()}")

# Pre-populating entity entities to simulate structural fraud rings
CUSTOMERS = [f"CUST_{10000 + i}" for i in range(500)]
DEVICES = [f"DEV_{i:05d}" for i in range(100)]
HIGH_RISK_DEVICES = DEVICES[:10]  # First 10 hardware assets are tainted
FRAUD_RING_CUSTOMERS = CUSTOMERS[:40]  # First 40 identities are mule accounts
MERCHANTS = [f"MER_{i:03d}" for i in range(30)]
HIGH_RISK_MERCHANTS = MERCHANTS[:3]

print("[*] Initialized Relational Data State Models. Pumping live events to Kafka...")

try:
    while True:
        # 1. Relational Entity Mapping Selection
        customer = random.choice(CUSTOMERS)
        device = random.choice(DEVICES)
        merchant = random.choice(MERCHANTS)
        tx_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
        
        # 2. Injected Heuristic Fraud Logic Pipeline
        is_fraud = False
        if customer in FRAUD_RING_CUSTOMERS:
            is_fraud = True
        elif device in HIGH_RISK_DEVICES and random.random() < 0.6:
            is_fraud = True
        elif merchant in HIGH_RISK_MERCHANTS and random.random() < 0.5:
            is_fraud = True
        
        # 3. Dynamic Lognormal Financial Pricing Engine
        if is_fraud:
            amount = round(float(np.random.lognormal(9.2, 0.4)), 2)
            risk_cat = "HIGH"
            fraud_prob = round(random.uniform(76.0, 99.8), 2)
            decision = random.choice(["BLOCKED", "REVIEW_REQUIRED"])
        else:
            amount = round(float(np.random.lognormal(6.8, 0.7)), 2)
            risk_cat = "LOW" if random.random() < 0.88 else "MEDIUM"
            fraud_prob = round(random.uniform(0.5, 42.0), 2)
            decision = "APPROVED" if risk_cat == "LOW" else "REVIEW_REQUIRED"

        # 4. Synthesizing Real-Time Behavioral Data Payload
        event_payload = {
            "transaction_id": tx_id,
            "customer_id": customer,
            "device_id": device,
            "merchant_id": merchant,
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "currency": "INR",
            "risk_profile": {
                "fraud_flag": is_fraud,
                "fraud_probability_pct": fraud_prob,
                "risk_category": risk_cat,
                "orchestrator_decision": decision
            },
            "telemetry": {
                "velocity_24h_count": random.randint(15, 50) if is_fraud else random.randint(1, 6),
                "device_compromised": device in HIGH_RISK_DEVICES,
                "location_anomaly": is_fraud and random.random() < 0.7
            },
            "agent_insights": {
                "graph_agent_output": f"Graph Cluster Node Match: Found edge connection to shared asset pool via {device}." if is_fraud else "Isolated single pathway node.",
                "behavioral_agent_output": "High frequency automation keystroke script detected." if is_fraud else "Normal biometric pattern match."
            }
        }

        # 5. Emitting serialized event packet to Kafka broker
        producer.produce(
            topic=TOPIC_NAME,
            key=customer,
            value=json.dumps(event_payload).encode('utf-8'),
            callback=delivery_report
        )
        
        # Flush the buffer memory out to the stream network
        producer.poll(0)
        
        # Interval control hook
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n[*] Gracefully stopping the stream producer engine.")
finally:
    producer.flush()