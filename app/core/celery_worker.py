from celery import Celery
from ..config import Config
from ..services.ollama_service import OllamaService

# Note: This file appears to be legacy. The main Celery app is in app.workers.tasks
# Keeping this for backward compatibility but it's not actively used

celery_app = Celery(
    "tasks",
    broker=Config.get_redis_url(),  # Redis for message queuing
    backend=Config.get_redis_url()  # Redis for task results
)

@celery_app.task(bind=True)
def analyze_pr_task(self, request_data):
    try:
        ollama_service = OllamaService()
        result = ollama_service.analyze_code(
            file_name=request_data.get('file_name', 'unknown'),
            content=request_data.get('content', '')
        )
        # Note: save_task_result might not exist, this is legacy code
        # from ..database import save_task_result
        # save_task_result(self.request.id, result)
        return result
    except Exception as e:
        print(f"Error in analyze_pr_task: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise