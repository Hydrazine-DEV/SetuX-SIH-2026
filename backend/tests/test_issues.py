"""
Tests for SetuX Issues API — Phase 8
Covers: RBAC enforcement, CRUD lifecycle, severity/status filtering, auto-resolved_date.
"""
import pytest


# ─── Helpers ────────────────────────────────────────────────────
def _create_project(client, officer_token):
    """Seed a project for issue testing."""
    resp = client.post(
        "/api/projects/",
        json={
            "name": "Issue Test Project",
            "sector": "Road Construction",
            "district": "Pune",
            "location": "Shivajinagar, Pune",
            "original_cost": 500.0,
            "start_date": "2026-01-01",
            "planned_completion_date": "2026-12-31",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp.status_code in (200, 201), f"Project creation failed: {resp.text}"
    return resp.json()


# ─── Test: RBAC — Citizens cannot create issues ────────────────
def test_create_issue_rbac(client, officer_token, citizen_token):
    """Officers can create issues; citizens should be rejected."""
    project = _create_project(client, officer_token)
    project_id = project["id"]

    # Citizen attempt → 403
    resp_citizen = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "Citizen-reported pothole",
            "description": "Large pothole near km 5 marker on approach road.",
            "severity": "HIGH",
        },
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert resp_citizen.status_code == 403

    # Officer attempt → 201
    resp_officer = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "Material quality concern",
            "description": "Bitumen grade lower than specification at km 3.",
            "severity": "CRITICAL",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert resp_officer.status_code == 201
    data = resp_officer.json()
    assert data["title"] == "Material quality concern"
    assert data["severity"] == "CRITICAL"
    assert data["status"] == "OPEN"
    assert data["project_id"] == project_id


# ─── Test: Full CRUD lifecycle ──────────────────────────────────
def test_issue_crud_lifecycle(client, officer_token):
    """Create → List → Get → Update → Delete full lifecycle."""
    project = _create_project(client, officer_token)
    project_id = project["id"]
    headers = {"Authorization": f"Bearer {officer_token}"}

    # 1. CREATE two issues
    resp1 = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "Drainage blockage",
            "description": "Storm drain blocked near site entrance, causing waterlogging.",
            "severity": "HIGH",
        },
        headers=headers,
    )
    assert resp1.status_code == 201
    issue1 = resp1.json()

    resp2 = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "Missing safety signage",
            "description": "No caution signs at the construction zone boundary.",
            "severity": "LOW",
        },
        headers=headers,
    )
    assert resp2.status_code == 201
    issue2 = resp2.json()

    # 2. LIST all issues for project
    resp_list = client.get(f"/api/projects/{project_id}/issues")
    assert resp_list.status_code == 200
    issues = resp_list.json()
    assert len(issues) >= 2

    # 3. GET single issue
    resp_get = client.get(f"/api/issues/{issue1['id']}")
    assert resp_get.status_code == 200
    assert resp_get.json()["title"] == "Drainage blockage"

    # 4. UPDATE issue — change severity and status
    resp_update = client.put(
        f"/api/issues/{issue1['id']}",
        json={"severity": "CRITICAL", "status": "IN_PROGRESS"},
        headers=headers,
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["severity"] == "CRITICAL"
    assert updated["status"] == "IN_PROGRESS"

    # 5. RESOLVE issue — should auto-set resolved_date
    resp_resolve = client.put(
        f"/api/issues/{issue1['id']}",
        json={"status": "RESOLVED"},
        headers=headers,
    )
    assert resp_resolve.status_code == 200
    resolved = resp_resolve.json()
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_date"] is not None

    # 6. DELETE issue
    resp_del = client.delete(f"/api/issues/{issue2['id']}", headers=headers)
    assert resp_del.status_code == 200
    assert resp_del.json()["success"] is True

    # 7. Verify deleted issue returns 404
    resp_gone = client.get(f"/api/issues/{issue2['id']}")
    assert resp_gone.status_code == 404


# ─── Test: Severity and status filtering ────────────────────────
def test_issue_filtering(client, officer_token):
    """Verify filtering issues by severity and status query params."""
    project = _create_project(client, officer_token)
    project_id = project["id"]
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Create issues with different severities
    for title, severity in [
        ("Low issue", "LOW"),
        ("Medium issue", "MEDIUM"),
        ("High issue", "HIGH"),
    ]:
        client.post(
            f"/api/projects/{project_id}/issues",
            json={"title": title, "description": f"Description for {title}.", "severity": severity},
            headers=headers,
        )

    # Filter by severity=HIGH
    resp_high = client.get(f"/api/projects/{project_id}/issues?severity=HIGH")
    assert resp_high.status_code == 200
    high_issues = resp_high.json()
    assert all(i["severity"] == "HIGH" for i in high_issues)
    assert len(high_issues) >= 1

    # Filter by status=OPEN (all new issues are OPEN)
    resp_open = client.get(f"/api/projects/{project_id}/issues?status=OPEN")
    assert resp_open.status_code == 200
    assert len(resp_open.json()) >= 3


# ─── Test: 404 for non-existent project and issue ───────────────
def test_issue_not_found(client, officer_token):
    """Verify 404 for non-existent project and issue."""
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Non-existent project
    resp = client.post(
        "/api/projects/99999/issues",
        json={"title": "Ghost issue", "description": "Should fail.", "severity": "LOW"},
        headers=headers,
    )
    assert resp.status_code == 404

    # Non-existent issue
    resp2 = client.get("/api/issues/99999")
    assert resp2.status_code == 404


# ─── Test: Validation Errors (Title, Severity, Status) ──────────
def test_issue_validation_rules(client, officer_token):
    """Verify validation rules for empty title, empty description, and bad enums."""
    project = _create_project(client, officer_token)
    project_id = project["id"]
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Empty title
    resp_empty_title = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "   ", "description": "Valid description.", "severity": "HIGH"},
        headers=headers,
    )
    assert resp_empty_title.status_code == 422 or resp_empty_title.status_code == 400

    # Invalid severity
    resp_bad_sev = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "Valid title", "description": "Valid desc.", "severity": "EXTREME"},
        headers=headers,
    )
    assert resp_bad_sev.status_code == 422 or resp_bad_sev.status_code == 400

    # Invalid status update
    valid_issue = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "Valid Issue", "description": "Valid description text.", "severity": "MEDIUM"},
        headers=headers,
    ).json()

    resp_bad_status = client.put(
        f"/api/issues/{valid_issue['id']}",
        json={"status": "DESTROYED"},
        headers=headers,
    )
    assert resp_bad_status.status_code == 422 or resp_bad_status.status_code == 400


