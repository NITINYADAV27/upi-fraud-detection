import os
import requests
from datetime import datetime

# Slack webhook URL ONLY from environment
OPS_SLACK_WEBHOOK_URL = os.getenv("OPS_SLACK_WEBHOOK_URL")


def send_alert(message: str, severity: str = "HIGH"):
    """
    Sends alert to Slack (if configured)
    Does NOT break project if Slack is not configured
    """

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    alert_text = (
        f"🚨 *UPI Fraud Alert*\n"
        f"*Severity:* {severity}\n"
        f"*Time:* {timestamp} UTC\n\n"
        f"{message}"
    )

    # If Slack is not configured, fail silently (important for production)
    if not OPS_SLACK_WEBHOOK_URL:
        print("⚠️ OPS_SLACK_WEBHOOK_URL not set. Alert skipped.")
        return

    payload = {"text": alert_text}

    try:
        response = requests.post(
            OPS_SLACK_WEBHOOK_URL,
            json=payload,
            timeout=5
        )

        if response.status_code != 200:
            print(
                f"Slack alert failed "
                f"(status={response.status_code}): {response.text}"
            )

    except Exception as e:
        print("Slack alert exception:", str(e))
