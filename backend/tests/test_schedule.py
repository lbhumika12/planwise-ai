def test_generate_and_apply_schedule(client):
    # Seed 3 tasks
    t1 = client.post("/tasks", json={"title": "Urgent bugfix", "priority": "urgent", "estimated_duration": 60}).json()
    t2 = client.post("/tasks", json={"title": "Write documentation", "priority": "medium", "estimated_duration": 30}).json()
    t3 = client.post("/tasks", json={"title": "Team sync", "priority": "high", "estimated_duration": 30}).json()

    schedule_req = {
        "date": "2026-10-20",
        "timezone": "Asia/Kolkata",
        "start_time": "09:00",
        "end_time": "17:00",
        "break_duration": 15,
        "include_completed": False
    }

    plan_res = client.post("/schedule/plan", json=schedule_req)
    assert plan_res.status_code == 200
    plan = plan_res.json()
    assert plan["date"] == "2026-10-20"
    assert len(plan["scheduled_blocks"]) == 3
    # First task scheduled should be urgent
    assert plan["scheduled_blocks"][0]["priority"] == "urgent"

    # Verify blocks are strictly chronological and non-overlapping
    prev_end = None
    for block in plan["scheduled_blocks"]:
        start = block["start_time"]
        end = block["end_time"]
        assert start < end
        if prev_end:
            assert start >= prev_end
        prev_end = end

    # Apply the schedule
    apply_payload = {
        "date": "2026-10-20",
        "scheduled_blocks": plan["scheduled_blocks"]
    }
    apply_res = client.post("/schedule/apply", json=apply_payload)
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["total_applied"] == len(plan["scheduled_blocks"])

    # Verify task in DB has scheduled_start set
    task1_db = client.get(f"/tasks/{t1['id']}").json()
    assert task1_db["scheduled_start"] == f"2026-10-20 {plan['scheduled_blocks'][0]['start_time']}"


def test_schedule_insufficient_time_and_overdue(client):
    # Overdue task + long tasks
    t_overdue = client.post("/tasks", json={
        "title": "Overdue client deliverable",
        "priority": "high",
        "due_date": "2026-10-01",
        "estimated_duration": 45
    }).json()

    t_huge = client.post("/tasks", json={
        "title": "Full refactor",
        "priority": "medium",
        "estimated_duration": 180
    }).json()

    # Short 60-minute window
    schedule_req = {
        "date": "2026-10-20",
        "timezone": "Asia/Kolkata",
        "start_time": "10:00",
        "end_time": "11:00",
        "break_duration": 0,
        "include_completed": False
    }

    res = client.post("/schedule/plan", json=schedule_req)
    assert res.status_code == 200
    data = res.json()
    # Overdue task should fit in 45m and be scheduled first
    assert len(data["scheduled_blocks"]) == 1
    assert data["scheduled_blocks"][0]["task_id"] == t_overdue["id"]

    # 180m task could not fit
    assert len(data["unscheduled_tasks"]) >= 1
    assert any(t["id"] == t_huge["id"] for t in data["unscheduled_tasks"])
    assert len(data["warnings"]) > 0
