"""
SetuX / VeriX — Analytics & Project Intelligence API Tests
Phase 10: Complete Test Suite for Database-Derived Analytics
"""
import pytest


def _seed_sample_project_data(client, officer_token):
    """Seed project, milestones, progress updates, and issues for analytics testing."""
    headers = {"Authorization": f"Bearer {officer_token}"}

    # 1. Create Project 1 (Road sector, Pune, cost overrun)
    p1 = client.post(
        "/api/projects/",
        json={
            "name": "Pune Highway Expansion",
            "sector": "Road Construction",
            "district": "Pune",
            "department_name": "Public Works Department",
            "original_cost": 1000.0,
            "revised_cost": 1250.0,
            "total_expenditure": 600.0,
            "start_date": "2026-01-01",
            "planned_completion_date": "2026-06-30",
            "physical_progress": 50.0,
            "financial_progress": 48.0,
            "status": "Under Review",
        },
        headers=headers,
    ).json()

    # Add historical progress updates for P1
    resp_pr1 = client.post(
        f"/api/projects/{p1['id']}/progress",
        json={"report_date": "2026-02-01", "physical_progress": 20.0, "financial_progress": 15.0, "expenditure": 200.0, "remarks": "Phase 1 complete"},
        headers=headers,
    )
    assert resp_pr1.status_code == 201, f"Progress update 1 failed: {resp_pr1.text}"

    resp_pr2 = client.post(
        f"/api/projects/{p1['id']}/progress",
        json={"report_date": "2026-03-01", "physical_progress": 50.0, "financial_progress": 48.0, "expenditure": 600.0, "remarks": "Phase 2 complete"},
        headers=headers,
    )
    assert resp_pr2.status_code == 201, f"Progress update 2 failed: {resp_pr2.text}"

    # Add milestones for P1
    resp_m1 = client.post(
        f"/api/projects/{p1['id']}/milestones",
        json={"name": "Land Acquisition", "planned_date": "2026-02-15", "actual_date": "2026-02-15", "status": "COMPLETED", "completion_percentage": 100.0},
        headers=headers,
    )
    assert resp_m1.status_code == 201, f"Milestone 1 failed: {resp_m1.text}"

    resp_m2 = client.post(
        f"/api/projects/{p1['id']}/milestones",
        json={"name": "Subgrade Compaction", "planned_date": "2026-03-01", "status": "DELAYED", "completion_percentage": 30.0},
        headers=headers,
    )
    assert resp_m2.status_code == 201, f"Milestone 2 failed: {resp_m2.text}"

    # Add issues for P1
    resp_i1 = client.post(
        f"/api/projects/{p1['id']}/issues",
        json={"title": "Bitumen Shortage", "description": "Supply delay from refiner.", "severity": "CRITICAL"},
        headers=headers,
    )
    assert resp_i1.status_code == 201, f"Issue creation failed: {resp_i1.text}"


    # 2. Create Project 2 (Bridge sector, Nagpur, completed)
    p2 = client.post(
        "/api/projects/",
        json={
            "name": "Nagpur Flyover",
            "sector": "Bridge Construction",
            "district": "Nagpur",
            "department_name": "Public Works Department",
            "original_cost": 800.0,
            "total_expenditure": 780.0,
            "start_date": "2026-01-01",
            "planned_completion_date": "2026-08-31",
            "physical_progress": 100.0,
            "financial_progress": 97.5,
            "status": "Completed",
        },
        headers=headers,
    ).json()

    return p1, p2


def test_analytics_overview_empty_and_populated(client, officer_token):
    """Test GET /api/analytics/overview handling both empty and populated states safely."""
    # 1. Overview on empty DB
    resp_empty = client.get("/api/analytics/overview")
    assert resp_empty.status_code == 200
    empty_data = resp_empty.json()
    assert "total_projects" in empty_data

    # 2. Populate data and test again
    _seed_sample_project_data(client, officer_token)
    resp = client.get("/api/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_projects"] >= 2
    assert data["total_original_cost"] >= 1800.0
    assert data["total_revised_cost"] >= 2050.0
    assert data["average_physical_progress"] > 0
    assert data["total_open_issues"] >= 1


