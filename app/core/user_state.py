user_state = {}

def update_user_state(tx):
    uid = tx.user_id

    if uid not in user_state:
        user_state[uid] = {
            "avg_amount": tx.amount,
            "tx_count": 1,
            "last_location": tx.location,
            "last_time": tx.time
        }
    else:
        state = user_state[uid]
        state["avg_amount"] = (state["avg_amount"] + tx.amount) / 2
        state["tx_count"] += 1
        state["last_location"] = tx.location
        state["last_time"] = tx.time

    return user_state[uid]
