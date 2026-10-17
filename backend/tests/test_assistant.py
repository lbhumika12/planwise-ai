from app.services.intent_parser import detect_intent, extract_duration, extract_priority


def test_intent_detection():
    assert detect_intent("Add a task to submit the assignment tomorrow") == "create_task"
    assert detect_intent("Remind me to buy groceries") == "create_task"
    assert detect_intent("Plan my day today") == "generate_schedule"
    assert detect_intent("What is on my schedule for today?") == "list_tasks"
    assert detect_intent("Mark finish project as done") == "complete_task"
    assert detect_intent("Delete task test") == "delete_task"


def test_slot_extraction():
    assert extract_priority("This is urgent: deploy fix") == "urgent"
    assert extract_priority("Low priority read book") == "low"
    assert extract_duration("Study for 45 minutes") == 45
    assert extract_duration("Work on project for 2 hours") == 120


def test_assistant_chat_deterministic_create_task(client, monkeypatch):
    """Test deterministic rule-based assistant creating a task."""
    from app.routers import assistant
    monkeypatch.setattr(
        assistant,
        "get_ai_status",
        lambda: {"available": False, "provider": None, "mode": "rule_based"}
    )

    res = client.post("/assistant/chat", json={
        "message": "Add a task to buy groceries tomorrow at 5pm",
        "timezone": "Asia/Kolkata"
    })
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert "✓ Task created" in data["message"]
    assert data["intent"] == "create_task"
    assert data["ai_powered"] is False

    # Verify task was created in DB
    tasks_res = client.get("/tasks?search=groceries")
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()["tasks"]) >= 1


def test_assistant_chat_ai_action_create_task(client, monkeypatch):
    """Test AI response action processing to create a task."""
    from app.routers import assistant

    async def mock_call_ai(*args, **kwargs):
        return {
            "message": "I have created your task.",
            "intent": "create_task",
            "action": {
                "action_type": "create_task",
                "task_data": {
                    "title": "Buy groceries",
                    "due_date": "2026-10-18",
                    "due_time": "17:00",
                    "priority": "medium"
                }
            },
            "suggested_prompts": ["Show tasks", "Plan day"]
        }

    monkeypatch.setattr(assistant, "get_ai_status", lambda: {"available": True, "provider": "gemini", "mode": "llm"})
    monkeypatch.setattr(assistant, "call_ai", mock_call_ai)

    res = client.post("/assistant/chat", json={
        "message": "Add a task to buy groceries tomorrow at 5pm",
        "timezone": "Asia/Kolkata"
    })
    assert res.status_code == 200
    data = res.json()
    assert "✓ Task created" in data["message"]
    assert data["ai_powered"] is True
    tasks_res = client.get("/tasks?search=groceries")
    assert tasks_res.status_code == 200
    assert len(tasks_res.json()["tasks"]) >= 1


def test_assistant_chat_status_request(client, monkeypatch):
    from app.routers import assistant
    monkeypatch.setattr(
        assistant,
        "get_ai_status",
        lambda: {"available": False, "provider": None, "mode": "rule_based"}
    )

    # Add a task first
    client.post("/tasks", json={"title": "Team Standup", "priority": "high"})

    res = client.post("/assistant/chat", json={
        "message": "What do I have to do?",
        "timezone": "Asia/Kolkata"
    })
    assert res.status_code == 200
    data = res.json()
    assert "message" in data
    assert "Team Standup" in data["message"] or data["intent"] in ["list_tasks", "general"]
    assert data["ai_powered"] is False


def test_assistant_destructive_action_confirmation(client, monkeypatch):
    """Verify destructive actions require confirmation."""
    from app.routers import assistant
    monkeypatch.setattr(
        assistant,
        "get_ai_status",
        lambda: {"available": False, "provider": None, "mode": "rule_based"}
    )

    # Seed a task
    t = client.post("/tasks", json={"title": "Important Document", "priority": "high"}).json()

    # Request to delete the task
    res = client.post("/assistant/chat", json={
        "message": f"Delete task {t['title']}",
        "timezone": "Asia/Kolkata"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action_card"] is not None
    assert data["action_card"]["action_type"] == "delete_task"
    assert data["action_card"]["requires_confirmation"] is True
    assert "Are you sure" in data["message"]

    # Verify task was NOT deleted silently
    check_task = client.get(f"/tasks/{t['id']}")
    assert check_task.status_code == 200


def test_assistant_ambiguous_task_resolution(client, monkeypatch):
    """Test ambiguous task names return candidate list."""
    from app.routers import assistant
    monkeypatch.setattr(
        assistant,
        "get_ai_status",
        lambda: {"available": False, "provider": None, "mode": "rule_based"}
    )

    client.post("/tasks", json={"title": "Submit Physics Homework", "priority": "high"})
    client.post("/tasks", json={"title": "Submit Chemistry Homework", "priority": "medium"})

    res = client.post("/assistant/chat", json={
        "message": "Mark Submit as done",
        "timezone": "Asia/Kolkata"
    })
    assert res.status_code == 200
    data = res.json()
    assert "found" in data["message"] and "Which one" in data["message"]
    assert data["tasks"] is not None
    assert len(data["tasks"]) == 2
