import joblib
import pandas as pd
import numpy as np
import json


def log_transform(x):
    return np.log1p(x)


def cyclical_hour_sine(x):
    return np.sin(2 * np.pi * x / 24.0)


def cyclical_hour_cosine(x):
    return np.cos(2 * np.pi * x / 24.0)


# Load inference dependencies
loaded_preprocessor = joblib.load("Artifacts/production_preprocessor_pipeline.pkl")
loaded_classifier = joblib.load("Artifacts/transformed_fraud_classifier.pkl")
loaded_regressor = joblib.load("Artifacts/transformed_risk_regressor.pkl")

# Incoming unmapped mock streaming message payload direct from Kafka consumer
kafka_event_message = {
    "transaction_id": "TXN_LIVE_STREAM_99B",
    "transaction_amount": 22450.00,
    "is_international": 1,
    "hour_of_day": 3,  # 3 AM Off-Hours
    "features_for_classifier": {
        "account_age_days": 5,
        "transaction_frequency_24h": 58,
        "failed_transaction_count_24h": 9,
        "avg_transaction_amount_7d": 120.00,
        "session_duration_minutes": 2,
        "device_risk_score": 98.40,
        "unusual_amount_flag": 1,
        "unusual_location_flag": 1,
        "typing_speed_flag": 1,
    },
    "agent_pipelines_telemetry": {
        "graph_agent_context": {
            "shared_device_mule_count": 19,
            "known_fraud_ring_edge": 1,
        },
        "behavioral_agent_context": {
            "biometric_anomaly_detected": 1,
            "automation_script_suspected": 1,
        },
    },
}


def stream_realtime_inference(event):
    # Unpack nested components precisely into a single row DataFrame
    f_class = event["features_for_classifier"]
    g_agent = event["agent_pipelines_telemetry"]["graph_agent_context"]
    b_agent = event["agent_pipelines_telemetry"]["behavioral_agent_context"]

    raw_record = {
        "transaction_amount": event["transaction_amount"],
        "avg_transaction_amount_7d": f_class["avg_transaction_amount_7d"],
        "hour_of_day": event["hour_of_day"],
        "account_age_days": f_class["account_age_days"],
        "transaction_frequency_24h": f_class["transaction_frequency_24h"],
        "failed_transaction_count_24h": f_class["failed_transaction_count_24h"],
        "session_duration_minutes": f_class["session_duration_minutes"],
        "device_risk_score": f_class["device_risk_score"],
        "shared_device_mule_count": g_agent["shared_device_mule_count"],
        "is_international": event["is_international"],
        "unusual_amount_flag": f_class["unusual_amount_flag"],
        "unusual_location_flag": f_class["unusual_location_flag"],
        "typing_speed_flag": f_class["typing_speed_flag"],
        "known_fraud_ring_edge": g_agent["known_fraud_ring_edge"],
        "biometric_anomaly_detected": b_agent["biometric_anomaly_detected"],
        "automation_script_suspected": b_agent["automation_script_suspected"],
    }

    df_raw = pd.DataFrame([raw_record])

    # Transform raw event features through our pre-fitted transformer pipeline
    transformed_vector = loaded_preprocessor.transform(df_raw)

    # Compute downstream score actions
    is_fraud_decision = loaded_classifier.predict(transformed_vector)[0]
    predicted_score = loaded_regressor.predict(transformed_vector)[0]

    return {
        "transaction_id": event["transaction_id"],
        "system_action": (
            "TERMINATE_TRANSACTION" if is_fraud_decision == 1 else "ALLOW_TRANSACTION"
        ),
        "realtime_risk_score": round(float(predicted_score), 2),
    }


# Execute inference process loop
output_payload = stream_realtime_inference(kafka_event_message)
print("📥 Real-Time Secure Process Inference Output:")
print(json.dumps(output_payload, indent=4))
