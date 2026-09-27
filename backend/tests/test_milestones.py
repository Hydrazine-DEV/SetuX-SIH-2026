"""
SetuX / VeriX — Milestones API Tests
Verifies:
- Milestone creation (Officer authorized)
- Non-officer blocked from creating/updating/deleting (403)
- Invalid project handling (404)
- Completion percentage validation (0 - 100%)
- Status validation (PENDING, IN_PROGRESS, COMPLETED, DELAYED, NOT_STARTED)
- Date validation (YYYY-MM-DD)
- List milestones for project
- Get milestone by ID
- Update milestone
- Delete milestone
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def target_project(client: TestClient, officer_token):
    res_check = client.get("/api/projects/MH-NAG-METRO-03")
    if res_check.status_code == 200:
        return "MH-NAG-METRO-03"

    res = client.post(
        "/api/projects",
        json={
            "name": "Nagpur Metro Reach 3 Extension",
            "project_code": "MH-NAG-METRO-03",
            "district": "Nagpur",
            "sector": "Urban Infrastructure",
            "original_cost": 12500.0,
            "planned_completion_date": "2027-06-30",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code in (200, 201)
    return "MH-NAG-METRO-03"


def test_create_milestone_rbac(client: TestClient, target_project, officer_token, citizen_token):
    payload = {
        "name": "Piling & Substructure Work",
        "description": "Foundations for 18 viaduct piers",
        "planned_date": "2026-11-30",
        "status": "PENDING",
        "completion_percentage": 0.0,
    }

    # 1. Citizen cannot create (403)
    res_cit = client.post(
        f"/api/projects/{target_project}/milestones",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer creates milestone (201)
    res_off = client.post(
        f"/api/projects/{target_project}/milestones",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 201
    data = res_off.json()
    assert data["name"] == payload["name"]
    assert data["planned_date"] == "2026-11-30"
    assert data["completion_percentage"] == 0.0
    assert "is_delayed" in data
    assert "delay_days" in data


def test_milestone_invalid_project(client: TestClient, officer_token):
    res = client.post(
        "/api/projects/NON-EXISTENT-PROJ/milestones",
        json={"name": "Test Milestone", "planned_date": "2026-12-31"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 404


def test_milestone_validation(client: TestClient, target_project, officer_token):
    # 1. Invalid completion percentage (> 100)
    res_pct = client.post(
        f"/api/projects/{target_project}/milestones",
        json={"name": "Bad Pct", "planned_date": "2026-12-31", "completion_percentage": 150.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_pct.status_code in (400, 422)

    # 2. Invalid date format
    res_date = client.post(
        f"/api/projects/{target_project}/milestones",
        json={"name": "Bad Date", "planned_date": "31-12-2026"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_date.status_code in (400, 422)

    # 3. Invalid status
    res_status = client.post(
        f"/api/projects/{target_project}/milestones",
        json={"name": "Bad Status", "planned_date": "2026-12-31", "status": "INVALID_STATUS"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_status.status_code in (400, 422)


def test_list_get_update_delete_milestone(client: TestClient, target_project, officer_token, citizen_token):
    # Create milestone
    res = client.post(
        f"/api/projects/{target_project}/milestones",
        json={"name": "Viaduct Girder Launching", "planned_date": "2026-12-31", "status": "IN_PROGRESS", "completion_percentage": 40.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 201
    m_id = res.json()["id"]

    # 1. List milestones
    list_res = client.get(f"/api/projects/{target_project}/milestones")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 2. Get milestone by ID
    get_res = client.get(f"/api/milestones/{m_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Viaduct Girder Launching"

    # 3. Citizen cannot update
    upd_cit = client.put(
        f"/api/milestones/{m_id}",
        json={"completion_percentage": 80.0},
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert upd_cit.status_code == 403

    # 4. Officer updates milestone to COMPLETED
    upd_off = client.put(
        f"/api/milestones/{m_id}",
        json={"status": "COMPLETED", "completion_percentage": 100.0, "actual_date": "2026-12-15"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert upd_off.status_code == 200
    upd_data = upd_off.json()
    assert upd_data["status"] == "COMPLETED"
    assert upd_data["actual_date"] == "2026-12-15"
    assert upd_data["completion_percentage"] == 100.0

    # 5. Citizen cannot delete
    del_cit = client.delete(
        f"/api/milestones/{m_id}",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert del_cit.status_code == 403

    # 6. Officer deletes milestone
    del_off = client.delete(
        f"/api/milestones/{m_id}",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert del_off.status_code == 200
    assert del_off.json()["success"] is True

    # 7. Verify 404
    assert client.get(f"/api/milestones/{m_id}").status_code == 404
