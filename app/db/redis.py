import redis
from ..config import Config

def get_redis_client():
    """
    Connects to the Redis database using the provided credentials.
    Supports both URL format and individual connection parameters.
    """
    # If REDIS_URL is provided, use it
    if Config.REDIS_URL:
        return redis.StrictRedis.from_url(Config.REDIS_URL, decode_responses=True)
    
    # Otherwise, use individual connection parameters
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        username=Config.REDIS_USERNAME,
        password=Config.REDIS_PASSWORD,
        decode_responses=True
    )
