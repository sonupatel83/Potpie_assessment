from celery import Celery
from sqlalchemy.orm import Session
from ..db.postgres import update_task_status
from ..db.models import SessionLocal
from ..config import Config
from ..logger import logging
from ..core.github_utils import fetch_pr_files, fetch_pr_commits
from ..core.file_comparison import fetch_file_from_raw_url, compute_unified_diff
from ..services.ollama_service import OllamaService
from ..services.comparison_service import ComparisonService
import json
import time

app = Celery(
    "tasks",
    broker=Config.get_redis_url(),  # Redis for message queuing
    backend=Config.get_redis_url()  # Redis for task results
)


@app.task(bind=True, name="analyze_pr_task")
def analyze_pr_task(self, repo_url: str, pr_number: int):
    logging.info(f"Received task for repo: {repo_url}, PR: {pr_number}")
    session = SessionLocal()
    try:
        # Update status to processing
        update_task_status(self.request.id, "processing", result=None, db=session)
        
        # Initialize Ollama service
        ollama_service = OllamaService()
        
        # Fetch 2 commits from the PR
        logging.info(f"Fetching commits from PR #{pr_number}...")
        commits = fetch_pr_commits(repo_url, pr_number, limit=2)
        
        if not commits:
            # Fallback to PR files if no commits found
            logging.info("No commits found, falling back to PR files...")
            files = fetch_pr_files(repo_url, pr_number)
            if not files:
                raise Exception("No files or commits found in the PR.")
            
            results = []
            for file in files:
                logging.info(f"Analyzing file: {file['filename']}")
                try:
                    analysis = ollama_service.analyze_code(
                        file_name=file["filename"],
                        content=file["content"]
                    )
                    results.append({
                        "file_name": file["filename"],
                        "analysis": analysis,
                    })
                except Exception as e:
                    logging.error(f"Error analyzing file {file['filename']}: {e}")
                    results.append({
                        "file_name": file["filename"],
                        "analysis": f"Error analyzing file: {str(e)}",
                    })
        else:
            # Analyze commits
            logging.info(f"Found {len(commits)} commits. Analyzing...")
            results = []
            
            for idx, commit in enumerate(commits, 1):
                logging.info(f"Analyzing commit {idx}/{len(commits)}: {commit['sha']}")
                commit_analysis = {
                    "commit_sha": commit["sha"],
                    "commit_message": commit["message"],
                    "author": commit["author"],
                    "date": commit["date"],
                    "files_analyzed": []
                }
                
                # Analyze each file in the commit
                for file in commit.get("files", []):
                    filename = file.get("filename", "unknown")
                    patch = file.get("patch", "")
                    status = file.get("status", "")
                    additions = file.get("additions", 0)
                    deletions = file.get("deletions", 0)
                    
                    logging.info(f"  Analyzing file: {filename} ({status}, +{additions}/-{deletions})")
                    
                    try:
                        if patch:
                            analysis = ollama_service.analyze_code(
                                file_name=filename,
                                content=patch
                            )
                        else:
                            analysis = f"File {status} (no patch available). Additions: {additions}, Deletions: {deletions}"
                        
                        commit_analysis["files_analyzed"].append({
                            "filename": filename,
                            "status": status,
                            "additions": additions,
                            "deletions": deletions,
                            "analysis": analysis
                        })
                    except Exception as e:
                        logging.error(f"Error analyzing file {filename} in commit {commit['sha']}: {e}")
                        commit_analysis["files_analyzed"].append({
                            "filename": filename,
                            "status": status,
                            "additions": additions,
                            "deletions": deletions,
                            "analysis": f"Error analyzing file: {str(e)}"
                        })
                
                results.append(commit_analysis)

        # Update task status in the database
        update_task_status(self.request.id, "completed", result=results, db=session)
        logging.info(f"Task {self.request.id} completed successfully. Analyzed {len(results)} commits.")
        return results
    except Exception as e:
        update_task_status(self.request.id, "failed", result=str(e), db=session)
        logging.error(f"Task {self.request.id} failed: {e}")
        raise
    finally:
        session.close()


