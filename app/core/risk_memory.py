from app.core.redis_client import redis_client

RISK_TTL = 3600  # 1 hour memory

def _sender_key(sender_vpa):
    return f"risk:sender:{sender_vpa}"

def _receiver_key(receiver_vpa):
    return f"risk:receiver:{receiver_vpa}"

def increase_risk(sender_vpa, receiver_vpa, score=20):
    redis_client.incrby(_sender_key(sender_vpa), score)
    redis_client.incrby(_receiver_key(receiver_vpa), score)

    redis_client.expire(_sender_key(sender_vpa), RISK_TTL)
    redis_client.expire(_receiver_key(receiver_vpa), RISK_TTL)

def get_risk(sender_vpa, receiver_vpa):
    sender_risk = redis_client.get(_sender_key(sender_vpa)) or 0
    receiver_risk = redis_client.get(_receiver_key(receiver_vpa)) or 0

    return int(sender_risk) + int(receiver_risk)
