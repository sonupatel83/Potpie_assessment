import redis
from ..config import Config

class RedisService:
    def __init__(self):
        # Use URL if provided, otherwise construct from components
        if Config.REDIS_URL:
            self.redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
        else:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                username=Config.REDIS_USERNAME,
                password=Config.REDIS_PASSWORD,
                decode_responses=True
            )

    def set(self, key, value, expiration=None):
        self.redis_client.set(key, value, ex=expiration)

    def get(self, key):
        return self.redis_client.get(key)

    def delete(self, key):
        self.redis_client.delete(key)
