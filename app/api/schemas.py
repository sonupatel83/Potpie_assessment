from pydantic import HttpUrl, BaseModel


class PRRequest(BaseModel):
    content: str
    token: str = None

class PRResponse(BaseModel):
    task_id: str
    status: str

class AnalyzePRRequest(BaseModel):
    repo_url: HttpUrl
    pr_number: int


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str

class AnalysisResults(BaseModel):
    task_id: str
    status: str
    results: dict
