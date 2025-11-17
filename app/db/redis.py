import redis
from ..config import Config

def get_redis_client():
    """
    Connects to the Redis database using the provided REDIS_URL from the environment.
    """
    return redis.StrictRedis.from_url(Config.REDIS_URL, decode_responses=True)
