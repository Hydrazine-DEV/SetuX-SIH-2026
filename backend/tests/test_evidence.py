"""
SetuX / VeriX — Evidence & Issue Evidence API Tests
Phase 9: Comprehensive Evidence Management & Security Validation
"""
import io
import pytest


def _create_project_and_issue(client, officer_token):
    """Helper to seed a project and issue for evidence testing."""
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    # 1. Create project
    proj_resp = client.post(
        "/api/projects/",
        json={
            "name": "Evidence Test Project",
            "sector": "Bridge Construction",
            "district": "Nagpur",
            "location": "Nagpur Bypass",
            "original_cost": 1200.0,
            "start_date": "2026-01-01",
            "planned_completion_date": "2026-12-31",
        },
        headers=headers,
    )
    assert proj_resp.status_code in (200, 201)
    project = proj_resp.json()

    # 2. Create issue
    issue_resp = client.post(
        f"/api/projects/{project['id']}/issues",
        json={
            "title": "Foundation Cracks Observed",
            "description": "Hairline cracks detected on Pier 3 during inspection.",
            "severity": "CRITICAL",
        },
        headers=headers,
    )
    assert issue_resp.status_code == 201
    issue = issue_resp.json()

    return project, issue


def test_issue_evidence_upload_and_retrieve(client, officer_token):
    """Test uploading evidence to an issue and retrieving it."""
    project, issue = _create_project_and_issue(client, officer_token)
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Prepare dummy image file
    fake_image_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00\xFF\xDB\x00C\x00"
    file_tuple = ("crack_photo.jpg", io.BytesIO(fake_image_bytes), "image/jpeg")

    # Upload evidence
    upload_resp = client.post(
        f"/api/issues/{issue['id']}/evidence",
        data={"description": "Close-up of Pier 3 hairline crack", "uploaded_by": "Inspector Ramesh"},
        files={"file": file_tuple},
        headers=headers,
    )
    assert upload_resp.status_code == 201
    ev = upload_resp.json()
    assert ev["issue_id"] == issue["id"]
    assert ev["project_id"] == project["id"]
    assert ev["file_name"] == "crack_photo.jpg"
    assert ev["file_type"] == "image"
    assert ev["file_url"].startswith("/uploads/evidence/")

    # List evidence for issue
    list_resp = client.get(f"/api/issues/{issue['id']}/evidence")
    assert list_resp.status_code == 200
    evidence_list = list_resp.json()
    assert len(evidence_list) == 1
    assert evidence_list[0]["id"] == ev["id"]

    # Retrieve single evidence record
    get_item_resp = client.get(f"/api/evidence/item/{ev['id']}")
    assert get_item_resp.status_code == 200
    assert get_item_resp.json()["evidence_id"] == ev["evidence_id"]

    # Delete evidence
    del_resp = client.delete(f"/api/evidence/{ev['id']}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Verify deleted evidence returns 404
    gone_resp = client.get(f"/api/evidence/item/{ev['id']}")
    assert gone_resp.status_code == 404


def test_issue_evidence_security_validation(client, officer_token):
    """Test safety validations: invalid file extensions, executable rejection, and empty files."""
    project, issue = _create_project_and_issue(client, officer_token)
    headers = {"Authorization": f"Bearer {officer_token}"}

    # 1. Executable file extension rejection (.exe)
    exe_file = ("script.exe", io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00"), "application/x-msdownload")
    resp_exe = client.post(
        f"/api/issues/{issue['id']}/evidence",
        files={"file": exe_file},
        headers=headers,
    )
    assert resp_exe.status_code == 400
    assert "not allowed" in resp_exe.json()["detail"].lower()

    # 2. Empty file rejection
    empty_file = ("empty.png", io.BytesIO(b""), "image/png")
    resp_empty = client.post(
        f"/api/issues/{issue['id']}/evidence",
        files={"file": empty_file},
        headers=headers,
    )
    assert resp_empty.status_code == 400
    assert "empty" in resp_empty.json()["detail"].lower()


def test_cross_project_evidence_boundary(client, officer_token):
    """Test that Project B cannot access Project A's issue evidence."""
    project_a, issue_a = _create_project_and_issue(client, officer_token)
    headers = {"Authorization": f"Bearer {officer_token}"}

    # Create Project B
    proj_b_resp = client.post(
        "/api/projects/",
        json={
            "name": "Project B",
            "sector": "Roads",
            "district": "Nashik",
            "original_cost": 300.0,
        },
        headers=headers,
    )
    project_b = proj_b_resp.json()

    # Attempt to query Project A's issue under Project B's URL path
    cross_resp = client.get(f"/api/projects/{project_b['id']}/issues/{issue_a['id']}/evidence")
    assert cross_resp.status_code == 403
    assert "cross-project access denied" in cross_resp.json()["detail"].lower()
