# app/core/alerts.py

from datetime import datetime

def send_alert(tx, decision_result):
    action = decision_result["action"]

    if action == "BLOCK":
        print("\n🚨 FRAUD ALERT 🚨")
        print(f"Transaction ID : {tx.tx_id}")
        print(f"Sender         : {tx.sender_vpa}")
        print(f"Receiver       : {tx.receiver_vpa}")
        print(f"Amount         : ₹{tx.amount}")
        print(f"Risk Score     : {decision_result['risk_score']}")
        print(f"Reasons        : {decision_result.get('top_risk_factors', [])}")
        print(f"Time           : {datetime.utcnow().isoformat()}")
        print("ACTION REQUIRED IMMEDIATELY\n")

    elif action == "STEP_UP_AUTH":
        print("\n⚠️ RISK WARNING ⚠️")
        print(f"Transaction ID : {tx.tx_id}")
        print(f"Amount         : ₹{tx.amount}")
        print(f"Risk Score     : {decision_result['risk_score']}")
        print(f"Time           : {datetime.utcnow().isoformat()}")
        print("Requires additional authentication\n")