def test_analytics_projects_and_filtering(client, officer_token):
    """Test GET /api/analytics/projects with sector, district, and status filters."""
    p1, p2 = _seed_sample_project_data(client, officer_token)

    # Filter by sector=Road Construction
    resp_sector = client.get("/api/analytics/projects?sector=Road Construction")
    assert resp_sector.status_code == 200
    road_projs = resp_sector.json()
    assert any(p["project_code"] == p1["project_code"] for p in road_projs)
    assert not any(p["project_code"] == p2["project_code"] for p in road_projs)

    # Filter by district=Nagpur
    resp_dist = client.get("/api/analytics/projects?district=Nagpur")
    assert resp_dist.status_code == 200
    nagpur_projs = resp_dist.json()
    assert any(p["project_code"] == p2["project_code"] for p in nagpur_projs)


def test_analytics_cost(client, officer_token):
    """Test GET /api/analytics/cost metrics calculation."""
    _seed_sample_project_data(client, officer_token)

    resp = client.get("/api/analytics/cost")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_original_cost"] >= 1800.0
    assert data["total_revised_cost"] >= 2050.0
    assert data["projects_with_cost_increase"] >= 1
    assert "cost_health_breakdown" in data


def test_analytics_progress(client, officer_token):
    """Test GET /api/analytics/progress metrics and gaps."""
    _seed_sample_project_data(client, officer_token)

    resp = client.get("/api/analytics/progress")
    assert resp.status_code == 200
    data = resp.json()

    assert data["average_physical_progress"] > 0
    assert "physical_vs_financial_gap" in data
    assert data["total_historical_updates"] >= 2


def test_analytics_milestones(client, officer_token):
    """Test GET /api/analytics/milestones status aggregations."""
    _seed_sample_project_data(client, officer_token)

    resp = client.get("/api/analytics/milestones")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_milestones"] >= 2
    assert data["completed_milestones"] >= 1
    assert data["delayed_milestones"] >= 1
    assert data["milestone_completion_percentage"] > 0


def test_analytics_issues(client, officer_token):
    """Test GET /api/analytics/issues breakdown."""
    _seed_sample_project_data(client, officer_token)

    resp = client.get("/api/analytics/issues")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_issues"] >= 1
    assert data["critical_issues"] >= 1
    assert data["projects_with_unresolved_critical_issues"] >= 1


def test_analytics_departments_and_sectors(client, officer_token):
    """Test department and sector breakdown endpoints."""
    _seed_sample_project_data(client, officer_token)

    # Departments
    resp_dept = client.get("/api/analytics/departments")
    assert resp_dept.status_code == 200
    depts = resp_dept.json()
    assert isinstance(depts, list)

    # Sectors
    resp_sec = client.get("/api/analytics/sectors")
    assert resp_sec.status_code == 200
    sectors = resp_sec.json()
    assert isinstance(sectors, list)
    assert any(s["sector"] == "Road Construction" for s in sectors)


def test_progress_trend(client, officer_token):
    """Test project progress trend chronological listing."""
    p1, _ = _seed_sample_project_data(client, officer_token)

    resp = client.get(f"/api/analytics/projects/{p1['id']}/progress-trend")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_reports_count"] == 2
    assert data["latest_physical_progress"] == 50.0
    assert len(data["timeline"]) == 2


def test_project_intelligence(client, officer_token):
    """Test project intelligence deterministic summary endpoint."""
    p1, _ = _seed_sample_project_data(client, officer_token)

    # Via /api/projects/{id}/intelligence
    resp1 = client.get(f"/api/projects/{p1['id']}/intelligence")
    assert resp1.status_code == 200
    intel = resp1.json()

    assert intel["project_code"] == p1["project_code"]
    assert intel["cost"]["overrun_percentage"] == 25.0
    assert intel["issues"]["critical"] == 1
    assert len(intel["observations"]) >= 2
    assert any("Cost overrun" in obs for obs in intel["observations"])

    # Via /api/analytics/projects/{id}/intelligence
    resp2 = client.get(f"/api/analytics/projects/{p1['id']}/intelligence")
    assert resp2.status_code == 200
    assert resp2.json()["project_code"] == p1["project_code"]
