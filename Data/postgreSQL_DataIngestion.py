"""
postgres_data_ingestion.py
Bulk CSV ingestion into PostgreSQL
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv("../.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CSV_DIR = r"D:\TCS\TCS_AMD_HACKATHON\Data\synthetic_fraud_data"

INGESTION_PIPELINE = [
    ("customers", "customers.csv"),
    ("devices", "devices.csv"),
    ("beneficiaries", "beneficiaries.csv"),
    ("merchants", "merchants.csv"),
    ("customer_devices", "customer_devices.csv"),
    ("customer_beneficiaries", "customer_beneficiaries.csv"),
    ("sanction_list", "sanction_list.csv"),
    ("transactions", "transactions.csv"),
    ("customer_behavior", "customer_behavior.csv"),
    ("transaction_analysis_logs", "transaction_analysis_logs.csv"),
]


def load_csv(cur, table, file_name):
    if not os.path.exists(file_name):
        print(f"Missing: {file_name}")
        return

    with open(file_name, "r", encoding="utf-8") as f:
        copy_sql = sql.SQL("COPY {} FROM STDIN WITH CSV HEADER").format(
            sql.Identifier(table)
        )

        cur.copy_expert(copy_sql.as_string(cur.connection), f)


def main():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("Loading CSV files...\n")

        for table, csv_file in INGESTION_PIPELINE:
            print(f"Loading {table}...")
            load_csv(cur, table, os.path.join(CSV_DIR, csv_file))
            conn.commit()
            print(f"Loaded {table}")

        print("\nSUCCESS - All data loaded.")

    except Exception as ex:
        print(f"\nERROR: {ex}")

        if conn:
            conn.rollback()

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()
