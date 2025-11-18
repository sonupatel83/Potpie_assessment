from app.db.redis import get_redis_client

def test_redis_connection():
    redis_client = get_redis_client()
    try:
        redis_client.set("test_key", "test_value", ex=60)  # Set a key with 60 seconds expiry
        value = redis_client.get("test_key")  # Retrieve the value
        print(f"Connection successful. Retrieved: {value}")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

if __name__ == "__main__":
    test_redis_connection()
