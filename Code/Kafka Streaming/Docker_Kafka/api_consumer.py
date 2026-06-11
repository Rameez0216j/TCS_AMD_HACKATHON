import os
import json
import sys
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv

# Load environment configuration
load_dotenv("../../../.env")

# Kafka Consumer Configuration Engine
config = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS"),
    "group.id": os.getenv("GROUP_ID"),
    "auto.offset.reset": "latest",
    "enable.auto.commit": True,
}

consumer = Consumer(config)
TOPIC_NAME = "fraud-transactions"
consumer.subscribe([TOPIC_NAME])

print("=" * 70)
print(" API SERVER CONSUMER STARTED: STREAMING REAL-TIME TRANSACTION AUDITS")
print(" Listening closely to topic: 'fraud-transactions' ...")
print("=" * 70)

# Terminal Coloring Sequences
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"      # Blocked/High Risk
COLOR_GREEN = "\033[92m"    # Safe/Approved
COLOR_YELLOW = "\033[93m"   # Warning/Review Needed
COLOR_CYAN = "\033[96m"     # Labels

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
        raw_payload = msg.value().decode("utf-8")
        data = json.loads(raw_payload)

        # --- SCHEMA ALIGNMENT FIXES ---
        # 1. Root Level Mappings
        tx_id = data["transaction_id"]
        cid = data["customer_id"]
        amount = data["transaction_amount"]  # Aligned from 'amount'

        # 2. Extract Agent Telemetry Nested Dictionary
        telemetry = data.get("agent_pipelines_telemetry", {})
        decision = telemetry.get("orchestrator_decision", "REVIEW_REQUIRED")
        prob = telemetry.get("initial_llm_probability", 0.0)
        risk_cat = telemetry.get("initial_risk_category", "MEDIUM")
        
        # 3. Extract Features Classifier & Context Objects
        features = data.get("features_for_classifier", {})
        behavioral_ctx = telemetry.get("behavioral_agent_context", {})
        graph_ctx = telemetry.get("graph_agent_context", {})

        velocity_24h = features.get("transaction_frequency_24h", 0)
        automation_suspected = behavioral_ctx.get("automation_script_suspected", False)
        fraud_flag = graph_ctx.get("known_fraud_ring_edge", False)
        mule_count = graph_ctx.get("shared_device_mule_count", 0)

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
        print(
            f" └── {COLOR_CYAN}Customer ID:{COLOR_RESET} {cid} | {COLOR_CYAN}Amount:{COLOR_RESET} ₹{amount:,.2f}"
        )
        print(
            f" └── {COLOR_CYAN}Fraud Risk Score:{COLOR_RESET} {alert_color}{prob}% ({risk_cat} RISK){COLOR_RESET}"
        )
        print(
            f" └── {COLOR_CYAN}Telemetry:{COLOR_RESET} Velocity 24h: {velocity_24h} calls | Automation Suspected: {automation_suspected}"
        )
        
        if fraud_flag:
            print(
                f" └── {COLOR_RED}Graph Guard Insight:{COLOR_RESET} Known fraud ring link identified! Shared Device Mule Count: {mule_count}"
            )
        print("-" * 60)

except KeyboardInterrupt:
    print("\n[*] Shutting down API Consumer interface safely.")
finally:
    consumer.close()