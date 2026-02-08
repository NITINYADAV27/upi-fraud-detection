import time
from app.core.event_queue import alert_queue
from app.core.alert_service import process_alert

def start_alert_worker():
    while True:
        if not alert_queue.empty():
            tx, result = alert_queue.get()
            process_alert(tx, result)
        time.sleep(0.1)
