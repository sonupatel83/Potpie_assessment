from celery import Celery
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from openai import Completion
from ..database import save_task_result
from ..config import Config
#celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


celery_app = Celery(
    "tasks",
    broker=Config.REDIS_URL,  # Redis for message queuing
    backend=Config.REDIS_URL  # PostgreSQL for task results
)
@celery_app.task(bind=True)
def analyze_pr_task(self, request_data):
    try:
        template = PromptTemplate(template="Analyze the following PR: {content}")
        chain = LLMChain(llm=Completion(), prompt=template)
        result = chain.run(request_data['content'])
        save_task_result(self.request.id, result)
        return result
    except Exception as e:
        print(f"Error in analyze_pr_task: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise