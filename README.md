# README.md — Potpie Assessment     
Here are the snapshots of the output we obtained : 

1. Docker Containers :
![Alt text](https://image2url.com/images/1763417656593-dbf5ce98-eba7-4e4b-9c78-152837decb4a.png)

2. PR Analysis Snapshot :
![Alt text](https://image2url.com/images/1763416942855-a7867e8e-f058-47dd-84aa-05209b0e1f9b.png)

3. File Comparison Snapshot :

![Alt text](https://image2url.com/images/1763417848841-79e05791-828e-4159-b623-472b324af6e8.png)

4. Exposed Endpoints :
   ![Alt text](https://image2url.com/images/1763417964203-5e39cea1-e2a7-403f-9341-991a2e70f7d9.png)

```markdown
# Potpie Assessment
**Autonomous AI-Powered Code Review & File Comparison System**

Potpie is an end-to-end AI-driven system that analyzes GitHub Pull Requests and compares source files across repositories using local LLMs (via Ollama). It demonstrates production-level patterns for building robust, asynchronous AI agents for developer tooling.

---

## 🚀 Highlights
- LLM-based autonomous PR analysis (Gemma3 via Ollama)
- File comparison across repositories with unified diffs and LLM summaries
- Fully asynchronous processing using Celery + Redis
- Persistent results stored in Neon Postgres
- Local LLM inference via Ollama (Gemma3:4b)
- Containerized with Docker Compose for easy deployment
- Clean JSON outputs suitable for machine consumption or UIs

---

## ✅ Features
**PR Analysis**
- Fetches PR diff directly from GitHub
- Detects:
  - Bugs
  - Performance issues
  - Security concerns
  - Code style problems
  - Best-practices violations
- Returns structured JSON results with per-file issues and an overall summary

**File Comparison**
- Compares files from two repo raw URLs
- Produces:
  - Unified diff
  - File metadata & commit info
  - LLM-based comparison report
- Progress checkpoints:
  - starting → fetch_file_a → fetch_file_b → compute_diff → llm_analysis → completed

**Asynchronous Processing**
- Celery workers handle heavy operations (diffing, LLM calls, GitHub fetches)
- Redis (Redis Cloud) as broker & result backend
- Neon Postgres for persisting results & task metadata

**Local LLMs**
- Ollama used to run Gemma3 locally (or within a container)
- Automatic model bootstrapping (ollama-init container pulls model)

**Production Considerations**
- Docker Compose setup for easy local and small-scale deployments
- Retry logic, error handling, task status tracking
- Extensible agent design for multi-model / multi-language support

---

## 🛠 Environment Variables
Create a `.env` file in the project root. Example:

```env
########################################
# FASTAPI SETTINGS
########################################
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

########################################
# REDIS CLOUD (Broker + Result Backend)
########################################
REDIS_URL=redis://default:<PASSWORD>@redis-xxxxx.c15.us-east-1-4.ec2.cloud.redislabs.com:12132/0
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

########################################
# NEON POSTGRES
########################################
DATABASE_URL=postgresql+asyncpg://neondb_owner:<PASSWORD>@ep-xxxxx.aws.neon.tech/git-cr-pr?sslmode=require&channel_binding=require
SYNC_DB_URL=postgresql://neondb_owner:<PASSWORD>@ep-xxxxx.aws.neon.tech/git-cr-pr?sslmode=require&channel_binding=require

########################################
# OLLAMA
########################################
OLLAMA_API_URL=http://ollama:11434/api
OLLAMA_MODEL=gemma3:4b

````

## 🐳 Running with Docker Compose

Build and start all services:

```bash
docker compose up -d --build
```

This will start:

* FastAPI server (web)
* Celery worker(s)
* Ollama service (ollama container)
* Any helper containers (ollama-init to pull models)
* Connectivity to Redis Cloud & Neon Postgres (external services)

Create required DB tables:

```bash
docker compose run --rm web python scripts/create_tables.py
```

---

## 🔌 API Endpoints

All endpoints expose JSON and are available at `http://<HOST>:<PORT>` (defaults: `0.0.0.0:8000`).

### POST `/analyze-pr`

```bash
curl -X POST "http://localhost:8000/analyze-pr?repo_url=https://github.com/psf/requests&pr_number=1"
```

### POST `/compare-files`

Compare two files from raw repo URLs.


```bash
curl -X POST "http://localhost:8000/compare-files?repo_a_raw_url=<urlA>&repo_b_raw_url=<urlB>" -H "Content-Type: application/json" -d "{}"
```

### GET `/status/{task_id}`

Check task status.

```bash
curl http://localhost:8000/status/<task_id>
```

## 🧠 LLM / Agent Behavior

* Agents communicate with Ollama using `OLLAMA_API_URL` + `OLLAMA_MODEL`.
* The `pr_agent` extracts the diff, splits large files into chunks, and asks the model to classify and explain issues. Outputs are normalized into structured JSON.
* The file comparison agent computes diffs and asks the model for a comparison narrative and recommendations.

---

## 🧩 Async & Persistence

* Celery tasks are queued in Redis and results persisted to Redis (short-term) and Neon Postgres (long-term).
* Task states: `pending`, `processing`, `completed`, `failed`.
* Tasks include progress checkpoint updates for frontend-friendly streaming.

---

## 🧪 Tests

Run the included test:

```bash
docker compose exec web python test_compare_files.py
```

Or run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```
