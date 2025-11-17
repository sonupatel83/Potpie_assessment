from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_pr():
    response = client.post("/analyze-pr", json={"content": "Test PR content"})
    assert response.status_code == 200
    assert "task_id" in response.json()


def test_task_status():
    task_id = "some-task-id"
    response = client.get(f"/task-status/{task_id}")
    assert response.status_code in [200, 404] 