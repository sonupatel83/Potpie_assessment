from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL"))
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL"))
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    SYNC_DB_URL = os.getenv("SYNC_DB_URL")
    
    # Convert asyncpg URL to psycopg2 for SQLAlchemy if needed
    if DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg://"):
        _sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if not SYNC_DB_URL:
            SYNC_DB_URL = _sync_url
    
    # Use SYNC_DB_URL for SQLAlchemy, or convert DATABASE_URL
    if SYNC_DB_URL:
        # Fix database name if it's wrong
        if "git-cr-pr" in SYNC_DB_URL:
            SYNC_DB_URL = SYNC_DB_URL.replace("git-cr-pr", "neondb")
        SQLALCHEMY_DATABASE_URL = SYNC_DB_URL
    elif DATABASE_URL:
        # Convert postgresql:// or postgresql+asyncpg:// to postgresql+psycopg2://
        SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1).replace("postgresql://", "postgresql+psycopg2://", 1)
        # Fix database name if it's wrong
        if "git-cr-pr" in SQLALCHEMY_DATABASE_URL:
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("git-cr-pr", "neondb")
    else:
        # Fallback default - using neondb (the actual database name)
        SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_u0Mn2XCpQZVT@ep-delicate-leaf-a4fku0da-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Ollama configuration
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434/api")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    
    # API Keys
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    @staticmethod
    def get_redis_url():
        """Get Redis URL for Celery"""
        return Config.CELERY_BROKER_URL or Config.REDIS_URL

    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.REDIS_URL and not Config.CELERY_BROKER_URL:
            raise ValueError("REDIS_URL or CELERY_BROKER_URL must be set")
        if not Config.DATABASE_URL and not Config.SYNC_DB_URL:
            raise ValueError("DATABASE_URL or SYNC_DB_URL must be set")
# # config.py
# import os
# from dotenv import load_dotenv
# from pydantic_settings import BaseSettings

# load_dotenv()

# class Config(BaseSettings):
#     REDIS_URL: str 
#     DATABASE_URL: str
#     OPENAI_API_KEY: str
#     GITHUB_TOKEN: str

#     class Config:
#         env_file = ".env"

# settings = Config()

# import os
# from dotenv import load_dotenv
# from pydantic_settings import BaseSettings

# load_dotenv()


# class Settings(BaseSettings):
#     REDIS_URL: str
#     DATABASE_URL: str
#     OPENAI_API_KEY: str
#     GITHUB_TOKEN: str

#     class Config:
#         env_file = ".env"

# settings = Settings()