# ─── Test: Issue Summary API ────────────────────────────────────
def test_issue_summary_aggregation(client, officer_token):
    """Verify aggregated issue count summary by status and severity."""
    project = _create_project(client, officer_token)
    project_id = project["id"]
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Create 3 issues: 1 CRITICAL, 1 HIGH, 1 LOW
    resp1 = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "Crit 1", "description": "Critical flaw.", "severity": "CRITICAL"},
        headers=headers,
    )
    resp2 = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "High 1", "description": "High flaw.", "severity": "HIGH"},
        headers=headers,
    )
    resp3 = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "Low 1", "description": "Low flaw.", "severity": "LOW"},
        headers=headers,
    )

    issue1_id = resp1.json()["id"]

    # Mark 1 issue RESOLVED
    client.put(
        f"/api/issues/{issue1_id}",
        json={"status": "RESOLVED"},
        headers=headers,
    )

    # Fetch summary
    resp_sum = client.get(f"/api/projects/{project_id}/issues/summary")
    assert resp_sum.status_code == 200
    summary = resp_sum.json()

    assert summary["total_issues"] == 3
    assert summary["resolved_issues"] == 1
    assert summary["open_issues"] == 2
    assert summary["critical_issues"] == 1
    assert summary["high_severity_issues"] == 1


# ─── Test: Status Transition & Resolved Date Reset ─────────────
def test_issue_status_transition_resolved_date(client, officer_token):
    """Verify resolved_date is set on RESOLVED and reset when reopened."""
    project = _create_project(client, officer_token)
    project_id = project["id"]
    headers = {"Authorization": f"Bearer {officer_token}"}

    issue = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": "Transitional issue", "description": "Testing status lifecycle.", "severity": "MEDIUM"},
        headers=headers,
    ).json()

    # Reopen -> resolved_date is None
    assert issue["resolved_date"] is None

    # Resolve -> resolved_date set
    resolved = client.put(
        f"/api/issues/{issue['id']}",
        json={"status": "RESOLVED"},
        headers=headers,
    ).json()
    assert resolved["resolved_date"] is not None

    # Reopen to IN_PROGRESS -> resolved_date reset to None
    reopened = client.put(
        f"/api/issues/{issue['id']}",
        json={"status": "IN_PROGRESS"},
        headers=headers,
    ).json()
    assert reopened["resolved_date"] is None

