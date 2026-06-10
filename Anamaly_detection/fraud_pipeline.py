"""
fraud_pipeline.py

End-to-End Fraud Detection Pipeline

Flow:

PostgreSQL
    ↓
Transaction Loader
    ↓
Anomaly Agent (Llama3)
    ↓
Behavior Agent (DeepSeek R1)
    ↓
Graph Agent (Neo4j + DeepSeek)
    ↓
Network Agent (DeepSeek)
    ↓
Sanction Engine
    ↓
RAG Engine (ChromaDB)
    ↓
Explanation Agent
    ↓
Risk Aggregator
    ↓
transaction_analysis_logs
"""

import json
import psycopg2
import pandas as pd
from datetime import datetime

from agents.anomaly_agent import AnomalyAgent
from agents.behavior_agent import BehaviorAgent
from agents.graph_agent import GraphAgent
from agents.network_agent import NetworkAgent
from agents.explanation_agent import ExplanationAgent

from rag.rag_engine import RAGEngine
from sanctions.sanction_engine import SanctionEngine

###########################################################################
# CONFIG
###########################################################################

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "fraud_db",
    "user": "postgres",
    "password": "postgres"
}

###########################################################################
# DATABASE
###########################################################################

class Database:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )

    #######################################################################

    def get_pending_transactions(self):

        sql = """
        SELECT
            t.*,
            c.customer_risk_rating,
            d.device_risk_score,
            b.risk_rating AS beneficiary_risk
        FROM transactions t

        LEFT JOIN customers c
            ON t.customer_id = c.customer_id

        LEFT JOIN devices d
            ON t.device_id = d.device_id

        LEFT JOIN beneficiaries b
            ON t.beneficiary_id = b.beneficiary_id

        WHERE t.transaction_id NOT IN (
            SELECT transaction_id
            FROM transaction_analysis_logs
        )
        """

        return pd.read_sql(sql, self.conn)

    #######################################################################

    def get_behavior(self, customer_id):

        sql = f"""
        SELECT *
        FROM customer_behavior
        WHERE customer_id='{customer_id}'
        ORDER BY login_timestamp DESC
        LIMIT 50
        """

        return pd.read_sql(sql, self.conn)

    #######################################################################

    def insert_analysis(self, result):

        cursor = self.conn.cursor()

        sql = """
        INSERT INTO transaction_analysis_logs (

            transaction_analysis_id,
            transaction_id,
            customer_id,

            fraud_probability,
            behavior_score,
            graph_score,
            sanction_score,
            overall_risk_score,

            risk_category,
            decision,

            agent1_output,
            agent2_output,
            agent3_output,
            agent4_output,
            agent5_output,

            recommended_action,
            investigation_status,

            report,

            created_at

        )
        VALUES (

            gen_random_uuid(),

            %s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,

            %s,%s,%s,%s,%s,

            %s,%s,
            %s,
            NOW()
        )
        """

        cursor.execute(
            sql,
            (
                result["transaction_id"],
                result["customer_id"],

                result["fraud_probability"],
                result["behavior_score"],
                result["graph_score"],
                result["sanction_score"],
                result["overall_risk_score"],

                result["risk_category"],
                result["decision"],

                json.dumps(result["anomaly_output"]),
                json.dumps(result["behavior_output"]),
                json.dumps(result["graph_output"]),
                json.dumps(result["network_output"]),
                json.dumps(result["explanation_output"]),

                result["recommended_action"],
                result["investigation_status"],

                result["report"]
            )
        )

        self.conn.commit()

###########################################################################
# RISK AGGREGATOR
###########################################################################

class RiskAggregator:

    @staticmethod
    def calculate(
            anomaly_score,
            behavior_score,
            graph_score,
            sanction_score,
            network_score
    ):

        risk = (

            anomaly_score * 0.30 +
            behavior_score * 0.20 +
            graph_score * 0.20 +
            sanction_score * 0.15 +
            network_score * 0.15

        )

        return round(risk, 2)

