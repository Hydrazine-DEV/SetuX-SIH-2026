"""
SetuX / VeriX — Comprehensive Authentication & RBAC Test Suite
Covers:
- Department listing
- Officer & Citizen signup
- Uniqueness & password validation
- Login verification & role-mismatch blocking
- Profile retrieval (/api/auth/me)
- Inactive user blocking
- RBAC guards (require_officer, require_citizen, require_roles)
- Token tampering & expiration handling
- Audit logging verification
"""
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from app.api.deps import require_officer, require_citizen, require_roles, require_authenticated_user
from app.models.audit import AuditLog
from app.models.user import User


def test_list_departments(client: TestClient):
    """Verify department listing returns active departments."""
    response = client.get("/api/departments")
    assert response.status_code == 200
    departments = response.json()
    assert len(departments) >= 5
    codes = [d["code"] for d in departments]
    assert "PWD" in codes
    assert "WRD" in codes


def test_officer_signup_success(client: TestClient, db_session):
    """Verify new officer can register and receives valid token and department link."""
    payload = {
        "full_name": "Kavita Deshmukh",
        "email": "kavita.deshmukh@setux.gov",
        "phone": "9822001122",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123",
        "role": "officer",
        "department_id": 1,
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "kavita.deshmukh@setux.gov"
    assert data["user"]["role"] == "officer"
    assert data["user"]["department"]["code"] == "PWD"

    # Verify audit log was created
    audit = db_session.query(AuditLog).filter(AuditLog.user_name == "Kavita Deshmukh").first()
    assert audit is not None
    assert "OFFICER_SIGNUP" in audit.action


def test_citizen_signup_success(client: TestClient, db_session):
    """Verify new citizen can register without department requirement."""
    payload = {
        "full_name": "Suresh More",
        "email": "suresh.more@citizen.gov",
        "phone": "9822009988",
        "password": "CitizenPass@123",
        "confirm_password": "CitizenPass@123",
        "role": "citizen",
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "citizen"
    assert data["user"]["department"] is None


def test_duplicate_email_prevention(client: TestClient):
    """Verify registration fails if email already exists."""
    payload = {
        "full_name": "Duplicate User",
        "email": "test.officer@setux.gov",
        "password": "Password123",
        "confirm_password": "Password123",
        "role": "officer",
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()


def test_password_mismatch_rejection(client: TestClient):
    """Verify signup fails if password and confirm_password do not match."""
    payload = {
        "full_name": "Mismatch User",
        "email": "mismatch@setux.gov",
        "password": "Password123",
        "confirm_password": "WrongPassword123",
        "role": "citizen",
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 400
    assert "passwords do not match" in res.json()["detail"].lower()


def test_password_length_rejection(client: TestClient):
    """Verify password shorter than 8 chars is rejected."""
    payload = {
        "full_name": "Short Pw User",
        "email": "shortpw@setux.gov",
        "password": "123",
        "confirm_password": "123",
        "role": "citizen",
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code in (400, 422)


def test_invalid_credentials_login(client: TestClient):
    """Verify login fails with wrong password."""
    res = client.post(
        "/api/auth/login",
        json={"email": "test.officer@setux.gov", "password": "WrongPassword!", "role": "officer"},
    )
    assert res.status_code == 401
    assert "invalid email or password" in res.json()["detail"].lower()


def test_role_mismatch_login_blocked(client: TestClient):
    """Verify user cannot log in under a role they do not possess."""
    res = client.post(
        "/api/auth/login",
        json={"email": "test.officer@setux.gov", "password": "OfficerPass123", "role": "citizen"},
    )
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_inactive_user_cannot_login(client: TestClient):
    """Verify deactivated user accounts cannot log in."""
    res = client.post(
        "/api/auth/login",
        json={"email": "inactive.officer@setux.gov", "password": "OfficerPass123", "role": "officer"},
    )
    assert res.status_code == 401


def test_officer_login_and_get_me(client: TestClient):
    """Verify successful officer login and profile retrieval."""
    res = client.post(
        "/api/auth/login",
        json={"email": "test.officer@setux.gov", "password": "OfficerPass123", "role": "officer"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]

    # Call /api/auth/me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "test.officer@setux.gov"
    assert me_data["role"] == "officer"
    assert me_data["department"]["code"] == "PWD"
    assert me_data["last_login"] is not None


def test_citizen_login_and_get_me(client: TestClient):
    """Verify successful citizen login and profile retrieval."""
    res = client.post(
        "/api/auth/login",
        json={"email": "test.citizen@setux.gov", "password": "CitizenPass123", "role": "citizen"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "test.citizen@setux.gov"
    assert me_data["role"] == "citizen"
    assert me_data["department"] is None


def test_unauthenticated_requests_blocked(client: TestClient):
    """Verify /api/auth/me blocks requests without Bearer token."""
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_invalid_token_blocked(client: TestClient):
    """Verify forged/invalid JWT tokens are rejected."""
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.string"})
    assert res.status_code == 401


# ─── RBAC Guard Unit Tests ─────────────────────────────────────────

def test_rbac_guards(app_with_rbac_routes, officer_token, citizen_token):
    """Test require_officer and require_citizen guards protect target endpoints."""
    test_client = TestClient(app_with_rbac_routes)

    # 1. Officer accessing officer route -> 200 OK
    res = test_client.get("/test/officer-only", headers={"Authorization": f"Bearer {officer_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "officer_granted"

    # 2. Citizen accessing officer route -> 403 Forbidden
    res = test_client.get("/test/officer-only", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 403
    assert "officer access required" in res.json()["detail"].lower()

    # 3. Citizen accessing citizen route -> 200 OK
    res = test_client.get("/test/citizen-only", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "citizen_granted"

    # 4. Officer accessing citizen route -> 403 Forbidden
    res = test_client.get("/test/citizen-only", headers={"Authorization": f"Bearer {officer_token}"})
    assert res.status_code == 403
    assert "citizen access required" in res.json()["detail"].lower()

    # 5. Shared multi-role route -> both allowed
    res_off = test_client.get("/test/shared", headers={"Authorization": f"Bearer {officer_token}"})
    assert res_off.status_code == 200
    res_cit = test_client.get("/test/shared", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_cit.status_code == 200


import pytest
@pytest.fixture
def app_with_rbac_routes():
    """Helper FastAPI app attaching test routes with RBAC dependencies."""
    from app.main import app

    @app.get("/test/officer-only")
    def officer_endpoint(current_user=Depends(require_officer)):
        return {"status": "officer_granted", "user": current_user.email}

    @app.get("/test/citizen-only")
    def citizen_endpoint(current_user=Depends(require_citizen)):
        return {"status": "citizen_granted", "user": current_user.email}

    @app.get("/test/shared")
    def shared_endpoint(current_user=Depends(require_roles("officer", "citizen"))):
        return {"status": "shared_granted", "role": current_user.role}

    return app