@app.task(bind=True, name="compare_files_task")
def compare_files_task(self, repo_a_raw_url: str, repo_b_raw_url: str, ref_a: str = "HEAD", ref_b: str = "HEAD"):
    """Compare two files from different repositories"""
    start_time = time.time()
    session = SessionLocal()
    
    try:
        # Update status to processing
        update_task_status(self.request.id, "processing", result=None, db=session, checkpoint="starting")
        
        # Step 1: Fetch file A
        logging.info(f"Step 1/3: Fetching file A from {repo_a_raw_url}")
        update_task_status(self.request.id, "processing", result=None, db=session, checkpoint="fetch_file_a")
        
        file_a_result = fetch_file_from_raw_url(repo_a_raw_url, ref_a)
        if not file_a_result["fetched"]:
            error_msg = f"Failed to fetch file A: {file_a_result.get('error', 'Unknown error')}"
            update_task_status(self.request.id, "failed", result={"error": error_msg}, db=session)
            raise Exception(error_msg)
        
        # Step 2: Fetch file B
        logging.info(f"Step 2/3: Fetching file B from {repo_b_raw_url}")
        update_task_status(self.request.id, "processing", result=None, db=session, checkpoint="fetch_file_b")
        
        file_b_result = fetch_file_from_raw_url(repo_b_raw_url, ref_b)
        if not file_b_result["fetched"]:
            error_msg = f"Failed to fetch file B: {file_b_result.get('error', 'Unknown error')}"
            update_task_status(self.request.id, "failed", result={"error": error_msg}, db=session)
            raise Exception(error_msg)
        
        # Step 3: Compute diff and analyze
        logging.info("Step 3/3: Computing diff and analyzing...")
        update_task_status(self.request.id, "processing", result=None, db=session, checkpoint="compute_diff")
        
        # Extract file names from URLs
        file_a_name = repo_a_raw_url.split("/")[-1]
        file_b_name = repo_b_raw_url.split("/")[-1]
        
        # Compute unified diff
        diff_result = compute_unified_diff(
            file_a_result["content"],
            file_b_result["content"],
            file_a_name,
            file_b_name
        )
        
        # Analyze using comparison service
        comparison_service = ComparisonService()
        analysis_result = comparison_service.analyze_comparison(
            file_a_result["content"],
            file_b_result["content"],
            file_a_name,
            file_b_name,
            diff_result["unified_diff"]
        )
        
        # Build final result
        duration = time.time() - start_time
        final_result = {
            "task": "compare_files",
            "repo_a": {
                "raw_url": repo_a_raw_url,
                "fetched": file_a_result["fetched"],
                "meta": file_a_result["meta"],
                "error": file_a_result["error"]
            },
            "repo_b": {
                "raw_url": repo_b_raw_url,
                "fetched": file_b_result["fetched"],
                "meta": file_b_result["meta"],
                "error": file_b_result["error"]
            },
            "diff": diff_result,
            "analysis": analysis_result.get("analysis", []),
            "summary": analysis_result.get("summary", {
                "total_issues": 0,
                "critical": 0,
                "major": 0,
                "minor": 0,
                "info": 0,
                "recommendation": "No analysis available"
            }),
            "meta": {
                "duration_seconds": round(duration, 2),
                "errors": []
            }
        }
        
        # Update task status
        update_task_status(self.request.id, "completed", result=final_result, db=session)
        logging.info(f"Task {self.request.id} completed successfully in {duration:.2f}s")
        return final_result
        
    except Exception as e:
        duration = time.time() - start_time
        error_result = {
            "task": "compare_files",
            "repo_a": {"raw_url": repo_a_raw_url, "fetched": False, "meta": {}, "error": str(e)},
            "repo_b": {"raw_url": repo_b_raw_url, "fetched": False, "meta": {}, "error": str(e)},
            "diff": {"unified_diff": "", "summary_lines_changed": {"added": 0, "removed": 0, "modified": 0}},
            "analysis": [],
            "summary": {
                "total_issues": 0,
                "critical": 0,
                "major": 0,
                "minor": 0,
                "info": 0,
                "recommendation": f"Error: {str(e)}"
            },
            "meta": {
                "duration_seconds": round(duration, 2),
                "errors": [str(e)]
            }
        }
        update_task_status(self.request.id, "failed", result=error_result, db=session)
        logging.error(f"Task {self.request.id} failed: {e}")
        raise
    finally:
        session.close()
