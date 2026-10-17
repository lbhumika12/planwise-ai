def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "PlanWise AI"
    assert "ai_available" in data


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "PlanWise AI API" in data["message"]


def test_get_and_update_settings(client):
    # GET default settings
    response = client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["timezone"] == "Asia/Kolkata"
    assert data["default_start_time"] == "09:00"

    # PATCH settings
    update_payload = {
        "preferred_name": "Antigravity User",
        "default_start_time": "08:30",
        "default_end_time": "20:00",
        "theme": "dark"
    }
    patch_res = client.patch("/settings", json=update_payload)
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["preferred_name"] == "Antigravity User"
    assert updated_data["default_start_time"] == "08:30"
    assert updated_data["theme"] == "dark"


def test_ai_status(client):
    response = client.get("/settings/ai-status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "mode" in data
