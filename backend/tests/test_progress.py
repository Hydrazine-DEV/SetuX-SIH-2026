"""
SetuX / VeriX — Historical Progress Tracking Tests
Verifies:
- Creation of progress updates (Officer authorized)
- Citizen access blocked (403)
- Invalid project handling (404)
- Physical & Financial progress percentage validation (0 - 100%)
- Non-negative expenditure validation
- Date formatting validation (YYYY-MM-DD)
- Immutability of history: multiple updates do not overwrite past records
- Chronological ordering of history
- Latest progress endpoint
- Project progress synchronization (current values match latest update while history is preserved)
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def progress_project(client: TestClient, officer_token):
    res_check = client.get("/api/projects/MH-NSK-BR-01")
    if res_check.status_code == 200:
        return "MH-NSK-BR-01"

    res = client.post(
        "/api/projects",
        json={
            "name": "Nashik Bridge Construction",
            "project_code": "MH-NSK-BR-01",
            "district": "Nashik",
            "sector": "Bridges",
            "original_cost": 850.0,
            "planned_completion_date": "2027-01-31",
            "physical_progress": 0.0,
            "financial_progress": 0.0,
            "total_expenditure": 0.0,
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code in (200, 201)
    return "MH-NSK-BR-01"


def test_create_progress_rbac(client: TestClient, progress_project, officer_token, citizen_token):
    payload = {
        "report_date": "2026-08-01",
        "physical_progress": 10.0,
        "financial_progress": 8.5,
        "expenditure": 72.25,
        "remarks": "Initial foundation concrete poured",
    }

    # 1. Citizen cannot submit progress
    res_cit = client.post(
        f"/api/projects/{progress_project}/progress",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer submits progress
    res_off = client.post(
        f"/api/projects/{progress_project}/progress",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 201
    data = res_off.json()
    assert data["physical_progress"] == 10.0
    assert data["financial_progress"] == 8.5
    assert data["expenditure"] == 72.25
    assert data["reported_by"] is not None


def test_progress_validation(client: TestClient, progress_project, officer_token):
    # 1. Invalid physical_progress (> 100)
    res = client.post(
        f"/api/projects/{progress_project}/progress",
        json={"report_date": "2026-08-01", "physical_progress": 120.0, "financial_progress": 50.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code in (400, 422)

    # 2. Invalid expenditure (negative)
    res = client.post(
        f"/api/projects/{progress_project}/progress",
        json={"report_date": "2026-08-01", "physical_progress": 50.0, "financial_progress": 50.0, "expenditure": -10.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code in (400, 422)

    # 3. Invalid date format
    res = client.post(
        f"/api/projects/{progress_project}/progress",
        json={"report_date": "01/08/2026", "physical_progress": 50.0, "financial_progress": 50.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code in (400, 422)

    # 4. Project not found
    res = client.post(
        "/api/projects/NON-EXISTENT-PROJ/progress",
        json={"report_date": "2026-08-01", "physical_progress": 50.0, "financial_progress": 50.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 404


def test_multiple_historical_updates_and_project_sync(client: TestClient, officer_token):
    """
    Test historical updates immutability:
    01 Jan -> 10%
    01 Feb -> 22%
    01 Mar -> 35%
    01 Apr -> 45%
    All four records must remain in history, and Project's current progress must sync to 45%.
    """
    proj_res = client.post(
        "/api/projects",
        json={
            "name": "Timeline Sync Project",
            "project_code": "MH-SYNC-PROJ-01",
            "district": "Nashik",
            "sector": "Bridges",
            "original_cost": 850.0,
            "planned_completion_date": "2027-01-31",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert proj_res.status_code in (200, 201)
    sync_proj = "MH-SYNC-PROJ-01"

    timeline = [
        {"report_date": "2026-01-01", "physical_progress": 10.0, "financial_progress": 8.0, "expenditure": 68.0, "remarks": "Jan Update"},
        {"report_date": "2026-02-01", "physical_progress": 22.0, "financial_progress": 18.0, "expenditure": 153.0, "remarks": "Feb Update"},
        {"report_date": "2026-03-01", "physical_progress": 35.0, "financial_progress": 30.0, "expenditure": 255.0, "remarks": "Mar Update"},
        {"report_date": "2026-04-01", "physical_progress": 45.0, "financial_progress": 40.0, "expenditure": 340.0, "remarks": "Apr Update"},
    ]

    for item in timeline:
        res = client.post(
            f"/api/projects/{sync_proj}/progress",
            json=item,
            headers={"Authorization": f"Bearer {officer_token}"},
        )
        assert res.status_code == 201

    # 1. Retrieve full history
    history_res = client.get(f"/api/projects/{sync_proj}/progress")
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) == 4, "All 4 historical updates must be preserved"
    dates = [h["report_date"] for h in history]
    assert dates == ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]

    # 2. Retrieve latest progress
    latest_res = client.get(f"/api/projects/{sync_proj}/progress/latest")
    assert latest_res.status_code == 200
    latest = latest_res.json()
    assert latest["physical_progress"] == 45.0
    assert latest["report_date"] == "2026-04-01"

    # 3. Verify Project's current progress was synchronized
    proj_get = client.get(f"/api/projects/{sync_proj}")
    assert proj_get.status_code == 200
    proj = proj_get.json()
    assert proj["physical_progress"] == 45.0
    assert proj["reported_progress"] == 45
    assert proj["financial_progress"] == 40.0
    assert proj["total_expenditure"] == 340.0
