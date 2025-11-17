from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    REDIS_URL = os.getenv("REDIS_URL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @staticmethod
    def validate():
        required_vars = ["REDIS_URL", "GITHUB_TOKEN", "DATABASE_URL", "OPENAI_API_KEY"]
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Environment variable {var} is missing.")
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
