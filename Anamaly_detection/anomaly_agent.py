"""
anomaly_agent.py

Fraud Anomaly Detection Agent

Uses:
1. Rule-based scoring
2. Isolation Forest
3. Customer historical baseline
4. Llama3 reasoning

Output:
{
    score: 87,
    anomalies: [...],
    explanation: ...
}
"""

import json
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest

from langchain_community.llms import Ollama


class AnomalyAgent:

    def __init__(self):

        self.llm = Ollama(
            model="llama3"
        )

    ##################################################################
    # RULE ENGINE
    ##################################################################

    def rule_engine(
        self,
        transaction,
        customer_profile,
        device_profile
    ):

        score = 0

        reasons = []

        amount = float(
            transaction["transaction_amount"]
        )

        ##########################################################
        # HIGH AMOUNT
        ##########################################################

        if amount > 100000:

            score += 25

            reasons.append(
                "High transaction amount"
            )

        ##########################################################
        # INTERNATIONAL
        ##########################################################

        if transaction["is_international"]:

            score += 15

            reasons.append(
                "International transaction"
            )

        ##########################################################
        # HIGH-RISK CUSTOMER
        ##########################################################

        if customer_profile[
            "customer_risk_rating"
        ] == "HIGH":

            score += 20

            reasons.append(
                "High-risk customer"
            )

        ##########################################################
        # HIGH-RISK DEVICE
        ##########################################################

        if (
            device_profile["device_risk_score"]
            > 75
        ):

            score += 20

            reasons.append(
                "High-risk device"
            )

        ##########################################################
        # BLACKLISTED DEVICE
        ##########################################################

        if device_profile["is_blacklisted"]:

            score += 40

            reasons.append(
                "Blacklisted device"
            )

        return score, reasons

    ##################################################################
    # HISTORICAL BASELINE
    ##################################################################

    def baseline_analysis(
        self,
        transaction,
        customer_transactions
    ):

        score = 0

        reasons = []

        if len(customer_transactions) < 10:

            return score, reasons

        historical_avg = (
            customer_transactions[
                "transaction_amount"
            ].mean()
        )

        current_amount = float(
            transaction["transaction_amount"]
        )

        ##########################################################

        if current_amount > historical_avg * 5:

            score += 30

            reasons.append(
                f"Amount is 5x historical average "
                f"({historical_avg:.2f})"
            )

        ##########################################################

        recent_txn = customer_transactions[
            customer_transactions[
                "transaction_timestamp"
            ]
            >
            (
                pd.Timestamp.now()
                - pd.Timedelta(hours=1)
            )
        ]

        if len(recent_txn) > 10:

            score += 25

            reasons.append(
                "High transaction velocity"
            )

        return score, reasons

    ##################################################################
    # ISOLATION FOREST
    ##################################################################

    def isolation_forest_analysis(
        self,
        transaction,
        customer_transactions
    ):

        if len(customer_transactions) < 20:

            return 0, []

        features = customer_transactions[
            [
                "transaction_amount"
            ]
        ]

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        model.fit(features)

        pred = model.predict(
            [[
                float(
                    transaction[
                        "transaction_amount"
                    ]
                )
            ]]
        )

        if pred[0] == -1:

            return 30, [
                "Isolation Forest anomaly"
            ]

        return 0, []

    ##################################################################
    # LLM REASONING
    ##################################################################

    def llm_reasoning(
        self,
        transaction,
        anomaly_score,
        anomaly_reasons
    ):

        prompt = f"""
You are a banking fraud investigator.

Transaction:

{json.dumps(transaction, indent=2, default=str)}

Anomaly Score:
{anomaly_score}

Reasons:
{anomaly_reasons}

Explain:

1. Why suspicious
2. Fraud indicators
3. Risk assessment

Return concise JSON:

{{
    "summary":"",
    "risk_level":"",
    "fraud_indicators":[]
}}
"""

        response = self.llm.invoke(prompt)

        return response

    ##################################################################
    # MAIN ANALYSIS
    ##################################################################

    def analyze(
        self,
        transaction,
        customer_profile,
        device_profile,
        customer_transactions
    ):

        final_score = 0

        anomalies = []

        ##########################################################

        score, reasons = self.rule_engine(
            transaction,
            customer_profile,
            device_profile
        )

        final_score += score

        anomalies.extend(reasons)

        ##########################################################

        score, reasons = self.baseline_analysis(
            transaction,
            customer_transactions
        )

        final_score += score

        anomalies.extend(reasons)

        ##########################################################

        score, reasons = (
            self.isolation_forest_analysis(
                transaction,
                customer_transactions
            )
        )

        final_score += score

        anomalies.extend(reasons)

        ##########################################################

        final_score = min(
            100,
            round(final_score, 2)
        )

        ##########################################################

        explanation = self.llm_reasoning(
            transaction,
            final_score,
            anomalies
        )

        ##########################################################

        return {

            "score": final_score,

            "anomalies": anomalies,

            "explanation": explanation
        }