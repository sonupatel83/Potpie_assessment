from fastapi import FastAPI
from .api.endpoints import router as api_router

app = FastAPI(title="GitHub PR Analysis API", version="1.0.0")
app.include_router(api_router)

# from fastapi import FastAPI
# from .api.endpoints import router as api_router
# from .config import Config
# from .database import get_db
# from .services.redis_service import RedisService
# from .services.github_service import GitHubService
# from .services.openai_service import OpenAIService
# app = FastAPI()
# app.include_router(api_router)

# # Validate environment variables
# Config.validate()

# redis_service = RedisService()
# github_service = GitHubService()
# openai_service = OpenAIService()

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the application!"}

# @app.get("/github/{username}/repos")
# def fetch_github_repos(username: str):
#     return github_service.get_user_repos(username)

# @app.get("/openai/generate")
# def generate_text(prompt: str):
#     return {"response": openai_service.generate_text(prompt)}