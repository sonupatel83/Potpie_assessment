import redis
from ..config import Config

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(Config.REDIS_URL)

    def set(self, key, value, expiration=None):
        self.redis_client.set(key, value, ex=expiration)

    def get(self, key):
        return self.redis_client.get(key)

    def delete(self, key):
        self.redis_client.delete(key)
