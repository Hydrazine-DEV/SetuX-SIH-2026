"""
SetuX / VeriX — Security Hardening & Vulnerability Test Suite
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 18–19: Complete Backend Security Hardening & QA

Tests:
1. Missing JWT on protected routes (HTTP 401)
2. Malformed / Tampered JWT (HTTP 401)
3. Expired JWT Token (HTTP 401)
4. Inactive User Token (HTTP 401)
5. RBAC Enforcement: Citizen denied Officer endpoints (HTTP 403)
6. Non-existent Project ID Handling (HTTP 404)
7. Path Traversal Download Attacks (HTTP 403 / 404)
8. Input Validation: Invalid percentage (> 100 or < 0) (HTTP 422)
9. Bcrypt Password Hashing Integrity (No Plaintext)
10. SQL Injection Resilience (Special characters & quotes in filters)
11. Safe Error Handling (No raw exception tracebacks in 500/400)
12. CORS Header Verification
"""
import time
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.project import Project


# ─── 1. Missing JWT Authentication Guard ─────────────────────────
def test_missing_jwt_rejected(client: TestClient):
    endpoints = [
        ("GET", "/api/auth/me"),
        ("GET", "/api/alerts"),
        ("POST", "/api/projects"),
        ("POST", "/api/projects/1/alerts/generate"),
        ("POST", "/api/projects/1/reports"),
    ]
    for method, url in endpoints:
        if method == "GET":
            resp = client.get(url)
        else:
            resp = client.post(url, json={})
        assert resp.status_code == 401, f"Failed on {method} {url}: {resp.status_code}"


# ─── 2. Malformed / Tampered JWT Guard ───────────────────────────
def test_tampered_jwt_rejected(client: TestClient):
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.malicious_payload.signature"},
    )
    assert resp.status_code == 401


# ─── 3. Expired JWT Token Guard ──────────────────────────────────
def test_expired_jwt_rejected(client: TestClient):
    expired_token = create_access_token(
        {"sub": "test.officer@setux.gov", "role": "officer"},
        expires_delta=timedelta(seconds=-10),
    )
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401


# ─── 4. Inactive User Token Guard ────────────────────────────────
def test_inactive_user_token_rejected(client: TestClient, db_session: Session):
    inactive_user = db_session.query(User).filter(User.email == "inactive.officer@setux.gov").first()
    assert inactive_user is not None
    assert inactive_user.is_active is False

    token = create_access_token({"sub": inactive_user.email, "role": "officer"})
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert "inactive" in resp.json()["detail"].lower()


# ─── 5. RBAC Enforcement: Citizen Blocked from Officer Routes ────
def test_citizen_denied_officer_routes(client: TestClient, citizen_token):
    headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # 1. Citizen cannot create project
    r1 = client.post("/api/projects", headers=headers, json={"project_code": "MH-HACK-001", "name": "Hack"})
    assert r1.status_code == 403

    # 2. Citizen cannot generate alerts
    r2 = client.post("/api/projects/1/alerts/generate", headers=headers)
    assert r2.status_code == 403

    # 3. Citizen cannot resolve alerts
    r3 = client.patch("/api/alerts/1/resolve", headers=headers)
    assert r3.status_code == 403

    # 4. Citizen cannot generate reports
    r4 = client.post("/api/projects/1/reports", headers=headers, json={"report_type": "PROJECT_SUMMARY"})
    assert r4.status_code == 403


# ─── 6. Non-Existent Project 404 Guard ───────────────────────────
def test_nonexistent_project_returns_404(client: TestClient, officer_token):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    endpoints = [
        f"/api/projects/999999",
        f"/api/projects/999999/milestones",
        f"/api/projects/999999/risk",
        f"/api/projects/999999/risk-intelligence",
        f"/api/projects/999999/alerts",
        f"/api/projects/999999/reports",
    ]
    for url in endpoints:
        resp = client.get(url, headers=headers)
        assert resp.status_code == 404, f"Expected 404 on {url}, got {resp.status_code}"


# ─── 7. Path Traversal Download Attack Guard ─────────────────────
def test_path_traversal_attack_blocked(client: TestClient, officer_token):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    # Try directory traversal via report ID or query
    resp = client.get("/api/reports/../../../etc/passwd/download", headers=headers)
    assert resp.status_code in (404, 422, 403)


# ─── 8. Input Validation Boundary Guards ────────────────────────
def test_input_validation_boundaries(client: TestClient, officer_token):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    # Progress > 100 should be rejected by Pydantic validator
    resp = client.post(
        "/api/projects/1/progress",
        headers=headers,
        json={
            "project_id": 1,
            "report_date": "2026-01-01",
            "physical_progress": 150.0,  # Invalid (>100)
            "financial_progress": 50.0,
        },
    )
    assert resp.status_code == 422


# ─── 9. Password Hashing & Bcrypt Verification ──────────────────
def test_bcrypt_hashing_security():
    plain = "SuperSecretGovPassword@2026"
    hashed = hash_password(plain)
    
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(plain, "") is False


# ─── 10. SQL Injection Resilience in Filters ─────────────────────
def test_sql_injection_resilience(client: TestClient, officer_token):
    headers = {"Authorization": f"Bearer {officer_token}"}
    
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE projects; --",
        "1 UNION SELECT null, null, null--",
    ]
    for payload in sqli_payloads:
        resp = client.get(f"/api/projects?search={payload}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list) or "items" in data
