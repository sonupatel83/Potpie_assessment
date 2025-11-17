from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from .core.celery_worker import analyze_pr_task
from .database import get_db
from .api.schemas import PRRequest, PRResponse

app = FastAPI()

@app.post("/analyze-pr", response_model=PRResponse)
def analyze_pr(
    request: PRRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)  # Ensure the correct type annotation for `db`
):
    try:
        task = analyze_pr_task.delay(request.dict())
        background_tasks.add_task(track_task_status, task.id, db)
        return PRResponse(task_id=task.id, status="Processing")  # Return PRResponse model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")


@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id)
    if result.state == 'FAILURE':
        raise HTTPException(status_code=500, detail="Task failed")
    return {"task_id": task_id, "status": result.state, "result": result.result if result.state == 'SUCCESS' else None}
