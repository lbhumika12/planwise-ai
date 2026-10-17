def test_create_and_get_task(client):
    payload = {
        "title": "Complete AI report",
        "description": "Write analysis of task prioritisation",
        "category": "Work",
        "priority": "high",
        "due_date": "2026-10-20",
        "due_time": "17:00",
        "estimated_duration": 45,
        "tags": ["report", "ai"]
    }
    res = client.post("/tasks", json=payload)
    assert res.status_code == 201
    task = res.json()
    assert task["id"] is not None
    assert task["title"] == "Complete AI report"
    assert task["priority"] == "high"
    assert task["status"] == "todo"
    assert "report" in task["tags"] and "ai" in task["tags"]
    assert task["estimated_duration"] == 45


    # Get single task
    get_res = client.get(f"/tasks/{task['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Complete AI report"


def test_task_filtering_and_sorting(client):
    # Create multiple tasks
    client.post("/tasks", json={"title": "High task", "priority": "high", "category": "Work"})
    client.post("/tasks", json={"title": "Low task", "priority": "low", "category": "Personal"})
    client.post("/tasks", json={"title": "Urgent task", "priority": "urgent", "category": "Work"})

    # Filter by priority
    res = client.get("/tasks?priority=urgent")
    assert res.status_code == 200
    tasks = res.json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Urgent task"

    # Filter by search
    res_search = client.get("/tasks?search=Personal")
    assert res_search.status_code == 200
    tasks_search = res_search.json()["tasks"]
    assert len(tasks_search) == 1
    assert tasks_search[0]["title"] == "Low task"


def test_task_lifecycle_and_update(client):
    res = client.post("/tasks", json={"title": "Review PR", "priority": "medium"})
    task_id = res.json()["id"]

    # Update task
    update_res = client.patch(f"/tasks/{task_id}", json={"title": "Review PR and Merge", "priority": "urgent"})
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Review PR and Merge"
    assert update_res.json()["priority"] == "urgent"

    # Complete task
    comp_res = client.patch(f"/tasks/{task_id}/complete")
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "completed"
    assert comp_res.json()["completed_at"] is not None

    # Reopen task
    reopen_res = client.patch(f"/tasks/{task_id}/reopen")
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "todo"

    # Delete task
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    # 404 on deleted task
    not_found = client.get(f"/tasks/{task_id}")
    assert not_found.status_code == 404


def test_task_validation_errors(client):
    # Empty title
    res_empty = client.post("/tasks", json={"title": ""})
    assert res_empty.status_code == 422

    # Invalid priority
    res_priority = client.post("/tasks", json={"title": "Valid title", "priority": "super-urgent"})
    assert res_priority.status_code == 422

    # Negative duration
    res_dur = client.post("/tasks", json={"title": "Valid title", "estimated_duration": -10})
    assert res_dur.status_code == 422

    # 404 on non-existent task ID
    assert client.get("/tasks/99999").status_code == 404
    assert client.patch("/tasks/99999", json={"title": "Updated"}).status_code == 404
    assert client.delete("/tasks/99999").status_code == 404



def test_dashboard_and_demo_seed(client):
    # Seed demo data
    seed_res = client.post("/tasks/demo/seed?timezone=Asia/Kolkata")
    assert seed_res.status_code == 201
    assert seed_res.json()["count"] > 0

    # Check dashboard stats
    dash_res = client.get("/tasks/dashboard?timezone=Asia/Kolkata")
    assert dash_res.status_code == 200
    stats = dash_res.json()
    assert stats["total_tasks"] > 0
    assert "high_priority_pending" in stats
    assert "due_today" in stats
    assert "completion_rate" in stats


    # Clear demo data
    clear_res = client.delete("/tasks/demo/clear")
    assert clear_res.status_code == 200
    assert clear_res.json()["count"] > 0
