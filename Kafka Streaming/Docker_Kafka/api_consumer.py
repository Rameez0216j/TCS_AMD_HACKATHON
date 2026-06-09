import json
import sys
from confluent_kafka import Consumer, KafkaError

# Kafka Consumer Configuration Engine
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'api-live-monitor-dashboard',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True
}

consumer = Consumer(config)
TOPIC_NAME = 'fraud-transactions'
consumer.subscribe([TOPIC_NAME])

print("=" * 70)
print(" API SERVER CONSUMER STARTED: STREAMING REAL-TIME TRANSACTION AUDITS")
print(" Listening closely to topic: 'fraud-transactions' ...")
print("=" * 70)

# Terminal Coloring Sequences 
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"    # Blocked/High Risk
COLOR_GREEN = "\033[92m"  # Safe/Approved
COLOR_YELLOW = "\033[93m" # Warning/Review Needed
COLOR_CYAN = "\033[96m"   # Labels

try:
    while True:
        # Continuous stream polling (timeout 0.5s to capture loops cleanly)
        msg = consumer.poll(timeout=0.5)
        
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"[-] Kafka Error encountered: {msg.error()}")
                break

        # Decode processing bytes stream
        raw_payload = msg.value().decode('utf-8')
        data = json.loads(raw_payload)

        # Destructure items for output logging
        tx_id = data["transaction_id"]
        cid = data["customer_id"]
        amount = data["amount"]
        risk = data["risk_profile"]
        decision = risk["orchestrator_decision"]
        prob = risk["fraud_probability_pct"]

        # Dynamically assign alert styling color maps based on data context
        if decision == "BLOCKED":
            alert_color = COLOR_RED
            prefix = "[🛑 BLOCKED FRAUD]"
        elif decision == "REVIEW_REQUIRED":
            alert_color = COLOR_YELLOW
            prefix = "[⚠️ UNDER REVIEW]"
        else:
            alert_color = COLOR_GREEN
            prefix = "[✅ APPROVED]"

        # Structured Scannable Output Terminal Layout
        print(f"\n{alert_color}{prefix} Transaction: {tx_id}{COLOR_RESET}")
        print(f" └── {COLOR_CYAN}Customer ID:{COLOR_RESET} {cid} | {COLOR_CYAN}Amount:{COLOR_RESET} ₹{amount:,.2f}")
        print(f" └── {COLOR_CYAN}Fraud Risk Score:{COLOR_RESET} {alert_color}{prob}% ({risk['risk_category']} RISK){COLOR_RESET}")
        print(f" └── {COLOR_CYAN}Telemetry:{COLOR_RESET} Velocity 24h: {data['telemetry']['velocity_24h_count']} calls | Dev Compromise: {data['telemetry']['device_compromised']}")
        if risk['fraud_flag']:
            print(f" └── {COLOR_RED}Graph Guard Insight:{COLOR_RESET} {data['agent_insights']['graph_agent_output']}")
        print("-" * 60)

except KeyboardInterrupt:
    print("\n[*] Shutting down API Consumer interface down safely.")
finally:
    consumer.close()