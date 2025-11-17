from ..config import Config

CELERY_BROKER_URL = Config.REDIS_URL
CELERY_RESULT_BACKEND = Config.REDIS_URL
