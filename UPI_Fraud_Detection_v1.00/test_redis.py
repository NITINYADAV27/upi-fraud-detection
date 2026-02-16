from app.core.redis_client import redis_client

def test_redis_connection():
    try:
        redis_client.set("health_check", "OK")
        value = redis_client.get("health_check")

        if value == "OK":
            print("✅ Redis connection successful")
        else:
            print("⚠️ Redis responded, but value mismatch:", value)

    except Exception as e:
        print("❌ Redis connection failed:", e)

if __name__ == "__main__":
    test_redis_connection()
