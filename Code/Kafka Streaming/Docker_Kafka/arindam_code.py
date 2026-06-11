import os
import time
import json
import random
import uuid
from datetime import datetime

from confluent_kafka import Producer
from dotenv import load_dotenv

# Load .env
load_dotenv("../../../.env")

# Kafka Configuration
config = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS"),
    "client.id": os.getenv("CLIENT_ID"),
}

producer = Producer(config)

TOPIC_NAME = "fraud-transactions"


def delivery_report(err, msg):
    if err is not None:
        print(f"[-] Message delivery failed: {err}")
    else:
        print(
            f"[+] Event Published | Topic={msg.topic()} "
            f"Partition={msg.partition()} Offset={msg.offset()}"
        )


# These IDs must already exist in PostgreSQL master tables
CUSTOMERS = [f"CUST_{10000 + i}" for i in range(2000)]

DEVICES = [f"DEV_{i:05d}" for i in range(1500)]

MERCHANTS = [f"MER_{i:03d}" for i in range(100)]

BENEFICIARIES = [f"BEN_{20000 + i}" for i in range(3000)]

COUNTRIES = [
    "India",
    "United States",
    "United Kingdom",
    "Singapore",
    "United Arab Emirates",
    "Germany",
]

TRANSACTION_TYPES = [
    "TRANSFER",
    "PAYMENT",
    "WITHDRAWAL",
    "DEPOSIT",
]

PAYMENT_METHODS = [
    "UPI",
    "NET_BANKING",
    "DEBIT_CARD",
    "CREDIT_CARD",
    "WALLET",
]

TRANSACTION_STATUS = [
    "PENDING",
    "COMPLETED",
    "FAILED",
]

CURRENCIES = ["INR"]

print("[*] Kafka Producer Started...")
print("[*] Publishing one transaction every 60 seconds")


try:
    while True:

        customer_id = random.choice(CUSTOMERS)
        beneficiary_id = random.choice(BENEFICIARIES)
        merchant_id = random.choice(MERCHANTS)
        device_id = random.choice(DEVICES)

        origin_country = random.choice(COUNTRIES)

        is_international = random.random() < 0.15

        destination_country = (
            random.choice(COUNTRIES) if is_international else origin_country
        )

        event_payload = {
            "transaction_id": f"TXN_{uuid.uuid4().hex[:16].upper()}",
            "customer_id": customer_id,
            "beneficiary_id": beneficiary_id,
            "merchant_id": merchant_id,
            "device_id": device_id,
            "transaction_timestamp": datetime.utcnow().isoformat(),
            "transaction_type": random.choice(TRANSACTION_TYPES),
            "transaction_amount": round(
                random.uniform(100.00, 500000.00),
                2,
            ),
            "currency": "INR",
            "payment_method": random.choice(PAYMENT_METHODS),
            "transaction_status": random.choice(TRANSACTION_STATUS),
            "ip_address": (
                f"{random.randint(1,255)}."
                f"{random.randint(0,255)}."
                f"{random.randint(0,255)}."
                f"{random.randint(1,255)}"
            ),
            "origin_country": origin_country,
            "destination_country": destination_country,
            "is_international": is_international,
        }

        producer.produce(
            topic=TOPIC_NAME,
            key=customer_id,
            value=json.dumps(event_payload).encode("utf-8"),
            callback=delivery_report,
        )

        producer.poll(0)

        print(
            f"[TXN] {event_payload['transaction_id']} | "
            f"{customer_id} | "
            f"₹{event_payload['transaction_amount']}"
        )

        # One event every minute
        time.sleep(60)

except KeyboardInterrupt:
    print("\n[*] Producer stopped by user.")

finally:
    producer.flush()
    print("[*] Kafka producer flushed and closed.")