###########################################################################
# FRAUD PIPELINE
###########################################################################

class FraudPipeline:

    def __init__(self):

        self.db = Database()

        self.anomaly_agent = AnomalyAgent()
        self.behavior_agent = BehaviorAgent()
        self.graph_agent = GraphAgent()
        self.network_agent = NetworkAgent()

        self.explanation_agent = ExplanationAgent()

        self.rag_engine = RAGEngine()
        self.sanction_engine = SanctionEngine()

    #######################################################################

    def process_transaction(self, transaction):

        transaction_id = transaction["transaction_id"]

        print(f"Processing {transaction_id}")

        ###############################################################
        # BEHAVIOR
        ###############################################################

        behavior_df = self.db.get_behavior(
            transaction["customer_id"]
        )

        ###############################################################
        # ANOMALY AGENT
        ###############################################################

        anomaly_result = self.anomaly_agent.analyze(
            transaction
        )

        ###############################################################
        # BEHAVIOR AGENT
        ###############################################################

        behavior_result = self.behavior_agent.analyze(
            behavior_df
        )

        ###############################################################
        # GRAPH AGENT
        ###############################################################

        graph_result = self.graph_agent.analyze(
            transaction
        )

        ###############################################################
        # NETWORK AGENT
        ###############################################################

        network_result = self.network_agent.analyze(
            transaction
        )

        ###############################################################
        # SANCTION
        ###############################################################

        sanction_result = self.sanction_engine.check(
            transaction
        )

        ###############################################################
        # RAG
        ###############################################################

        similar_cases = self.rag_engine.search(
            transaction
        )

        ###############################################################
        # FINAL SCORE
        ###############################################################

        overall_score = RiskAggregator.calculate(

            anomaly_result["score"],
            behavior_result["score"],
            graph_result["score"],
            sanction_result["score"],
            network_result["score"]

        )

        ###############################################################
        # DECISION
        ###############################################################

        if overall_score >= 85:

            decision = "BLOCK"
            risk_category = "HIGH"

        elif overall_score >= 60:

            decision = "REVIEW"
            risk_category = "MEDIUM"

        else:

            decision = "APPROVE"
            risk_category = "LOW"

        ###############################################################
        # EXPLANATION
        ###############################################################

        explanation = self.explanation_agent.explain(

            transaction=transaction,

            anomaly=anomaly_result,

            behavior=behavior_result,

            graph=graph_result,

            network=network_result,

            sanction=sanction_result,

            rag_context=similar_cases,

            final_score=overall_score,

            decision=decision

        )

        ###############################################################
        # RESULT
        ###############################################################

        result = {

            "transaction_id":
                transaction["transaction_id"],

            "customer_id":
                transaction["customer_id"],

            "fraud_probability":
                overall_score,

            "behavior_score":
                behavior_result["score"],

            "graph_score":
                graph_result["score"],

            "sanction_score":
                sanction_result["score"],

            "overall_risk_score":
                overall_score,

            "risk_category":
                risk_category,

            "decision":
                decision,

            "recommended_action":
                explanation["recommended_action"],

            "investigation_status":
                explanation["investigation_status"],

            "anomaly_output":
                anomaly_result,

            "behavior_output":
                behavior_result,

            "graph_output":
                graph_result,

            "network_output":
                network_result,

            "explanation_output":
                explanation,

            "report":
                explanation["summary"]
        }

        ###############################################################
        # WRITE TO DB
        ###############################################################

        self.db.insert_analysis(result)

        return result

    #######################################################################

    def run(self):

        transactions = self.db.get_pending_transactions()

        print(
            f"Transactions Found: {len(transactions)}"
        )

        for _, row in transactions.iterrows():

            try:

                self.process_transaction(
                    row.to_dict()
                )

            except Exception as ex:

                print(
                    f"Failed {row['transaction_id']}: {ex}"
                )

###########################################################################
# MAIN
###########################################################################

if __name__ == "__main__":

    pipeline = FraudPipeline()

    pipeline.run()