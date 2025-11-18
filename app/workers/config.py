from ..config import Config

# Use the get_redis_url method to construct the Redis URL for Celery
CELERY_BROKER_URL = Config.CELERY_BROKER_URL or Config.get_redis_url()
CELERY_RESULT_BACKEND = Config.CELERY_RESULT_BACKEND or Config.get_redis_url()
