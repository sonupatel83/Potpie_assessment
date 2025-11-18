from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.postgres import get_db, create_task, get_task, update_task_status
from ..workers.tasks import analyze_pr_task, compare_files_task
from ..db.redis import get_redis_client
import json


router = APIRouter()

@router.post("/analyze-pr")
async def analyze_pr(repo_url: str, pr_number: int, db: Session = Depends(get_db)):
    task = analyze_pr_task.delay(repo_url, pr_number)
    create_task(task.id, db)
    return {"task_id": task.id}

@router.get("/status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    redis_client = get_redis_client()
    
    # Try Redis first
    redis_data = redis_client.get(f"task:{task_id}")
    if redis_data:
        task_data = json.loads(redis_data)
        response = {"task_id": task_id, "status": task_data["status"]}
        # Include checkpoint if available
        if "checkpoint" in task_data:
            response["checkpoint"] = task_data["checkpoint"]
        return response

    # Fallback to PostgreSQL
    task = get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": task.status}

@router.get("/results/{task_id}")
async def get_results(task_id: str, db: Session = Depends(get_db)):
    redis_client = get_redis_client()
    
    # Try Redis first
    redis_data = redis_client.get(f"task:{task_id}")
    if redis_data:
        task_data = json.loads(redis_data)
        if task_data["status"] != "completed":
            return {"status": task_data["status"]}
        return {"task_id": task_id, "results": task_data["result"]}

    # Fallback to PostgreSQL
    task = get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != "completed":
        return {"status": task.status}
    return {"task_id": task_id, "results": task.result}

@router.post("/compare-files")
async def compare_files(
    repo_a_raw_url: str,
    repo_b_raw_url: str,
    ref_a: str = "HEAD",
    ref_b: str = "HEAD",
    db: Session = Depends(get_db)
):
    """Compare two files from different repositories"""
    task = compare_files_task.delay(repo_a_raw_url, repo_b_raw_url, ref_a, ref_b)
    create_task(task.id, db)
    return {"task_id": task.id}

# from fastapi import APIRouter, Depends, HTTPException
# from ..db.postgres import get_db, create_task, get_task, update_task_status
# from ..workers.tasks import analyze_pr_task
# from sqlalchemy.orm import Session

# router = APIRouter()

# @router.post("/analyze-pr")
# async def analyze_pr(repo_url: str, pr_number: int, db: Session = Depends(get_db)):
#     task = analyze_pr_task.delay(repo_url, pr_number)
#     create_task(task.id, db)
#     return {"task_id": task.id}

# @router.get("/status/{task_id}")
# async def get_status(task_id: str, db: Session = Depends(get_db)):
#     task = get_task(task_id, db)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return {"task_id": task_id, "status": task.status}

# @router.get("/results/{task_id}")
# async def get_results(task_id: str, db: Session = Depends(get_db)):
#     task = get_task(task_id, db)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     if task.status != "completed":
#         return {"status": task.status}
#     return {"task_id": task_id, "results": task.result}
