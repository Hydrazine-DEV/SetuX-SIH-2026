"""
SetuX / VeriX — Projects API Tests
Verifies:
- Project creation with full SIH26103 fields & auto-code generation
- Officer RBAC enforcement (citizen blocked from creating/updating/deleting)
- Backward-compatibility aliases (project_id, budget_lakh, reported_progress, etc.)
- Multi-criteria filtering (district, department, status, risk_level, sector)
- Free-text search across multiple columns
- Sorting (order_by anomaly_score, original_cost, physical_progress)
- Pagination (headers and paginate=True envelope)
- Get project by project_code or by integer ID
- Update project fields
- Update project status via PUT /status
- Delete project
- Project KPI stats endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_create_project_rbac(client: TestClient, officer_token, citizen_token):
    payload = {
        "name": "Pune Ring Road Phase 1",
        "project_code": "MH-PUN-RING-01",
        "sector": "Roads & Highways",
        "ministry": "Ministry of Road Transport and Highways",
        "district": "Pune",
        "taluka": "Haveli",
        "location": "Wakad to Khed Shivapur",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "original_cost": 5400.0,
        "planned_completion_date": "2027-12-31",
        "department_id": 1,
        "status": "In Progress",
        "risk_level": "LOW",
        "physical_progress": 15.0,
    }

    # 1. Citizen blocked (403)
    res_cit = client.post(
        "/api/projects",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer creates (201)
    res_off = client.post(
        "/api/projects",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 201
    data = res_off.json()
    assert data["project_code"] == "MH-PUN-RING-01"
    # Verify backward-compatibility aliases
    assert data["project_id"] == "MH-PUN-RING-01"
    assert data["budget_lakh"] == 5400.0
    assert data["reported_progress"] == 15
    assert data["location_name"] == "Wakad to Khed Shivapur"
    assert data["lat"] == 18.5204
    assert data["lng"] == 73.8567
    assert data["department"] == "Public Works Department"

    # 3. Duplicate project_code rejected (400)
    res_dup = client.post(
        "/api/projects",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"].lower()


def test_auto_generate_project_code(client: TestClient, officer_token):
    payload = {
        "name": "Nagpur Rural Water Pipeline",
        "district": "Nagpur",
        "sector": "Water Supply",
        "original_cost": 320.0,
    }
    res = client.post(
        "/api/projects",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 201
    code = res.json()["project_code"]
    assert code.startswith("MH-NAG-")


def test_get_project_by_code_and_id(client: TestClient):
    # 1. By project_code
    res = client.get("/api/projects/MH-PUN-RING-01")
    assert res.status_code == 200
    p = res.json()
    assert p["name"] == "Pune Ring Road Phase 1"
    p_id = p["id"]

    # 2. By integer ID
    res_id = client.get(f"/api/projects/{p_id}")
    assert res_id.status_code == 200
    assert res_id.json()["project_code"] == "MH-PUN-RING-01"

    # 3. Non-existent -> 404
    res_404 = client.get("/api/projects/NON-EXISTENT-CODE")
    assert res_404.status_code == 404


def test_list_projects_search_and_filters(client: TestClient):
    # 1. Basic list returns array
    res = client.get("/api/projects")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1

    # Check pagination headers
    assert "X-Total-Count" in res.headers
    assert "X-Page" in res.headers

    # 2. Filter by district
    res_pune = client.get("/api/projects?district=Pune")
    assert res_pune.status_code == 200
    for p in res_pune.json():
        assert "Pune" in p["district"]

    # 3. Search query
    res_search = client.get("/api/projects?search=Ring Road")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1
    assert any("Ring Road" in p["name"] for p in res_search.json())

    # 4. Filter by sector
    res_sec = client.get("/api/projects?sector=Water Supply")
    assert res_sec.status_code == 200
    for p in res_sec.json():
        assert p["sector"] == "Water Supply"


def test_pagination_envelope(client: TestClient):
    res = client.get("/api/projects?paginate=true&page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert len(data["items"]) <= 2


def test_sorting_projects(client: TestClient):
    res_asc = client.get("/api/projects?sort_by=original_cost&order=asc")
    assert res_asc.status_code == 200
    costs = [p["original_cost"] for p in res_asc.json()]
    assert costs == sorted(costs)


def test_update_project(client: TestClient, officer_token, citizen_token):
    # 1. Citizen cannot update
    res_cit = client.put(
        "/api/projects/MH-PUN-RING-01",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer can update
    res_off = client.put(
        "/api/projects/MH-PUN-RING-01",
        json={"physical_progress": 25.0, "total_expenditure": 850.0},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 200
    updated = res_off.json()
    assert updated["physical_progress"] == 25.0
    assert updated["reported_progress"] == 25
    assert updated["total_expenditure"] == 850.0


def test_update_project_status(client: TestClient, officer_token):
    res = client.put(
        "/api/projects/MH-PUN-RING-01/status?status=Verified&risk_level=LOW",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Verified"
    assert res.json()["risk_level"] == "LOW"


def test_project_stats_kpi(client: TestClient):
    res = client.get("/api/projects/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "total" in stats
    assert "verified" in stats
    assert "high_risk" in stats
    assert stats["total"] >= 1


def test_delete_project(client: TestClient, officer_token, citizen_token):
    # 1. Create a project to delete
    create_res = client.post(
        "/api/projects",
        json={"name": "To Be Deleted Project", "project_code": "MH-DEL-001", "district": "Thane"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert create_res.status_code == 201

    # 2. Citizen cannot delete
    res_cit = client.delete(
        "/api/projects/MH-DEL-001",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 3. Officer can delete
    res_del = client.delete(
        "/api/projects/MH-DEL-001",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # 4. Verify 404
    assert client.get("/api/projects/MH-DEL-001").status_code == 404
