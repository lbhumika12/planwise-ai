# PlanWise AI — Backend Service

FastAPI-powered REST API backend with persistent SQLite storage, deterministic daily scheduling, and multi-provider AI integration.

## Features
- **FastAPI Framework**: High-performance asynchronous endpoints with automatic OpenAPI/Swagger documentation.
- **SQLAlchemy with SQLite**: Persistent relational storage (`planwise.db`) with Write-Ahead Logging (WAL) enabled.
- **Task Management**: Full CRUD, category filtering, search, pagination, and completion tracking.
- **Smart Scheduling Engine**: Scores tasks based on urgency, deadline proximity, duration, and status, and produces non-overlapping chronological schedule blocks.
- **Conversational Assistant**: Rule-based fallback parser with support for Google Gemini, Anthropic Claude, and OpenAI GPT models.
- **Automated Tests**: 18 comprehensive pytest integration test cases.

## Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env

# 3. Start server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Running Tests
```bash
python -m pytest -v
```

## API Endpoints
- `GET /health` — Service health and active AI status
- `GET /docs` — Swagger UI API documentation
- `GET /tasks` — List tasks with filters (search, priority, category, status)
- `POST /tasks` — Create new task
- `PATCH /tasks/{id}` — Update task
- `PATCH /tasks/{id}/complete` — Mark task completed
- `DELETE /tasks/{id}` — Delete task
- `GET /tasks/dashboard` — Live dashboard metrics
- `POST /schedule/plan` — Generate proposed schedule
- `POST /schedule/apply` — Persist schedule to tasks
- `POST /assistant/chat` — Conversational assistant interaction
- `GET /settings` — Application preferences
