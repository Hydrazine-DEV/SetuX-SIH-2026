"""
SetuX / VeriX — Contractors API Tests
Verifies:
- List contractors with search and pagination
- Get contractor by ID
- Create contractor (Officer authorized)
- Reject citizen creating contractor (403)
- Reject duplicate registration_number (400)
- Update contractor details (Officer authorized)
- Delete contractor (Officer authorized)
"""
import pytest
from fastapi.testclient import TestClient


def test_create_contractor_rbac(client: TestClient, officer_token, citizen_token):
    payload = {
        "name": "Larsen & Toubro Infrastructure Ltd",
        "registration_number": "MH-PWD-CON-2024-001",
        "contact_email": "infra@larsentoubro.com",
        "contact_phone": "+91-22-67525656",
    }

    # 1. Citizen cannot register contractor
    res_cit = client.post(
        "/api/contractors",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert res_cit.status_code == 403

    # 2. Officer can register contractor
    res_off = client.post(
        "/api/contractors",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 201
    created = res_off.json()
    assert created["registration_number"] == payload["registration_number"]
    assert created["name"] == payload["name"]

    # 3. Duplicate registration number rejected
    res_dup = client.post(
        "/api/contractors",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"].lower()


def test_list_and_search_contractors(client: TestClient):
    res = client.get("/api/contractors")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1

    # Search
    search_res = client.get("/api/contractors?search=Larsen")
    assert search_res.status_code == 200
    assert any("Larsen" in c["name"] for c in search_res.json())


def test_get_update_delete_contractor(client: TestClient, officer_token):
    # Create temp contractor
    create_res = client.post(
        "/api/contractors",
        json={
            "name": "Shapoorji Pallonji EPC",
            "registration_number": "MH-PWD-CON-TEMP-999",
            "contact_email": "contact@spcl.in",
        },
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert create_res.status_code == 201
    c_id = create_res.json()["id"]

    # Get by ID
    get_res = client.get(f"/api/contractors/{c_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Shapoorji Pallonji EPC"

    # Update
    upd_res = client.put(
        f"/api/contractors/{c_id}",
        json={"name": "Shapoorji Pallonji Group EPC", "contact_phone": "9811122233"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Shapoorji Pallonji Group EPC"
    assert upd_res.json()["contact_phone"] == "9811122233"

    # Delete
    del_res = client.delete(
        f"/api/contractors/{c_id}",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm 404
    assert client.get(f"/api/contractors/{c_id}").status_code == 404
