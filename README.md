# PlanWise AI — Your Day, Thoughtfully Planned

> **Amazon Developer Hackathon | Alexa+ Simulated Experience**  
> An intelligent conversational task manager and daily schedule planner that turns messy to-do lists into realistic, prioritized, conflict-free daily routines.

---

## 🌟 Overview

**PlanWise AI** is designed to address the reality of busy students and professionals: overwhelming task lists, constant priority juggling, and the friction of manual calendar planning. 

Rather than requiring users to manually calculate time slots or drag items onto a calendar, PlanWise AI offers an **Alexa+ simulated conversational experience**:
- Speak or type natural requests (*"Add an urgent report due tomorrow at 5pm"*, *"Plan my day from 9 AM to 6 PM"*, *"What should I focus on first?"*).
- An intelligent assistant parses dates, priorities, durations, and intents.
- A deterministic, mathematical scheduling algorithm scores tasks by urgency, deadline proximity, and duration, then builds chronological, non-overlapping time blocks with automated break buffers.
- If an external LLM is configured (Google Gemini, Anthropic Claude, or OpenAI), PlanWise AI elevates conversational nuance; if no API key is set, the system gracefully and transparently falls back to a deterministic rule-based engine (`ai_powered: false`).

---

## 🏗️ Architecture

```
PlanWise AI/
├── backend/
│   ├── app/
│   │   ├── config.py             # Environment & settings configuration
│   │   ├── database.py           # SQLite & SQLAlchemy engine
│   │   ├── models.py             # Task and AppSettings database models
│   │   ├── schemas.py            # Pydantic v2 validation models
│   │   ├── main.py               # FastAPI application entrypoint
│   │   ├── routers/
│   │   │   ├── tasks.py          # CRUD & dashboard statistics endpoints
│   │   │   ├── assistant.py      # Conversational AI & fallback router
│   │   │   ├── schedule.py       # Day planning & schedule application
│   │   │   └── settings.py       # User preferences & AI status
│   │   └── services/
│   │       ├── ai_service.py     # Multi-provider LLM caller (Gemini/OpenAI/Anthropic)
│   │       ├── intent_parser.py  # Rule-based intent & entity parser
│   │       ├── date_service.py   # Natural language date & time parsing
│   │       ├── task_service.py   # Task business logic & filtering
│   │       └── scheduling_service.py # Priority scoring & timeline allocation
│   ├── tests/                    # 18 automated pytest integration tests
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/           # Reusable UI components (Sidebar, Header, TaskCard, TaskForm, etc.)
    │   ├── pages/                # Overview, Tasks, MyDay, Assistant, Settings
    │   ├── services/api.js       # Centralized typed HTTP API service
    │   ├── utils/helpers.js      # Formatting, date utilities, priority helpers
    │   ├── App.jsx               # Navigation, layout shell, and theme provider
    │   └── main.jsx
    └── package.json
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **npm**

---

### Step 1: Set Up Backend

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run backend server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Health Endpoint:** `http://127.0.0.1:8000/health`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

---

### Step 2: Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

- Open your browser at `http://127.0.0.1:5173`.

---

## 🤖 AI Configuration (Optional)

PlanWise AI works **out of the box with zero external API keys** using its deterministic intent parser and local scheduling engine.

To enable multi-provider LLM responses, set your API key in `backend/.env`:

```env
# Choose one of: gemini | openai | anthropic
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🧪 Testing

### Backend Automated Tests
PlanWise AI includes 18 automated integration tests covering CRUD operations, filtering, schedule allocation, intent parsing, destructive action confirmation, and deterministic fallback:

```bash
cd backend
python -m pytest -v
```

### Frontend Build & Lint Verification
```bash
cd frontend
npm run lint
npm run build
```

---

## 🔒 Security & Data Privacy
- No hardcoded secrets, keys, or tokens exist in source code.
- `.env`, `.db`, `node_modules`, and build artifacts are strictly excluded via `.gitignore`.
- All user data and tasks persist locally in the SQLite database (`planwise.db`).

---

## 📜 License
MIT License. Built for the Amazon Developer Hackathon.
