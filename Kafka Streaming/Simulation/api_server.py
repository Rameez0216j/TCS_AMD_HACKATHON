from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/transactions', methods=['POST'])
def receive_transaction():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data payload received"}), 400
    
    # Extract structural variables for terminal logging
    tx_id = data.get("transaction_id")
    cid = data.get("customer_id")
    amount = data.get("transaction_amount")
    tx_type = data.get("transaction_type")
    telemetry = data.get("behavioral_telemetry", {})
    
    # Log directly to the VS Code terminal screen
    print(f"\n[📥 API RECEIVER] Incoming Event: {tx_id}")
    print(f" └── Customer: {cid} | Amount: ₹{amount:,.2f} | Type: {tx_type}")
    print(f" └── Route: {data.get('origin_country')} -> {data.get('destination_country')} (Intl: {data.get('is_international')})")
    print(f" └── Telemetry -> Typing Score: {telemetry.get('typing_speed_score')} | Mouse Score: {telemetry.get('mouse_movement_score')}")
    print("-" * 70)
    
    # Your downstream Feature Engineering & XGBoost pipeline would hook in right here
    
    return jsonify({"status": "success", "message": "Transaction logged successfully"}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("API SERVER ACTIVE ON http://127.0.0.1:5000")
    print("Awaiting live HTTP transaction stream data...")
    print("=" * 60)
    app.run(port=5000, debug=False)