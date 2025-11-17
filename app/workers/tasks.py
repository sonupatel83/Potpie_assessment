import requests
from celery import Celery
from sqlalchemy.orm import Session
from ..db.postgres import update_task_status
from ..db.models import SessionLocal
from ..config import Config
from ..logger import logging
from ..core.github_utils import fetch_pr_files
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

app = Celery(
    "tasks",
    broker=Config.REDIS_URL,  # Redis for message queuing
    backend=Config.REDIS_URL  # PostgreSQL for task results
)


@app.task(bind=True, name="analyze_pr_task")
def analyze_pr_task(self, repo_url: str, pr_number: int):
    logging.info(f"Received task for repo: {repo_url}, PR: {pr_number}")
    session = SessionLocal()
    try:
        # Fetch PR files
        files = fetch_pr_files(repo_url, pr_number)
        if not files:
            raise Exception("No files found in the PR.")

        # Initialize LLM
        llm = ChatOpenAI(
            openai_api_key=Config.OPENAI_API_KEY,
            model_name="gpt-4"
        )

        prompt = PromptTemplate(
            input_variables=["file_name", "content"],
            template="""
                Analyze the following GitHub Pull Request file for potential issues:
                File Name: {file_name}
                Content:
                {content}
            """
        )
        chain = LLMChain(llm=llm, prompt=prompt)

        # Analyze files
        results = []
        for file in files:
            analysis = chain.run(file_name=file["filename"], content=file["content"])
            results.append({
                "file_name": file["filename"],
                "analysis": analysis,
            })

        # Update task status in the database
        update_task_status(self.request.id, "completed", result=results, db=session)
        return results
    except Exception as e:
        update_task_status(self.request.id, "failed", result=str(e), db=session)
        logging.error(f"Task {self.request.id} failed: {e}")
        raise
    finally:
        session.close()

#print(os.getenv("REDIS_URL"))  # Check if this prints the correct URL
