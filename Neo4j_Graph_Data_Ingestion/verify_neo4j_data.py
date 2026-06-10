import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv("../.env")  # Ensure this path points to your .env file

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    print("❌ Error: Missing Neo4j credentials in the .env file.")
    sys.exit(1)


def run_diagnostic_query(session, cypher_query, title):
    print(f"\n📊 {title}")
    print("-" * 50)
    try:
        result = session.run(cypher_query)
        records = list(result)
        if not records:
            print("   (No data found or returned empty)")
            return

        # Dynamically fetch keys for clean tabular printing
        keys = records[0].keys()
        header = " | ".join(f"{key:<25}" for key in keys)
        print(header)
        print("-" * 50)

        for record in records:
            row = " | ".join(f"{str(record[key]):<25}" for key in keys)
            print(row)
    except Exception as e:
        print(f"❌ Query execution failed: {e}")


def main():
    print("🚀 Connecting to Neo4j Aura to verify data ingestion...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    with driver.session() as session:

        # 1. Check Node Counts broken down by Label
        q_node_counts = """
        MATCH (n)
        RETURN labels(n)[0] AS NodeLabel, count(n) AS TotalCount
        ORDER BY TotalCount DESC
        """
        run_diagnostic_query(session, q_node_counts, "NODE COUNT SUMMARY")

        # 2. Check Relationship Counts broken down by Type
        q_rel_counts = """
        MATCH ()-[r]->()
        RETURN type(r) AS RelationshipType, count(r) AS TotalCount
        ORDER BY TotalCount DESC
        """
        run_diagnostic_query(session, q_rel_counts, "RELATIONSHIP SUMMARY")

        # 3. Fraud Ring Validation (Smoke Test)
        # Your dataGenerator.py file intentionally links 45 customers to a single mule device.
        # This query checks if that high-risk structural pattern was successfully captured.
        q_fraud_smoke_test = """
        MATCH (d:Device)<-[:HAS_DEVICE]-(c:Customer)
        WITH d, count(c) AS shared_count
        WHERE shared_count > 5
        RETURN d.device_id AS FlaggedDeviceID, shared_count AS ConnectedMuleCustomers
        ORDER BY shared_count DESC
        LIMIT 3
        """
        run_diagnostic_query(
            session, q_fraud_smoke_test, "INTEGRITY TEST: MULE DEVICE CLUSTERS DETECTED"
        )

        # 4. Check Sample Sanction Matches
        q_sanction_check = """
        MATCH (b:Beneficiary)-[:SANCTION_MATCH]->(s:SanctionEntity)
        RETURN b.receiver_name AS BeneficiaryName, s.sanction_category AS Reason, s.risk_level AS Severity
        LIMIT 5
        """
        run_diagnostic_query(
            session, q_sanction_check, "INTEGRITY TEST: CROSS-ENTITY SANCTION MATCHES"
        )

    driver.close()
    print("\n✅ Verification complete.")


if __name__ == "__main__":
    main()
